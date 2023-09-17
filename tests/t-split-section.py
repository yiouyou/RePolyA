import re

def split_sections_regex(text):
    sections = ["Abstract", "Introduction", "(Methods|Algorithm)", "(Results|Conclusions)"]
    section_dict = {}
    _flags = re.MULTILINE | re.IGNORECASE
    last_pos = 0  # 记录上一个匹配节的结束位置
    for i in range(len(sections)):
        pattern = f"^({sections[i]})$\n"
        for match in re.finditer(pattern, text, _flags):
            matched_title = match.group(1)
            start_pos = match.end()  # 当前匹配节内容的起始位置
            next_pos = len(text)  # 下一个匹配节的起始位置，默认为文本末尾
            # 找到下一个匹配节的起始位置
            for j in range(i + 1, len(sections)):
                next_match = re.search(f"^({sections[j]})$\n", text[start_pos:], _flags)
                if next_match:
                    next_pos = start_pos + next_match.start()
                    break
            # 截取当前匹配节的内容
            section_content = text[start_pos:next_pos].strip()
            section_dict[matched_title] = section_content
            last_pos = next_pos  # 更新上一个匹配节的结束位置
    return section_dict

pdf_text = """Abstract
...some abstract content...

Introduction
...some introduction content...

Algorithm
...some methods content...

Conclusions
...some results content...
"""

sections = split_sections_regex(pdf_text)
print(sections)
