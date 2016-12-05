# -*-coding:utf-8 -*-

import urllib2
import cookielib
from keywords import keywords_list
from datas import dict_data, newest_data, last_update, cookie_value
from lxml import etree
import hashlib
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class BilibiliSearch():
    '''
    批量搜索
    获取这些关键字的视频是否已经更新
    仅仅从http://www.bilibili.com获取数据，并用于个人使用（偷懒）
    '''
    def __init__(self, dict_data, newest_data, last_update, cookie_value, pages = 1):
        self.pages = pages
        today = time.strftime('%Y-%m-%d')
        self.today_hash = self.str2md5(today)
        self.dict_data = dict_data
        self.newest_data = newest_data
        self.last_update = last_update
        self.cookie_value = cookie_value

    def download(self, url, headers = {}):
        '''
        下载页面
        '''
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), urllib2.HTTPHandler)
        req = urllib2.Request(
            url = url,
            headers = headers
        )
        # response = urllib2.urlopen(url)
        response = opener.open(req)
        doc = response.read()
        response.close()
        # with open('bilibili.html', 'w') as f:
        #     f.write(doc)
        return doc, cookie

    def update_cookie(self):
        '''
        更新cookie的值，保证每次获取的页面都是按照综合排序的结果
        '''
        now_stamp = int(time.time() * 1000)
        url = 'http://data.bilibili.com/v/web/web_page_view?mid=&fts={0}&url=http%253A%252F%252Fsearch.bilibili.com%252Fall%253Fkeyword%253D%2525E9%252580%252597%2525E9%2525B1%2525BC%2525E6%252597%2525B6%2525E5%252588%2525BB&proid=1&ptype=1&module=search&title=%E9%80%97%E9%B1%BC%E6%97%B6%E5%88%BB_-_%E6%90%9C%E7%B4%A2%E7%BB%93%E6%9E%9C_-_%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E5%BC%B9%E5%B9%95%E8%A7%86%E9%A2%91%E7%BD%91_-_(_%E3%82%9C-_%E3%82%9C)%E3%81%A4%E3%83%AD_%E4%B9%BE%E6%9D%AF~_-_bilibili&ajaxtag=&ajaxid=&page_ref=&_={1}'.format(now_stamp / 1000, now_stamp)
        doc, cookie = self.download(url)
        for cook in cookie:
            if cook.name == 'buvid3':
                self.cookie_value = cook.value
                break

    def str2md5(self, string):
        '''
        数据的md5
        '''
        md5 = hashlib.md5()
        md5.update(string)
        return md5.hexdigest()

    @property
    def keywords(self):
        return keywords_list

    def keywords_setter(self, list_data):
        pass

    def update(self, keyword, links):
        '''
        判断是否有数据更新
        '''
        keyword_hash = self.str2md5(keyword)
        try:
            history_links = self.dict_data[keyword_hash]
        except KeyError:
            history_links = set()
        try:
            newest_links = self.newest_data[keyword_hash]
        except KeyError:
            newest_links = set()
        update_links = set(links) - (set(links) & history_links)
        if update_links:
            for link in update_links:
                newest_links.add(link)
            self.newest_data[keyword_hash] = newest_links

    def parse(self, keyword):
        '''
        获取本次查询的链接
        '''
        url = 'http://search.bilibili.com/all?keyword={0}'.format(urllib2.quote(str(keyword)))
        headers = {
            'Cookie': 'buvid3=%s'%self.cookie_value
        }
        doc, cookie = self.download(url, headers)
        sel = etree.HTML(doc)
        data = sel.xpath('//*[@class="ajax-render"]/li')
        links = [i.xpath('./a[1]/@href')[0].split('/')[-1] for i in data]
        return links

    def update_all(self):
        '''
        更新所有关键字的搜索结果，并保存
        '''
        if self.today_hash != self.last_update:# 如果隔天开始更新，则初始化所有数据为未更新
            self.update_cookie()
            for key in self.dict_data:
                self.newest_data[key] = set()
        link_dict = {}
        for keyword in self.keywords:
            links = self.parse(keyword)
            link_dict[self.str2md5(keyword)] = links
            self.update(keyword, links)
        self.dict_data = link_dict
        update_dict_str = self.links2str(self.newest_data)
        link_dict_str = self.links2str(self.dict_data)
        self.set_data([link_dict_str, update_dict_str, self.cookie_value])

    def links2str(self, link_dict):
        '''
        将搜索结果保存为字符串的形式
        '''
        return ',\n'.join(['    \'' + key + '\': ' + str(set(link_dict[key])) for key in link_dict])

    def set_data(self, list_value):
        '''
        将字符串以变量的形式保存到内容文件中
        '''
        lines = [
            r"# -*-coding:utf-8 -*-", r"", r"# 点击时更新", r"dict_data = {", list_value[0],
            r"}", r"", r"# 隔天点击更新", r"newest_data = {", list_value[1],
            r"}", r"", r"last_update = '%s'", r"", r"cookie_value = '%s'"
        ]
        doc = "\n".join(lines)
        with open('datas.py', 'w') as f:
            doc = doc%(self.today_hash, list_value[2])
            f.write(doc)


if __name__ == '__main__':
    bili = BilibiliSearch(dict_data, newest_data, last_update, cookie_value)
    bili.update_all()