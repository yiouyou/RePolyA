# from paper import querypapers
# papers = querypapers('bispecific antibody manufacture', 10)
# for i in sorted(papers.keys()):
#     print('-'*40)
#     print(i)
#     print('-'*40)
#     for j in sorted(papers[i].keys()):
#         print(f"{j}: {papers[i][j]}")
#     print("\n")
# _list = []
# for path, data in papers.items():
#     _list.append(path)

# from paper import query2jsonl
# covid19 = ['COVID-19', 'SARS-CoV-2']
# ai = ['Artificial intelligence', 'Deep learning', 'Machine learning']
# mi = ['Medical imaging']
# _query = [covid19, ai, mi]
# query2jsonl(_query)


from paper import qadocs
_query = "What manufacturing challenges are unique to bispecific antibodies?"
_list = []
import os
_dir = './paper/_pdf'
# print(_dir)
_files = os.listdir(_dir)
for _fn in _files:
    _fp = os.path.join(_dir, _fn)
    if os.path.isfile(_fp):
        _list.append(_fp)
print(_list)
_ans = qadocs(_query, _list)
print(_ans)

