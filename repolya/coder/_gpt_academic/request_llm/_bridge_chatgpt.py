# 借鉴了 https://github.com/GaiZhenbiao/ChuanhuChatGPT 项目
"""
    该文件中主要包含的函数，是所有LLM的通用接口，它们会继续向下调用更底层的LLM模型，处理多模型并行等细节
    具备多线程调用能力的函数：在函数插件中被调用，灵活而简洁
    predict_no_ui_long_connection(...)
    在实验过程中发现调用predict_no_ui处理长文档时，和openai的连接容易断掉，这个函数用stream的方式解决这个问题，同样支持多线程
"""
import json
import time
import tiktoken
import traceback
import requests
from functools import lru_cache
# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from repolya.coder._gpt_academic._toolbox import trimmed_format_exc
from repolya._const import TIMEOUT_SECONDS, MAX_RETRY, OPENAI_ENDPOINT
from repolya._log import logger_coder


class LazyloadTiktoken(object):
    def __init__(self, model):
        self.model = model

    @staticmethod
    @lru_cache(maxsize=128)
    def get_encoder(model):
        # print('正在加载tokenizer，如果是第一次运行，可能需要一点时间下载参数')
        tmp = tiktoken.encoding_for_model(model)
        # print('加载tokenizer完毕')
        return tmp
    
    def encode(self, *args, **kwargs):
        encoder = self.get_encoder(self.model) 
        return encoder.encode(*args, **kwargs)
    
    def decode(self, *args, **kwargs):
        encoder = self.get_encoder(self.model) 
        return encoder.decode(*args, **kwargs)

# 获取tokenizer
tokenizer_gpt35 = LazyloadTiktoken("gpt-3.5-turbo")
tokenizer_gpt4 = LazyloadTiktoken("gpt-4")
get_token_num_gpt35 = lambda txt: len(tokenizer_gpt35.encode(txt, disallowed_special=()))
get_token_num_gpt4 = lambda txt: len(tokenizer_gpt4.encode(txt, disallowed_special=()))

# 初始化模型
model_info = {
    "gpt-3.5-turbo": {
        "max_token": 4096,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },
    "gpt-3.5-turbo-16k": {
        "max_token": 1024*16,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },
    "gpt-4": {
        "max_token": 8192,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    }
}


def generate_payload(inputs, llm_kwargs, history, system_prompt, stream):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                  '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'
    api_key = llm_kwargs['api_key']
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    conversation_cnt = len(history) // 2
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_cnt:
        for index in range(0, 2*conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index+1]
            if what_i_have_asked["content"] != "":
                if what_gpt_answer["content"] == "":
                    continue
                if what_gpt_answer["content"] == timeout_bot_msg:
                    continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]['content'] = what_gpt_answer['content']
    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = inputs
    messages.append(what_i_ask_now)
    payload = {
        "model": llm_kwargs['llm_model'],
        "messages": messages, 
        "temperature": llm_kwargs['temperature'],  # 1.0,
        "top_p": llm_kwargs['top_p'],  # 1.0,
        "n": 1,
        "stream": stream,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }
    try:
        _str = f"{llm_kwargs['llm_model']} : {conversation_cnt} : {inputs[:100]} .........."
        # print(_str)
        logger_coder.debug(_str)
    except:
        _str = '输入中可能存在乱码。'
        # print(_str)
        logger_coder.debug(_str)
    # logger_coder.debug(f"{headers}")
    logger_coder.debug(f"{payload}")
    return headers, payload

