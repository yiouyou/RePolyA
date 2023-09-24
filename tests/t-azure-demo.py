import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya.azure.app import run


run("Create a system that can summarize a powerpoint file", "PPT")
