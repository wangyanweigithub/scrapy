# -*- coding: utf-8 -*-
import scrapy
from pyquery import PyQuery as pq
import re,execjs,requests,time
from tengxunhouse.items import DetailItem
from tengxunhouse.items import PhotoItem
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

class DbhouseSpider(scrapy.Spider):
    name = 'dbhouse'
    allowed_domains = ['house.qq.com']
    # start_urls = ['http://db.house.qq.com/index.php?mod=search&city=jinzhou']
    # start_urls  = ['http://db.house.qq.com/index.php?mod=search&city=sh']
    start_urls  = ['http://db.house.qq.com/index.php?mod=search&city=jingmen#LXNob3d0eXBlXzE=']
    page_no = 1
    cityen = ''

    def parse(self, response):
        print("debug01")
        print('response.url',response.url,len(response.url))
        self.cityen = re.split(r'city=', response.url)[1]
        self.cityen = re.split(r'#\S*', self.cityen)[0]
        print(self.cityen, type(self.cityen))
        request = 'http://db.house.qq.com/index.php?mod=search&act=newsearch&city=' + str(
            self.cityen) + '&showtype=1&page_no=' + str(self.page_no) + '&mod=search&city=' + str(self.cityen)
        print(request)
        data = {}
        data['cityen'] = self.cityen
        yield scrapy.Request(request,meta={'data': data}, callback=self.parse_item)

    def parse_item(self,response):
        print('debug02')
        print(response.url)
        data = response.meta['data']
        print(data)
        html = response.body.decode('gb18030')
        # print('html',html)
        pattern1 = r'\s*var\s*search_result\s*=\s*\s*'
        res1 = re.split(pattern1, html)
        print(res1)
        pattern2 = r'\s*;var\s*search_result_list_num\s*=\s*\d*;'
        res2 = re.split(pattern2, res1[1])
        print(res2)

        with open(str("testdb1.html"), "w+") as f:
            f.write(res2[0])

        result = execjs.eval(res2[0])
        doc = pq(result)
        # print("doc",doc)
        link = []
        links = doc('li.title > h2 > a')
        # print('links:', links)
        if links:
            for val in links.items():
                link.append(val.attr('href'))
            print("links",len(link), link)
            if link:
                for val in link:
                    print("link:",val)
                    yield scrapy.Request(val, callback=self.parse_building)

        next = doc('#search_result_page a.grey:contains("下一页")')
        print('next',next)
        if  not next:   #if not next:
            print('end2')
            self.page_no += 1
            request = 'http://db.house.qq.com/index.php?mod=search&act=newsearch&city=' + str(
                data['cityen']) + '&showtype=1&page_no=' + str(self.page_no) + '&mod=search&city=' + str(data['cityen'])
            print('request',request,self.page_no)
            yield scrapy.Request(request,meta={'data': data}, callback=self.parse_item)

    def parse_building(self,response):
        print('debug03')
        print(response.url)
        html = response.body#.decode('gb18030')
        link = response.url
        print('link:',link,type(link))
        doc = pq(html)
        data = {}
        city = doc("div.fcHd.cf > div.fl.subBox > div.mbx > a:nth-child(2)").text()
        area = doc("div.fcHd.cf > div.fl.subBox > div.mbx > a:nth-child(3)").text()

        if not (city and area):
            print("failed")
            dcap = dict(DesiredCapabilities.PHANTOMJS)  # DesiredCapabilities.PHANTOMJS.copy()
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.3"
            )
            driver = webdriver.PhantomJS(desired_capabilities=dcap)  # desired_capabilities=desired_capabilities
            # driver.start_session(dcap)
            driver.implicitly_wait(20)
            driver.get(response.url)
            doc = pq(driver.page_source)
            city = doc("div.fcHd.cf > div.fl.subBox > div.mbx > a:nth-child(2)").text()
            area = doc("div.fcHd.cf > div.fl.subBox > div.mbx > a:nth-child(3)").text()
            driver.close()

        data['city'] = city
        data['area'] = area
        data['link'] = link

        print('data:',data)

        detailhref = response.url + '/info.html'
        yield scrapy.Request(detailhref, meta={'data': data}, callback=self.parse_detail)
        photohref = response.url.replace('//db.','//photo.')+'/photo/'
        yield scrapy.Request(photohref, meta={'data': data}, callback=self.parse_photo)



        # a = doc('#nav > div > ul.fl > li>a:contains("详细信息")')
        # if a:
        #     detailhref = 'http://db.house.qq.com' + a.attr('href')
        #     print("detailhref:", a.attr('href'), detailhref)
        #     yield scrapy.Request(detailhref,meta={'data': data}, callback=self.parse_detail)
        #
        # b = doc('#nav > div > ul.fl > li > a:contains("楼盘相册")')
        # if b:
        #     photohref = b.attr('href')
        #     print("photohref:", photohref)
        #     yield scrapy.Request(photohref, meta={'data': data}, callback=self.parse_photo)


    def parse_detail(self,response):
        print('debug04')
        print(response.url)
        data = response.meta['data']
        html = response.body#.decode('gb18030')
        doc = pq(html)
        if not (doc('#housedetailless') and doc("#property > div.bd > ul > li > p")):
            print("failed04")
            dcap = dict(DesiredCapabilities.PHANTOMJS)  # DesiredCapabilities.PHANTOMJS.copy()
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.3"
            )
            driver = webdriver.PhantomJS(desired_capabilities=dcap)  # desired_capabilities=desired_capabilities
            # driver.start_session(dcap)
            driver.implicitly_wait(20)
            driver.get(response.url)
            doc = pq(driver.page_source)
            driver.close()
        item = DetailItem()
        basicinfo = {}
        set = []
        value = []
        bulidding = doc('div.elite.layout.picContent.bgf > div > h2').text()
        print("bulidding", bulidding)


        xval = doc("#basics > div.bd > ul > li > span")
        yval = doc("#basics > div.bd > ul > li > p")
        for val in xval.items():
            set.append(val.text())
        for val in yval.items():
            value.append(val.text())

        xval = doc("#saleIntro > div.bd > ul > li > span")
        yval = doc("#saleIntro > div.bd > ul > li > p")
        for val in xval.items():
            set.append(val.text())
        for val in yval.items():
            value.append(val.text())

        xval = doc("#building > div.bd > ul > li > span")
        yval = doc("#building > div.bd > ul > li > p")
        for val in xval.items():
            set.append(val.text())
        for val in yval.items():
            value.append(val.text())

        xval = doc("#property > div.bd > ul > li > span")
        yval = doc("#property > div.bd > ul > li > p")
        for val in xval.items():
            set.append(val.text())
        for val in yval.items():
            value.append(val.text())

        for i in range(len(set)):
            basicinfo[set[i]] = value[i]

        intro = doc('#housedetailless')
        if intro:
            print(intro)
            basicinfo['楼盘简介'] = intro.text().replace('\n', '')

        print(len(set), value, '\nbasicinfo\n', len(basicinfo), basicinfo)

        item['city'] = str(data['city'])
        item['area'] = str(data['area'])
        item['link'] = str(data['link'])
        item['building']  = str(bulidding)
        item['basicinfo'] = basicinfo

        print("DetailItem",item)
        yield item

    def parse_photo(self,response):
        print('debug05')
        print(response.url)
        data = response.meta['data']
        html = response.body.decode('gb18030')
        headers = {'Accept-Encoding': 'gzip, deflate, compress',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Connection': 'keep-alive',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        doc = pq(html)
        build = doc('div.name.fl > h2').text()
        if not build:
            print("failed05")
            dcap = dict(DesiredCapabilities.PHANTOMJS)  # DesiredCapabilities.PHANTOMJS.copy()
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.3"
            )
            driver = webdriver.PhantomJS(desired_capabilities=dcap)  # desired_capabilities=desired_capabilities
            # driver.start_session(dcap)
            driver.implicitly_wait(20)
            driver.get(response.url)
            doc = pq(driver.page_source)
            driver.close()
        typephoto = doc('#container_1 > ul > li > div > a > img')
        housephoto = doc('#container_5 > ul > li > div > a > img')
        item = PhotoItem()
        list1 = []
        list2 = []
        for val in typephoto.items():
            list1.append(val.attr('src'))
        for val in housephoto.items():
            list2.append(val.attr('src'))

        Aimg = doc('#container_1 > ul > li> div:nth-child(2) > a')
        Dimg = doc('#container_5 > ul > li > a')
        Aimgname = []
        Dimgname = []
        # if not Aimg:
        #     print("change")
        #     Aimg = doc('#container_1 > ul > li> div:nth-child(2) > a')
        for val in Aimg.items():
            Aimgname.append(val.text())
        for val in Dimg.items():
            Dimgname.append(val.text())
        print('name:', Aimgname, '\n', Dimgname)

        Aloadmore = doc('#_apartment > div.bd > a.loadMore')
        Dloadmore = doc('#_draw > div.bd > a.loadMore')

        if Aloadmore:
            print("test1")
            print("loadmore:", Aloadmore.text())
            list3 = []
            print(response.url)
            houseid = re.search('_\d{4,6}', response.url)
            id = houseid.group()[1:]
            type = Aloadmore.attr('type')
            page = Aloadmore.attr('page')
            if id and type and page:
                print('houseid:', houseid.group()[1:], type, page)
                clickurl = 'http://photo.house.qq.com/index.php?mod=photo&act=getmore&houseid=' + id + '&type=' + type + '&page=' + page
                # more = ' http://photo.house.qq.com/index.php?mod=photo&act=getmore&houseid=167454&type=5&page=1'
                html = requests.get(clickurl, headers=headers).content.decode('gb18030')
                pattern1 = r'\s*var\s*show_more_jsloader\s*=\s*{"code":"0","msg":"","data":{"html":\s*'
                res1 = re.split(pattern1, html)
                print('res1', res1)
                pattern2 = r',\s*"hasmore":'
                res2 = re.split(pattern2, res1[1])
                print('res2', res2[0])
                result = execjs.eval(res2[0])
                doc = pq(result)
                print('\ndoc:', doc)
                imgurl = doc('img')
                imgname = doc('li>div:nth-child(2)>a')
                for val in imgurl.items():
                    print(val.attr('src'))
                    # list3.append(val)
                    list1.append(val.attr('src'))

                for val in imgname.items():
                    # print('\n',val)
                    # list3.append(val.text())
                    Aimgname.append(val.text())
                # print('list3', list3)
                print('\nAimgname:', Aimgname)

        if Dloadmore:
            print("test2")
            print("loadmore:", Dloadmore.text())
            list3 = []
            # print(response.url)
            houseid = re.search('_\d{4,6}', response.url)
            id = houseid.group()[1:]
            type = Dloadmore.attr('type')
            page = Dloadmore.attr('page')
            if id and type and page:
                print('houseid:', houseid.group()[1:], type, page)
                clickurl = 'http://photo.house.qq.com/index.php?mod=photo&act=getmore&houseid=' + id + '&type=' + type + '&page=' + page
                html = requests.get(clickurl, headers=headers).content.decode('gb18030')
                pattern1 = r'\s*var\s*show_more_jsloader\s*=\s*{"code":"0","msg":"","data":{"html":\s*'
                res1 = re.split(pattern1, html)
                print('res1', res1)
                pattern2 = r',\s*"hasmore":'
                res2 = re.split(pattern2, res1[1])
                print('res2', res2[0])
                result = execjs.eval(res2[0])
                doc = pq(result)
                imgurl = doc('img')
                imgname = doc('li>a')
                for val in imgurl.items():
                    list2.append(val.attr('src'))

                for val in imgname.items():
                    # print('\n',val)
                    # list3.append(val.text())
                    Dimgname.append(val.text())
                print('\nDimgname:',Dimgname)

        if list1:
            print("list1 has url")
            for i in range(len(list1)):
                list1[i] = list1[i].replace('180', '1024')

        if list2:
            print("list2 has url")
            for i in range(len(list2)):
                list2[i] = list2[i].replace('180', '1024')

        print(len(list1), "list1:", list1, '\n', len(list2), 'list2:', list2)


        item['city'] = str(data['city'])
        item['area'] = str(data['area'])
        item['building'] = str(build)
        item['Aimgurl'] = list1
        item['Aimgname'] = Aimgname
        item['Dimgurl'] = list2
        item['Dimgname'] = Dimgname
        print("PhotoItem",item)

        yield item