def get_full_error(chunk, stream_response):
    """
        获取完整的从Openai返回的报错
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk

def chatgpt_noui(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None, console_slience=False):
    """
    发送至chatGPT，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
    inputs：
        是本次问询的输入
    sys_prompt:
        系统静默prompt
    llm_kwargs：
        chatGPT的内部调优参数
    history：
        是之前的对话列表
    observe_window = None：
        用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
    """
    watch_dog_patience = 5 # 看门狗的耐心, 设置5秒即可
    headers, payload = generate_payload(inputs, llm_kwargs, history, system_prompt=sys_prompt, stream=True)
    retry = 0
    while True:
        try:
            # make a POST request to the API endpoint, stream=False
            endpoint = OPENAI_ENDPOINT
            response = requests.post(endpoint, headers=headers, json=payload, stream=True, timeout=TIMEOUT_SECONDS); break
        except requests.exceptions.ReadTimeout as e:
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY:
                raise TimeoutError
            if MAX_RETRY != 0:
                logger_coder.debug(f'请求超时，正在重试 ({retry}/{MAX_RETRY}) ……')
    stream_response = response.iter_lines()
    result = ''
    while True:
        try: chunk = next(stream_response).decode()
        except StopIteration: 
            break
        except requests.exceptions.ConnectionError:
            chunk = next(stream_response).decode() # 失败了，重试一次？再失败就没办法了。
        if len(chunk)==0: continue
        if not chunk.startswith('data:'): 
            error_msg = get_full_error(chunk.encode('utf8'), stream_response).decode()
            if "reduce the length" in error_msg:
                raise ConnectionAbortedError("OpenAI拒绝了请求:" + error_msg)
            else:
                raise RuntimeError("OpenAI拒绝了请求：" + error_msg)
        if ('data: [DONE]' in chunk): break # api2d 正常完成
        json_data = json.loads(chunk.lstrip('data:'))['choices'][0]
        delta = json_data["delta"]
        if len(delta) == 0: break
        if "role" in delta: continue
        if "content" in delta: 
            result += delta["content"]
            # if not console_slience:
            #     print(delta["content"], end='')
            if observe_window is not None: 
                # 观测窗，把已经获取的数据显示出去
                if len(observe_window) >= 1: observe_window[0] += delta["content"]
                # 看门狗，如果超过期限没有喂狗，则终止
                if len(observe_window) >= 2:  
                    if (time.time()-observe_window[1]) > watch_dog_patience:
                        raise RuntimeError("用户取消了程序。")
        else: raise RuntimeError("意外Json结构："+delta)
    if json_data['finish_reason'] == 'content_filter':
        raise RuntimeError("由于提问含不合规内容被Azure过滤。")
    if json_data['finish_reason'] == 'length':
        raise ConnectionAbortedError("正常结束，但显示Token不足，导致输出不完整，请削减单次输入的文本量。")
    return result

# model_info["gpt-3.5-turbo"]["fn_without_ui"] = chatgpt_noui
# model_info["gpt-3.5-turbo-16k"]["fn_without_ui"] = chatgpt_noui
# model_info["gpt-4"]["fn_without_ui"] = chatgpt_noui


colors = ['#FF00FF', '#00FFFF', '#FF0000', '#990099', '#009999', '#990044']

def LLM_CATCH_EXCEPTION(f):
    """
    装饰器函数，将错误显示出来
    """
    def decorated(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience):
        try:
            return f(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience)
        except Exception as e:
            tb_str = '\n```\n' + trimmed_format_exc() + '\n```\n'
            observe_window[0] = tb_str
            return tb_str
    return decorated

def predict_no_ui_long_connection(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience=False):
    """
    发送至LLM，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
    inputs：
        是本次问询的输入
    sys_prompt:
        系统静默prompt
    llm_kwargs：
        LLM的内部调优参数
    history：
        是之前的对话列表
    observe_window = None：
        用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
    """
    model = llm_kwargs['llm_model']
    n_model = 1
    if '&' not in model:
        # 如果只询问1个大语言模型：
        method = chatgpt_noui
        return method(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience)
    else:
        logger_coder.debug("同时询问多个大语言模型")
        # # 如果同时询问多个大语言模型，这个稍微啰嗦一点，但思路相同，您不必读这个else分支
        # executor = ThreadPoolExecutor(max_workers=4)
        # models = model.split('&')
        # n_model = len(models)        
        # window_len = len(observe_window)
        # assert window_len==3
        # window_mutex = [["", time.time(), ""] for _ in range(n_model)] + [True]
        # futures = []
        # for i in range(n_model):
        #     model = models[i]
        #     method = model_info[model]["fn_without_ui"]
        #     llm_kwargs_feedin = copy.deepcopy(llm_kwargs)
        #     llm_kwargs_feedin['llm_model'] = model
        #     future = executor.submit(LLM_CATCH_EXCEPTION(method), inputs, llm_kwargs_feedin, history, sys_prompt, window_mutex[i], console_slience)
        #     futures.append(future)
        # def mutex_manager(window_mutex, observe_window):
        #     while True:
        #         time.sleep(0.25)
        #         if not window_mutex[-1]: break
        #         # 看门狗（watchdog）
        #         for i in range(n_model): 
        #             window_mutex[i][1] = observe_window[1]
        #         # 观察窗（window）
        #         chat_string = []
        #         for i in range(n_model):
        #             chat_string.append( f"【{str(models[i])} 说】: <font color=\"{colors[i]}\"> {window_mutex[i][0]} </font>" )
        #         res = '<br/><br/>\n\n---\n\n'.join(chat_string)
        #         # # # # # # # # # # #
        #         observe_window[0] = res
        # t_model = threading.Thread(target=mutex_manager, args=(window_mutex, observe_window), daemon=True)
        # t_model.start()
        # return_string_collect = []
        # while True:
        #     worker_done = [h.done() for h in futures]
        #     if all(worker_done):
        #         executor.shutdown()
        #         break
        #     time.sleep(1)
        # for i, future in enumerate(futures):  # wait and get
        #     return_string_collect.append( f"【{str(models[i])} 说】: <font color=\"{colors[i]}\"> {future.result()} </font>" )
        # window_mutex[-1] = False # stop mutex thread
        # res = '<br/><br/>\n\n---\n\n'.join(return_string_collect)
        # return res


