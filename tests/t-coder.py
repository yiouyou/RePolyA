import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya.coder import parsesource

_project_folder = "/mnt/disks/data/RePolyA/repolya/_workspace/recommendationengine-master"
_type = "js"

parsesource(_project_folder, _type)

