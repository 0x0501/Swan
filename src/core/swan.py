import re
import os
import sys
from DataRecorder import Recorder
from DrissionPage import Chromium
from DrissionPage import ChromiumOptions
from loguru import logger
from DrissionPage.errors import *
from enum import Enum, unique
from pathlib import Path
from src.utils.config import Config


@unique
class Location(Enum):
    SHUHE_TOWN = 'https://www.dianping.com/shop/iDYbcrjcbQJyvJyu/review_all',
    BAISHA_TOWN = 'https://www.dianping.com/shop/k6ttY31GVwu40nbW/review_all'


# remove the trailing whitespace
def sanitize_text(text: str, remove_all: bool = True) -> str:
    if remove_all:
        return re.sub(r'\s+', '', text.strip())
    else:
        return text.strip()


class Swan():

    config_file_path = ''
    data_directory = ''
    __config: Config = None
    config = None
    location: Location = None
    chromium_tabs: list = []
    chromium_options = ChromiumOptions

    def __init__(self, config_file_path: str) -> None:
        self.config_file_path = config_file_path
        self.__config = Config(config_file_path=config_file_path)
        self.config = self.__config.load()

        # log initialization
        logger.add(self.config['application']['log_file_path'])
        pass

    def launch(self):

        logger.info("Comment Swan started!")
        chrome_executable_path = Path(
            self.config['application']['chrome_executable_path'])

        if not os.path.exists(chrome_executable_path):
            error_msg = "Can't find chrome executable file at %s" % chrome_executable_path
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        else:
            logger.info("chrome_executable_path: %s" % chrome_executable_path)
            self.chromium_options = ChromiumOptions().set_browser_path(
                path=chrome_executable_path)

        return self

    def set_location(self, location: Location) -> Location:

        # initialized enum data
        match location:
            case Location.SHUHE_TOWN:
                location.literal = '束河古镇'
            case Location.BAISHA_TOWN:
                location.literal = '白沙古镇'
        self.location = location
        return location

    def grace_shutdown(self):
        if len(self.chromium_tabs) == 0:
            logger.warning('No tab was opened, shut down Swan right now.')
            return
        for i in self.chromium_tabs:
            # close all the tabs
            i.stop_loading()
            i.close()
        logger.warning('Grace shutdown Swan, closing all the tabs.')

    def extract_and_convert_score(self, text: str):
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

    def task_dzdp(self):
        # launch a new tab
        tab = Chromium(self.chromium_options).latest_tab

        # push the tab into list
        self.chromium_tabs.append(tab)

        # visit dazhongdianping land-page, and show error message
        tab.get(
            'https://account.dianping.com/pclogin?redir=https://m.dianping.com/dphome',
            True)
        # switch_manual_login, if already logged in, skip this

        logged_in_cookie = dict(
            filter(lambda i: i[0] == 'logan_session_token',
                   tab.cookies().as_dict().items()))

        if len(logged_in_cookie) == 0:
            tab.ele('@@class=bottom-password-login@@tag()=span').click()
            tab.ele('@@class=pwd@@tag()=div').click()
            logger.info(
                "Switch to manual login, trying to input username and password."
            )

            # filling info
            phone_number = tab.ele('@id=mobile-number-textbox').input(
                self.config['account']['dzdp']['username'])
            password = tab.ele('@id=password-textbox').input(
                self.config['account']['dzdp']['password'])
            user_agreement = tab.ele('@class=pc-agreement').ele(
                '@id=pc-check').check()
            login_button = tab.ele('@class=login-box').ele(
                '@class=button-pc').click()
        else:
            # detect cookie, skip login
            logger.info('Got logan_session_token, skip login.')

        # waiting navigation change
        if tab.wait.url_change('https://m.dianping.com/dphome') != False:
            logger.info('Logging success.')

        # setting land-page location
        tab.get('https://www.dianping.com/%s' %
                self.config['account']['dzdp']['location'])
        logger.info('Setting land-page location to %s.' %
                    self.config['account']['dzdp']['location'])

        # check whether the search field exist
        if tab.ele('@id=J-search-input') != None:
            logger.info('Location fixed successfully. [%s]' %
                        self.config['account']['dzdp']['location'])
        else:
            # TODO! 2024-11-16 how to handle location fixing failed
            logger.error('Location fixing failed. [%s]' %
                         self.config['account']['dzdp']['location'])

        # navigate to shuhe/baisha town
        self.set_location(Location.SHUHE_TOWN)

        tab.get(self.location.value[0])
        logger.info('Navigate to %s.' % self.location.name)

        # check whether the shop name match the intended one
        logger.debug('Shop name value: %s' %
                     tab.ele('@@tag()=h1@@class=shop-name').texts(
                         text_node_only=True)[0])
        logger.debug('desired_location: %s ' % self.location.literal)
        if tab.ele('@@tag()=h1@@class=shop-name').texts(
                text_node_only=True)[0] == self.location.literal:
            logger.info(
                'Successfully Navigated to %s. Preparing data collector.' %
                self.location.name)

        ############################## Data collector #######################################

        # change browser mode to `s` (session mode)
        tab.change_mode()
        tab.close()
        logger.info('Change browser mode to: `%s`' % tab.mode)

        # change page element to static element
        page_maximum: int = self.config['account']['dzdp']['page_maximum']
        # current_page = 0

        for current_page in range(1, page_maximum):
            logger.info("Task `dzdp` current page %d" % current_page)

            # if the page number >= 2, we need to change the url
            # https://www.dianping.com/shop/iDYbcrjcbQJyvJyu/review_all/p2
            if current_page >= 2:
                updated_url = self.location.value[0] + '/p%d' % current_page
                tab.get(updated_url)
                logger.info('Update the url to %s' % updated_url)

            root = tab.ele('@tag()=body')

            try:
                review_list = root.s_eles(
                    'css:div[class=reviews-items] > ul > li')
                logger.info("The page %d has %d comments, grab them!" %
                            (current_page, len(review_list)))
                # iterate review items
                for review_item in review_list:
                    raw_review_content: list[str] = review_item.ele(
                        '@@tag()=div@@class=main-review').ele(
                            '@|class=review-words@|class=review-words Hide'
                        ).texts(text_node_only=True)
                    # review content
                    review_content = list(
                        map(lambda s: sanitize_text(s), raw_review_content))
                    # review date
                    review_date = sanitize_text(
                        review_item.ele('@@tag()=div@@class=main-review').ele(
                            'css:div.misc-info > span.time').texts()[0], False)

                    # review score
                    review_score = self.extract_and_convert_score(
                        review_item.ele('@@tag()=div@@class=main-review').ele(
                            'css:div.review-rank > span').attr('class'))

                    # joint them together
                    review_content.append(review_date)
                    review_content.append(review_score)
                    logger.info(review_content)
                    # TODO! write comment data to file
                    
                    

                # sleep for 3 ~ 10 secs
                tab.wait(3, 10)

            except ElementNotFoundError:
                logger.error(
                    'Cannot find review elements, by: css:div[class=reviews-items] > ul > li'
                )
        logger.warning('The task `dzdp` has finished.')


def comment_swan_main():
    swan = Swan('./swan.config.toml').launch()
    try:
        swan.task_dzdp()
    except KeyboardInterrupt:
        swan.grace_shutdown()
        sys.exit(0)


if __name__ == '__main__':
    comment_swan_main()
