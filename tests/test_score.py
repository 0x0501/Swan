import re

def extract_and_convert_score(text):
    # 定义映射关系
    score_mapping = {
        'sml-str5': 0.5,
        'sml-str10': 1.0,
        'sml-str15': 1.5,
        'sml-str20': 2.0,
        'sml-str25': 2.5,
        'sml-str30': 3.0,
        'sml-str35': 3.5,
        'sml-str40': 4.0,
        'sml-str45': 4.5,
        'sml-str50': 5.0
    }

    # 正则表达式模式，用于匹配 `sml-str*` 或 `sml-strs*`
    pattern = r'\bsml-str[s]?\d+\b'

    # 查找第一个匹配的子字符串
    match = re.search(pattern, text)

    if match:
        semantic_text = match.group(0)
        # 将匹配的子字符串转换为对应的分数
        if semantic_text in score_mapping:
            return score_mapping[semantic_text]
        else:
            return -1
    else:
        return -1
    
s = extract_and_convert_score("sml-rank-stars sml-str45 star")
print(s)