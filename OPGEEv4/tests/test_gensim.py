from opgee.tool import opg
from opgee.mcs.simulation import Simulation
from .utils_for_tests import tmpdir

def test_gensim():
    sim_dir = tmpdir('test-sim-dir')
    field_name = 'gas_lifting_field'
    trials = 100
    cmdline = f'gensim -t {trials} -s {sim_dir} -a example -f {field_name} --overwrite'
    opg(cmdline)

    sim = Simulation(sim_dir)
    df = sim.field_trial_data(field_name)
    assert len(df) == trials
