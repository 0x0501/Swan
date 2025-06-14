import os
import requests
import traceback
import sys
import time
import pandas as pd
from bs4 import BeautifulSoup
from PySide6.QtCore import QSettings
from random import randint
from DataRecorder import Recorder
from DrissionPage import Chromium
from DrissionPage import ChromiumOptions
from loguru import logger
from DrissionPage.errors import *
from pathlib import Path
from src.core.location import Location
from src.utils.text import (concatenate_with_conditions,
                            extract_and_convert_score, extract_update_date,
                            sanitize_text, star_string_to_int)
from src.gui.event.task_progress_tracker import TaskProgressTracker
from typing import Optional, Union, Tuple
from src.core.encryption import Encryption
from src.core.location_mapping import LocationMapping
from src.core.swan_platform import Platform


class Swan():
    _swan_version = '1.0.1'
    log_file_path = ''
    data_directory = ''
    land_page_location = 'Lijiang'
    start_time = 0.0
    settings: QSettings
    location: Location = None
    chromium_tabs: list = []
    platform: Platform = Platform.DAZHONGDIANPING
    chromium_options = ChromiumOptions
    _encryption = Encryption

    def __init__(self,
                 q_settings: QSettings,
                 progress_tracker: TaskProgressTracker = None) -> None:
        self.settings = q_settings
        self.log_file_path = self.settings.value('log_path', './logs/swan.log')
        self._running = False
        self._encryption = Encryption(
            self.settings.value('encryption_dir_path', './bin'), self.settings,
            None)
        self.page_maximum = self.settings.value('page_maximum', 600, type=int)
        # log initialization
        # logger.add(self.log_file_path)
        self.progress_tracker = progress_tracker
        # attempt-retry
        self.retry_count = 0

    @staticmethod
    def swan_version() -> str:
        return Swan._swan_version

    def is_running(self) -> bool:
        return self._running

    def calculate_sleep_time(self, start_time) -> int:
        """
        计算休眠时间和处理休息时间的函数。

        :param start_time: 程序开始运行的时间（以秒为单位）
        :return: 本次循环的休眠时间（秒）
        """
        current_time = time.time()
        runtime_minutes = (current_time - start_time) // 60

        # 每运行一个小时休息10分钟
        if runtime_minutes % 60 == 0 and runtime_minutes > 0:
            logger.debug(
                f"Running for {runtime_minutes} minutes, taking a 10-minute break..."
            )
            return randint(600, 700)  # 返回10分钟的休眠时间，以便重置开始时间

        # 每运行三个小时休息15分钟
        if runtime_minutes % 180 == 0 and runtime_minutes > 0:
            logger.debug(
                f"Running for {runtime_minutes} minutes, taking a 15-minute break..."
            )
            return randint(900, 1100)  # 返回15分钟的休眠时间，以便重置开始时间

        # 动态调整休眠时间
        if runtime_minutes < 30:
            sleep_time = randint(15, 20)
        elif runtime_minutes < 60:
            sleep_time = randint(25, 35)
        else:
            sleep_time = randint(35, 40)

        return sleep_time

    def launch(self):
        logger.info("Comment Swan started!")
        chrome_executable_path = Path(
            self.settings.value('chrome_executable_path', ''))

        if not os.path.exists(chrome_executable_path):
            error_msg = "Can't find chrome executable file at %s" % chrome_executable_path
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        else:
            logger.info("chrome_executable_path: %s" % chrome_executable_path)
            self.chromium_options = ChromiumOptions().set_browser_path(
                path=chrome_executable_path)
        # setting running state
        # self._running = True
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

    def set_platform(self, platform: Platform) -> Platform:
        self.platform = platform
        return self.platform

    def safe_wait(self, tab, sec: int):
        if self._running == False:
            return
        else:
            tab.wait(sec)

    def grace_shutdown(
        self,
        recorder: Optional[Recorder] = None,
    ):
        # change running state
        logger.warning('Swan inner _running: %s' % self._running)
        self._running = False
        # flush the cache first (这个操作应该很快)
        if recorder is not None:
            logger.debug('Flush the data (in grace_shutdown)! Way to go!')
            recorder.record()
            logger.debug('Auto save file at: %s' % recorder.path)
            logger.debug('Date in Recorder: %s' % recorder.data)

        # 移除长时间等待的操作，改用非阻塞方式
        if len(self.chromium_tabs) == 0:
            logger.warning('No tab was opened, shut down Swan right now.')
            return

        # 只是发送关闭信号，不等待
        for tab in self.chromium_tabs:
            try:
                tab.stop_loading()
                tab.close()
            except Exception as e:
                logger.error(f'Error closing tab: {e}')
        logger.warning('Grace shutdown Swan, closing all the tabs.')
        return

    # return [page, index], index started from 0
    # every page has 15 items
    def read_resume_status(
            self, data_file_path: Path) -> Union[int, Tuple[int, int]]:

        last_row_data = 0

        try:
            # data frame
            csv_data = pd.read_csv(data_file_path, sep='|').tail(1)

            if csv_data.empty:
                return -1

            last_row = csv_data.iloc[-1]
            last_row_data = int(last_row['Page']), int(last_row['Index'])
        except Exception as e:
            logger.error(e)
            last_row_data = -1
        finally:
            return last_row_data

    def task_dzdp_login(self, tab):
        logger.debug('Re-login has been triggered. (dzdp)')
        tab.cookies().clear()  # clear all the cookies
        tab.clear_cache()  # clear all the cache
        # switch to dynamic mode
        tab.change_mode('d')
        username = self.settings.value('dzdp_username', '')
        password = self._encryption.get_encrypted('dzdp_password', '')

        if username == '' or password == '':
            logger.error('Username or password don\'t configure properly.')
            raise Exception('Username or password don\'t configure properly.')

        tab.get(
            'https://account.dianping.com/pclogin?redir=https://m.dianping.com/dphome',
            True)
        tab.ele('@@class=bottom-password-login@@tag()=span').click()
        tab.ele('@@class=pwd@@tag()=div').click()
        logger.info(
            "Switch to manual login, trying to input username and password.")
        # filling info
        tab.ele('@id=mobile-number-textbox').input(
            self.settings.value('dzdp_username'))
        tab.ele('@id=password-textbox').input(
            self._encryption.get_encrypted('dzdp_password'))
        user_agreement = tab.ele('@class=pc-agreement').ele(
            '@id=pc-check').check()
        login_button = tab.ele('@class=login-box').ele('@class=button-pc')

        # try to directly log in
        login_button.click()

        # check whether CAPTCHA was displayed
        try:
            login_captcha = tab.ele('@class=login-box').ele('css:.pc-mask')
            logger.warning(
                'CAPTCHA required. Please input them in 30 seconds.')
            # wait 10 seconds
            tab.wait(30)
        except ElementNotFoundError:
            logger.debug('No CAPTCHA was detected.')

        # check whether the account is restricted
        try:
            login_warning: list[str] = tab.ele('@class=login-box').ele(
                'css:.warning').texts()
            if login_warning[0] == '你的账号存在安全隐患，为保障您的账号安全，请使用扫码登录':
                logger.warning(
                    'This account has been restricted, please scan the QRCode to log within 60 seconds.'
                )
                # wait 10 seconds
                tab.wait(60)
            else:
                logger.error('Unexpected logging error: %s' % login_warning)
        except ElementNotFoundError:
            logger.debug('This account doesn\'t trigger restricted policy.')

        # check whether verification code was required
        if 'meituan' in tab.url:
            logger.warning(
                'Verification code was required, please get it and fill out in the box, Swan will wait 60 seconds.'
            )
            tab.wait(60)
        # switch to session mode
        tab.change_mode('s')

    def task_dzdp(self) -> Recorder:
        # change running state
        self._running = True
        # store the data as CSV file
        data_file_path = Path.joinpath(
            Path(self.settings.value('data_directory', './data')),
            'dazhongdianping.csv')
        recorder = Recorder(path=data_file_path, cache_size=75)
        logger.debug('Swan (in) _running state: %s' % self._running)
        try:
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
                self.task_dzdp_login(tab)
                # tab.ele('@@class=bottom-password-login@@tag()=span').click()
                # tab.ele('@@class=pwd@@tag()=div').click()
                # logger.info(
                #     "Switch to manual login, trying to input username and password."
                # )
            else:
                # detect cookie, skip login
                logger.info('Got logan_session_token, skip login.')

            # waiting navigation change
            if tab.wait.url_change('https://m.dianping.com/dphome') != False:
                logger.info('Logging success.')

            # setting land-page location
            tab.get('https://www.dianping.com/%s' % self.land_page_location)
            logger.info('Setting land-page location to %s.' %
                        self.land_page_location)

            # check whether the search field exist
            if tab.ele('@id=J-search-input') != None:
                logger.info('Location fixed successfully. [%s]' %
                            self.land_page_location)
            else:
                # TODO! 2024-11-16 how to handle location fixing failed
                logger.error('Location fixing failed. [%s]' %
                             self.land_page_location)
            # check the running state for the second time
            if self._running == False:
                logger.error(
                    'Swan received `stop` command on the second layer.')
                # flush the data first, and return `recorder` for convenient
                recorder.record()
                return recorder

            # navigate to shuhe/baisha town, given them the literal name
            self.set_location(self.location)
            logger.debug('Swan location (inner): %s' % self.location)
            logger.debug("Swan location URL (inner): %s" % self.location.value)
            tab.get(self.location.value)
            logger.info('Navigate to %s.' % self.location.name)

            # check whether the shop name match the intended one
            try:
                shop_name = tab.ele('@@tag()=h1@@class=shop-name')
                logger.debug('Shop name value: %s' %
                             shop_name.texts(text_node_only=True)[0])
                logger.debug('desired_location: %s ' % self.location.literal)
                if tab.ele('@@tag()=h1@@class=shop-name').texts(
                        text_node_only=True)[0] == self.location.literal:
                    logger.info(
                        'Successfully Navigated to %s. Preparing data collector.'
                        % self.location.name)
            except ElementNotFoundError as e:
                # if the ip has been banned, clear all the cookies, and re-login
                logger.warning(
                    'Oops, our ip address might have been banned, let\'s try to re-login in. :('
                )
                logger.info('Clear all the cookies and cache.')
                # tab.cookies().clear()  # clear all the cookies
                # tab.clear_cache()  # clear all the cache
                self.task_dzdp_login(tab)

            ############################## Data collector #######################################

            # change browser mode to `s` (session mode)
            tab.change_mode()
            # tab.close()
            logger.info('Change browser mode to: `%s`' % tab.mode)

            # change page element to static element
            page_maximum: int = self.page_maximum
            # current_page = 0

            if self.progress_tracker:
                self.progress_tracker.total_pages = page_maximum

            # set the start time from here
            start_time = time.time()
            # if `dazhongdianping.csv` exist, read the last line from this file, and started task from that point (page + item)
            initial_page = 1
            last_row_data = self.read_resume_status(data_file_path)

            if last_row_data != -1:
                # get item index
                if last_row_data[1] < 14:
                    initial_page = last_row_data[0]
                else:
                    initial_page = last_row_data[0] + 1
                logger.debug('Resume data collect from page: [%d].' %
                             initial_page)

            if initial_page >= page_maximum:
                logger.error(
                    'Initial page number >= page_maximum. That\'s impossible.')
                return recorder

            for current_page in range(initial_page, page_maximum):

                # check the running state
                if self._running == False:
                    logger.warning(
                        'Swan received `stop` command on the first layer.')
                    # flush the data first, and return `recorder` for convenient
                    recorder.record()
                    return recorder

                if self.progress_tracker:
                    self.progress_tracker.current_page = current_page
                logger.info("Task `dzdp` current page %d" % current_page)

                # if the page number >= 2, we need to change the url
                # https://www.dianping.com/shop/iDYbcrjcbQJyvJyu/review_all/p2
                if current_page >= 2:
                    updated_url = self.location.value + '/p%d' % current_page
                    tab.get(updated_url)
                    logger.info('Update the url to %s' % updated_url)

                root = tab.ele('@tag()=body')

                try:
                    review_list = root.s_eles(
                        'css:div[class=reviews-items] > ul > li')
                    logger.info("The page %d has %d comments, grab them!" %
                                (current_page, len(review_list)))

                    # if the comment list was empty, try re-login
                    if len(review_list) == 0:
                        self.task_dzdp_login(tab)
                    # iterate review items
                    logger.debug('Review list length: %d' % len(review_list))
                    for index, review_item in enumerate(review_list):

                        # check the running state for the second time
                        if self._running == False:
                            logger.error(
                                'Swan received `stop` command on the second layer.'
                            )
                            # flush the data first, and return `recorder` for convenient
                            recorder.record()
                            return recorder

                        raw_review_content: list[str] = review_item.ele(
                            '@@tag()=div@@class=main-review').ele(
                                '@|class=review-words@|class=review-words Hide'
                            ).texts(text_node_only=True)
                        # For emoji and other rendering problem, we have to join the str list

                        # review content
                        review_content = [
                            '。'.join(
                                list(
                                    map(lambda s: sanitize_text(s),
                                        raw_review_content)))
                        ]

                        # review date
                        review_date = sanitize_text(
                            review_item.ele('@@tag()=div@@class=main-review').
                            ele('css:div.misc-info > span.time').texts()[0],
                            False)

                        if "更新于" in review_date:
                            review_date = extract_update_date(review_date)
                            logger.debug(
                                'Got updated date, trying to extract it. The result: %s'
                                % review_date)

                        # review score
                        review_score = extract_and_convert_score(
                            review_item.ele('@@tag()=div@@class=main-review').
                            ele('css:div.review-rank > span').attr('class'))
                        # joint them together
                        review_content.append(review_date)
                        review_content.append(review_score)
                        review_content.append(current_page)
                        review_content.append(index)  # index started from 0
                        logger.info(review_content)
                        # TODO! write comment data to file

                        # write the data
                        recorder.set.delimiter('|')
                        recorder.set.encoding('utf-8')
                        # set header and backup
                        recorder.set.head([
                            'Comment', 'Comment Date', 'Score', 'Page', 'Index'
                        ])
                        recorder.set.auto_backup(60)
                        recorder.add_data(review_content)

                    # sleep for 3 ~ 10 secs
                    sleep_time = self.calculate_sleep_time(start_time)
                    if sleep_time in [600, 1100]:
                        start_time = time.time()

                    logger.info(
                        "Sleep %s seconds before the next move. Take your time master >_="
                        % sleep_time)
                    tab.wait(sleep_time)

                except ElementNotFoundError:
                    logger.error(
                        'Cannot find review elements, by: css:div[class=reviews-items] > ul > li'
                    )
                    # flush the cache
                    recorder.record()
            logger.warning('The task `dzdp` has finished.')
        except Exception as e:
            # if the document is empty, it means we got some problem:
            # 1. The account was restricted, we need to re-login
            # 2. Other error occurred. (Have no idea)
            logger.error(f"Error in task_dzdp: {e}")
            traceback.print_exc()
            if self.retry_count <= 3:
                logger.warning(
                    'Retrying re-login solving this problem, attempt: %d (maximum 3 times)'
                    % self.retry_count)
                self.retry_count += 1
                self.task_dzdp_login(tab)
                #retry
                self.task_dzdp()
            else:
                logger.warning(
                    'Retry attempt was up to maximum(3), Swan has to stop, please check Swan log. Chances are that your account has been banned.'
                )
        finally:
            # 确保资源被清理
            logger.debug('Swan state in Finally Statement: %s' % self._running)
            if not self._running:
                logger.debug('Finally statement revoke grace shutdown!')
                self.grace_shutdown(recorder)
                return recorder

    def _map_location_to_xiecheng(self, location: Location) -> LocationMapping:
        match location:
            case Location.SHUHE_TOWN:
                return LocationMapping(
                    location.name,
                    'https://you.ctrip.com/sight/lijiang32/17963.html', '束河古镇')
            case Location.BAISHA_TOWN:
                return LocationMapping(
                    location.name,
                    'https://you.ctrip.com/sight/yulong1446279/17965.html',
                    '白沙古镇')
        return location

    def _map_location_to_red(self, location: Location) -> Location:
        match location:
            case Location.SHUHE_TOWN:
                return LocationMapping(
                    location.name,
                    'https://www.xiaohongshu.com/search_result/?keyword=%25E6%259D%259F%25E6%25B2%25B3%25E5%258F%25A4%25E9%2595%2587&type=54&source=web_note_detail_r10',
                    '束河古镇')
            case Location.BAISHA_TOWN:
                return LocationMapping(
                    location.name,
                    'https://www.xiaohongshu.com/search_result?keyword=%25E7%2599%25BD%25E6%25B2%2599%25E5%258F%25A4%25E9%2595%2587&source=web_search_result_notes',
                    '白沙古镇')
        return location

    def _map_location_to_qnw(self, location: Location) -> Location:
        match location:
            case Location.SHUHE_TOWN:
                return LocationMapping(
                    location.name,
                    'https://travel.qunar.com/p-oi715281-shuheguzhen-0-1#lydp',
                    '束河古镇')
            case Location.BAISHA_TOWN:
                return LocationMapping(
                    location.name,
                    'https://travel.qunar.com/p-oi5475589-baishaguzhen-0-1#lydp',
                    '白沙古镇')
        return location

    def task_xiecheng(self) -> Recorder:

        # change running state
        self._running = True
        # store the data as CSV file
        data_file_path = Path.joinpath(
            Path(self.settings.value('data_directory', './data')),
            'xiecheng.csv')
        recorder = Recorder(path=data_file_path, cache_size=75)
        logger.debug('Swan (in) _running state: %s' % self._running)

        is_never_jumped = True

        try:
            # launch a new tab
            tab = Chromium(self.chromium_options).latest_tab

            # push the tab into list
            self.chromium_tabs.append(tab)

            # set location and map it to corresponding links
            self.set_location(self.location)
            location = self._map_location_to_xiecheng(self.location)

            logger.info(location.name)
            logger.info(location.value)

            # navigate to shuhe/baisha town
            tab.get(location.value)

            # get the maximum page number
            page_maximum_label = tab.ele('css:.myPagination > ul').child(
                index=8)
            page_maximum: int = int(page_maximum_label.texts()[0])

            # change browser mode to `s` (session mode)
            # tab.change_mode()
            # tab.close()
            # logger.info('Change browser mode to: `%s`' % tab.mode)

            if self.progress_tracker:
                self.progress_tracker.total_pages = page_maximum

            # set the start time from here
            start_time = time.time()
            # if `dazhongdianping.csv` exist, read the last line from this file, and started task from that point (page + item)
            initial_page = 1
            last_row_data = self.read_resume_status(data_file_path)

            if last_row_data != -1:
                # get item index
                initial_page = last_row_data[0] + 1
                logger.debug('Resume data collect from page: [%d].' %
                             initial_page)

            if initial_page >= page_maximum:
                logger.error(
                    'Initial page number >= page_maximum. That\'s impossible.')
                return recorder

            logger.info('Page maximum %s' % page_maximum)
            for current_page in range(initial_page, page_maximum):

                # check the running state
                if self._running == False:
                    logger.warning(
                        'Swan received `stop` command on the first layer.')
                    # flush the data first, and return `recorder` for convenient
                    recorder.record()
                    return recorder

                if self.progress_tracker:
                    self.progress_tracker.current_page = current_page
                logger.info("Task `xiecheng` current page %d" % current_page)

                if initial_page != 1 and is_never_jumped == True:
                    # jump to the specified page
                    jump_input = tab.ele(
                        'css:.ant-pagination-options-quick-jumper > input')
                    jump_input.input(initial_page)
                    jump_btn = tab.ele(
                        'css:.ant-pagination-options-quick-jumper button')
                    # wait until all the elements were loaded
                    tab.wait(3)
                    jump_btn.click()
                    logger.info(jump_btn)
                    is_never_jumped = False

                tab.wait(3)
                # alter comment sort method
                sort_list = tab.ele('css:.sortList').child(index=-1)
                sort_list.click()
                # wait until all the elements were loaded
                tab.wait(3)

                # retrieve comment list (wrapper)
                root = tab.ele('@tag()=body')
                review_list = root.s_eles('css:.commentList .contentInfo')
                logger.info('Comment list length: %d' % len(review_list))

                # parse the content
                for index, review_item in enumerate(review_list):

                    # check the running state for the second time
                    if self._running == False:
                        logger.error(
                            'Swan received `stop` command on the second layer.'
                        )
                        # flush the data first, and return `recorder` for convenient
                        recorder.record()
                        return recorder

                    raw_score = review_item.ele(
                        'css:.scroreInfo > span').texts(text_node_only=True)[0]
                    raw_date = review_item.ele(
                        'css:.commentFooter > .commentTime').texts(
                            text_node_only=True)[0]
                    raw_content = review_item.ele('css:.commentDetail').texts(
                        text_node_only=True)[0]

                    review_content = [sanitize_text(raw_content)]
                    review_content.append(raw_date)
                    review_content.append(int(raw_score))
                    review_content.append(current_page)
                    review_content.append(index)

                    logger.info(review_content)

                    # write the data
                    recorder.set.delimiter('|')
                    recorder.set.encoding('utf-8')
                    # set header and backup
                    recorder.set.head(
                        ['Comment', 'Comment Date', 'Score', 'Page', 'Index'])
                    recorder.set.auto_backup(60)
                    recorder.add_data(review_content)

                # sleep for 3 ~ 10 secs
                sleep_time = self.calculate_sleep_time(start_time)
                if sleep_time in [600, 1100]:
                    start_time = time.time()

                logger.info(
                    "Sleep %s seconds before the next move. Take your time master >_="
                    % sleep_time)
                tab.wait(sleep_time)

                # navigate to the next page
                next_page_btn = tab.ele(
                    'css:.myPagination > ul > .ant-pagination-next')
                next_page_btn.click()

        except Exception as e:
            logger.error(f"Error in task_xiecheng: {e}")
            traceback.print_exc(e)
        finally:
            # 确保资源被清理
            logger.debug('Swan state in Finally Statement: %s' % self._running)
            if not self._running:
                logger.debug('Finally statement revoke grace shutdown!')
                self.grace_shutdown(recorder)
                return recorder

    # 去哪网
    def task_qnw(self) -> Recorder:
        # change running state
        self._running = True
        # store the data as CSV file
        data_file_path = Path.joinpath(
            Path(self.settings.value('data_directory', './data')),
            'qunaerwang.csv')
        recorder = Recorder(path=data_file_path, cache_size=75)
        logger.debug('Swan (in) _running state: %s' % self._running)

        try:
            # launch a new tab
            tab = Chromium(self.chromium_options).latest_tab

            # push the tab into list
            self.chromium_tabs.append(tab)

            # set location and map it to corresponding links
            self.set_location(self.location)
            location = self._map_location_to_qnw(self.location)

            # logger.info(location.name)
            # logger.info(location.value)

            # navigate to shuhe/baisha town
            tab.get(location.value)
            navigation_retry_count = 0
            while not tab.ele('css:.b_paging > .page.next'
                              ) and navigation_retry_count <= 5:
                sleep_time = randint(3, 5)
                logger.warning(
                    'Navigate to url: %s failed, sleep %d sec and retrying.' %
                    (location.value, sleep_time))
                tab.wait(sleep_time)
                logger.warning('Retrying to navigate to %s (%d)' %
                               (location.value, navigation_retry_count))
                tab.refresh()
                navigation_retry_count += 1

            if not tab.ele('css:.b_paging > .page.next'
                           ) and navigation_retry_count == 3:
                logger.error('Oops. our ip seems to be banned, stop Swan.')
                return recorder
            # get the maximum page number
            page_maximum_label = tab.ele('css:.b_paging > .page.next').prev()
            page_maximum: int = int(page_maximum_label.texts()[0])

            if self.progress_tracker:
                self.progress_tracker.total_pages = page_maximum + 1

            # set the start time from here
            start_time = time.time()
            # if `qunaerwang.csv` exist, read the last line from this file, and started task from that point (page + item)
            initial_page = 1
            last_row_data = self.read_resume_status(data_file_path)
            logger.info('Page maximum %s' % page_maximum)

            if last_row_data != -1:
                # get item index
                if last_row_data[1] < 9:
                    initial_page = last_row_data[0]
                else:
                    initial_page = last_row_data[0] + 1
                logger.debug('Resume data collect from page: [%d].' %
                             initial_page)

            if initial_page > page_maximum:
                logger.error(
                    'Initial page number >= page_maximum. That\'s impossible.')
                return recorder

            for current_page in range(initial_page, page_maximum + 1):

                # check the running state
                if self._running == False:
                    logger.warning(
                        'Swan received `stop` command on the first layer.')
                    # flush the data first, and return `recorder` for convenient
                    recorder.record()
                    return recorder

                if self.progress_tracker:
                    self.progress_tracker.current_page = current_page
                logger.info("Task `qnw` current page %d" % current_page)

                # # retrieve comment list (wrapper)
                # root = tab.ele('@tag()=body')
                # review_list = root.s_eles('css:#comment_box > li')
                # logger.info('Comment list length: %d' % len(review_list))
                headers = {
                    "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                }

                request_uri = 'https://travel.qunar.com/place/api/html/comments/poi/715281?poiList=true&sortField=0&rank=0&pageSize=10&page=%d' % current_page

                response = requests.get(request_uri, headers=headers)
                json_data = response.json()

                navigation_retry_count = 0
                while json_data['success'] == False and json_data[
                        'data'] == None and navigation_retry_count <= 5:
                    if navigation_retry_count <= 3:
                        sleep_time = randint(8, 15)
                    else:
                        sleep_time = randint(15, 30)
                    time.sleep(sleep_time)
                    logger.info('Sleep %s sec, and retry.' % sleep_time)
                    response = requests.get(request_uri, headers=headers)
                    json_data = response.json()
                    logger.warning('Retrying to navigate to: %s (%s)' %
                                   (request_uri, navigation_retry_count))
                    navigation_retry_count += 1
                if json_data[
                        'success'] == False and navigation_retry_count <= 5:
                    logger.error('Failed to navigate to url: %s' % request_uri)
                    return recorder
                else:
                    logger.debug('Successful get json data, size: %d' %
                                 sys.getsizeof(json_data))
                    logger.debug('Json data: %s' % json_data)
                soup = BeautifulSoup(json_data['data'], 'lxml')
                logger.info('Loading json data to BeautifulSoup4...')
                review_list = soup.select('#comment_box > li')
                # parse the content
                for index, review_item in enumerate(review_list):
                    # check the running state for the second time
                    if self._running == False:
                        logger.error(
                            'Swan received `stop` command on the second layer.'
                        )
                        # flush the data first, and return `recorder` for convenient
                        recorder.record()
                        return recorder
                    raw_content = ''
                    raw_date = review_item.select(
                        '.e_comment_add_info > ul > li:first-child'
                    )[0].get_text(separator='|').split('|')[0]
                    raw_score = review_item.select(
                        '.e_comment_star_box > .total_star > span')[0].get(
                            'class')[1]
                    if len(review_item.select(
                            '.e_comment_content .seeMore')) == 0:
                        logger.warning('No expanded content was detected.')
                        raw_content = ''.join(
                            review_item.select('.e_comment_content')
                            [0].getText(strip=True))
                    else:
                        # if the review has expanded content, we need to parse it
                        deep_link = review_item.select(
                            '.e_comment_content .seeMore')[0].get('href')
                        logger.info('Deep link: %s' % deep_link)
                        deep_link_tab = Chromium(
                            self.chromium_options).new_tab(deep_link)

                        retry_count = 0
                        while not deep_link_tab.ele(
                                'css:.comment_content') and retry_count <= 5:
                            sleep_time = randint(3, 8)
                            logger.warning(
                                'No deep content was found, sleep %d sec and retry.'
                                % sleep_time)
                            # sleep
                            deep_link_tab.wait(sleep_time)
                            retry_count += 1
                            logger.warning('Now, retrying...(%d)' %
                                           retry_count)
                            deep_link_tab.refresh()
                            deep_link_tab.wait(1)

                        if not deep_link_tab.ele('css:.comment_content'):
                            logger.warning(
                                'No deep content was found, leave it nothing, skip it'
                            )
                        else:
                            # chances are that some page trending to have more than one `comment_content` element
                            deep_contents = deep_link_tab.eles(
                                'css:.comment_content')
                            temp = []
                            for content in deep_contents:
                                # logger.info(content.texts())
                                temp.append(''.join(content.texts()))

                            # concatenate strings
                            raw_content = concatenate_with_conditions(temp)

                            logger.debug('Get content from the deep link: %s' %
                                         raw_content)

                        deep_link_tab.scroll.to_half()
                        deep_link_tab.scroll.up(randint(30, 150))
                        deep_link_tab.scroll.down(randint(10, 60))
                        deep_link_tab.wait(3, 5)
                        deep_link_tab.close()
                        Chromium(self.chromium_options).activate_tab(tab)

                    # preparing data
                    review_score = star_string_to_int(raw_score)
                    review_content = [raw_content]
                    review_content.append(raw_date)
                    review_content.append(review_score)
                    review_content.append(current_page)
                    review_content.append(index)
                    # logger.info(review_content)

                    recorder.set.delimiter('|')
                    recorder.set.encoding('utf-8')
                    # set header and backup
                    recorder.set.head(
                        ['Comment', 'Comment Date', 'Score', 'Page', 'Index'])
                    recorder.set.auto_backup(60)
                    recorder.add_data(review_content)

                # sleep for 3 ~ 10 secs
                sleep_time = self.calculate_sleep_time(start_time)
                if sleep_time in [400, 900]:
                    start_time = time.time()

                logger.info(
                    "Sleep %s seconds before the next move. Take your time master >_="
                    % sleep_time)
                # tab.wait(sleep_time)
                time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"Error in task_qnw: {e}")
            traceback.print_exc(e)
        finally:
            # 确保资源被清理
            logger.debug('Swan state in Finally Statement: %s' % self._running)
            if not self._running:
                logger.debug('Finally statement revoke grace shutdown!')
                self.grace_shutdown(recorder)
                return recorder

        return None

    def task_red(self) -> Recorder:
        # change running state
        self._running = True
        # store the data as CSV file
        data_file_path = Path.joinpath(
            Path(self.settings.value('data_directory', './data')),
            'red.csv')
        recorder = Recorder(path=data_file_path, cache_size=75)
        logger.debug('Swan (in) _running state: %s' % self._running)

        try:
            # launch a new tab
            tab = Chromium(self.chromium_options).latest_tab

            # push the tab into list
            self.chromium_tabs.append(tab)

            # set location and map it to corresponding links
            self.set_location(self.location)
            location = self._map_location_to_red(self.location)

            # logger.info(location.name)
            # logger.info(location.value)

            # navigate to shuhe/baisha town
            tab.get(location.value)
            
            # RED require login before any operations
            
        except Exception as e:
            logger.error(f"Error in task_qnw: {e}")
            traceback.print_exc(e)
        finally:
            # 确保资源被清理
            logger.debug('Swan state in Finally Statement: %s' % self._running)
            if not self._running:
                logger.debug('Finally statement revoke grace shutdown!')
                self.grace_shutdown(recorder)
                return recorder
        return None

    def run_task(self) -> Recorder:
        match self.platform:
            case Platform.DAZHONGDIANPING:
                return self.task_dzdp()
            case Platform.XIECHENG:
                return self.task_xiecheng()
            case Platform.RED:
                return self.task_red()
            case Platform.QUNAERWANG:
                return self.task_qnw()


def comment_swan_main():

    swan = Swan('./swan.config.toml').launch()
    try:
        swan.task_dzdp()
    except KeyboardInterrupt:
        swan.grace_shutdown()
        sys.exit(0)


if __name__ == '__main__':
    comment_swan_main()
