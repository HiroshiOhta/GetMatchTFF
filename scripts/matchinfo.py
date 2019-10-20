#!/usr/bin/env python

# 標準ライブラリ
import os
from sys import exit, argv
from datetime import datetime
from datetime import timedelta

# サードパーティライブラリ
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.support.ui import Select


def get_matchinformation(query_conv_no: str):
    """
    [summary]

    Parameters
    ----------
    query_conv_no : str
        [description]
    """

    options = FirefoxOptions()
    # ヘッドレスモードを有効にする
    options.add_argument('-headless')
    # FirefoxのWebDriverオブジェクトを作成する。
    driver = Firefox(options=options, service_log_path=os.devnull)

    rakuza_url = 'https://www.pitin.com/rakuza/pc/common/conv/ConvResult.cfm'
    query_vid = '00065'
    query_tpl = '11'
    # query_conv_no = '13873'
    # query_conv_no = '13852'

    target_utl = rakuza_url + '?vid=' + query_vid + \
        '&OutMode=0&tpl=' + query_tpl + '&CONV_NO=' + query_conv_no

    driver.get(target_utl)

    select_xpath = '//*[@id="f5_comment"]/table/tbody/tr[1]/td/select'
    match_days = driver.find_element_by_xpath(select_xpath)
    match_days_select = Select(match_days)
    match_days_count = len(match_days_select.options)

    for match_day in range(1, match_days_count):

        match_days = driver.find_element_by_xpath(select_xpath)
        match_days_select = Select(match_days)
        match_days_select.select_by_value(str(match_day))

        input_xpath = '//*[@id="f5_comment"]/table/tbody/tr[1]/td/input[1]'
        driver.find_element_by_xpath(input_xpath).click()

        # 試合のリーグ名、開催節、開催日を取得する。
        # ------------------------------------------------------------------------------
        m_info = []
        target_xpath = '//*[@id="f5_info"]/table/tbody/tr[1]/td'
        m_info.append(driver.find_element_by_xpath(target_xpath).text)

        target_xpath = '//*[@id="f5_comment"]/table/tbody'
        match_table = driver.find_element_by_xpath(target_xpath)

        # テーブルの行数を取得
        table_rows = len(match_table.find_elements_by_xpath('.//tr'))
        for table_row in range(2, table_rows):
            target_xpath = 'tr[' + str(table_row) + ']/td[2]'
            m_info.append(match_table.find_element_by_xpath(target_xpath).text)

        # 各節の試合情報を取得する。
        # ------------------------------------------------------------------------------
        m_data = []
        target_xpath = '//*[@id="gameResult"]/table/tbody'
        match_table = driver.find_element_by_xpath(target_xpath)

        # テーブルの行数を取得
        table_rows = len(match_table.find_elements_by_xpath('.//tr')) + 1

        for table_row in range(2, table_rows):
            m_data_tmp = []

            # 試合会場、開始時間、ホーム、アウェイのデータを取得する
            for table_colmun in [1, 3, 4, 8]:
                target_xpath = 'tr[' + str(table_row) + \
                    ']/td[' + str(table_colmun) + ']'
                m_data_tmp.append(
                    match_table.find_element_by_xpath(target_xpath).text)

            m_data.append(m_data_tmp)

        # 試合情報を出力する
        # ------------------------------------------------------------------------------
        print("\n--------------------------------------------------")
        league_name = m_info[0].split(' ', 2)
        print(f"{league_name[2]}: {m_info[1]}")

        time_last = datetime.strptime(
            m_info[2] + ' ' + m_data[len(m_data)-1][1], '%Y/%m/%d %H:%M')

        end_time = time_last + timedelta(hours=1)

        print(f"日時: {m_info[2]} {m_data[0][1]} - {end_time.strftime('%H:%M')}")

        # チーム名の最大サイズを取得する
        tmlen = 0
        for cnt in range(0, len(m_data)):

            if tmlen < len(m_data[cnt][2]):
                tmlen = len(m_data[cnt][2])

        print("\n[詳細]")
        for i in range(0, len(m_data)):

            print(
                f"{m_data[i][1]}  {m_data[i][2]: >{tmlen}} - {m_data[i][3]}")

    driver.quit()


if __name__ == "__main__":

    get_matchinformation(argv[1])

    exit(0)
