#
# OPGEE Attribute and related classes
#
# Authors: Richard Plevin and Wennan Long
#
# Copyright (c) 2021-2022 The Board of Trustees of the Leland Stanford Junior
# University. See LICENSE.txt for license details.
#
import pandas as pd

from .core import STP
from .core import TemperaturePressure
from .log import getLogger
from .stream import PHASE_LIQUID, Stream
from .thermodynamics import Oil, Gas, Water

_logger = getLogger(__name__)


# TODO: improve this to use temp and press
def combine_streams(streams, API):
    """
    Thermodynamically combine multiple streams' components into a new
    anonymous Stream. This is used on input streams since it makes no
    sense for output streams.

    :param streams: (list of Streams) the Streams to combine
    :param API (pint.Quantity): API value

    :return: (Stream) if len(streams) > 1, returns a new Stream. If
       len(streams) == 1, the input stream (streams[0]) is returned.
    """
    if len(streams) == 1:  # corner case
        return streams[0]

    non_empty_streams = [stream for stream in streams if not stream.is_uninitialized()]
    non_empty_streams_pressure = [stream.tp.P for stream in non_empty_streams]

    if not non_empty_streams:
        return Stream("empty_stream", TemperaturePressure(None, None))

    comp_matrix = sum([stream.components for stream in streams])

    stream_temperature = pd.Series([stream.tp.T.to("kelvin").m for stream in non_empty_streams],
                                   dtype="pint[kelvin]")

    stream_specific_heat = pd.Series([mixture_specific_heat_capacity(API, stream).m for
                                      stream in non_empty_streams],
                                     dtype="pint[btu/degF/day]")

    stream_sp_heat_sum = stream_specific_heat.sum()
    if stream_sp_heat_sum.m != 0.0:
        temperature = (stream_temperature * stream_specific_heat).sum() / stream_sp_heat_sum
        temperature = temperature.to("degF")
        min_pressure = min(non_empty_streams_pressure)
        stream = Stream('combined',
                        TemperaturePressure(temperature, max(STP.P, min_pressure)),
                        comp_matrix=comp_matrix)
    else:
        stream = Stream('empty_stream', tp=STP)
    return stream


def mixture_specific_heat_capacity(API, stream):
    """
    cp_mix = (mass_1/mass_mix)cp_1 + (mass_2/mass_mix)cp_2 + ...

    :param API:
    :param stream:
    :return: (float) heat capacity of mixture (unit = btu/degF/day)
    """
    temperature = stream.tp.T
    oil_heat_capacity = stream.hydrocarbon_rate(PHASE_LIQUID) * Oil.specific_heat(API, temperature)
    water_heat_capacity = Water.heat_capacity(stream)
    gas_heat_capacity = Gas.heat_capacity(stream)

    heat_capacity = oil_heat_capacity + water_heat_capacity + gas_heat_capacity
    return heat_capacity.to("btu/delta_degF/day")
