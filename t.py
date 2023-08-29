s = '@Article{Pillarisetti2020ATC,\n author = {K. Pillarisetti and S. Edavettal and M. Mendonca and Yingzhe Li and M. Tornetta and A. Babich and Nate Majewski and Matt Husovsky and D. Reeves and Eileen Walsh and D. Chin and L. Luistro and J. Joseph and G. Chu and K. Packman and Shoba Shetty and Y. Elsayed and R. Attar and F. Gaudet},\n booktitle = {Blood},\n journal = {Blood},\n title = {A T CELL REDIRECTING BISPECIFIC G-PROTEIN COUPLED RECEPTOR CLASS 5 MEMBER DxCD3 ANTIBODY TO TREAT MULTIPLE MYELOMA.},\n year = {2020}\n}\n'

import re
def parse_bibtex(_bibtex):
    _txt = ""
    match = re.search(r'@Article\{(.*?),', text)
    if match:
        print("Found:", match.group(1))
    else:
        print("Not found")
    return _txt

