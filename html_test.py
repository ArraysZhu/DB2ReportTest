#! /usr/bin/python
# -*-coding:utf-8 -*-

from html_parser import HtmlParser
from db_func import DBConnect

file_path = r'C:\Analyzer\Case\RepoterDefaultOutput\Case_20190321095409_20190321_134109\IPHONE_5C__Apple_iPhone 5C_20170905201748871(+86 156-5164-0362).20190321134130-html'
htmlp = HtmlParser(file_path)
htmlp.catalog_parser()
# db_obj = DBConnect('temp_data.db')
# def get_html_content():
#     html_file_sql = 'select distinct(url) from tree_node;'
#     url_list = [x[0] for x in db_obj.execute_sqls(html_file_sql)]
#     html_content_dict = {}
#     for url in url_list:
#         if url == u'content0.html':
#             html_content_dict[url] = htmlp.case_report_parser(url)
#         else:
#             html_content_dict[url] = htmlp.common_html_parser(url)
#             try:
#                 assert isinstance(html_content_dict[url], dict)
#             except AssertionError:
#                 print u'标题数据显示的条数与实际条数不同'

