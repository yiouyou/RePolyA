import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

import re
def extract_and_sum(text):
    # 用于存储总和
    total_tokens = 0
    total_prompt = 0
    total_completion = 0
    total_cost = 0.0
    # 使用正则表达式找出所有符合格式的行
    matches = re.findall(r"Tokens: (\d+) = \(Prompt (\d+) \+ Completion (\d+)\) Cost: \$(\d+.\d+)\n", text)
    # 遍历所有匹配项并加总
    for match in matches:
        # print(match)
        tokens, prompt, completion = map(int, match[:-1])
        cost = float(match[-1])
        total_tokens += tokens
        total_prompt += prompt
        total_completion += completion
        total_cost += cost
    # 整合结果
    _res = f"Tokens: {total_tokens} = (Prompt {total_prompt} + Completion {total_completion}) Cost: ${total_cost:.3f}"
    return _res

with open(sys.argv[1], 'r') as rf:
    _text = rf.read()

print(extract_and_sum(_text))

