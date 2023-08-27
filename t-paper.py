# bispecific antibody manufacture
# What manufacturing challenges are unique to bispecific antibodies?

# from paper import query2jsonl
# covid19 = ['COVID-19', 'SARS-CoV-2']
# ai = ['Artificial intelligence', 'Deep learning', 'Machine learning']
# mi = ['Medical imaging']
# _query = [covid19, ai, mi]
# query2jsonl(_query)



# import logging
# class CustomFormatter(logging.Formatter):
#     # https://stackoverflow.com/a/56944256/2392535
#     grey = "\x1b[38;20m"
#     yellow = "\x1b[33;20m"
#     red = "\x1b[31;20m"
#     bold_red = "\x1b[31;1m"
#     reset = "\x1b[0m"
#     format = (
#         "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
#     )
#     FORMATS = {
#         logging.DEBUG: grey + format + reset,
#         logging.INFO: grey + format + reset,
#         logging.WARNING: yellow + format + reset,
#         logging.ERROR: red + format + reset,
#         logging.CRITICAL: bold_red + format + reset,
#     }
#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno)
#         formatter = logging.Formatter(log_fmt)
#         return formatter.format(record)

# logger = logging.getLogger("paper-scraper")
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setFormatter(CustomFormatter())
# logger.addHandler(ch)

_list = []
from paper import querypapers
papers = querypapers('bispecific antibody manufacture', 5)
if papers:
    for i in sorted(papers.keys()):
        print('-'*40)
        print(i)
        print('-'*40)
        for j in sorted(papers[i].keys()):
            print(f"{j}: {papers[i][j]}")
        print("\n")
    for path, data in papers.items():
        _list.append(path)
# ----------------------------------------
# /mnt/disks/data/RePolyA/paper/_pdf/ff1ac706f9ce58c79053c8d5707508aeef02896e.pdf
# ----------------------------------------
# bibtex: @article{Pillarisetti2020ATC,
#  author = {K. Pillarisetti and S. Edavettal and M. Mendonca and Yingzhe Li and M. Tornetta and A. Babich and Nate Majewski and Matt Husovsky and D. Reeves and Eileen Walsh and D. Chin and L. Luistro and J. Joseph and G. Chu and K. Packman and Shoba Shetty and Y. Elsayed and R. Attar and F. Gaudet},
#  booktitle = {Blood},
#  journal = {Blood},
#  title = {A T CELL REDIRECTING BISPECIFIC G-PROTEIN COUPLED RECEPTOR CLASS 5 MEMBER DxCD3 ANTIBODY TO TREAT MULTIPLE MYELOMA.},
#  year = {2020}
# }

# citation: K. Pillarisetti, S. Edavettal, M. Mendonca, Yingzhe Li, M. Tornetta, A. Babich, Nate Majewski, Matt Husovsky, D. Reeves, Eileen Walsh, D. Chin, L. Luistro, J. Joseph, G. Chu, K. Packman, Shoba Shetty, Y. Elsayed, R. Attar, and F. Gaudet. A t cell redirecting bispecific g-protein coupled receptor class 5 member dxcd3 antibody to treat multiple myeloma. Blood, 2020.
# citationCount: 59
# doi: 10.1182/blood.2019003342
# key: Pillarisetti2020ATC
# paperId: ff1ac706f9ce58c79053c8d5707508aeef02896e
# title: A T CELL REDIRECTING BISPECIFIC G-PROTEIN COUPLED RECEPTOR CLASS 5 MEMBER DxCD3 ANTIBODY TO TREAT MULTIPLE MYELOMA.
# tldr: None
# url: https://www.semanticscholar.org/paper/ff1ac706f9ce58c79053c8d5707508aeef02896e
# year: 2020



# from paper import qadocs
# _query = "What manufacturing challenges are unique to bispecific antibodies?"
# _list = []
# import os
# _dir = './paper/_pdf'
# # print(_dir)
# _files = os.listdir(_dir)
# for _fn in _files:
#     _fp = os.path.join(_dir, _fn)
#     if os.path.isfile(_fp):
#         _list.append(_fp)
# print(_list)
# _ans = qadocs(_query, _list)
# print('-'*40)
# print(_ans.formatted_answer)
# print('-'*40)
# print(_ans.question)
# print('-'*40)
# print(_ans.answer)
# print('-'*40)
# print(_ans.references)
# print('-'*40)
# print(_ans.context)
# print('-'*40)

