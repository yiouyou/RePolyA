import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)


from repolya.paper._digest.pmc_fetcher import pmc_to_md

_pmcID = 'PMC10238377' # PMC384712 PMC10238377
_md = pmc_to_md(_pmcID, 't.md')
