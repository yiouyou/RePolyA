import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya._const import PAPER_PDF
from repolya.paper.digestpaper import (
    digest_pdf,
    qa_pdf,
    sum_pdf,
    trans_en2zh,
)


# _fp = PAPER_PDF / 'Abanades2021ABlooperFA_10.1101_2021.07.26.453747.pdf'
_fp = PAPER_PDF / 'The company landscape for artificial intelligence in large-molecule drug discovery.pdf'

# digest_pdf(_fp)

# qa_pdf(_fp, 'Whats the paper talking about?', 'stuff')

# sum_pdf(_fp, 'stuff')
# sum_pdf(_fp, 'map_reduce')
# sum_pdf(_fp, 'refine')

_en = "This article discusses the use of artificial intelligence (AI) in large-molecule drug discovery, focusing on structural predictions, functional predictions, and new candidate generation. It highlights advancements in machine learning models such as AlphaFold2 and RoseTTAFold for predicting protein structures and the development of AI tools for predicting the functions of large-molecule therapeutic candidates. The article also mentions the growing availability of data supporting the development of algorithms for generating large-molecule therapeutic candidates. Additionally, it provides insights into the emerging company landscape for AI-driven biotech companies engaged in large-molecule drug design. The analysis identifies 82 companies active in this field, with over 60% of them founded in the past 5 years, indicating a nascent industry driven by recent technological advancements. The article includes information on the number of partnerships formed by these companies with top-20 biopharma companies, the total capital invested in these companies, and the number of pipeline assets they have at different development stages and indications. In 2021, the companies in this space raised $3.9 billion, with notable activity from companies like AbCellera, Absci, and Generate Biomedicines. Established biopharma companies are also investing in AI capabilities for large-molecule drug discovery through acquisitions and partnerships. The pipelines of AI-driven biotechs are currently at an early stage, with assets in phase II and phase I clinical development. The largest group of assets under development by AI-driven biotech companies in the preclinical pipeline is in the oncology area, with eight molecules. The article emphasizes the need for fully integrating AI models into research processes, establishing technical environments, and combining AI technologies across the R&D process to realize the full potential of AI in large-molecule drug discovery. It is important to note that the authors of this article are employees of McKinsey & Company, a management consultancy that works with biopharmaceutical and biotechnology companies, and the research for this specific article was funded by McKinsey's Life Sciences practice."


_zh = trans_en2zh(_en)
print(_zh)
