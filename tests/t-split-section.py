import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya.paper._digest.split_sections import clean_and_split
from repolya.paper._digest.vdb_generate import get_RecursiveCharacterTextSplitter


_fp = sys.argv[1]
with open(_fp ,'r') as rf:
    pdf_text = rf.read()

# pdf_text = """blabla1
# Abstract
# blabla2
# Conclusions
# blabla3
# references
# blabla4
# """
print(pdf_text)

print("="*80)
sections = clean_and_split(pdf_text)
for i in sections:
    print("="*40)
    print(f"{i} ({len(sections[i])})")
    print(f"'{sections[i]}'")


_sec = []
### del References
for i in sections:
    if i.lower() != "references":
        if i == "_PRE":
            _sec.append(f"{sections[i]}")
        else:
            _sec.append(f"{i}\n{sections[i]}")
_pdf_text = "\n".join(_sec)
print("="*80)
print(_pdf_text)


print("="*80, "docs")
text_splitter = get_RecursiveCharacterTextSplitter()
_docs = text_splitter.create_documents([_pdf_text])
_n = 0
for i in _docs:
    _m = i.metadata
    _m['file_path'] = _fp
    _pdf = _m['file_path'].split('/')[-1]
    i.metadata['source'] = f"{_pdf}, s{_n}"
    _n += 1
for i in _docs:
    print("="*40)
    print(i)

