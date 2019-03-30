#! /usr/bin/python
# -*-coding:utf-8 -*-

import time
import sys
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
delete_status_conf = create_uni_conf_en('delete_status')
store_source_conf = create_uni_conf_ch('store_source')
encrypt_status_conf = create_uni_conf_ch('encrypt_status')


# 联系人信息处理
def contact_info_deal():
    phone_label_conf = {
        u"电话号码": (u"pb_num_type", 3),
        u"Email": (u"pb_email_type", 3),
        u"地址": (u"pb_addr_type", 3),
        u"即时通讯": (u"im_app", 3),
        u"网站": (u"pb_url_type", 3),
        u"纪念日": (u"pb_calendar_type", 4),
        u"备注": (u"pb_remark_type", 4),
        u"群组": (u"分组", 2),
        u"传真": (u"pb_fix_type", 3),
        u"人际关系": (u"pb_relationship_type", 4),
        u"工作相关": (u"pb_work_type", 4)
    }
    phone_value_conf = {y['db']:({n['db']:m for m,n in GLOBAL_CONF[phone_label_conf[x][0]].items()}, phone_label_conf[x][1])
                        if x in phone_label_conf.keys() and phone_label_conf[x][0] in GLOBAL_CONF.keys()
                        else phone_label_conf[x] if x in phone_label_conf.keys()
                        else x for x,y in GLOBAL_CONF['phonebook_type'].items()}
    get_results_sql = u'''
    SELECT
        a.RECORDID,
        a.RELATIONSHIP_NAME,
        a.STORE_SOURCE,
        a.PRIVACYCONFIG,
        a.DELETE_STATUS,
        a.LAST_UPDATE_TIME,
        b.PHONE_VALUE_TYPE,
        b.RELATIONSHIP_LABEL,
        b.RELATIONSHIP_VALUE 
    FROM
        Contact_tab a
        LEFT JOIN ContactDetail_tab b ON a.RELATIONSHIP_ID = b.RELATIONSHIP_ID 
    WHERE
        a.APPCLASS_TYPE = 'PHONE';
    '''
    get_del_num_sql = u"select count(*) from Contact_tab where DELETE_STATUS = 1 and APPCLASS_TYPE = 'PHONE';"
    get_sum_num_sql = u"select count(*) from Contact_tab where APPCLASS_TYPE = 'PHONE';"
    sum_num_result = result_db_obj.execute_sqls(get_sum_num_sql)[0][0]
    del_num_result = result_db_obj.execute_sqls(get_del_num_sql)[0][0]
    results_list = result_db_obj.execute_sqls(get_results_sql)
    get_data_url_sql = u"select url from tree_node where name = '{0}' and pid = {1}".format(u'联系人', 0)
    data_url = temp_db_obj.execute_sqls(get_data_url_sql)[0][0]
    data_dict = htmlp.common_html_parser(data_url)
    assert_equal(sum_num_result, data_dict['total_num'])
    assert_equal(del_num_result, data_dict['del_num'])
    act_data_list = data_dict['datas']
    last_record_id = -1
    for result in results_list:
        if result[0] != last_record_id:
            # 判断联系人姓名
            if result[1]:
                name_result = u"姓名:"+result[1].strip().replace('\n','').replace('\r','')
                name_data = act_data_list[result[0]-1][2].strip()
                assert_in(name_result, name_data)
            # 判断联系人数据存储源
            store_source = store_source_conf[result[2]]
            store_source_result = u"数据存储源:"+store_source
            store_source_data = act_data_list[result[0]-1][4]
            assert_in(store_source_result, store_source_data)
            # 判断联系人加密状态
            encrypt_status = encrypt_status_conf[result[3]]
            encrypt_status_result = u'加密状态:'+encrypt_status
            encrypt_status_data = act_data_list[result[0]-1][4]
            assert_in(encrypt_status_result, encrypt_status_data)
            # 判断联系人删除状态
            delete_status = delete_status_conf[result[4]]
            delete_status_result = delete_status.lower()
            delete_status_data = act_data_list[result[0]-1][1].lower()
            assert_in(delete_status_result, delete_status_data)
            # 判断联系人更新时间
            if result[5]:
                update_time_result = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(result[5])))
                update_time_data = act_data_list[result[0] - 1][4]
                assert_in(update_time_result, update_time_data)
        last_record_id = result[0]
        # 判断联系人详细值
        if not result[6] or int(result[6]) > 11:
            continue
        elif result[6]=='08':
            data_pre = phone_value_conf[result[6]][0]
            relation_result = result[8].strip()
            relation_data = act_data_list[result[0]-1][phone_value_conf[result[6]][1]]
            compare_tuple = (relation_result, data_pre+u':'+relation_result)
            assert_in(compare_tuple, relation_data)
        else:
            data_pre = phone_value_conf[result[6]][0][result[7]]
            relation_result = data_pre + u':' + result[8].strip()
            relation_data = act_data_list[result[0] - 1][phone_value_conf[result[6]][1]]
            assert_in(relation_result, relation_data)


