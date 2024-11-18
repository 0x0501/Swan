import re

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

# 示例文本
text = """
                                2024-10-10
  更新于2024-10-12 09:12                            
"""

# 提取更新日期
# update_date = extract_update_date(text)
# if update_date:
#     print(f"提取的更新日期: {update_date}")
# else:
#     print("未找到更新日期")
    
# u2 = extract_update_date('2024-10-14\n  更新于2024-10-15 17:07')
# print(u2)