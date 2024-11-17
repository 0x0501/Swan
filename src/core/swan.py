import os
import sys
from DataRecorder import Recorder
from DrissionPage import Chromium
from DrissionPage import ChromiumOptions
from loguru import logger
from DrissionPage.errors import *
from pathlib import Path
from src.core.location import Location
from src.utils.config import Config
from src.utils.text import extract_and_convert_score, extract_update_date, sanitize_text


class Swan():

    config_file_path = ''
    data_directory = ''
    __config: Config = None
    config = None
    location: Location = None
    chromium_tabs: list = []
    chromium_options = ChromiumOptions
    recorder: Recorder = None

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
        # flush the cache
        self.recorder.record()
        if len(self.chromium_tabs) == 0:
            logger.warning('No tab was opened, shut down Swan right now.')
            return
        for i in self.chromium_tabs:
            # close all the tabs
            i.stop_loading()
            i.close()
        logger.warning('Grace shutdown Swan, closing all the tabs.')

    def task_dzdp_login(self, tab):
        tab.get(
            'https://account.dianping.com/pclogin?redir=https://m.dianping.com/dphome',
            True)
        tab.ele('@@class=bottom-password-login@@tag()=span').click()
        tab.ele('@@class=pwd@@tag()=div').click()
        logger.info(
            "Switch to manual login, trying to input username and password.")
        # filling info
        phone_number = tab.ele('@id=mobile-number-textbox').input(
            self.config['account']['dzdp']['username'])
        password = tab.ele('@id=password-textbox').input(
            self.config['account']['dzdp']['password'])
        user_agreement = tab.ele('@class=pc-agreement').ele(
            '@id=pc-check').check()
        login_button = tab.ele('@class=login-box').ele(
            '@class=button-pc').click()
        
        # check whether CAPTCHA was displayed
        
        pass
    
    def task_dzdp(self, loc: Location = Location.SHUHE_TOWN):
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
            self.task_dzdp_login()
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
        self.set_location(loc)

        tab.get(self.location.value[0])
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
                    'Successfully Navigated to %s. Preparing data collector.' %
                    self.location.name)
        except ElementNotFoundError as e:
            # if the ip has been banned, clear all the cookies, and re-login
            logger.warning(
                'Oops, our ip address might have been banned, let\'s try to re-login in. :('
            )
            logger.info('Clear all the cookies and cache.')
            tab.cookies().clear()  # clear all the cookies
            tab.clear_cache()  # clear all the cache
            self.task_dzdp_login(tab)

        ############################## Data collector #######################################

        # change browser mode to `s` (session mode)
        tab.change_mode()
        # tab.close()
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
                for index, review_item in enumerate(review_list):
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
                        review_item.ele('@@tag()=div@@class=main-review').ele(
                            'css:div.misc-info > span.time').texts()[0], False)

                    if "更新于" in review_date:
                        review_date = extract_update_date(review_date)
                        logger.debug(
                            'Got updated date, trying to extract it. The result: %s'
                            % review_date)

                    # review score
                    review_score = extract_and_convert_score(
                        review_item.ele('@@tag()=div@@class=main-review').ele(
                            'css:div.review-rank > span').attr('class'))
                    # joint them together
                    review_content.append(review_date)
                    review_content.append(review_score)
                    review_content.append(current_page)
                    review_content.append(index)  # index started from 0
                    logger.info(review_content)
                    # TODO! write comment data to file

                    # store the data as CSV file
                    data_file_path = Path.joinpath(
                        Path(self.config['application']['data_directory']),
                        'dazhongdianping.csv')

                    recorder = Recorder(path=data_file_path, cache_size=75)
                    recorder.set.delimiter('|')
                    recorder.set.encoding('utf-8')
                    # set header and backup
                    recorder.set.head(
                        ['Comment', 'Comment Date', 'Score', 'Page', 'Index'])
                    recorder.set.auto_backup(60)
                    recorder.add_data(review_content)

                # sleep for 3 ~ 10 secs
                tab.wait(5, 10)

            except ElementNotFoundError:
                logger.error(
                    'Cannot find review elements, by: css:div[class=reviews-items] > ul > li'
                )
                # flush the cache
                self.recorder.record()
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