# 彩信和短信通用逻辑
def sms_mms_info_deal(infotype, get_data_urls_sql, get_results_num_sql, get_results_sql):
    name2url_dict = dict(temp_db_obj.execute_sqls(get_data_urls_sql))
    results_num = result_db_obj.execute_sqls(get_results_num_sql)
    read_type_conf = create_uni_conf_ch('read_type')
    save_folder_conf = create_uni_conf_ch('save_folder')
    results_list = result_db_obj.execute_sqls(get_results_sql)
    start_index = 0
    for result_num in results_num:
        relationship_account = result_num[0]
        sum_num_result = result_num[1]
        sum_index = start_index+sum_num_result
        account_result_list = results_list[start_index:sum_index]
        start_index = sum_index
        if relationship_account == '':
            relationship_account = u'未知联系人'
        if account_result_list[0][1]:
            data_url = name2url_dict[u'{}({})'.format(account_result_list[0][1], relationship_account)]
        else:
            data_url = name2url_dict[relationship_account]
        data_dict = htmlp.common_html_parser(data_url)
        act_data_list = data_dict['datas']
        assert_equal(sum_num_result, data_dict['total_num'])
        del_num_result = 0
        for i, account_result in enumerate(account_result_list):
            # 判断短信/彩信删除状态
            delete_status = account_result[3]
            delete_status_result = delete_status_conf[delete_status].lower()
            delete_status_data = act_data_list[i][1].lower()
            assert_in(delete_status_result, delete_status_data)
            if delete_status == u'1':
                del_num_result += 1
            # 判断短信/彩信内容
            content = str(account_result[4])
            contact_result = content.strip().replace('\r','').replace('\n', '').replace(u'\xa0', ' ')
            content_data = act_data_list[i][2]
            assert_in(contact_result, content_data)
            # 判断短信/彩信发送时间
            if account_result[5]:
                send_time_result = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(account_result[5])))
                send_time_data = act_data_list[i][3]
                assert_in(send_time_result, send_time_data)
            # 判断短信/彩信已读状态
            read_type = read_type_conf[account_result[6]]
            read_type_result = u'查看状态:'+read_type
            read_type_data = act_data_list[i][4]
            assert_in(read_type_result, read_type_data)
            # 判断短信/彩信存储位置
            save_folder = save_folder_conf[account_result[7]]
            save_folder_result = u'存储位置:'+save_folder
            save_folder_data = act_data_list[i][4]
            assert_in(save_folder_result, save_folder_data)
            # 判断短信数据存储源
            if infotype==0:
                store_source = store_source_conf[account_result[8]]
                store_source_result = u"数据存储源:"+store_source
                store_source_data = act_data_list[i][4]
                assert_in(store_source_result, store_source_data)
            # 判断彩信加密状态
            elif infotype==1:
                encrypt_status = encrypt_status_conf[account_result[8]]
                encrypt_status_result = u'加密状态:' + encrypt_status
                encrypt_status_data = act_data_list[i][4]
                assert_in(encrypt_status_result, encrypt_status_data)
        assert_equal(del_num_result, data_dict['del_num'])


