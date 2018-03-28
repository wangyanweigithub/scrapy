# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib.request
from tengxunhouse.items import DetailItem
from tengxunhouse.items import PhotoItem
import os
import codecs
import json

class TengxunhousePipeline(object):
    def __init__(self):
        # 创建了一个文件
        # self.filename = open("teacher.json", "w")
        pass

    def process_item(self, item, spider):
        if item.__class__.__name__ == 'PhotoItem':
            print("output1")
            data = dict(item)
            print(data)
            path = 'E:\\腾讯房产\\'+data['city']+'\\'+data['area']+'\\'+data['building']+"\\"+"Apartment"
            # 判断结果
            if not (os.path.exists(path)):
                os.makedirs(path)

            try:
                for i in range(len(data['Aimgurl'])):
                    data['Aimgname'][i] = data['Aimgname'][i].replace('/','_').replace('\\','_')\
                    .replace('*','_').replace('#','_').replace('?','_').replace(' ','_').replace('|','_')
                    imgname =path +'\\'+data['Aimgname'][i]+'_'+str(i)+'.jpg'
                    imgurl = data['Aimgurl'][i]
                    print("image:",imgname,imgurl)
                    urllib.request.urlretrieve(imgurl, imgname)
                    print("sucess")
            except:
                print("Aimg error")
                pass

            path = 'E:\\腾讯房产\\' + data['city'] + '\\' + data['area'] + '\\' + data['building'] + "\\" + "Draw"
            if not (os.path.exists(path)):
                os.makedirs(path)

            try:
                for i in range(len(data['Dimgurl'])):
                    data['Dimgname'][i] = data['Dimgname'][i].replace('/','_').replace('\\','_')\
                    .replace('*','_').replace('#','_').replace('?','_').replace(' ','_')
                    imgname =path +'\\'+data['Dimgname'][i]+'_'+str(i)+'.jpg'
                    imgurl = data['Dimgurl'][i]
                    print("image:",imgname,imgurl)
                    urllib.request.urlretrieve(imgurl, imgname)
                    print("sucess")
            except:
                print("Dimg error")
                pass

        if item.__class__.__name__ == 'DetailItem':
            print("output2")
            data = dict(item)
            print(data)
            path = 'E:\\腾讯房产\\'+data['city']+'\\'+data['area']+'\\'+data['building']
            # 判断结果
            if not (os.path.exists(path)):
                os.makedirs(path)
            try:
                print("start")
                filename = path +"\\"+data['building']+".txt"
                file = codecs.open(filename, "w+", encoding="utf-8")
                content = json.dumps(data['basicinfo'], ensure_ascii=False) + "\n"
                file.write(content)
                file.close()
                print("filename",filename)
            except:
                print("txt error",filename)
            try:
                filename = path + "\\" + data['building'] + ".json"
                file = codecs.open(filename, "w+", encoding="utf-8")
                content = json.dumps(data['basicinfo'], ensure_ascii=False) + "\n"
                file.write(content)
                file.close()
            except:
                print("txt error",filename)
            try:
                filename = path + "\\" + 'link.txt'
                file = codecs.open(filename, "w+", encoding="utf-8")
                content = data['link']
                file.write(content)
                file.close()
            except:
                print("txt error",filename)
        return item

    # close_spider方法是可选的，结束时调用这个方法
    def close_spider(self, spider):
        # self.file.close()
        pass
