# 虚拟的论文数据
papers = [
    {
        "title": "An academic search engine for scientific articles",
        "doi": "10.1145/2983323.2983686"
    },
    {
        "title": "The new generation of citation indexes",
        "doi": "10.1016/j.libres.2005.06.005"
    },
    {
        "title": "Plagiarism detection using natural language processing techniques",
        "doi": "10.1109/ICDIM.2018.8847040"
    }
] # 创建一个包含三篇文献信息的列表

from paper import querypapers
def search_topic_papers(_topic):
    papers = []
    _papers = querypapers(_topic, 5)
    for i in sorted(_papers.keys()):
        print(f"{'-'*40}\n{i}\n{'-'*40}")
        for j in sorted(_papers[i].keys()):
            print(f"{j}: {_papers[i][j]}")
        _i = {
            "title": _papers[i]['title'],
            "bibtex": _papers[i]['bibtex'],
            "doi": _papers[i]['doi'],
            "citationCount": _papers[i]['citationCount'],
            "year": _papers[i]['year'],
            "url": _papers[i]['url'],
            "pdf": i
        }
        papers.append(_i)
        print("\n")
    print(papers)
    return papers

from paper import qadocs
def answer_question(_ask, _pdf):
    _ans = "Answer to the question based on papers"
    _res = qadocs(_ask, _pdf)
    _ans = _res.formatted_answer
    return _ans


import gradio as gr

def chg_btn_color_if_input(_topic):
    if _topic:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")

def search_topic(_topic):
    res = []
    papers = []
    if not _topic:
        raise gr.Error("请先输入'研究主题'")
    else:
        papers = search_topic_papers(_topic)
        for i in papers:
            title = i['title']
            res.append(title)
    return [gr.update(choices=res), papers]
    

def show_last_meta(_checkbox, _papers):
    _titles = [_checkbox[-1]]
    # print(_titles)
    _meta = []
    for i in _titles:
        for j in _papers:
            if i == j['title']:
                _meta.append(f"\ncitationCount: {j['citationCount']}\nurl: {j['url']}\nbibtex: {j['bibtex']}\n")
                break
    return "".join(_meta)

def fetch_selected_pdf(_checkbox, _papers):
    _fp = []
    if _checkbox is None:
        raise gr.Error("请先选取'相关文献'")
    else:
        for i in _checkbox:
            for j in _papers:
                if i == j['title']:
                    _fp.append(j['pdf'])
    return gr.update(value=_fp)


_description = "输入研究主题，获取相关文献，根据文献问答问题"
with gr.Blocks(title=_description) as demo:
    # gr.Markdown(_description)

    _papers = gr.State([])
    with gr.Tab(label="输入研究主题，获取相关文献，根据文献问答问题"):
        _topic = gr.Textbox(label="研究主题")
        search_btn = gr.Button("搜索")
        with gr.Row(equal_height=True):
            _papers_tile = gr.CheckboxGroup(label="相关文献")
            _papers_meta = gr.Textbox(label="文献信息")
        select_btn = gr.Button("获取PDF")
        _pdf = gr.File(label="已获取", file_count="single", type="file", file_types=['.pdf'], interactive=False)
        _ask = gr.Textbox(label="问题")
        ask_btn = gr.Button("提问")
        _ans = gr.Textbox(label="回答")
        _topic.change(
            chg_btn_color_if_input,
            [_topic],
            [search_btn]
        )
        search_btn.click(
            search_topic,
            [_topic],
            [_papers_tile, _papers]
        )
        _papers_tile.select(
            show_last_meta,
            [_papers_tile, _papers],
            [_papers_meta]
        )
        select_btn.click(
            fetch_selected_pdf,
            [_papers_tile, _papers],
            [_pdf]
        )
        _ask.change(
            chg_btn_color_if_input,
            [_ask],
            [ask_btn]
        )
        ask_btn.click(
            answer_question,
            [_ask, _pdf],
            [_ans]
        )
        



if __name__ == "__main__":

    import sys
    if sys.argv[1]:
        _port = int(sys.argv[1])
    else:
        _port = 7788
    demo.queue(concurrency_count=1).launch(
        server_name="0.0.0.0",
        server_port=_port,
        share=False,
        favicon_path="./asset/favicon_wa.png",
        # auth = ('sz','1123'),
        # auth_message= "欢迎回来！",
        ssl_verify=False,
        # ssl_keyfile="./localhost+2-key.pem",
        # ssl_certfile="./localhost+2.pem",
        ssl_keyfile="./ssl/key.pem",
        ssl_certfile="./ssl/cert.pem",
    )

