# -*-coding:utf-8 -*-

import webbrowser
from html_maker import HTMLMaker
from search import BilibiliSearch
from datas import dict_data, newest_data, last_update, cookie_value
from keywords import keywords_list

bili = BilibiliSearch(dict_data, newest_data, last_update, cookie_value)
bili.update_all()

hm = HTMLMaker(cookie_value)
hm.make_html(newest_data, keywords_list)

webbrowser.open('bilibili.html', new = 0, autoraise = 0)
# 修改关键词的交互