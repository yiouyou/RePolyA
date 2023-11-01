from langchain.callbacks import get_openai_callback
from langchain.chains import create_tagging_chain
from langchain.chat_models import ChatOpenAI

from repolya.rag.doc_loader import clean_txt

import os
from dotenv import load_dotenv
load_dotenv()


##### v1
def call_openai_tagging(chain, _sentence):
    _re = ""
    _tokens = 0
    _cost = 0
    _log = ""
    with get_openai_callback() as cb:
        _re = chain.run(_sentence)
        _tokens = cb.total_tokens
        _cost = cb.total_cost
        _log += f"\nTokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens})\n"
        _cost_str = format(cb.total_cost, ".5f")
        _log += f"Cost: ${_cost_str}\n\n"
    print(_sentence, _re)
    print(_log)
    return [_re, _tokens, _cost, _log]


def JQ_openai_tagging(txt_lines):
    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo-16k')
    #####
    schema = {
        "properties": {
            "时间": {
                "type": "string",
                "description": """新闻事件发生的时间点。下面是一些csv格式的新闻句子分析示例，其中新闻句子已用双引号括起来，逗号后面是句子的分析结果，请着重注意'时间'的分析：

"2023年6月3日20时10分，乌克兰防空预警检测外籍导弹入境，乌克兰军事指挥中心依据《军事入侵防御紧急方案》（乌-防空10586号），对该事件做出紧急应对措施，导弹途径基辅市、哈尔科夫市、奥德赛市、最终20时35分在顿涅茨克市发生爆炸，造成两座大楼炸毁，约160名平民伤亡，出动乌克兰防空1军和防空13军，共计10辆防空导弹装甲车，50枚防空导弹，150名士兵，对袭击时间做出紧急处理。", {"时间":"2023年6月3日20时10分,20时35分", "地点":"基辅市,哈尔科夫市,奥德赛市,顿涅茨克市", "人物": "", "军队":"乌克兰防空1军,乌克兰防空13军", "武器":"10辆防空导弹装甲车,50枚防空导弹", "伤亡":"160名平民伤亡,150名士兵"}

"2023年6月3日20时10分，乌克兰防空部队编号1136部队，在哈尔科夫市布朗尼镇检测到导弹袭击，立即分析上报。", {"时间":"2023年6月3日20时10分", "地点":"哈尔科夫市布朗尼镇", "人物": "", "军队":"乌克兰防空部队编号1136部队", "武器": "", "伤亡": ""}

"202306032020，乌克兰防空部队编号11316部队，在奥德赛市奥德赛特镇检测到导弹袭击，立即分析上报。", {"时间":"202306032020", "地点":"奥德赛市奥德赛特镇", "人物": "", "军队":"乌克兰防空部队编号11316部队", "武器": "", "伤亡": ""}

"202306032025，乌克兰军事指挥中心瓦列里·扎卢日内将军，做出紧急预案，《军事入侵防御紧急方案》（乌-防空10586号），命令乌克兰陆军部队编号11316部队，乌克兰陆军部队编号11316部队，立即做出应对措施，立即处理。", {"时间":"202306032025", "地点": "", "人物":"瓦列里·扎卢日内将军", "军队":"乌克兰陆军部队编号11316部队,乌克兰陆军部队编号11316部队", "武器": "", "伤亡": ""}

"202306032025，导弹在乌克兰基辅市沙拉克镇发生爆炸，造成两座大楼炸毁，约160名平民伤亡。", {"时间":"202306032025", "地点":"基辅市沙拉克镇", "人物": "", "军队":"", "武器": "", "伤亡":"160名平民伤亡"}

"据央视军事消息，据缅甸媒体报道，10月27日，缅北腊戌、贵慨等多地的缅军军事据点遭武装袭击并爆发交火，战事激烈。", {"时间":"10月27日", "地点":"缅北腊戌,缅北贵慨", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据当地居民消息，今日凌晨4点开始，有武装团体同时袭击掸邦北部腊戌、登尼、贵概、达莫尼、南非卡、木姐、南坎、瑟兰、滚弄、货班、清水河、老街地军事部署区。", {"时间":"凌晨4点", "地点":"掸邦北部腊戌,登尼,贵概,达莫尼,南非卡,木姐,南坎,瑟兰,滚弄,货班,清水河,老街", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据确切消息，从10月27日凌晨4点开始，以上多个地区军事部署区、收费站、警察哨所、所有的警察局均同时受到相关武装力量攻击。", {"时间":"10月27日凌晨4点", "地点": "军事部署区,收费站,警察哨所,警察局", "人物": "", "军队": "", "武器": "", "伤亡": ""}
""",
            },
            "地点": {
                "type": "string",
                "description": """新闻事件发生的地点。下面是一些csv格式的新闻句子分析示例，其中新闻句子已用双引号括起来，逗号后面是句子的分析结果，请着重注意'地点'的分析：

"2023年6月3日20时10分，乌克兰防空预警检测外籍导弹入境，乌克兰军事指挥中心依据《军事入侵防御紧急方案》（乌-防空10586号），对该事件做出紧急应对措施，导弹途径基辅市、哈尔科夫市、奥德赛市、最终20时35分在顿涅茨克市发生爆炸，造成两座大楼炸毁，约160名平民伤亡，出动乌克兰防空1军和防空13军，共计10辆防空导弹装甲车，50枚防空导弹，150名士兵，对袭击时间做出紧急处理。", {"时间":"2023年6月3日20时10分,20时35分", "地点":"基辅市,哈尔科夫市,奥德赛市,顿涅茨克市", "人物": "", "军队":"乌克兰防空1军,乌克兰防空13军", "武器":"10辆防空导弹装甲车,50枚防空导弹", "伤亡":"160名平民伤亡,150名士兵"}

"2023年6月3日20时10分，乌克兰防空部队编号1136部队，在哈尔科夫市布朗尼镇检测到导弹袭击，立即分析上报。", {"时间":"2023年6月3日20时10分", "地点":"哈尔科夫市布朗尼镇", "人物": "", "军队":"乌克兰防空部队编号1136部队", "武器": "", "伤亡": ""}

"202306032020，乌克兰防空部队编号11316部队，在奥德赛市奥德赛特镇检测到导弹袭击，立即分析上报。", {"时间":"202306032020", "地点":"奥德赛市奥德赛特镇", "人物": "", "军队":"乌克兰防空部队编号11316部队", "武器": "", "伤亡": ""}

"202306032025，导弹在乌克兰基辅市沙拉克镇发生爆炸，造成两座大楼炸毁，约160名平民伤亡。", {"时间":"202306032025", "地点":"基辅市沙拉克镇", "人物": "", "军队":"", "武器": "", "伤亡":"160名平民伤亡"}

"据央视军事消息，据缅甸媒体报道，10月27日，缅北腊戌、贵慨等多地的缅军军事据点遭武装袭击并爆发交火，战事激烈。", {"时间":"10月27日", "地点":"缅北腊戌,缅北贵慨", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据中国侨网消息，据称，果敢民族民主同盟军发布公告对此次武装袭击负责，称行动旨在打击老街的电诈民团，因此从即日起封锁腊戌至清水河、木姐的道路。", {"时间": "", "地点":"腊戌,清水河,木姐", "人物": "", "军队": "果敢民族民主同盟军", "武器": "", "伤亡": ""}

"还有消息称，清水河多个据点已被同盟军占领，禁止通行。", {"时间": "", "地点":"清水河", "人物": "", "军队": "同盟军", "武器": "", "伤亡": ""}

"据当地居民消息，今日凌晨4点开始，有武装团体同时袭击掸邦北部腊戌、登尼、贵概、达莫尼、南非卡、木姐、南坎、瑟兰、滚弄、货班、清水河、老街地军事部署区。", {"时间":"凌晨4点", "地点":"掸邦北部腊戌,登尼,贵概,达莫尼,南非卡,木姐,南坎,瑟兰,滚弄,货班,清水河,老街", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据确切消息，从10月27日凌晨4点开始，以上多个地区军事部署区、收费站、警察哨所、所有的警察局均同时受到相关武装力量攻击。", {"时间":"10月27日凌晨4点", "地点": "军事部署区,收费站,警察哨所,警察局", "人物": "", "军队": "", "武器": "", "伤亡": ""}
""",
            },
            "人物": {
                "type": "string",
                "description": """新闻事件里提到的重要人物。下面是一些csv格式的新闻句子分析示例，其中新闻句子已用双引号括起来，逗号后面是句子的分析结果，请着重注意'人物'的分析：

"202306032025，乌克兰军事指挥中心瓦列里·扎卢日内将军，做出紧急预案，《军事入侵防御紧急方案》（乌-防空10586号），命令乌克兰陆军部队编号11316部队，乌克兰陆军部队编号11316部队，立即做出应对措施，立即处理。", {"时间":"202306032025", "地点": "", "人物":"瓦列里·扎卢日内将军", "军队":"乌克兰陆军部队编号11316部队,乌克兰陆军部队编号11316部队", "武器": "", "伤亡": ""}
""",
            },
            "军队": {
                "type": "string",
                "description": """新闻事件里提到的相关军队。下面是一些csv格式的新闻句子分析示例，其中新闻句子已用双引号括起来，逗号后面是句子的分析结果，请着重注意'军队'的分析：

"2023年6月3日20时10分，乌克兰防空预警检测外籍导弹入境，乌克兰军事指挥中心依据《军事入侵防御紧急方案》（乌-防空10586号），对该事件做出紧急应对措施，导弹途径基辅市、哈尔科夫市、奥德赛市、最终20时35分在顿涅茨克市发生爆炸，造成两座大楼炸毁，约160名平民伤亡，出动乌克兰防空1军和防空13军，共计10辆防空导弹装甲车，50枚防空导弹，150名士兵，对袭击时间做出紧急处理。", {"时间":"2023年6月3日20时10分,20时35分", "地点":"基辅市,哈尔科夫市,奥德赛市,顿涅茨克市", "人物": "", "军队":"乌克兰防空1军,乌克兰防空13军", "武器":"10辆防空导弹装甲车,50枚防空导弹", "伤亡":"160名平民伤亡,150名士兵"}

"2023年6月3日20时10分，乌克兰防空部队编号1136部队，在哈尔科夫市布朗尼镇检测到导弹袭击，立即分析上报。", {"时间":"2023年6月3日20时10分", "地点":"哈尔科夫市布朗尼镇", "人物": "", "军队":"乌克兰防空部队编号1136部队", "武器": "", "伤亡": ""}

"202306032020，乌克兰防空部队编号11316部队，在奥德赛市奥德赛特镇检测到导弹袭击，立即分析上报。", {"时间":"202306032020", "地点":"奥德赛市奥德赛特镇", "人物": "", "军队":"乌克兰防空部队编号11316部队", "武器": "", "伤亡": ""}

"202306032025，乌克兰军事指挥中心瓦列里·扎卢日内将军，做出紧急预案，《军事入侵防御紧急方案》（乌-防空10586号），命令乌克兰陆军部队编号11316部队，乌克兰陆军部队编号11316部队，立即做出应对措施，立即处理。", {"时间":"202306032025", "地点": "", "人物":"瓦列里·扎卢日内将军", "军队":"乌克兰陆军部队编号11316部队,乌克兰陆军部队编号11316部队", "武器": "", "伤亡": ""}

"指挥中心派遣陆军第三保障部队前往。", {"时间":"", "地点":"", "人物": "", "军队":"陆军第三保障部队", "武器": "", "伤亡":""}

"据中国侨网消息，据称，果敢民族民主同盟军发布公告对此次武装袭击负责，称行动旨在打击老街的电诈民团，因此从即日起封锁腊戌至清水河、木姐的道路。", {"时间": "", "地点":"腊戌,清水河,木姐", "人物": "", "军队": "果敢民族民主同盟军", "武器": "", "伤亡": ""}

"还有消息称，清水河多个据点已被同盟军占领，禁止通行。", {"时间": "", "地点":"清水河", "人物": "", "军队": "同盟军", "武器": "", "伤亡": ""}
""",
            },
            "武器": {
                "type": "string",
                "description": """新闻事件里提到的相关武器。下面是一些csv格式的新闻句子分析示例，其中新闻句子已用双引号括起来，逗号后面是句子的分析结果，请着重注意'武器'的分析：

"2023年6月3日20时10分，乌克兰防空预警检测外籍导弹入境，乌克兰军事指挥中心依据《军事入侵防御紧急方案》（乌-防空10586号），对该事件做出紧急应对措施，导弹途径基辅市、哈尔科夫市、奥德赛市、最终20时35分在顿涅茨克市发生爆炸，造成两座大楼炸毁，约160名平民伤亡，出动乌克兰防空1军和防空13军，共计10辆防空导弹装甲车，50枚防空导弹，150名士兵，对袭击时间做出紧急处理。", {"时间":"2023年6月3日20时10分,20时35分", "地点":"基辅市,哈尔科夫市,奥德赛市,顿涅茨克市", "人物": "", "军队":"乌克兰防空1军,乌克兰防空13军", "武器":"10辆防空导弹装甲车,50枚防空导弹", "伤亡":"160名平民伤亡,150名士兵"}
""",
            },
            "伤亡": {
                "type": "string",
                "description": """新闻事件里提到的相关伤亡。下面是一些csv格式的新闻句子分析示例，其中新闻句子已用双引号括起来，逗号后面是句子的分析结果，请着重注意'伤亡'的分析：

"202306032025，导弹在乌克兰基辅市沙拉克镇发生爆炸，造成两座大楼炸毁，约160名平民伤亡。", {"时间":"202306032025", "地点":"基辅市沙拉克镇", "人物": "", "军队":"", "武器": "", "伤亡":"160名平民伤亡"}
""",
            },
        },
        "required": ["时间", "地点", "人物", "军队", "武器", "伤亡"],
    }
    chain = create_tagging_chain(schema, llm)
    ##### split notes to sentences
    _sentences = []
    for i in txt_lines:
        i_li = i.strip()
        if i_li:
            for j in i_li.split("。"):
                if j:
                    jj = j+"。"
                    _sentences.append(jj)
    # print(len(_sentences))
    ##### 
    _log = ""
    _total_cost = 0
    _JQ = []
    ##### call OpenAI API with _content and _example
    for i in range(0, len(_sentences)):
        [i_re, i_tokens, i_cost, i_log] = call_openai_tagging(chain, _sentences[i])
        _log += f"'{_sentences[i]}'\n> {i_re}\n\n"
        _total_cost += i_cost
        _JQ.append(i_re)
    _total_cost_str = format(_total_cost, ".5f")
    # print(len(_JQ))
    # print(_JQ)
    ##### parse response, generate _log and _JQ_str
    # _log += f"\nTotal Cost: ${_total_cost_str}\n"
    _JQ_str = ""
    if len(_sentences) == len(_JQ):
        _JQ_str = str(_JQ)
    else:
        _log = "Error: len(sentences) != len(JQ)" + "\n"
    return [_log, _JQ_str, _total_cost_str, _sentences]

