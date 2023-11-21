import gradio as gr
from repolya.rag.doc_loader import clean_txt
from repolya.local.textgen import get_textgen_llm


##### tagging
def read_file(file):
    if file:
        with open(file.name, encoding="utf-8") as f:
            content = f.read()
            return content


def call_yi_tag(_sentence):
    _textgen_url = "http://127.0.0.1:5552"
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    llm = get_textgen_llm(_textgen_url)
    _t1 = """### System:

假定你是情报分析员，请从给定新闻句子中，抽取如下实体：'时间'，'地点'，'人物'，'军队'，'武器'，'伤亡'。下面是一些csv格式的新闻句子分析示例，其中新闻句子已用双引号括起来，逗号后面是句子的分析结果：

"202306032020，乌克兰防空部队编号11316部队，在奥德赛市奥德赛特镇检测到导弹袭击，立即分析上报。", {"时间":"202306032020", "地点":"奥德赛市奥德赛特镇", "人物": "", "军队":"乌克兰防空部队编号11316部队", "武器": "", "伤亡": ""}

"202306032025，导弹在乌克兰基辅市沙拉克镇发生爆炸，造成两座大楼炸毁，约160名平民伤亡。", {"时间":"202306032025", "地点":"基辅市沙拉克镇", "人物": "", "军队":"", "武器": "", "伤亡":"160名平民伤亡"}

"202306032025，乌克兰军事指挥中心瓦列里·扎卢日内将军，做出紧急预案，《军事入侵防御紧急方案》（乌-防空10586号），命令乌克兰陆军部队编号11316部队，乌克兰陆军部队编号11316部队，立即做出应对措施，立即处理。", {"时间":"202306032025", "地点": "", "人物":"瓦列里·扎卢日内将军", "军队":"乌克兰陆军部队编号11316部队,乌克兰陆军部队编号11316部队", "武器": "", "伤亡": ""}

"2023年6月3日20时10分，乌克兰防空部队编号1136部队，在哈尔科夫市布朗尼镇检测到导弹袭击，立即分析上报。", {"时间":"2023年6月3日20时10分", "地点":"哈尔科夫市布朗尼镇", "人物": "", "军队":"乌克兰防空部队编号1136部队", "武器": "", "伤亡": ""}

"还有消息称，清水河多个据点已被同盟军占领，禁止通行。", {"时间": "", "地点":"清水河", "人物": "", "军队": "同盟军", "武器": "", "伤亡": ""}

"据当地居民消息，今日凌晨4点开始，有武装团体同时袭击掸邦北部腊戌、登尼、贵概、达莫尼、南非卡、木姐、南坎、瑟兰、滚弄、货班、清水河、老街地军事部署区。", {"时间":"凌晨4点", "地点":"掸邦北部腊戌,登尼,贵概,达莫尼,南非卡,木姐,南坎,瑟兰,滚弄,货班,清水河,老街", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据确切消息，从10月27日凌晨4点开始，以上多个地区军事部署区、收费站、警察哨所、所有的警察局均同时受到相关武装力量攻击。", {"时间":"10月27日凌晨4点", "地点": "军事部署区,收费站,警察哨所,警察局", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据央视军事消息，据缅甸媒体报道，10月27日，缅北腊戌、贵慨等多地的缅军军事据点遭武装袭击并爆发交火，战事激烈。", {"时间":"10月27日", "地点":"缅北腊戌,缅北贵慨", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据中国侨网消息，据称，果敢民族民主同盟军发布公告对此次武装袭击负责，称行动旨在打击老街的电诈民团，因此从即日起封锁腊戌至清水河、木姐的道路。", {"时间": "", "地点":"腊戌,清水河,木姐", "人物": "", "军队": "果敢民族民主同盟军", "武器": "", "伤亡": ""}

"指挥中心派遣陆军第三保障部队前往。", {"时间":"", "地点":"", "人物": "", "军队":"陆军第三保障部队", "武器": "", "伤亡":""}

### Instruction: 

"""
    _t2 = """
以json格式( {"时间":"", "地点":"", "人物": "", "军队":"", "武器":"", "伤亡":""} )输出；如果某个实体里包含多项信息，请将它们用'，'隔开。

### Response:

"""
    jinja2_template = _t1 + "请分析\"{{_sentence}}\"" + _t2
    prompt = PromptTemplate.from_template(jinja2_template, template_format="jinja2")
    # prompt.format(_sentence="2023年6月3日20时10分，乌克兰防空预警检测外籍导弹入境，乌克兰军事指挥中心依据《军事入侵防御紧急方案》（乌-防空10586号），对该事件做出紧急应对措施，导弹途径基辅市、哈尔科夫市、奥德赛市、最终20时35分在顿涅茨克市发生爆炸，造成两座大楼炸毁，约160名平民伤亡，出动乌克兰防空1军和防空13军，共计10辆防空导弹装甲车，50枚防空导弹，150名士兵，对袭击时间做出紧急处理。")
    # print(prompt)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    _res = llm_chain.run(_sentence)
    _tag = _res.replace("\n", '')
    return _tag


def tag_sentence(_sentence):
    if _sentence:
        _tag = call_yi_tag(_sentence)
        return _tag
    else:
        return "Error: sentence is empty!"


def text_tagging(_txt):
    _txt = clean_txt(_txt)
    txt_lines = _txt.split('\n')
    _sentences = []
    for i in txt_lines:
        i_li = i.strip()
        if i_li:
            for j in i_li.split("。"):
                if j:
                    jj = j+"。"
                    _sentences.append(jj)
    _JQ = []
    _log = []
    for i in range(0, len(_sentences)):
        i_re = tag_sentence(_sentences[i])
        _JQ.append(i_re)
        _log.append(f"'{_sentences[i]}'\n> {i_re}")        
    _JQ_str = ""
    if len(_sentences) == len(_JQ):
        _JQ_str = str(_JQ)
    else:
        _log = "Error: len(sentences) != len(JQ)" + "\n"
    return _JQ_str, "\n\n".join(_log)


def parse_txt(_txt):
    if _txt:
        _log = ""
        _JQ_str, _log = text_tagging(_txt)
        global output_JQ_file
        output_JQ_file = f"_tag.txt"
        with open(output_JQ_file, "w", encoding='utf-8') as wf:
            wf.write(_JQ_str)
        return _log
    else:
        return ["错误: TXT不能为空！"]


# def parse_file(file):
#     if file:
#         _log = ""
#         if os.path.exists(file.name):
#             with open(file.name, encoding='utf-8') as rf:
#                 _txt = rf.read()
#             _JQ_str, _log = text_tagging(_txt)
#             left, right = os.path.splitext(os.path.basename(file.name))
#             global output_JQ_file
#             output_JQ_file = f"{left}_JQ.txt"
#             with open(output_JQ_file, "w", encoding='utf-8') as wf:
#                 wf.write(_JQ_str)
#         return _log
#     else:
#         return ["错误: 请先上传一个TXT文件！"]


def show_JQ_file(text):
    # print(f"text: {text}")
    if text:
        if output_JQ_file:
            return gr.File(value=output_JQ_file, visible=True)
    else:
        if output_JQ_file:
            return gr.File(value=output_JQ_file)

