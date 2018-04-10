# -*- coding: utf-8 -*-
import scrapy
from pyquery import PyQuery as pq
import re,execjs,requests,time
from tengxunhouse.items import DetailItem
from tengxunhouse.items import PhotoItem
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from scrapy.selector import Selector

class DbhouseSpider(scrapy.Spider):
    name = 'dbhouse'
    allowed_domains = ['house.qq.com']
    start_urls = ['http://db.house.qq.com/index.php?mod=search&city=bj']

    def __init__(self, city=None, area=None):
        super(DbhouseSpider, self).__init__()
        self.city = city
        self.area = area

    def parse(self, response):
        try:
            result = response.xpath("//div[@class='qgcity']/div[@id='tabb']//div[@id='scrollBox']/"
                                    "div[@class='scrollContent']/dl")
            all_citys = {}
            for each in result:
                for dd in each.xpath("dd/a"):
                    href = dd.xpath("@href").extract()
                    city = dd.xpath("text()").extract()
                    city_link = dict(zip(city, href))
                    all_citys.update(city_link)

            self.all_citys = all_citys
            for k, url in all_citys.items():
                if not self.city:
                    yield scrapy.Request(url, callback=self.get_city_areas)

            if self.city:
                yield scrapy.Request(all_citys[self.city], callback=self.get_city_areas)
        except Exception as e:
            print(e)

    def get_city_areas(self, response):
        try:
            city_name = response.xpath("//div[@id='cityName']/a/text()").extract()[0]
            area_code_dic = {}
            for area in response.xpath("//ul[@id='search_condition_region1']/li"):
                params = area.xpath("a/@onclick").extract()[0]
                area_num = re.search(r"(\d*:\d*)", params).group(1)
                area_name = area.xpath("a/text()").extract()[0]
                area_code_dic.update({area_name: area_num})

                if not self.area:
                    url = "%s&act=newsearch&showtype=1&page_no=1& unit=1&all=&CA=%s" % (self.all_citys[city_name], area_num)
                    yield scrapy.Request(url, callback=self.get_area_house)
            if self.area:
                print(area_code_dic)
                url = "%s&act=newsearch&showtype=1&page_no=1&" \
                      "unit=1&all=&CA=%s" % (self.all_citys[city_name], area_code_dic[self.area])
                yield scrapy.Request(url, callback=self.get_area_house)
        except Exception as e:
            print(e)

    def get_area_house(self, response):
        try:
            print(response.url)
            body = response.body.decode("utf8")
            groups = re.search("\s*var search_result = \s*(.*);var search_result_list_num\s*=\s*\d", body)
            body = execjs.eval(groups[1])
            with open("a.html", 'w', encoding="utf-8") as f:
                f.write(body)
            body = Selector(text=body)
            for each in body.xpath("//li[@class='title']/h2"):
                url = each.xpath("a/@href").extract()[0]
                yield scrapy.Request(url, callback=self.parse_building)

            for each in body.xpath("//div[@id='search_result_page']/a[@onclick]"):
                if each.xpath("text()").extract()[0] == "下一页>":
                    search_result = re.search(r".*\(.*,.*,.*,(\d*)\)", each.xpath("@onclick").extract()[0])
                    page_no = search_result.group(1)
                    url = re.sub("page_no=\d*", "page_no=%s" % page_no, response.url, 1)
                    yield scrapy.Request(url, callback=self.get_area_house)
        except Exception as e:
            self.log("!!!!!error %s" % e)

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










