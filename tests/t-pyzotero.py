import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from pyzotero import zotero

# 运行 paper/__init__.py 里的 load_dotenv()
import repolya.paper


api_key = os.getenv("ZOTERO_API_KEY")

library_id = os.getenv("ZOTERO_USER_ID")
group_fujun = os.getenv("ZOTERO_GROUP_FUJUN")

zot_lib = zotero.Zotero(library_id, 'user', api_key)
items_lib = zot_lib.top(limit=20)
# we've retrieved the latest five top-level items in our library
# we can print each item's item type and ID
for item in items_lib:
    print('LIB Item: %s | Key: %s' % (item['data']['itemType'], item['data']['key']))

zot_grp = zotero.Zotero(group_fujun, 'group', api_key)
items_grp = zot_grp.top(limit=20)
# we've retrieved the latest five top-level items in our library
# we can print each item's item type and ID
for item in items_grp:
    print('GRP Item: %s | Key: %s' % (item['data']['itemType'], item['data']['key']))

