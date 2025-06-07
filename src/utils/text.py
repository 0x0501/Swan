import re
from PySide6.QtCore import QFile, QTextStream
from loguru import logger
import json


def load_json(qt_resource_path: str) -> dict:
    json_file = QFile(qt_resource_path)
    if not json_file.open(QFile.OpenModeFlag.ReadOnly
                          | QFile.OpenModeFlag.Text):
        logger.error(f"Cannot open file {qt_resource_path} for reading.")
        return {}
    stream = QTextStream(json_file)
    json_data = stream.readAll()
    json_file.close()

    try:
        return json.loads(json_data)
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file {qt_resource_path}.")


def extract_update_date(text):
    # 使用正则表达式匹配“更新于”后面的日期
    # \s* 表示任意数量的空白字符（包括空格、制表符、换行符等）
    # \d{4}-\d{2}-\d{2} 表示 YYYY-MM-DD 格式的日期
    # \s*\d{2}:\d{2} 表示 HH:MM 格式的时分
    match = re.search(r'更新于\s*(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})', text)

    if match:
        # 提取匹配的日期和时间
        update_date = match.group(1).strip()
        return update_date
    else:
        return text


# remove the trailing whitespace
def sanitize_text(text: str, remove_all: bool = True) -> str:
    if remove_all:
        return re.sub(r'\s+', '', text.strip())
    else:
        return text.strip()


def sanitize_text_for_red(text: str) -> str:
    # 去除所有 #符号及其后面的文字，直到空白符或字符串结尾
    text = re.sub(r'#\S*', '', text)
    
    # 替换多个连续的句号为一个句号
    text = re.sub(r'。+', '。', text)
    
    # 删除所有空白符（包括 \t、\n 和空格）
    text = re.sub(r'\s+', '', text)
    
    return text.strip()


def extract_and_convert_score(text: str):
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


def star_string_to_int(text: str):
    # 定义一个字典，用于映射不同的星星字符串到其对应的整数值
    star_mapping = {
        'star_5': 5,
        'star_4': 4,
        'star_3': 3,
        'star_2': 2,
        'star_1': 1,
        'star_0': 0
    }

    # 使用正则表达式查找匹配的星星字符串
    match = re.search(r'star_(\d)', text)

    # 如果找到匹配项，则根据字典返回对应的整数值
    if match:
        matched_star = match.group(0)  # 获取匹配的整个字符串
        return star_mapping.get(matched_star, None)  # 根据字典返回值或None

    # 如果没有找到匹配项，则返回None或其他默认值
    return -1


def concatenate_with_conditions(str_list):
    if not str_list:  # 如果列表为空，则返回空字符串
        return ''

    result = []
    for i, s in enumerate(str_list):
        result.append(s)
        if i < len(str_list) - 1:  # 检查是否是最后一个元素
            # 检查当前字符串的最后一个字符是否不是指定的标点符号，并且不是最后一个元素
            if not s.endswith(('。', '，', '！', '!', '~', ',', '.', '……')):
                result.append('。')  # 添加分隔符

    # 移除可能在最后一个字符串后面多加的分隔符
    final_string = ''.join(result)
    for punct in ('。', '，', '！', '!', '~', ',', '.', '……'):
        if final_string.endswith(punct + '。'):
            final_string = final_string[:-1]
            break

    return final_string
