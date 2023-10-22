import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import AUTOGEN_REF
from repolya.autogen.workflow import do_rag_doc, do_rag_code, do_rag_code_aid, do_rag_code_call_aid
from repolya.autogen.util import cost_usage
from autogen import ChatCompletion


ChatCompletion.start_logging(reset_counter=True, compact=False)


_n = int(sys.argv[1])

if _n == 1:
    re = do_rag_doc(
        msg="Which film came out first, Blind Shaft or The Mask Of Fu Manchu?",
        search_string="",
        docs_path="https://huggingface.co/datasets/thinkall/2WikiMultihopQA/resolve/main/corpus.txt",
        collection_name="rag_doc",
    )
    print(f"{re}")


if _n == 2:
    re = do_rag_code(
        msg="How can I use FLAML to perform a classification task and use spark to do parallel training. Train 30 seconds and force cancel jobs if time limit is reached.",
        search_string="spark",
        docs_path=str(AUTOGEN_REF),
        collection_name="rag_code",
    )
    print(f"{re}")


if _n == 11:
    from autogen.retrieve_utils import create_vector_db_from_dir, query_vector_db
    import chromadb
    print("Trying to create collection.")
    create_vector_db_from_dir(
        dir_path="https://huggingface.co/datasets/thinkall/2WikiMultihopQA/resolve/main/corpus.txt",
        max_tokens=16000*0.4,
        client=chromadb.Client(),
        collection_name="rag_doc",
        embedding_model="all-mpnet-base-v2", #"all-MiniLM-L12-v2",
        chunk_mode="one_line",
        must_break_at_empty_line=True,
        get_or_create=False,
    )
    problem = "Which film came out first, Blind Shaft or The Mask Of Fu Manchu?" #"who is Maheen Khan?"
    results = query_vector_db(
        query_texts=[problem],
        n_results=10,
        search_string="",
        client=chromadb.Client(),
        collection_name="rag_doc",
        embedding_model="all-mpnet-base-v2", #"all-MiniLM-L12-v2",
    )
    print("doc_ids: ", results["ids"])
    for i in results["ids"][0]:
        i_txt = results["ids"][0][i]
        print(f"{i}: '{i_txt}'")


if _n == 22:
    from autogen.retrieve_utils import create_vector_db_from_dir, query_vector_db
    import chromadb
    print("Trying to create collection.")
    create_vector_db_from_dir(
        dir_path=str(AUTOGEN_REF),
        max_tokens=8000*0.4,
        client=chromadb.Client(),
        collection_name="rag_code",
        embedding_model="all-mpnet-base-v2",
        chunk_mode="multi_lines",
        must_break_at_empty_line=True,
        get_or_create=False,
    )
    problem = "How can I use FLAML to perform a classification task and use spark to do parallel training. Train 30 seconds and force cancel jobs if time limit is reached.",
    results = query_vector_db(
        query_texts=[problem],
        n_results=10,
        search_string="spark",
        client=chromadb.Client(),
        collection_name="rag_code",
        embedding_model="all-mpnet-base-v2",
    )
    print("doc_ids: ", results["ids"])
    for i in results["ids"][0]:
        i_txt = results["ids"][0][i]
        print(f"{i}: '{i_txt}'")


if _n == 3:
    re = do_rag_code_aid(
        msg="How to use spark for parallel training in FLAML? Give me sample code.",
        docs_path="https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md",
        collection_name="rag_code_aid",
    )
    print(f"{re}")


if _n == 4:
    re = do_rag_code_call_aid(
        msg="How to use spark for parallel training in FLAML? Give me sample code.",
        docs_path="https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md",
        collection_name="rag_code_aid",
    )
    print(f"{re}")


print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")

