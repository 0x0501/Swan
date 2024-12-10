from random import randint
import requests
import traceback
from DataRecorder import Recorder
import time
from bs4 import BeautifulSoup

def task_qnw() -> Recorder:

    page_maximum = 100

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    }

    try:
        for i in range(1, page_maximum):
            response = requests.get(
                'https://travel.qunar.com/place/api/html/comments/poi/715281?poiList=true&sortField=0&rank=0&pageSize=10&page=%d'
                % i, headers=headers)
            json_data = response.json()
            navigation_retry_count = 0
            while json_data['success'] == False and navigation_retry_count <=5:
                if navigation_retry_count <=3:
                        sleep_time = randint(3, 5)
                else:
                        sleep_time = randint(5, 10)
                time.sleep(sleep_time)
                print('Sleep %s sec, and retry.' % sleep_time)
                response = requests.get(
                'https://travel.qunar.com/place/api/html/comments/poi/715281?poiList=true&sortField=0&rank=0&pageSize=10&page=%d'
                % i, headers=headers)
                json_data = response.json()
                navigation_retry_count += 1
                print('Retrying to navigate (%s)' % navigation_retry_count)
            # print(json_data)

            # 解析JSON数据
            parsed_json = json_data

            # 获取data字段的值并解码Unicode转义序列
            # html_content = parsed_json['data'].encode().decode(
            #     'unicode-escape')
            soup = BeautifulSoup(parsed_json['data'], 'lxml')
            review_list = soup.select('#comment_box > li')

            for index, review_item in enumerate(
                    review_list):  #.get_text(strip=True)
                raw_date = review_item.select(
                    '.e_comment_add_info > ul > li:first-child')[0].get_text(
                        separator='|').split('|')[0]
                raw_score = review_item.select(
                    '.e_comment_star_box > .total_star > span')[0].get(
                        'class')[1]

                raw_content = ''
                # if no element was found, return false
                if len(review_item.select('.e_comment_content .seeMore')) == 0:
                    raw_content = ''.join(
                        review_item.select('.e_comment_content')[0].getText(
                            strip=True))
                else:
                    deep_link = review_item.select('.e_comment_content .seeMore')[0].get('href')
                    print(deep_link)
                print(raw_date)
                print(raw_score)
                print([raw_content, raw_date, raw_score])

            time.sleep(3)
            # print(json_data)
    except Exception as e:
        traceback.print_exc(e)
    return None


task_qnw()
