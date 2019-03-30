#! /usr/bin/python
# -*-coding:utf-8 -*-

import json
from html_parser import HtmlParser
from db_func import DBConnect


with open(r'E:\2019\db2report_test\dictionary.txt', 'r') as f:
    GLOBAL_CONF = json.load(f)
APP_TYPE_LIST = [x for x in  GLOBAL_CONF.keys() if x.endswith('_app')]

def create_uni_conf_en(key_name):
    return {y['db']:y['display_enus'] for x,y in GLOBAL_CONF[key_name].items()}


def create_uni_conf_ch(key_name):
    return {y['db']:x for x,y in GLOBAL_CONF[key_name].items()}


def assert_in(a, b):
    if isinstance(a, tuple):
        flag = False
        for data in a:
            result = data in b
            flag = flag or result
        try:
            assert flag
        except AssertionError:
            print a
            print b
    else:
        try:
            assert a in b
        except AssertionError:
            print a
            print b


def assert_equal(a, b):
    try:
        assert a == b
    except AssertionError:
        print a
        print b

file_path = r'C:\Analyzer\Case\RepoterDefaultOutput\Case_20190321095409_20190326_091734\IPHONE_5C__Apple_iPhone 5C_20170905201748871(+86 156-5164-0362).20190326091750-html'
htmlp = HtmlParser(file_path)
htmlp.catalog_parser()
temp_db_obj = DBConnect('temp_data.db')
result_db_obj = DBConnect(r'C:\Analyzer\Case\AnCaseBank\Case_20190321095409\DB\Evid2.db')
delete_status_conf = create_uni_conf_en('delete_status')
store_source_conf = create_uni_conf_ch('store_source')
encrypt_status_conf = create_uni_conf_ch('encrypt_status')


# 单页报告通用逻辑
def uni_logic_single_page(url_sql, result_sql, assert_func):
    data_url = temp_db_obj.execute_sqls(url_sql)[0][0]
    data_dict = htmlp.common_html_parser(data_url)
    act_data_list = data_dict['datas']
    sum_num_data = data_dict['total_num']
    del_num_data = data_dict['del_num']
    results_list = result_db_obj.execute_sqls(result_sql)
    sum_num_result = len(results_list)
    # 判断数据总量是否一致
    assert_equal(sum_num_result, sum_num_data)
    del_num_result = 0
    for i, result in enumerate(results_list):
        # 删除状态判断
        delete_status = result[1]
        delete_status_result = delete_status_conf[delete_status].lower()
        delete_status_data = act_data_list[i][1].lower()
        assert_in(delete_status_result, delete_status_data)
        if delete_status == u'1':
            del_num_result += 1
        assert_func(i, act_data_list, result)
    # 判断数据删除量是否一致
    assert_equal(del_num_result, del_num_data)