# 短信信息处理
def sms_info_deal():
    get_data_urls_sql = u'''
        SELECT
            name,
            url
        FROM
            tree_node
        WHERE
            pId = (SELECT id FROM tree_node WHERE name='{}' and pId = {});
            '''.format('短信', '0')
    get_results_num_sql = u'''
        SELECT
            RELATIONSHIP_ACCOUNT_FORMAT,
            COUNT( * ) 
        FROM
            SMS_tab 
        GROUP BY
            RELATIONSHIP_ACCOUNT_FORMAT 
        ORDER BY
            RELATIONSHIP_ACCOUNT_FORMAT;'''
    get_results_sql = u'''
        SELECT
            m.recordid,
            n.RELATIONSHIP_NAME,
            m.RELATIONSHIP_ACCOUNT_FORMAT,
            m.DELETE_STATUS,
            m.CONTENT,
            m.MAIL_SEND_TIME,
            m.MAIL_VIEW_STATUS,
            m.MAIL_SAVE_FOLDER,
            m.STORE_SOURCE
        FROM
            SMS_tab m
            LEFT JOIN (
            SELECT DISTINCT
                a.RELATIONSHIP_NAME,
                b.RELATIONSHIP_VALUE 
            FROM
                Contact_tab a
                LEFT JOIN ContactDetail_tab b ON a.RELATIONSHIP_ID = b.RELATIONSHIP_ID 
            WHERE
                a.APPCLASS_TYPE = 'PHONE' 
                AND b.PHONE_VALUE_TYPE = '01' 
                AND a.RELATIONSHIP_NAME <> '' 
            )  n ON m.RELATIONSHIP_ACCOUNT_FORMAT = n.RELATIONSHIP_VALUE 
        WHERE
            m.APPCLASS_TYPE = 'PHONE' 
        ORDER BY
            RELATIONSHIP_ACCOUNT_FORMAT;'''
    sms_mms_info_deal(0, get_data_urls_sql, get_results_num_sql, get_results_sql)


# 彩信信息处理
def mms_info_deal():
    get_data_urls_sql = u'''
        SELECT
            name,
            url
        FROM
            tree_node
        WHERE
            pId = (SELECT id FROM tree_node WHERE name='{}' and pId = {});
            '''.format('彩信', '0')
    get_results_num_sql = u'''
        SELECT
            RELATIONSHIP_ACCOUNT_FORMAT,
            COUNT( * ) 
        FROM
            MMS_tab 
        GROUP BY
            RELATIONSHIP_ACCOUNT_FORMAT 
        ORDER BY
            RELATIONSHIP_ACCOUNT_FORMAT;'''
    get_results_sql = u'''
        SELECT
            m.recordid,
            n.RELATIONSHIP_NAME,
            m.RELATIONSHIP_ACCOUNT_FORMAT,
            m.DELETE_STATUS,
            m.CONTENT,
            m.MAIL_SEND_TIME,
            m.MAIL_VIEW_STATUS,
            m.MAIL_SAVE_FOLDER,
            m.PRIVACYCONFIG
        FROM
            MMS_tab m
            LEFT JOIN (
            SELECT DISTINCT
                a.RELATIONSHIP_NAME,
                b.RELATIONSHIP_VALUE 
            FROM
                Contact_tab a
                LEFT JOIN ContactDetail_tab b ON a.RELATIONSHIP_ID = b.RELATIONSHIP_ID 
            WHERE
                a.APPCLASS_TYPE = 'PHONE' 
                AND b.PHONE_VALUE_TYPE = '01' 
                AND a.RELATIONSHIP_NAME <> '' 
            )  n ON m.RELATIONSHIP_ACCOUNT_FORMAT = n.RELATIONSHIP_VALUE 
        WHERE
            m.APPCLASS_TYPE = 'PHONE' 
        ORDER BY
            RELATIONSHIP_ACCOUNT_FORMAT;'''
    sms_mms_info_deal(1, get_data_urls_sql, get_results_num_sql, get_results_sql)





