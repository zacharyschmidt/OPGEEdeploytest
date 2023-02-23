#
# CrudeOilTransport class
#
# Author: Wennan Long
#
# Copyright (c) 2021-2022 The Board of Trustees of the Leland Stanford Junior University.
# See LICENSE.txt for license details.
#
import pandas as pd

from .compressor import Compressor
from .shared import get_energy_carrier, predict_blower_energy_use, get_bounded_value
from .. import ureg
from ..core import STP
from ..emissions import EM_COMBUSTION, EM_FUGITIVES
from ..error import OpgeeException
from ..log import getLogger
from ..process import Process
from ..process import run_corr_eqns
from ..stream import PHASE_GAS
from ..thermodynamics import ChemicalInfo

_logger = getLogger(__name__)


class Demethanizer(Process):
    def _after_init(self):
        super()._after_init()
        self.field = field = self.get_field()
        self.gas = field.gas
        self.feed_press_demethanizer = self.attr("feed_press_demethanizer")
        self.column_pressure = self.attr("column_pressure")
        self.methane_to_NLG_ratio = self.attr("methane_to_NLG_ratio")
        self.demethanizer_tbl = field.model.demethanizer
        self.mol_per_scf = field.model.const("mol-per-scf")
        self.eta_reboiler_demethanizer = self.attr("eta_reboiler_demethanizer")
        self.air_cooler_speed_reducer_eff = self.attr("air_cooler_speed_reducer_eff")
        self.air_cooler_delta_T = self.attr("air_cooler_delta_T")
        self.air_cooler_fan_eff = self.attr("air_cooler_fan_eff")
        self.air_cooler_press_drop = self.attr("air_cooler_press_drop")
        self.water_press = field.water.density() * \
                           self.air_cooler_press_drop * \
                           field.model.const("gravitational-acceleration")
        self.eta_compressor = self.attr("eta_compressor")
        self.prime_mover_type = self.attr("prime_mover_type")

    def run(self, analysis):
        self.print_running_msg()
        field = self.field

        # mass rate
        input = self.find_input_stream("gas for demethanizer")
        if input.is_uninitialized():
            return

        loss_rate = self.venting_fugitive_rate()
        gas_fugitives = self.set_gas_fugitives(input, loss_rate)

        # Demethanizer modeling based on Aspen HYSYS
        # Input values for variable getting from HYSYS
        variable_bound_dict = {"feed_gas_press": [600.0, 1000.0],  # unit in psia
                               "column_press": [155.0, 325.0],  # unit in psia
                               "methane_to_NGL_ratio": [0.01, 0.05],
                               "inlet_C1_mol_frac": [0.50, 0.95],
                               "inlet_C2_mol_frac": [0.05, 0.95]}
        feed_gas_press =\
            get_bounded_value(self.feed_press_demethanizer.to("psia").m, "feed_gas_press", variable_bound_dict)
        column_press =\
            get_bounded_value(self.column_pressure.to("psia").m, "column_press", variable_bound_dict)
        methane_to_NGL_ratio =\
            get_bounded_value(self.methane_to_NLG_ratio.to("frac").m, "methane_to_NGL_ratio", variable_bound_dict)

        feed_gas_mol_frac = self.gas.component_molar_fractions(input)

        if "C1" not in feed_gas_mol_frac.index:
            _logger.warning(f"Feed gas does not contain C1")
            inlet_C1_mol_frac = 0
        else:
            inlet_C1_mol_frac =\
                get_bounded_value(feed_gas_mol_frac["C1"].to("frac").m, "inlet_C1_mol_frac", variable_bound_dict)

        if "C2" not in feed_gas_mol_frac.index:
            _logger.warning(f"Feed gas does not contain C2")
            inlet_C2_mol_frac = 0
        else:
            inlet_C2_mol_frac =\
                get_bounded_value(feed_gas_mol_frac["C2"].to("frac").m, "inlet_C2_mol_frac", variable_bound_dict)

        gas_volume_rate = self.gas.volume_flow_rate_STP(input)

        # Multiplier for gas load in correlation equation
        multiplier = 99.8
        scale_value = gas_volume_rate.to("mmscf/day").m / multiplier

        x1 = feed_gas_press
        x2 = column_press
        x3 = methane_to_NGL_ratio
        x4 = inlet_C1_mol_frac
        x5 = inlet_C2_mol_frac
        corr_result_df = run_corr_eqns(x1, x2, x3, x4, x5, self.demethanizer_tbl)
        reboiler_heavy_duty = ureg.Quantity(max(0., corr_result_df.loc["Reboiler", :].sum() * scale_value), "kW")
        cooler_thermal_load = ureg.Quantity(max(0., corr_result_df.loc["HEX", :].sum() * scale_value), "kW")
        NGL_label = ["NGL C1", "NGL C2", "NGL C3", "NGL C4"]
        fuel_gas_label = ["fuel gas C1", "fuel gas C2", "fuel gas C3", "fuel gas C4"]
        hydrocarbon_label = ["C1", "C2", "C3", "C4"]
        NGL_mol_frac = pd.Series({name: max(0, corr_result_df.loc[tbl_name, :].sum()) for name, tbl_name in
                                  zip(hydrocarbon_label, NGL_label)},
                                 dtype="pint[frac]")
        fuel_gas_mol_frac = pd.Series({name: max(0, corr_result_df.loc[tbl_name, :].sum()) for name, tbl_name in
                                       zip(hydrocarbon_label, fuel_gas_label)},
                                      dtype="pint[frac]")

        hydrocarbon_mol_rate = pd.Series({name: self.gas.molar_flow_rate(input, name) for name in hydrocarbon_label})

        if NGL_mol_frac["C2"].m == 0 or (
                fuel_gas_mol_frac["C1"] - NGL_mol_frac["C1"] * fuel_gas_mol_frac["C2"] / NGL_mol_frac["C2"]).m == 0:
            fuel_gas_prod = ureg.Quantity(0, "mole/day")
        else:
            fuel_gas_prod = \
                (hydrocarbon_mol_rate["C1"] - NGL_mol_frac["C1"] / NGL_mol_frac["C2"] * hydrocarbon_mol_rate["C2"]) / \
                (fuel_gas_mol_frac["C1"] - NGL_mol_frac["C1"] * fuel_gas_mol_frac["C2"] / NGL_mol_frac["C2"])

        reboiler_fuel_use = reboiler_heavy_duty * self.eta_reboiler_demethanizer
        cooler_energy_consumption = predict_blower_energy_use(self, cooler_thermal_load)

        fuel_gas_mass = fuel_gas_prod * fuel_gas_mol_frac * ChemicalInfo.mol_weight(fuel_gas_mol_frac.index)

        gas_to_gather = self.find_output_stream("gas for gas partition")
        gas_to_gather.copy_flow_rates_from(input)
        gas_to_gather.subtract_rates_from(gas_fugitives)
        gas_to_gather.set_rates_from_series(fuel_gas_mass, PHASE_GAS, upper_bound_stream=input)

        gas_to_LNG = self.find_output_stream("gas for NGL")
        gas_to_LNG.copy_flow_rates_from(input)
        gas_to_LNG.tp.set(T=STP.T)
        gas_to_LNG.subtract_rates_from(gas_to_gather)

        self.set_iteration_value(gas_to_gather.total_flow_rate() + gas_to_LNG.total_flow_rate())

        # TODO: ethane to petrochemicals

        input_tp = input.tp

        # inlet boosting compressor
        inlet_compressor_energy_consump, _, _ = \
            Compressor.get_compressor_energy_consumption(field,
                                                         self.prime_mover_type,
                                                         self.eta_compressor,
                                                         self.feed_press_demethanizer / input_tp.P,
                                                         gas_to_gather,
                                                         inlet_tp=input.tp)

        # outlet compressor
        feed_gas_exit_press = ureg.Quantity(corr_result_df.loc["fuel gas pressure", :].sum(), "psia")
        outlet_compressor_energy_consump, _, _ = \
            Compressor.get_compressor_energy_consumption(field,
                                                         self.prime_mover_type,
                                                         self.eta_compressor,
                                                         input_tp.P / feed_gas_exit_press,
                                                         gas_to_gather,
                                                         inlet_tp=input.tp)

        # energy-use
        energy_use = self.energy
        energy_carrier = get_energy_carrier(self.prime_mover_type)
        energy_use.set_rate(energy_carrier,
                            inlet_compressor_energy_consump + outlet_compressor_energy_consump + reboiler_fuel_use)
        energy_use.set_rate("Electricity", cooler_energy_consumption)

        # import/export
        self.set_import_from_energy(energy_use)

        # emissions
        emissions = self.emissions
        energy_for_combustion = energy_use.data.drop("Electricity")
        combustion_emission = (energy_for_combustion * self.process_EF).sum()
        emissions.set_rate(EM_COMBUSTION, "CO2", combustion_emission)

        emissions.set_from_stream(EM_FUGITIVES, gas_fugitives)
