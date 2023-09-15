from selenium import webdriver
from markdownify import markdownify
import re


class PMCArticleFetcher:
    def __init__(self, PMC_ID: str):
        self._PMC_ID = PMC_ID

    def get_PMC_article_source(self):
        base_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/"
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")  # linux only
        driver = webdriver.Chrome(options=options)
        driver.get(f"{base_url}{self._PMC_ID}")
        article_source = driver.execute_script("return document.getElementById('mc').outerHTML;")
        head_source = driver.execute_script("return document.getElementsByTagName('head')[0].innerHTML;")
        driver.quit()
        return article_source, head_source

    def fetch_article(self):
        article_body_src, head_src = self.get_PMC_article_source()
        article_body_src = article_body_src.replace('href="//doi.org', 'href="https://www.doi.org')
        article_body_src = article_body_src.replace('href="/', 'href="https://www.ncbi.nlm.nih.gov/')\
            .replace('src="/', 'src="https://www.ncbi.nlm.nih.gov/')
        head_src = head_src.replace('href="/', 'href="https://www.ncbi.nlm.nih.gov/')\
            .replace('src="/',  'src="https://www.ncbi.nlm.nih.gov/')
        head_src = head_src.replace("url(/corehtml/pmc/pmcgifs",
                                    "url(https://www.ncbi.nlm.nih.gov/corehtml/pmc/pmcgifs")
        return article_body_src, head_src


def pmc_to_md(_pmcID, _out):
    article_body_src, head_src = PMCArticleFetcher(_pmcID).fetch_article()
    _t1 = markdownify(article_body_src, heading_style="ATX")
    _t2 = re.sub(r'\n\s*\n', '\n\n', _t1)
    _t3 = re.sub(r'\[Go to\:\]\(\# \"Go to other sections in this page\"\)', '', _t2)
    _t4 = re.sub(r'\(http[^\)]+\)', '', _t3)
    _t5 = re.sub(r'\(#ref[^\)]+\)', '', _t4)
    _t6 = re.sub(r'\(#[^\)]+\)', '', _t5)
    _t7 = re.sub(r'\[\!\[An external file that holds a picture, illustration, etc\..*?\]\]\[Open in a separate window\]', '', _t6, flags=re.DOTALL)
    _t8 = re.sub(r'\nIntroduction\n\n##', "\n## Introduction", _t7)
    _t9 = re.sub(r'(## Abstract\n\n.*?\n\n)## \n', r'\1## Introduction', _t8, flags=re.DOTALL)
    _t10 = _t9.split("\n## References")[0]
    _t11 = re.sub(r'^.*?\](# .+?)\n\n.*?\n## Abstract', r'\1\n\n## Abstract', _t10, flags=re.DOTALL)
    _t12 = re.sub(r'\[Click here to view.\]', '', _t11)
    with open(_out, "w") as wf:
        wf.write(_t12)

