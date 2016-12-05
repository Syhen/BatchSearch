# -*-coding:utf-8 -*-

from search import BilibiliSearch
from datas import newest_data, cookie_value
from keywords import keywords_list
import hashlib
# from lxml import etree
from bs4 import BeautifulSoup
import re
import urllib2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class HTMLMaker():
    '''
    '''
    def __init__(self, cookie_value):
        self.searcher = BilibiliSearch({}, {}, {}, cookie_value)
        self.html = None
        self.cookie_value = cookie_value

    def make_html(self, dict_links, keyword_list):
        num = 0
        for key in dict_links:
            num += len(dict_links[key])
        html = self.search_all(dict_links, keyword_list)
        with open('bilibili.html', 'r') as f:
            doc = f.read()
            tag = r'<ul class="ajax-render" style="width:1100px;">'
            start_find = doc.find(tag)
            end_ul = doc.find(r'</ul>', start_find)
            doc = doc[: start_find + len(tag)] + r'%s' + doc[end_ul:]
            reg = re.compile(r'共有 \d{1,} 条更新')
            doc = reg.sub('共有 %s 条更新'%num, doc)
        with open('bilibili.html', 'w') as f:
            doc = doc%html
            f.write(doc)

    def search_detail(self, keyword, links):
        url = 'http://search.bilibili.com/all?keyword={0}'.format(urllib2.quote(str(keyword)))
        headers = {
            'Cookie': 'buvid3=%s'%self.cookie_value
        }
        doc, cookie = self.searcher.download(url, headers)
        soup = BeautifulSoup(doc, 'lxml').find_all('li', {'class': 'video matrix '})
        list_data = []
        for s in soup:
            href = s.find('a')['href']
            if href.split('/')[-1] in links:
                list_data.append(str(s))
        return list_data

    def search_all(self, dict_links, keyword_list):
        html = []
        for keyword in keyword_list:
            keyword_hash = self.searcher.str2md5(keyword)
            links = dict_links[keyword_hash]
            html.append(u'\n'.join(self.search_detail(keyword, links)))
        html = u'\n'.join(html)
        return html


if __name__ == '__main__':
    hm = HTMLMaker(cookie_value)
    hm.make_html(newest_data, keywords_list)