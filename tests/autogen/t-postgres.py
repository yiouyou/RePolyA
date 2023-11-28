import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import AUTOGEN_REF
from repolya.autogen.workflow import do_postgre_organizer
_msg = sys.argv[1]
re = do_postgre_organizer(_msg)
print(f"{re}")


# import psycopg2
# conn = psycopg2.connect(
#     user="sz",
#     password="1123",
#     host="192.168.76.148",
#     port="5432",
#     database="dvdrental"
# )
# cur = conn.cursor()
# cur.execute("SELECT first_name FROM actor;")
# _re = cur.fetchall()
# for i in _re:
#     print(i)
# cur.close()
# conn.close()

