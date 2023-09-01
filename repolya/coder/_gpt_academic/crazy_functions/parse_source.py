import glob, os, copy
from repolya.coder._gpt_academic._toolbox import write_results_to_file
from repolya.coder._gpt_academic.crazy_functions._crazy_utils import input_clipping, request_gpt_model_in_new_thread_with_ui_alive, request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from repolya._const import WORKSPACE_ROOT
from repolya._log import logger_coder


def parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot):
    summary_batch_isolation = True
    inputs_array = []
    inputs_show_user_array = []
    history_array = []
    sys_prompt_array = []
    report_part_1 = []
    assert len(file_manifest) <= 512, "源文件太多（超过512个）, 请缩减输入文件的数量。或者, 您也可以选择删除此行警告, 并修改代码拆分file_manifest列表, 从而实现分批次处理。"
    ############################## <第一步，逐个文件分析，多线程> ##################################
    for index, fp in enumerate(file_manifest):
        # 读取文件
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            file_content = f.read()
        _rel_path = os.path.relpath(fp, project_folder)
        i_say = f'请概述下面的程序文件: {_rel_path}，文件代码是 ```{file_content}```'
        i_say_show_user = f'[{index}/{len(file_manifest)}] 请概述下面的程序文件: {_rel_path}'
        # 装载请求内容
        inputs_array.append(i_say)
        inputs_show_user_array.append(i_say_show_user)
        history_array.append([])
        sys_prompt_array.append("你是一个程序架构分析师，正在分析一个源代码项目。你的回答必须简单明了。")
    # print(inputs_show_user_array)
    # 文件读取完成，对每一个源代码文件，生成一个请求线程，发送到chatgpt进行分析
    gpt_response_collection = request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array = inputs_array,
        inputs_show_user_array = inputs_show_user_array,
        history_array = history_array,
        sys_prompt_array = sys_prompt_array,
        llm_kwargs = llm_kwargs,
        chatbot = chatbot,
        show_user_at_complete = True
    )
    # print(gpt_response_collection)
    # 全部文件解析完成，结果写入文件，准备对工程源代码进行汇总分析
    report_part_1 = copy.deepcopy(gpt_response_collection)
    history_to_return = report_part_1
    # res = write_results_to_file(project_folder, report_part_1)
    # chatbot.append(("完成？", "逐个文件分析已完成。" + res + "\n\n正在开始汇总。"))
    # logger_coder.debug(f"{chatbot}")
    ############################## <第二步，综合，单线程，分组+迭代处理> ##################################
    batchsize = 16  # 10个文件为一组
    report_part_2 = []
    previous_iteration_files = []
    last_iteration_result = ""
    while True:
        if len(file_manifest) == 0:
            break
        this_iteration_file_manifest = file_manifest[:batchsize]
        this_iteration_gpt_response_collection = gpt_response_collection[:batchsize*2]
        file_rel_path = [os.path.relpath(fp, project_folder) for index, fp in enumerate(this_iteration_file_manifest)]
        # 把“请对下面的程序文件做一个概述” 替换成 精简的 "文件名：{all_file[index]}"
        for index, content in enumerate(this_iteration_gpt_response_collection):
            if index%2==0:
                this_iteration_gpt_response_collection[index] = f"{file_rel_path[index//2]}" # 只保留文件名节省token
        this_iteration_files = [os.path.relpath(fp, project_folder) for index, fp in enumerate(this_iteration_file_manifest)]
        previous_iteration_files.extend(this_iteration_files)
        previous_iteration_files_string = ', '.join(previous_iteration_files)
        current_iteration_focus = ', '.join(this_iteration_files)
        if summary_batch_isolation:
            focus = current_iteration_focus
        else:
            focus = previous_iteration_files_string
        i_say = f'用一张Markdown表格简要描述以下文件的功能：{focus}。根据以上分析，用一句话概括程序的整体功能。'
        if last_iteration_result != "":
            sys_prompt_additional = "已知某些代码的局部作用是:" + last_iteration_result + "\n请继续分析其他源代码，从而更全面地理解项目的整体功能。"
        else:
            sys_prompt_additional = ""
        inputs_show_user = f'根据以上分析，对程序的整体功能和构架重新做出概括，由于输入长度限制，可能需要分组处理，本组文件为 {current_iteration_focus} + 已经汇总的文件组。'
        this_iteration_history = copy.deepcopy(this_iteration_gpt_response_collection)
        this_iteration_history.append(last_iteration_result)
        # 裁剪input
        inputs, this_iteration_history_feed = input_clipping(inputs=i_say, history=this_iteration_history, max_token_limit=2560)
        result = request_gpt_model_in_new_thread_with_ui_alive(
            inputs=inputs,
            inputs_show_user=inputs_show_user,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history=this_iteration_history_feed,   # 迭代之前的分析
            sys_prompt="你是一个程序架构分析师，正在分析一个项目的源代码。" + sys_prompt_additional)
        summary = "请用一句话概括这些文件的整体功能"
        summary_result = request_gpt_model_in_new_thread_with_ui_alive(
            inputs=summary, 
            inputs_show_user=summary, 
            llm_kwargs=llm_kwargs, 
            chatbot=chatbot,
            history=[i_say, result],   # 迭代之前的分析
            sys_prompt="你是一个程序架构分析师，正在分析一个项目的源代码。" + sys_prompt_additional)
        report_part_2.extend([i_say, result])
        last_iteration_result = summary_result
        file_manifest = file_manifest[batchsize:]
        gpt_response_collection = gpt_response_collection[batchsize*2:]
    ############################## <END> ##################################
    history_to_return.extend(report_part_2)
    res, wfn = write_results_to_file(project_folder, history_to_return)
    chatbot.append(("完成了吗？", res))
    # logger_coder.debug(f"{chatbot}")
    return wfn


