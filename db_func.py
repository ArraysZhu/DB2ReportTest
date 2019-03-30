#! /usr/bin/python
# -*-coding:utf-8 -*-

import sqlite3

class DBConnect(object):
    def __init__(self, db_file):
        self.con = sqlite3.connect(db_file)
        self.cur = self.con.cursor()

    def execute_sqls(self, sqls):
        if isinstance(sqls, list):
            for sql in sqls:
                self.cur.execute(sql)
        else:
            self.cur.execute(sqls)
        self.con.commit()
        return self.cur.fetchall()

    def close_connect(self):
        self.con.close()

    def close_cursor(self):
        self.cur.close()