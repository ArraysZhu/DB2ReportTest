#! /usr/bin/python
# -*-coding:utf-8 -*-

import time
import sys
import collections

from uni_func import *
from html_parser import HtmlParser
from db_func import DBConnect

reload(sys)
sys.setdefaultencoding('utf8')

file_path = r'C:\Analyzer\Case\RepoterDefaultOutput\Case_20190321095409_20190326_091734\IPHONE_5C__Apple_iPhone 5C_20170905201748871(+86 156-5164-0362).20190326091750-html'
htmlp = HtmlParser(file_path)
htmlp.catalog_parser()
temp_db_obj = DBConnect('temp_data.db')
result_db_obj = DBConnect(r'C:\Analyzer\Case\AnCaseBank\Case_20190321095409\DB\Evid2.db')
sex_conf = create_uni_conf_ch('sex_type')

def assert_func_add(desc_list, result, result_dis_dict):
    result_dis_list = []
    for act_data_index, counts in result_dis_dict.items():
        result_dis_list.extend([act_data_index]*counts)
    for i, field_data in enumerate(result[2:]):
        if field_data:
            assert_in(desc_list[i]+unicode(field_data), result_dis_list[i])


def account_info_deal():
    get_data_url_sql = '''
    SELECT
        URL 
    FROM
        tree_node 
    WHERE
        name = '登陆账号列表' 
        AND pID = ( SELECT id FROM tree_node WHERE name = '{0}' AND pId = {1} );
    '''.format('微信', 96)
    get_results_sql = '''
    SELECT
        recordid,
        DELETE_STATUS,
        ACCOUNT,
        REGIS_NICKNAME,
        PERSONAL_DESC,
        SIGN_NAME,
        NAME,
        PASSWORD,
        AREA,
        CITY_CODE,
        SEXCODE,
        AGE,
        GRADUATESCHOOL,
        BIRTHDAY,
        CURRENT_CITY,
        REG_CITY,
        REL_APP_TYPE,
        REL_TYPE,
        EMAIL_ACCOUNT,
        MSISDN 
    FROM
        Account_tab 
    WHERE
        APPCLASS_TYPE = '{}' 
        AND APP_TYPE = '{}';
    '''.format('IM', '1030036')

    app_type_conf = {}
    for app_type in APP_TYPE_LIST:
        app_type_conf.update(create_uni_conf_ch(app_type))
    account_associate_conf = create_uni_conf_ch('account_associate')
    def assert_func(result_index, act_data_list, result):
        account_info_data_2 = act_data_list[result_index][2]
        account_info_data_3 = act_data_list[result_index][3]
        account_info_data_4 = act_data_list[result_index][4]
        result_dis_dict = collections.OrderedDict()
        result_dis_dict[account_info_data_2] = 6
        result_dis_dict[account_info_data_3] = 10
        result_dis_dict[account_info_data_4] = 2
        desc_list = [u'账号:', u'昵称:', u'个人说明:', u'个性签名:', u'真实名字:',
                     u'密码:', u'国家代码:', u'行政区划:', u'性别:', u'年龄:',
                     u'毕业学校:', u'出生年月:', u'当前所在城市:', u'注册城市:',
                     u'关联账号类型:', u'账号关联类型:', u'邮箱:', u'移动电话:']
        if result[10]:
            result = list(result)
            result[10] = sex_conf[result[10]]
            result = tuple(result)
        if result[16]:
            result = list(result)
            result[16] = app_type_conf[result[16]]
            result = tuple(result)
        if result[17]:
            result = list(result)
            result[17] = account_associate_conf[result[17]]
            result = tuple(result)
        assert_func_add(desc_list, result, result_dis_dict)
    uni_logic_single_page(get_data_url_sql, get_results_sql, assert_func)


def friend_info_deal():
    get_data_url_sql = '''
    SELECT
        URL 
    FROM
        tree_node 
    WHERE
        name = '{}' 
        AND pId = (
        SELECT
            id 
        FROM
            tree_node 
        WHERE
            name = '好友信息' 
            AND pId = (
            SELECT
                id 
            FROM
                tree_node 
            WHERE
            name = '{}' 
        AND pId = ( SELECT id FROM tree_node WHERE name = '{}' AND pId = 96 )));
    '''.format('新的朋友', 'xhunter0362', '易信')
    get_results_sql = '''
    SELECT
        recordid,
        DELETE_STATUS,
        FRIEND_ACCOUNT,
        FRIEND_NICKNAME,
        FRIEND_GROUP,
        NAME,
        FRIEND_REMARK,
        SIGN_NAME,
        PERSONAL_DESC,
        AREA,
        CITY_CODE,
        SEXCODE,
        AGE,
        OCCUPATION_NAME,
        REG_CITY,
        BIRTHDAY,
        MSISDN,
        EMAIL_ACCOUNT 
    FROM
        Friends_tab 
    WHERE
        APPCLASS_TYPE = 'IM' 
        AND APP_TYPE = '{}' 
        AND ACCOUNT = '{}' 
        AND FRIEND_TYPE = '{}'
    ORDER BY
        DELETE_STATUS;
        '''.format('1030047', 'xhunter0362', '12')

    def assert_func(result_index, act_data_list, result):
        friend_info_data_2 = act_data_list[result_index][2]
        friend_info_data_3 = act_data_list[result_index][3]
        friend_info_data_4 = act_data_list[result_index][4]
        result_dis_dict = collections.OrderedDict()
        result_dis_dict[friend_info_data_2] = 5
        result_dis_dict[friend_info_data_3] = 9
        result_dis_dict[friend_info_data_4] = 2
        desc_list = [u'好友账号:', u'好友昵称:', u'好友分组:', u'真实姓名:', u'好友备注:',
                     u'个性签名:', u'个人说明:', u'国家代码:', u'行政区划:', u'性别:',
                     u'年龄:', u'职业:', u'注册城市:', u'出生年月:',
                     u'移动电话:', u'邮箱:']
        if result[11]:
            result = list(result)
            result[11] = sex_conf[result[11]]
            result = tuple(result)
        assert_func_add(desc_list, result, result_dis_dict)
    uni_logic_single_page(get_data_url_sql, get_results_sql, assert_func)


