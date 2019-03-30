#! /usr/bin/python
# -*-coding:utf-8 -*-

from bs4 import BeautifulSoup as bs
import os
import re
import time
import copy
from db_func import DBConnect

class HtmlParser(object):
    def __init__(self, files_path):
        self.html_path = files_path
        self.node_temp = dict(id = '', name='', url='', childrens=[])
        self.leaf_node_temp = dict(id = '', name='', url='')
        self.node_list = []
        self.dbc_obj = DBConnect('temp_data.db')
        self.create_node_table()
        self.insert_sqls = []

    def create_node_table(self):
        table_is_exists_sql = '''
        select * from sqlite_master where type = 'table' and name = '{0}'
        '''.format('tree_node')
        drop_table_sql = '''
        drop table {0}
        '''.format('tree_node')
        if self.dbc_obj.execute_sqls(table_is_exists_sql):
            self.dbc_obj.execute_sqls(drop_table_sql)
        create_sql = '''
        create table if not exists {0}
        (id int, pId int, name varchar(255), url varchar(255), sum_num int, del_num int)
        '''.format('tree_node')
        self.dbc_obj.execute_sqls(create_sql)

    def insert_node(self, node_id, pid, name, url):
        pattern = re.compile(r'(.*)\[(\d+)/(\d+)\]$')
        flag = pattern.search(name)
        if flag:
            name = flag.group(1).strip()
            sum_num = flag.group(2)
            del_num = flag.group(3)
        else:
            sum_num = None
            del_num = None
        insert_sql = '''
        insert into {0} (id, pId, name, url, sum_num, del_num) values ('{1}', '{2}', '{3}', '{4}', '{5}', '{6}')
        '''.format('tree_node', node_id, pid, name, url, sum_num, del_num)
        self.insert_sqls.append(insert_sql)

    def catalog_parser(self):
        with open(os.path.join(self.html_path, 'Report', 'catalog.html')) as f:
            data_list = f.readlines()
            pattern = re.compile(r'{.*}')
            dict_temp = dict(id='', pId='', name='', url='')
            for data in data_list:
                if pattern.match(data):
                    dict_act = copy.deepcopy(dict_temp)
                    dict_act['id'] = re.findall(r"id:'*(.*?)'*,", data)[0]
                    dict_act['pId'] = re.findall(r"pId:'*(.*?)'*,", data)[0]
                    dict_act['name'] = re.findall(r"name:'*(.*?)'*,", data)[0]
                    dict_act['url'] = re.findall(r"url:'*(.*?)'*,", data)[0]
                    self.node_list.append(dict_act)
                    self.insert_node(dict_act['id'], dict_act['pId'], dict_act['name'], dict_act['url'])
            self.dbc_obj.execute_sqls(self.insert_sqls)

    def case_report_parser(self, html_name):
        with open(os.path.join(self.html_path, 'Report', html_name), 'r') as f:
            html_data = f.read()
        dict_list = []
        soup = bs(html_data, 'html.parser')
        tr_tag_list_dou = [tag.select('tr') for tag in soup.select('div#content > table > tbody')]
        for tr_tag_list in tr_tag_list_dou:
            dict_temp = {}
            for tr_tag in tr_tag_list:
                td_tag_list = tr_tag.select('td')
                dict_temp[td_tag_list[0].get_text().strip()] = td_tag_list[1].get_text().strip()
            dict_list.append(copy.deepcopy(dict_temp))
        return dict_list

    def common_html_parser(self, html_name):
        with open(os.path.join(self.html_path, 'Report', html_name), 'r') as f:
            html_data = f.read()
        soup = bs(html_data, 'lxml')
        info_dict = dict(name='', total_num=0, del_num=0, datas=[])
        span_tag_texts = [x.get_text().strip(' |(|)') for x in soup.select('span.s14')]
        info_dict['name'] = span_tag_texts[0]
        info_dict['total_num'] = int(span_tag_texts[1])
        # thead_th_texts = [x.get_text().strip() for x in soup.select('div#content > table > thead th')]
        tbody_tr_tags = soup.select('div#content > table > tbody tr')
        for tr_tag in tbody_tr_tags:
            td_tag_texts = []
            for tag in tr_tag.select('td'):
                if tag.select('img'):
                    img_src = tag.select('img')[0].attrs['src']
                    td_tag_texts.append(img_src)
                    if 'deleted.png' in img_src:
                        info_dict['del_num'] += 1
                else:
                    td_tag_texts.append(tag.get_text().replace(u'\xa0', u' ').strip())
            # info_dict['datas'].append(dict(zip(thead_th_texts, td_tag_texts)))
            info_dict['datas'].append(td_tag_texts)
        # try:
        #     assert len(info_dict['datas']) == info_dict['total_num'],  u'标题数据显示的条数与实际条数不同'
        # except AssertionError:
        #     return []
        return info_dict


if __name__ == '__main__':
    file_path = r'E:\testdata\Xiaomi_Redmi 4A_20190130140611401.20190314094738-html'
    htmlp = HtmlParser(file_path)
    htmlp.catalog_parser()