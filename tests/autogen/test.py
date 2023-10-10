import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import AUTOGEN_REF
from repolya.autogen.workflow import do_simple_task, do_simple_code, do_rd, do_math, do_plan_task, do_res, do_rag_doc, do_rag_code


_n = int(sys.argv[1])

if _n == 1:
    re = do_simple_task("查找一下长沙的天气.")
    print(f"{re}")


if _n == 2:
    re = do_simple_code("For certain cloud services (such as computing), assuming there are several given attributes (such as vCore, memory, iops, storage, backup, etc.) of each computing resource sku, write a flexible and basic recommendation class to filter out unfitted skus and find the lowest price as the recommendation for customers.")
    print(f"{re}")


if _n == 3:
    # _do = "UDP-GlcA大规模生成"
    _do = "查找UDP-Glc，UDP-GlcA，orotate，hypotaurine各自的量产菌株，以及大规模生成的方法。以列表的形式输出结果，并给出参考文献。"
    re = do_rd(_do)
    print(f"{re}")


if _n == 4:
    re = do_math("Find all numbers $a$ for which the graph of $y=x^2+a$ and the graph of $y=ax$ intersect. Express your answer in interval notation.")
    print(f"{re}")


if _n == 5:
    re = do_plan_task("Suggest a fix to an open good first issue of flaml")
    print(f"{re}")


if _n == 6:
    # _do = "find papers on LLM applications from arxiv in the last week, create a markdown table of different domains."
    _do = "查找UDP-Glc，UDP-GlcA，orotate，hypotaurine各自的量产菌株，以及大规模生成的方法。以列表的形式输出结果，并给出参考文献。"
    re = do_res(_do)
    print(f"{re}")


if _n == 7:
    re = do_rag_doc(
        msg="Which film came out first, Blind Shaft or The Mask Of Fu Manchu?",
        search_string="",
        docs_path="https://huggingface.co/datasets/thinkall/2WikiMultihopQA/resolve/main/corpus.txt",
        collection_name="rag_doc",
    )
    print(f"{re}")


if _n == 8:
    re = do_rag_code(
        msg="How can I use FLAML to perform a classification task and use spark to do parallel training. Train 30 seconds and force cancel jobs if time limit is reached.",
        search_string="spark",
        docs_path=str(AUTOGEN_REF),
        collection_name="rag_code",
    )
    print(f"{re}")


if _n == 77:
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


if _n == 88:
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

