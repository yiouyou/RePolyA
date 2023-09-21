_s = """
Tokens: 7428 = (Prompt 3818 + Completion 3610) Cost: $0.02589

1. 这篇文章的研究目标是什么？
2. 本文的研究目标有哪些？
3. 研究的目的是什么？
4. 这篇文章的研究目的是为了什么？
5. 作者在这篇文章中想要达到什么目标？
Tokens: 13217 = (Prompt 6559 + Completion 6658) Cost: $0.04631

1. 这篇文章的研究背景有哪些？
2. 请介绍一下本文的研究背景。
3. 本文的研究背景涉及哪些方面？
4. 研究背景对本文的研究有何影响？
5. 为了解本文的内容，我需要了解一下研究背景是什么。
Tokens: 2179 = (Prompt 1318 + Completion 861) Cost: $0.00740

1. 这篇文章的研究假设是什么内容？
2. 请问这篇文章的研究假设是什么？
3. 作者在这篇文章中提出了什么样的研究假设？
4. 有关这篇文章的研究假设，请问是什么？
5. 我想了解一下这篇文章的研究假设是什么。
Tokens: 10312 = (Prompt 5044 + Completion 5268) Cost: $0.03620

1. 这篇文章采用了哪种研究方法？
2. 请问这篇文章是如何进行研究的？
3. 研究方法方面，这篇文章采用了什么样的方式？
4. 你能告诉我一下这篇文章的研究方法是什么吗？
5. 对于这篇文章，它使用了怎样的研究方法？
Tokens: 2278 = (Prompt 1348 + Completion 930) Cost: $0.00776

1. 这篇文章得出了什么样的研究结论？
2. 请问这篇文章的研究结论是什么？
3. 你能告诉我这篇文章的研究结论是什么吗？
4. 研究的结论是什么？我想了解一下。
5. 请问这篇文章得出了怎样的研究结论？
Tokens: 5617 = (Prompt 5041 + Completion 576) Cost: $0.01743

1. 这篇文章有哪些研究限制？
2. 有哪些方面限制了本文的研究？
3. 本文的研究有哪些局限性？
4. 有哪些因素限制了本文的研究范围？
5. 本文的研究存在哪些限制性条件？
Tokens: 6020 = (Prompt 5714 + Completion 306) Cost: $0.01837

1. 这篇文章使用了哪些数据分析工具？
2. 本文中采用了哪些数据分析工具？
3. 哪些数据分析工具被应用在这篇文章中？
4. 这篇文章中使用了哪些工具进行数据分析？
5. 本文中用到了哪些数据分析工具？
Tokens: 5106 = (Prompt 4730 + Completion 376) Cost: $0.01569

1. 这篇文章使用了哪些统计学方法？
2. 本文中采用了哪些统计学技术？
3. 哪些统计学工具被应用在这篇文章中？
4. 这篇文章使用了哪些统计学手段？
5. 本文中运用了哪些统计学工具进行分析？
Tokens: 7457 = (Prompt 6723 + Completion 734) Cost: $0.02310

1. 这篇文章有哪些亮点和创新之处？
2. 有哪些方面使得这篇文章在闪光点和创新性方面脱颖而出？
3. 这篇文章有哪些独特之处和创新点？
4. 请列举一些使得这篇文章在闪光点和创新性方面与众不同的地方。
5. 你认为这篇文章有哪些亮点和创新性的特点？
Tokens: 7970 = (Prompt 7717 + Completion 253) Cost: $0.02416

1. 有哪些地方需要对本文进行改进或优化？
2. 本文有哪些方面需要改进或优化？
3. 针对本文，有哪些需要改进或优化的地方？
4. 本文中有哪些需要进行改进或优化的部分？
5. 需要对本文进行哪些改进或优化？
Tokens: 5932 = (Prompt 5180 + Completion 752) Cost: $0.01855

1. 有哪些研究思路可以在本文中找到？
2. 本文中有哪些研究思路可以参考？
3. 有哪些可以借鉴的研究思路在本文中被提及？
4. 本文中提到了哪些可以借鉴的研究思路？
5. 有哪些研究思路可以从本文中获取灵感？"""

import re
def extract_and_sum(text):
    # 用于存储总和
    total_tokens = 0
    total_prompt = 0
    total_completion = 0
    total_cost = 0.0
    # 使用正则表达式找出所有符合格式的行
    matches = re.findall(r"\nTokens: (\d+) = \(Prompt (\d+) \+ Completion (\d+)\) Cost: \$(\d+.\d+)\n", text)
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
    result = f"Tokens: {total_tokens} = (Prompt {total_prompt} + Completion {total_completion}) Cost: ${total_cost:.3f}"
    return result

print(extract_and_sum(_s))

