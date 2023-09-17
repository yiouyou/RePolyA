import re


def join_broken_sentences(text):
    lines = text.split('\n')
    current_line = ""
    result = []
    for line in lines:
        stripped_line = line.strip()
        word_count = len(re.findall(r'\b\w+\b', stripped_line))
        # Check if the line only contains digits or special characters like '/'
        if re.fullmatch(r'[\d\s/.-\\]+', stripped_line):
            if current_line:
                result.append(current_line)
                current_line = ""
            result.append(stripped_line)
            continue
        # Check if the line ends with a punctuation mark that typically ends or pauses a sentence
        if stripped_line and stripped_line[-1] in ('.', '!', '?', ':', ';', '-'):
            # If we've accumulated text in current_line, append it first
            if current_line:
                result.append(current_line + " " + stripped_line)
                current_line = ""
            else:
                result.append(stripped_line)
        else:
            # If it's not an ending or pausing punctuation, it's likely a broken sentence.
            # Append it to the current line only if the line has 5 or more words.
            if word_count >= 5:
                if current_line:
                    current_line += " " + stripped_line
                else:
                    current_line = stripped_line
            else:
                # If the line has fewer than 5 words, append it as is and reset the current_line
                if current_line:
                    result.append(current_line)
                result.append(stripped_line)
                current_line = ""
    # Append any remaining text
    if current_line:
        result.append(current_line)
    return '\n'.join(result)


def split_on_duplicate_lines(text):
    lines = text.split('\n')
    seen = set()
    duplicate_lines = set()
    splits = []
    current_split = []
    # First pass: Identify all duplicate lines
    for line in lines:
        if line in seen:
            duplicate_lines.add(line)
        else:
            seen.add(line)
    # Second pass: Split text and remove duplicates
    seen = set()
    for line in lines:
        if line in duplicate_lines:
            if current_split:
                splits.append('\n'.join(current_split).strip())
                current_split = []
            seen = set()  # Clear 'seen' for the new section
        else:
            current_split.append(line)
            seen.add(line)
    if current_split:
        splits.append('\n'.join(current_split).strip())
    return splits
# pdf_text = """2023/9/7
# The company landscape for artificial intelligence in large-molecule drug discovery
# 1/7
# blabla1
# blabla2
# blabla3
# 2023/9/7
# The company landscape for artificial intelligence in large-molecule drug discovery
# 2/7
# blabla4
# blabla5
# blabla6
# """
# sections = split_on_duplicate_lines(pdf_text)
# for i in range(len(sections)):
#     print('='*40)
#     print(f"'{sections[i]}'")


def split_sections_regex(text):
    sections = ["Abstract", "Introduction", "(Methods|Materials and Methods)", "(Results|Conclusions)", "References"]
    section_dict = {}
    _flags = re.MULTILINE | re.IGNORECASE
    first_match_pos = len(text)  # 第一个匹配节的起始位置，默认为文本末尾
    for i in range(len(sections)):
        pattern = f"^[\d\.]*\s*({sections[i]})\s*$\n"
        for match in re.finditer(pattern, text, _flags):
            first_match_pos = min(first_match_pos, match.start())
            break
    # 截取未定义节的内容并存储在 "_PRE" 键下
    if first_match_pos != 0:
        section_dict['_PRE'] = text[:first_match_pos].strip()
    last_pos = first_match_pos  # 记录上一个匹配节的结束位置
    for i in range(len(sections)):
        pattern = f"^[\d\.]*\s*({sections[i]})\s*$\n"
        for match in re.finditer(pattern, text, _flags):
            matched_title = match.group(1)
            start_pos = match.end()  # 当前匹配节内容的起始位置
            next_pos = len(text)  # 下一个匹配节的起始位置，默认为文本末尾
            # 找到下一个匹配节的起始位置
            for j in range(i + 1, len(sections)):
                next_match = re.search(f"^[\d\.]*\s*({sections[j]})\s*$\n", text[start_pos:], _flags)
                if next_match:
                    next_pos = start_pos + next_match.start()
                    break
            # 截取当前匹配节的内容
            section_content = text[start_pos:next_pos].strip()
            section_dict[matched_title] = section_content
            last_pos = next_pos  # 更新上一个匹配节的结束位置
    return section_dict
# pdf_text = """Abstract
# ...some abstract content...
# Introduction
# ...some introduction content...
# Algorithm
# ...some methods content...
# Conclusions
# ...some results content...
# """
# sections = split_sections_regex(pdf_text)
# print(sections)


def clean_and_split(text):
    uniq_lines = split_on_duplicate_lines(text)
    uniq_text = "\n".join(uniq_lines)
    _join = join_broken_sentences(uniq_text)
    sections = split_sections_regex(_join)
    return sections