def JQ_llm_tagging(_txt):
    import re
    _log = ""
    _JQ_str = ""
    _total_cost = 0
    txt_lines = clean_txt(_txt)
    txt_lines = txt_lines.split('\n')
    [_log, _JQ_str, _total_cost_str, _sentences] = JQ_openai_tagging(txt_lines)
    # print(_log)
    # print(_JQ_str)
    import ast
    _JQ = ast.literal_eval(_JQ_str)
    # print(type(_JQ), _JQ)
    return [_JQ, _total_cost_str]



if __name__ == "__main__":

    _txt = """2023年6月3日20时10分，乌克兰防空预警检测外籍导弹入境，乌克兰军事指挥中心依据《军事入侵防御紧急方案》（乌-防空10586号），对该事件做出紧急应对措施，导弹途径基辅市、哈尔科夫市、奥德赛市、最终20时35分在顿涅茨克市发生爆炸，造成两座大楼炸毁，约160名平民伤亡，出动乌克兰防空1军和防空13军，共计10辆防空导弹装甲车，50枚防空导弹，150名士兵，对袭击时间做出紧急处理。

2023年6月3日20时10分，乌克兰防空部队编号1136部队，在哈尔科夫市布朗尼镇检测到导弹袭击，立即分析上报。

202306032020，乌克兰防空部队编号11316部队，在奥德赛市奥德赛特镇检测到导弹袭击，立即分析上报。

202306032025，乌克兰军事指挥中心瓦列里·扎卢日内将军，做出紧急预案，《军事入侵防御紧急方案》（乌-防空10586号），命令乌克兰陆军部队编号11316部队，乌克兰陆军部队编号11316部队，立即做出应对措施，立即处理。

202306032025，导弹在乌克兰基辅市沙拉克镇发生爆炸，造成两座大楼炸毁，约160名平民伤亡。指挥中心派遣陆军第三保障部队前往。

据央视军事消息，据缅甸媒体报道，10月27日，缅北腊戌、贵慨等多地的缅军军事据点遭武装袭击并爆发交火，战事激烈。

据中国侨网消息，据称，果敢民族民主同盟军发布公告对此次武装袭击负责，称行动旨在打击老街的电诈民团，因此从即日起封锁腊戌至清水河、木姐的道路。还有消息称，清水河多个据点已被同盟军占领，禁止通行。

据当地居民消息，今日凌晨4点开始，有武装团体同时袭击掸邦北部腊戌、登尼、贵概、达莫尼、南非卡、木姐、南坎、瑟兰、滚弄、货班、清水河、老街地军事部署区。

据确切消息，从10月27日凌晨4点开始，以上多个地区军事部署区、收费站、警察哨所、所有的警察局均同时受到相关武装力量攻击。
"""
    # _sentences = []
    # txt_lines = clean_txt(_txt)
    # txt_lines = txt_lines.split('\n')
    # for i in txt_lines:
    #     i_li = i.strip()
    #     if i_li:
    #         for j in i_li.split("。"):
    #             if j:
    #                 jj = j+"。"
    #                 _sentences.append(jj)
    # print(_sentences, len(_sentences))
    [_re, _cost] = JQ_llm_tagging(_txt)
    print(type(_re))
    for i in _re:
        print(i)
    print(type(_cost), _cost)