# 蓝牙信息处理
def bluetooth_info_deal():
    get_data_url_sql = '''
    SELECT
        url 
    FROM
        tree_node 
    WHERE
        name = '{}' 
    AND pId = ( SELECT id FROM tree_node WHERE name = '{}' AND pID = {} );
    '''.format('连接信息', '蓝牙', 0)
    get_results_sql = '''
        SELECT
        recordid,
        DELETE_STATUS,
        FRIEND_BLUETOOTH_MAC,
        MATERIALS_NAME,
        BLUETOOTH_TYPE,
        LAST_TIME 
    FROM
        BlueToothInfo_tab
    WHERE
        APPCLASS_TYPE = 'PHONE';'''
    bt_type_conf = create_uni_conf_ch('bluetooth_type')

    def assert_func(result_index, act_data_list, result):
        mac_result = u'MAC地址:' + result[2]
        mac_data = act_data_list[result[0] - 1][2]
        assert_in(mac_result, mac_data)
        # 判断蓝牙信息的设备名称
        device_name_result = u'设备名称:' + result[3]
        device_name_data = act_data_list[result[0] - 1][2]
        assert_in(device_name_result, device_name_data)
        # 判断蓝牙信息的设备类型
        bt_type_result = bt_type_conf[result[4]]
        bt_type_data = act_data_list[result[0] - 1][3]
        assert_in(bt_type_result, bt_type_data)
        # 判断蓝牙信息时间
        last_time_result = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(result[5])))
        last_time_data = act_data_list[result[0] - 1][4]
        assert_in(last_time_result, last_time_data)
    uni_logic_single_page(get_data_url_sql, get_results_sql, assert_func)


# WiFi信息处理
def wifi_info_deal():
    get_data_url_sql = '''
    SELECT
        URL 
    FROM
        tree_node 
    WHERE
        name = '{}' 
    AND pId = {};
    '''.format('Wifi', 0)
    get_results_sql = '''
    SELECT
        recordid,
        DELETE_STATUS,
        SSID,
        ENCRYPT_ALGO,
        PASSWORD,
        AP_MAC 
    FROM
        WifiInfo_tab 
    WHERE
        APPCLASS_TYPE = 'PHONE';
    '''
    encrypt_way_conf = create_uni_conf_ch('encrypt_way')

    def assert_func(result_index, act_data_list, result):
        # 判断wifi信息的SSID
        ssid_result = result[2]
        ssid_data = act_data_list[result[0] - 1][2]
        assert_in(ssid_result, ssid_data)
        # 判断WiFi信息的加密方式
        encrypt_way_result = u'加密方式:' + encrypt_way_conf[result[3]]
        encrypt_way_data = act_data_list[result[0] - 1][3]
        assert_in(encrypt_way_result, encrypt_way_data)
        # 判断WiFi信息的密码
        if result[4]:
            password_result = u'密码:' + result[4]
            password_data = act_data_list[result[0] - 1][3]
            assert_in(password_result, password_data)
        # 判断WiFi信息的物理地址
        ap_mac_result = u'物理地址:' + result[5]
        ap_mac_data = act_data_list[result[0] - 1][4]
        assert_in(ap_mac_result, ap_mac_data)
    uni_logic_single_page(get_data_url_sql, get_results_sql, assert_func)


