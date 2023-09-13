import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya.paper._paperqa.contrib import ZoteroDB
from repolya.paper._paperqa import Docs
from repolya._const import PAPER_PDF
from repolya._log import logger_paper

_storage = PAPER_PDF

# _id = os.getenv("ZOTERO_USER_ID")
# print(f"zotero ID: {_id}")

_fujun = os.getenv("ZOTERO_GROUP_FUJUN")
print(f"zotero FUJUN: {_fujun}")

docs = Docs()
zotero = ZoteroDB(
  library_id=_fujun,
  library_type="group",
  storage=_storage
)

_z = zotero.iterate(limit=25)

for item in _z:
    if item.num_pages > 40:
        continue
    print(f"{'-'*40}")
    print(f"{item.pdf}")
    print(f"{item.title}")
    print(f"{item.num_pages}")
    _abs = item.details["data"]["abstractNote"]
    print(f"{_abs}")
    # print(f"{item.key}")
    # print(f"{item.zotero_key}")
    print(f"{'-'*40}")
    try:
        docs.add(item.pdf, docname=item.key)
    except Exception as e:
        logger_paper.info(f"{item.pdf} is corrupt: {e}")

# {
#   'key': 'X37H6DMJ', 
#   'version': 2, 
#   'library': {
#     'type': 'group', 
#     'id': 5172571, 
#     'name': 'fujun', 
#     'links': {'alternate': {'href': 'https://www.zotero.org/groups/fujun', 'type': 'text/html'}}
#   }, 
#   'links': {
#     'self': {'href': 'https://api.zotero.org/groups/5172571/items/X37H6DMJ', 
#     'type': 'application/json'}, 
#     'alternate': {'href': 'https://www.zotero.org/groups/fujun/items/X37H6DMJ', 'type': 'text/html'}
#   }, 
#   'meta': {
#     'createdByUser': {
#       'id': 12303562, 
#       'username': 'sz112358', 
#       'name': '', 
#       'links': {'alternate': {'href': 'https://www.zotero.org/sz112358', 'type': 'text/html'}}
#     }, 
#     'creatorSummary': 'Sun et al.', 
#     'parsedDate': '2023-08', 
#     'numChildren': 1
#   }, 
#   'data': {
#     'key': 'X37H6DMJ', 
#     'version': 2, 
#     'itemType': 'journalArticle', 
#     'title': 'Anxiety adds the risk of cognitive progression and is associated with axon/synapse degeneration among cognitively unimpaired older adults', 
#     'creators': [{'creatorType': 'author', 'firstName': 'Lin', 'lastName': 'Sun'}, {'creatorType': 'author', 'firstName': 'Wei', 'lastName': 'Li'}, {'creatorType': 'author', 'firstName': 'Qi', 'lastName': 'Qiu'}, {'creatorType': 'author', 'firstName': 'Yang', 'lastName': 'Hu'}, {'creatorType': 'author', 'firstName': 'Zhi', 'lastName': 'Yang'}, {'creatorType': 'author', 'firstName': 'Shifu', 'lastName': 'Xiao'}, {'creatorType': 'author', 'name': "Alzheimer's Disease Neuroimaging Initiative"}], 
#     'abstractNote': "BACKGROUND: Mental symptoms have been shown to be associated with dementia. As the most common neuropsychiatric disorder, it is unclear whether and why anxiety increases the risk of cognitive progression in elderly.\nMETHODS: The aim of this study was to investigate the longitudinal effects of anxiety on cognitive impairment in non-dementia elderly and to explore the underlying biological processes using multi-omics including microarray-based transcriptomics, mass spectrometry-based proteomics and metabolomics, cerebrospinal fluid (CSF) biochemical markers, and brain diffusion tensor imaging (DTI). The Alzheimer's Disease Neuroimaging Initiative (ADNI), Chinese Longitudinal Healthy Longevity Survey (CLHLS) and Shanghai Mental Health Centre (SMHC) cohorts were included.\nFINDINGS: Anxiety was found to increase the risk of subsequent cognitive progression in the ADNI, and a similar result was observed in the CLHLS cohort. Enrichment analysis indicated activated axon/synapse pathways and suppressed mitochondrial pathways in anxiety, the former confirmed by deviations in frontolimbic tract morphology and altered levels of axon/synapse markers, and the latter supported by decreased levels of carnitine metabolites. Mediation analysis revealed that anxiety's effect on the longitudinal cognition was mediated by brain tau burden. Correlations of mitochondria-related expressed genes with axon/synapse proteins, carnitine metabolites, and cognitive changes were found.\nINTERPRETATION: This study provides cross-validated epidemiological and biological evidence that anxiety is a risk factor for cognitive progression in non-dementia elderly, and that axon/synapse damage in the context of energy metabolism imbalance may contribute to this phenomenon.\nFUNDING: The National Natural Science Foundation of China (82271607, 81971682, and 81830059) for data analysis and data collection.", 
#     'publicationTitle': 'EBioMedicine', 
#     'volume': '94', 
#     'issue': '', 
#     'pages': '104703', 
#     'date': '2023-08', 
#     'series': '', 
#     'seriesTitle': '', 
#     'seriesText': '', 
#     'journalAbbreviation': 'EBioMedicine', 
#     'language': 'eng', 
#     'DOI': '10.1016/j.ebiom.2023.104703', 
#     'ISSN': '2352-3964', 
#     'shortTitle': '', 
#     'url': '', 
#     'accessDate': '', 
#     'archive': '', 
#     'archiveLocation': '', 
#     'libraryCatalog': 'PubMed', 
#     'callNumber': '', 
#     'rights': '', 
#     'extra': 'PMID: 37429081\nPMCID: PMC10435838', 
#     'tags': [{'tag': 'Aged', 'type': 1}, {'tag': 'Alzheimer Disease', 'type': 1}, {'tag': 'Amyloid beta-Peptides', 'type': 1}, {'tag': 'Anxiety', 'type': 1}, {'tag': 'Axon/synapse damage', 'type': 1}, {'tag': 'Biomarkers', 'type': 1}, {'tag': 'China', 'type': 1}, {'tag': 'Cognition', 'type': 1}, {'tag': 'Cognitive Dysfunction', 'type': 1}, {'tag': 'Cognitive progression', 'type': 1}, {'tag': 'Diffusion Tensor Imaging', 'type': 1}, {'tag': 'Disease Progression', 'type': 1}, {'tag': 'Energy metabolism', 'type': 1}, {'tag': 'Humans', 'type': 1}, {'tag': 'Mitochondrial function', 'type': 1}, {'tag': 'tau Proteins', 'type': 1}], 
#     'collections': [], 
#     'relations': {}, 
#     'dateAdded': '2023-09-07T08:20:04Z', 
#     'dateModified': '2023-09-07T08:20:04Z'
#   }
# }


while True:
    user_query = input("Please enter your query (type 'exit' to quit): ")
    # 检查是否需要退出
    if user_query.lower() == 'exit':
        print("Exiting the program. Goodbye!")
        break
    # 执行查询并获取答案
    _ans = docs.query(user_query)
    # 打印答案
    print("-"*40)
    # print(f"Q: {_ans.question}")
    print(f"Ans:\n{_ans.answer}")
    print(f"Ref:\n{_ans.references}")
    print("-"*40)
    print(_ans.context)
    print("-"*40)

