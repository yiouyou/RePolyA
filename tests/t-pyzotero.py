import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from pyzotero import zotero

# 运行 paper/__init__.py 里的 load_dotenv()
import repolya.paper


library_id = os.getenv("ZOTERO_USER_ID")
library_type = 'user'
api_key = os.getenv("ZOTERO_API_KEY")

zot = zotero.Zotero(library_id, library_type, api_key)
items = zot.top(limit=20)

# we've retrieved the latest five top-level items in our library
# we can print each item's item type and ID
for item in items:
    print('Item: %s | Key: %s' % (item['data']['itemType'], item['data']['key']))