def vpn_info_deal():
    get_data_url_sql = '''
    SELECT
        url 
    FROM
        tree_node 
    WHERE
        name = 'VPN' 
    AND pId = 0;
    '''
    get_results_sql = '''
    SELECT
        recordid,
        DELETE_STATUS,
        USER_DEFINED_NAME,
        SUB_TYPE,
        type,
        ACCOUNT,
        PASSWORD,
        REMOTE_ADDRESS,
        ENCRYPT_ALGO 
    FROM
        VPNInfo_tab
    WHERE
        APPCLASS_TYPE = 'PHONE';
    '''

    def assert_func(result_index, act_data_list, result):
        vpn_info_data_2 = act_data_list[result[0]-1][2]
        vpn_info_data_3 = act_data_list[result[0]-1][3]
        # 判断vpn信息的配置信息
        defined_name_result = u'配置名称:'+result[2]
        assert_in(defined_name_result, vpn_info_data_2)
        # 判断连接类型
        sub_type_result = u'连接类型:'+result[3]
        assert_in(sub_type_result, vpn_info_data_3)
        # 判断协议类型
        type_result = u'协议类型:'+result[4]
        assert_in(type_result, vpn_info_data_3)
        # 判断账号
        if result[5]:
            account_result = u'账号:'+result[5]
            assert_in(account_result, vpn_info_data_3)
        # 判断密码
        if result[6]:
            password_result = u'密码:'+result[6]
            assert_in(password_result, vpn_info_data_3)
        # 判断服务器地址
        remote_addr_result = u'服务器地址:'+result[7]
        assert_in(remote_addr_result, vpn_info_data_3)
        # 判断加密方式
        if result[8]:
            encrypt_type_result = u'加密方式:'+result[8]
            assert_in(encrypt_type_result, vpn_info_data_3)
    uni_logic_single_page(get_data_url_sql, get_results_sql, assert_func)


def app_info_deal():
    get_data_url_sql = '''
    SELECT
        url 
    FROM
        tree_node 
    WHERE
        name = '安装应用' 
    AND pId = 0;
    '''
    get_results_sql = '''
    SELECT
        recordid,
        DELETE_STATUS,
        APP_NAME,
        INSTALL_FILE_NAME,
        INSTALL_FILE_VERSION
    FROM
        AppInfo_tab
    WHERE
        APPCLASS_TYPE = 'PHONE';
    '''

    def assert_func(result_index, act_data_list, result):
        app_info_data_2 = act_data_list[result[0]-1][2]
        app_info_data_3 = act_data_list[result[0]-1][3]
        # 判断应用名称
        app_name_result = result[2]
        assert_in(app_name_result, app_info_data_2)
        # 判断安装包名称
        install_file_name_result = u'安装包名称:'+result[3]
        assert_in(install_file_name_result, app_info_data_3)
        # 判断安装包版本
        install_file_version_result = u'安装包版本:'+result[4]
        assert_in(install_file_version_result, app_info_data_3)
    uni_logic_single_page(get_data_url_sql, get_results_sql, assert_func)


def media_info_deal():
    get_data_url_sql = '''
    SELECT
        url 
    FROM
        tree_node 
    WHERE
        name = '多媒体' 
    AND pId = 0;
    '''
    get_results_sql = '''
    SELECT
        recordid,
        DELETE_STATUS,
        FILE_NAME,
        FILE_SIZE,
        FILE_TYPE,
        FILE_PATH,
        CREATE_TIME,
        MODIFY_TIME 
    FROM
        Multimedia_tab 
    WHERE
        APPCLASS_TYPE = 'PHONE';
    '''

    def assert_func(result_index, act_data_list, result):
        media_info_data_3 = act_data_list[result[0]-1][3]
        # 判断文件名称
        file_name_result = u'文件名称:'+result[2]
        assert_in(file_name_result, media_info_data_3)
        # 判断文件大小
        file_size_result = u'文件大小:'+unicode(result[3])
        assert_in(file_size_result, media_info_data_3)
        # 判断文件类型
        file_type_result = u'文件类型:'+result[4]
        assert_in(file_type_result, media_info_data_3)
        # 判断文件路径
        file_path_result = u'文件路径:'+result[5]
        assert_in(file_path_result, media_info_data_3)
        # 判断创建时间
        create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(result[6])))
        create_time_result = u'创建时间:'+create_time
        assert_in(create_time_result, media_info_data_3)
        # 判断修改时间
        modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(result[7])))
        modify_time_result = u'修改时间:'+modify_time
        assert_in(modify_time_result, media_info_data_3)
    uni_logic_single_page(get_data_url_sql, get_results_sql, assert_func)


def close():
    temp_db_obj.close_cursor()
    temp_db_obj.close_connect()
    result_db_obj.close_cursor()
    result_db_obj.close_connect()


# contact_info_deal()
# sms_info_deal()
# mms_info_deal()
# bluetooth_info_deal()
# wifi_info_deal()
# vpn_info_deal()
# app_info_deal()
# media_info_deal()
close()