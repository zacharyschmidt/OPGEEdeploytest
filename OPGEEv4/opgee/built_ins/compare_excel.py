from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
#from scipy import stats

# Could load this from opgee.built_ins.compare_plugin (RP)

process_translator = {
    'Acid gas removal' : 'AcidGasRemoval',
    'CO2 gas reinjection compressor' : 'GasReinjectionCompressor',
    'CO2 membrane' : 'CO2Membrane',
    'Chiller' : 'PreMembraneChiller',
    'Crude oil dewatering' : 'CrudeOilDewatering',
    'Crude oil stabilization' : 'CrudeOilStabilization',
    'Crude oil storage' : 'CrudeOilStorage',
    'Crude oil transport' : 'CrudeOilTransport',
    'Demethanizer' : 'Demethanizer',
    'Downhole pump (Lifting)' : 'DownholePump',
    'Flaring' : 'Flaring',
    'Gas dehydration' : 'GasDehydration',
    'Gas distribution' : 'GasDistribution',
    'Gas flooding compressor' : 'GasReinjectionCompressor',
    'Gas gathering' : 'GasGathering',
    'Gas lifting compressor' : 'GasLiftingCompressor',
    'Gas storage wells' : 'StorageWell',
    'Gas transmission' : 'TransmissionCompressor',
    'HC gas reinjection compressor' : 'GasReinjectionCompressor',
    'Heavy oil dilution' : 'HeavyOilDilution',
    'Heavy oil upgrading' : 'HeavyOilUpgrading',
    'Liquefaction' : 'LNGLiquefaction',
    'Water treatment' : 'WaterTreatment',
    'Mining' : 'BitumenMining',
    'Petcoke handling and storage' : 'PetrocokeTransport',
    'Post-storage compressor' : 'PostStorageCompressor',
    'Pre-membrane compressor' : 'PreMembraneCompressor',
    'Regasification' : 'LNGRegasification',
    'Ryan-Holmes unit' : 'RyanHolmes',
    'Separation' : 'Separation',
    'Sour gas reinjection compressor' : 'SourGasCompressor',
    'Steam generation' : 'SteamGeneration',
    'Storage compressor' : 'StorageCompressor',
    'Storage separator' : 'StorageSeparator',
    'Transport' : 'LNGTransport',
    'VRU compressor' : 'VRUCompressor',
    'Venting' : 'Venting',
    'Water injection' : 'WaterInjection',
    'Exploration' : 'Exploration',
    'Drilling & Development' : 'Drilling',
    'Diluent transport' : 'HeavyOilDilution',
    'Makeup water treatment': 'WaterTreatment',
    'Produced water treatment': 'WaterTreatment',
}

dirpath = '/Users/rjp/Projects/OPGEE Python/comparison/'

status = pd.read_csv(dirpath + "status_excel_test_fields.csv", index_col='status')


def read_results(filename):
    df = pd.read_csv(dirpath + filename, index_col='process')
    df = df.rename(index=process_translator).sort_index(axis='rows')
    return df

def save_fig(fig, filename):
    fig.savefig(dirpath + filename, bbox_inches='tight')

df1 = read_results("comparison.csv")
df2 = read_results("test_fields_excel.csv")

good_fields = [c for c in status.columns if status[c]["Status"] == "OK" and c != 'Field 1']

python = df1.loc[df2.index]
excel = df2[python.columns]

excel = excel[good_fields]
python = python[good_fields]

sns.set_context('talk')
sns.set_style("darkgrid")

fig, ax = plt.subplots(figsize=(8, 8))
plt.scatter(excel.sum(), python.sum(), alpha=0.5)
plt.xlim(0, 5200)
plt.ylim(0, 5200)
plt.ylabel("OPGEE v4")
plt.xlabel("OPGEE v3")
plt.title("V3 vs. V4 total energy consumption (mmbtu/day)", pad=20)
ax.set_aspect('equal')

save_fig(fig, 'V3-vs-V4-total-energy-consumption.pdf')

absolute_error = abs(excel - python).T

# def rsquared(x, y):
#     """
#     Return R^2 where x and y are array-like.
#     """
#     slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
#     return r_value**2
#
# x = excel.sum().to_numpy()
# y = python.sum().to_numpy()


with sns.plotting_context("notebook"):
    fig, ax = plt.subplots(figsize=(30,5))
    absolute_error.boxplot(ax=ax)
    labels = ax.get_xticklabels()
    ax.set_xticklabels(labels, rotation=90)
    ax.set_ylim(0, 2000)
    save_fig(fig, 'absolute-error-boxplot.pdf')

median_error = absolute_error.median().sort_values(ascending=False)
print(median_error)
process_name = median_error.index[:5].to_numpy()

with sns.plotting_context("talk"):
    for name in process_name:
        fig, ax = plt.subplots(figsize=(8, 8))
        plt.scatter(excel.loc[[name]], python.loc[[name]], alpha=0.5)
        plt.xlim(0, 20000)
        plt.ylim(0, 20000)
        plt.ylabel("OPGEE v4")
        plt.xlabel("OPGEE v3")

        ax.ticklabel_format(style='sci', scilimits=(3, 3), axis='both')

        ax.set_aspect('equal')
        plt.title(name + " Comparison (mmbtu/day)", pad=20)
        save_fig(fig, name + "_comparison.pdf")


# excel_RH = excel.loc[["GasLiftingCompressor"]]
# python_RH = python.loc[["GasLiftingCompressor"]]
#
# for i, j in excel_RH.iteritems():
#     if python_RH[i].isnull().to_numpy()[0] or excel_RH[i].isnull().to_numpy()[0]:
#         continue
#     if python_RH[i].to_numpy()[0] == excel_RH[i].to_numpy()[0]:
#         continue
#
#     print(i)
#
#
# python_RH["Field 2"].to_numpy()[0]
#
# excel_RH["Field 2"]