@logger_coder.catch
def parse_source_python(txt, llm_kwargs, chatbot):
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        logger_coder.error(f"找不到本地项目或无权访问: {txt}")
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.py', recursive=True)]
    logger_coder.debug(f"{file_manifest}")
    if len(file_manifest) == 0:
        logger_coder.error(f"找不到任何python文件: {txt}")
        return
    wfn = parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot)
    return wfn


@logger_coder.catch
def parse_source_c(txt, llm_kwargs, chatbot):
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        logger_coder.error(f"找不到本地项目或无权访问: {txt}")
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.h', recursive=True)]  + \
                    [f for f in glob.glob(f'{project_folder}/**/*.cpp', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.hpp', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.c', recursive=True)]
    logger_coder.debug(f"{file_manifest}")
    if len(file_manifest) == 0:
        logger_coder.error(f"找不到任何c文件: {txt}")
        return
    wfn = parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot)
    return wfn


@logger_coder.catch
def parse_source_java(txt, llm_kwargs, chatbot):
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        logger_coder.error(f"找不到本地项目或无权访问: {txt}")
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.java', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.jar', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.xml', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.sh', recursive=True)]
    logger_coder.debug(f"{file_manifest}")
    if len(file_manifest) == 0:
        logger_coder.error(f"找不到任何java文件: {txt}")
        return
    wfn = parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot)
    return wfn


@logger_coder.catch
def parse_source_js(txt, llm_kwargs, chatbot):
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        logger_coder.error(f"找不到本地项目或无权访问: {txt}")
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.ts', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.tsx', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.json', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.js', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.vue', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.less', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.sass', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.wxml', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.wxss', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.css', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.jsx', recursive=True)]
    logger_coder.debug(f"{file_manifest}")
    if len(file_manifest) == 0:
        logger_coder.error(f"找不到任何js相关文件: {txt}")
        return
    wfn = parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot)
    return wfn


@logger_coder.catch
def parse_source_golang(txt, llm_kwargs, chatbot):
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        logger_coder.error(f"找不到本地项目或无权访问: {txt}")
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.go', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/go.mod', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/go.sum', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/go.work', recursive=True)]
    logger_coder.debug(f"{file_manifest}")
    if len(file_manifest) == 0:
        logger_coder.error(f"找不到任何golang文件: {txt}")
        return
    wfn = parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot)
    return wfn


@logger_coder.catch
def parse_source_rust(txt, llm_kwargs, chatbot):
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        logger_coder.error(f"找不到本地项目或无权访问: {txt}")
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.rs', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.toml', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.lock', recursive=True)]
    logger_coder.debug(f"{file_manifest}")
    if len(file_manifest) == 0:
        logger_coder.error(f"找不到任何rust文件: {txt}")
        return
    wfn = parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot)
    return wfn


@logger_coder.catch
def parse_source_lua(txt, llm_kwargs, chatbot):
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        logger_coder.error(f"找不到本地项目或无权访问: {txt}")
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.lua', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.xml', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.json', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.toml', recursive=True)]
    logger_coder.debug(f"{file_manifest}")
    if len(file_manifest) == 0:
        logger_coder.error(f"找不到任何lua文件: {txt}")
        return
    wfn = parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot)
    return wfn


@logger_coder.catch
def parse_source_csharp(txt, llm_kwargs, chatbot):
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        logger_coder.error(f"找不到本地项目或无权访问: {txt}")
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.cs', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.csproj', recursive=True)]
    logger_coder.debug(f"{file_manifest}")
    if len(file_manifest) == 0:
        logger_coder.error(f"找不到任何CSharp文件: {txt}")
        return
    wfn = parse_source_new(file_manifest, project_folder, llm_kwargs, chatbot)
    return wfn