def group_info_deal():
    get_url_sql = '''
    SELECT
        URL 
    FROM
        tree_node 
    WHERE
        name = '{}' 
        AND pId = (
        SELECT
            id 
        FROM
            tree_node 
        WHERE
        name = '{}' 
        AND pId = ( SELECT id FROM tree_node WHERE name = '{}' AND pId = 96 ));
    '''.format('讨论组列表', '2994584647', 'QQ')
    get_results_sql = '''
    SELECT
        recordid,
        DELETE_STATUS,
        GROUP_NAME,
        GROUP_NUM,
        GROUP_MEMBER_COUNT,
        GROUP_MAX_MEMBER_COUT,
        FRIEND_ACCOUNT,
        GROUP_OWNER_NICKNAME,
        GROUP_NOTICE,
        GROUP_DESCRIPTION 
    FROM
        GroupInfo_tab 
    WHERE
        APPCLASS_TYPE = 'IM' 
        AND APP_TYPE = '{}' 
        AND ACCOUNT = '{}' 
        AND SESSION_TYPE = '{}' 
    ORDER BY
        DELETE_STATUS;
    '''.format('1030001', '2994584647', '68')

    def assert_func(result_index, act_data_list, result):
        group_info_data_2 = act_data_list[result_index][2]
        group_info_data_3 = act_data_list[result_index][3]
        group_info_data_4 = act_data_list[result_index][4]
        group_info_data_5 = act_data_list[result_index][5]
        result_dis_dict = collections.OrderedDict()
        result_dis_dict[group_info_data_2] = 4
        result_dis_dict[group_info_data_3] = 2
        result_dis_dict[group_info_data_4] = 1
        result_dis_dict[group_info_data_5] = 1
        desc_list = [u'群名称:', u'群号:', u'成员数:', u'最大成员数:', u'群主帐号:', u'群主昵称:', u'', u'']
        assert_func_add(desc_list, result, result_dis_dict)
    uni_logic_single_page(get_url_sql, get_results_sql, assert_func)


def dynamic_info_deal():
    get_url_sql = '''
    SELECT
        URL 
    FROM
        tree_node 
    WHERE
        name = '{}' 
        AND pId = (
        SELECT
            id 
        FROM
            tree_node 
        WHERE
        name = '{}' 
    AND pId = ( SELECT id FROM tree_node WHERE name = '{}' AND pId = 96 ));
    '''.format('动态信息', '2994584647', 'QQ')
    get_results_sql = '''
    SELECT
        t1.recordid,
        t1.DELETE_STATUS,
        t1.friend_account,
        t1.FRIEND_NICKNAME,
        t1.WEIBO_TYPE,
        t1.MAIL_SEND_TIME,
        t1.WEIBO_MESSAGE,
        t2.CONTENT_SUB,
        t2.MULTMSG_URL_SUB 
    FROM
        Dynamic_tab AS t1
        LEFT JOIN AttachedMap_tab AS t2 ON t1.MBLOG_ID = t2.TALK_ID 
    WHERE
        t1.APPCLASS_TYPE = 'IM' 
        AND t1.APP_TYPE = '1030001' 
        AND t1.ACCOUNT = '2994584647' 
        AND t1.WEIBO_TYPE <> 99 
    ORDER BY
        t1.DELETE_STATUS ASC,
        t1.recordid DESC;
    '''
    dynamic_type_conf = create_uni_conf_ch('content_type')

    def assert_func(result_index, act_data_list, result):
        dynamic_info_data_2 = act_data_list[result_index][2]
        dynamic_info_data_3 = act_data_list[result_index][3]
        dynamic_info_data_4 = act_data_list[result_index][4]
        # 判断动态信息的账号字段
        account_result = u'帐号:'+result[2]
        assert_in(account_result, dynamic_info_data_2)
        # 判断昵称字段
        nickname_result = u'昵称:'+result[3]
        assert_in(nickname_result, dynamic_info_data_2)
        # 判断内容类型字段
        content_type_result = u'内容类型:'+dynamic_type_conf[result[4]]
        assert_in(content_type_result, dynamic_info_data_3)
        # 判断时间字段
        sendtime_result = u'时间:'+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(result[5])))
        assert_in(sendtime_result, dynamic_info_data_3)
        # 判断消息内容字段
        if result[6]:
            content_result = u'消息内容:'+result[6]
            assert_in(content_result, dynamic_info_data_4)
        if result[7]:
            content_result = u'消息内容:'+result[7]
            assert_in(content_result, dynamic_info_data_4)
        # 判断附件URL字段
        if result[8]:
            url_result = u'附件URL:'+result[8]
            assert_in(url_result, dynamic_info_data_4)
    uni_logic_single_page(get_url_sql, get_results_sql, assert_func)


# friend_info_deal()
# account_info_deal()
# group_info_deal()
dynamic_info_deal()