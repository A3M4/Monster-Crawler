# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

class MonsterPipeline(object):


    def __init__(self):
        self.create_connection()  #whenevr the class is initialized the two methods are automatically called
        self.create_table()

    def create_connection(self):
        self.conn = sqlite3.connect("jobinformation.db")  #exits connect not exits create
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS jobtable_tb""")
        self.curr.execute("""create table jobtable_tb(
                        title text,
                        companyname text,
                        companyurl text,
                        jobLocationRegion text,
                        jobLocationCity text,
                        jobdescription text

                        )""")

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self,item):
        self.curr.execute("""insert into jobtable_tb values(?,?,?,?,?,?)""",(
            item['title'],
            item['companyname'],
            item["companyurl"],
            item['jobLocationRegion'],
            item['jobLocationCity'],
            item['jobdescription']
        ))
        self.conn.commit()

