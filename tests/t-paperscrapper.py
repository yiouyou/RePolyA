import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya.paper._paperscraper import QUERY_FN_DICT
from repolya.paper._paperscraper.postprocessing import aggregate_paper
from repolya.paper._paperscraper.utils import get_filename_from_query, load_jsonl
from repolya.paper._paperscraper.plotting import plot_comparison

from repolya.paper.query2jsonl import query2jsonl
from repolya._const import PAPER_JSONL, WORKSPACE_ROOT


# Define search terms and their synonyms
ml = ['Deep learning', 'Neural Network', 'Machine learning']
mol = ['molecule', 'molecular', 'drug', 'ligand', 'compound']
gnn = ['gcn', 'gnn', 'graph neural', 'graph convolutional', 'molecular graph']
smiles = ['SMILES', 'Simplified molecular']
fp = ['fingerprint', 'molecular fingerprint', 'fingerprints']

# Define queries
queries = [[ml, mol, smiles], [ml, mol, fp], [ml, mol, gnn]]

##### 先生成搜索结果数据
# for _query in queries:
#     query2jsonl(_query)
# exit()

##### 再制图
start_year=2019
last_year=2023

data_dict = dict()
for _query in queries:
    _qn = get_filename_from_query(_query)
    print(_qn)
    data_dict[_qn] = dict()
    for i in QUERY_FN_DICT.keys():
        i_file = str(PAPER_JSONL / f"{i}_{_qn}")
        data = load_jsonl(i_file)
        data_dict[_qn][i], filtered = aggregate_paper(
            data=data,
            start_year=start_year, last_year=last_year, bins_per_year=1,
            filtering=True,
            filter_keys=_query,
            return_filtered=True
        )
print(data_dict)
data_keys = [
    'deeplearning_molecule_fingerprint.jsonl',
    'deeplearning_molecule_smiles.jsonl', 
    'deeplearning_molecule_gcn.jsonl'
]
plot_comparison(
    data_dict,
    data_keys,
    x_ticks=[str(year) for year in range(start_year, last_year+1)],
    title_text="'Deep Learning' AND 'Molecule' AND X",
    keyword_text=['Fingerprint', 'SMILES', 'Graph'],
    figpath=str(WORKSPACE_ROOT / 'mol_representation.pdf')
)

