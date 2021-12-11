import parsel, sqlite3, cloudscraper
import configparser
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
class BookCore:
    def __init__(self):
        self.read_config()
        self.scraper = cloudscraper.create_scraper(browser = {"browser":"chrome", "desktop":False, "platform":"android"}, delay = 5)
        self.change_websites(0)
        self.get_websites_list()
        self.get_proxy_ip()
    def get_html_page(self, url, encoding):
        while True:
            try:
                proxy = self.random_ip()
                req = self.scraper.get(url = url, proxies = proxy, timeout=2)
                break
            except:
                print("error",proxy)
                continue
        req.encoding=encoding
        return req.text
    def get_book_chapters(self, url):
        html=self.get_html_page(url, self.get_encoding(1))
        selector=parsel.Selector(html)

        chapter_titles=selector.css(self.result[10]).extract()
        chapter_urls=selector.css(self.result[11]).extract()
        
        chapter_titles=self.process_chapter_titles(chapter_titles)
        chapter_urls = ["https://" + self.result[2] + i for i in chapter_urls if i != "javascript:dd_show()"]

        chapter_info=dict(zip(chapter_titles,chapter_urls))
        return chapter_info
    def get_book_contents(self, url):
        html = self.get_html_page(url, self.get_encoding(2))
        selector = parsel.Selector(html)

        title = selector.css(self.result[12]).extract_first()
        contents = selector.css(self.result[13]).extract()
        contents = [i for i in contents if i != "\r\n\t\t"]

        return [title,"\n".join(contents)]
    def get_book_info(self, url):
        html=self.get_html_page(url, self.get_encoding(1))
        selector=parsel.Selector(html)

        info=selector.css(self.result[8]).extract()
        intro=selector.css(self.result[9]).extract()

        return self.process_info(info + intro)
    def process_info(self, info):
        processed = info
        for i in info:
            if str(i).endswith("："):
                index = info.index(i)
                processed[index] = i + info [index + 1]
                del processed[index + 1]
                break
        return "\n".join(processed)
    def process_chapter_titles(self, chapter_titles):
        remove_str='<<---展开全部章节--->>'
        temp=list(chapter_titles)
        if temp.count(remove_str)!=0:
            temp.remove(remove_str)
        return temp
    def search_book(self, bookname):
        encoding = self.get_encoding(0)
        search_url = self.result[4] + quote (bookname, encoding=encoding)

        html = self.get_html_page(search_url, encoding)
        selector = parsel.Selector(html)

        result_names = selector.css(self.result[5]).extract()
        result_urls = selector.css(self.result[6]).extract()
        result_authors = selector.css(self.result[7]).extract()

        result_urls = ["https://" + self.result[2] + i for i in result_urls]
        result_authors = self.process_authors(result_authors)

        return dict(zip(result_names,list(zip(result_urls,result_authors))))
    def process_authors(self, result_authors):
        if  len(result_authors)==0 or not result_authors[0].startswith("作者"):
            return result_authors
        return [i[3:] for i in result_authors]
    def change_websites(self, type):
        self.result = self.sql_query("*", type)
    def sql_query(self, args, type):
        self.db = sqlite3.connect("book.db", check_same_thread = False)
        self.cursor = self.db.cursor()
        self.cursor.execute('''SELECT %s FROM book_websites WHERE id=%d''' % (args, type))
        return self.cursor.fetchone()
    def get_encoding(self, index):
        return self.result[3].split(" | ")[index]
    def get_websites_list(self):
        self.cursor.execute('''SELECT website,baseurl FROM book_websites''')
        result=self.cursor.fetchall()
        self.website_list=[]
        for index,value in enumerate(result):
            self.website_list.append("%d.%s (%s)" % (index + 1,value[0],value[1]))
    def get_proxy_ip(self):
        if self.ip_type == 0:
            return
        self.ip = []
        self.port = []
        thread = ThreadPoolExecutor(max_workers = 10)
        task = [thread.submit(self.get_each_page_ip, i) for i in range(1, int(self.ip_amounts / 10))]
    def get_each_page_ip(self, page):
        html=self.scraper.get("http://www.ip3366.net/?stype=1&page=%d" % page)
        html.encoding="gbk"

        selector=parsel.Selector(html.text)

        current_ip=selector.css("#list > table > tbody > tr > td:nth-child(1) ::text").extract()
        current_port=selector.css("#list > table > tbody > tr > td:nth-child(2) ::text").extract()

        self.ip.extend(current_ip)
        self.port.extend(current_port)
    def random_ip(self):
        if self.ip_type == 0:
            return {}
        elif self.ip_type == 2:
            return {"http":self.ip_addres}
        import random
        index = random.randint(0, len(self.ip) - 1)
        return {"http":self.ip[index] + ":" + self.port[index]}
    def read_config(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.conf")

        self.ip_type = int(self.config.get("proxy_ip","ip_type"))
        self.ip_amounts = int(self.config.get("proxy_ip","ip_amounts"))
        self.ip_addres = self.config.get("proxy_ip","ip_address")
        self.thread_amounts = int(self.config.get("thread_pool","thread_amounts"))
    def save_config(self, ip_type, ip_amounts, ip_address, thread_amounts):
        self.config.set("proxy_ip", "ip_type", str(ip_type))
        self.config.set("proxy_ip", "ip_amounts", str(ip_amounts))
        self.config.set("proxy_ip", "ip_address", ip_address)
        self.config.set("thread_pool", "thread_amounts", str(thread_amounts))
        with open("config.conf", "w", encoding = "utf-8") as f:
            self.config.write(f)
        self.__init__()
class HtmlCore:
    def save_css(self, path):
        css = '.page {background-color: #E9FAFF; font-family: 微软雅黑; }\n.list {overflow: hidden; margin: 0 auto 10px;}\n.list dt {font-size: 18px; line-height: 36px; text-align: center; background: #C3DFEA; overflow: hidden;}\n.list dd {zoom: 1; padding: 0 10px; border-bottom: 1px dashed #CCC; float: left; width: 250px;}\n.list dd a {font-size: 16px; line-height: 36px; white-space: nowrap; color: #2a779d;}\n.list dd a:link {text-decoration: none;}\n.content h1 {font-size: 24px ; font-weight: 400; text-align: center ; color: #CC3300 ; line-height: 40px ;margin: 20px; border-bottom: 1px dashed #CCC;}\n.content p {font-size: 20px ;border-bottom: 1px dashed #CCC; margin: 20px;}\n.pagedown {padding: 0; background: #d4eaf2; height: 40px ; line-height: 40px ; margin-bottom: 10px ;text-align: center;}\n.pagedown a {font-size: 16px; padding: 10px ; line-height: 30px;}\n.pagedown a:link {text-decoration: none;}\n.pagedown .p_contents {color: #2a779d; background-size: 90px;}\n.pagedown .p_up {color: #2a779d; background-size: 90px;}\n.pagedown .p_down {color: #2a779d; background-size: 90px;}'
        with open(path, "w", encoding = "utf-8") as file:
            file.write(css)
    def process_contents(self, chapter_name, text, index, isFirst, isLast):
        html_page = []
        html_title = '\n<title>' + chapter_name + '</title>'
        html_head = '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' + html_title + '\n<link rel="stylesheet" href="style.css">\n</head>\n<body class="page">\n<div class="content">'
        html_page.append(html_head)

        content_lines = str(text[1]).replace("\n","\n<br /><br />\n")
        html_body = '<h1>' + chapter_name + '</h1>\n'+'<p>' + content_lines + '</p>\n'
        html_page.append(html_body)

        if isFirst :
            previous_c = ""
            next_c = '<a href="' + str(index + 1) +'.html" class="p_down">下一章</a>\n'
        elif isLast:
            previous_c = '<a href="' + str(index - 1)+'.html" class="p_up">上一章</a>\n'
            next_c = ""
        else:
            previous_c = '<a href="' + str(index - 1)+'.html" class="p_up">上一章</a>\n'
            next_c = '<a href="' + str(index + 1) +'.html" class="p_down">下一章</a>\n'

        html_bottom = '</div>\n<div class="pagedown">\n<a href="contents.html" class="p_contents" >目录</a>\n' + previous_c + next_c + '</div>\n</body>\n</html>'

        html_page.append(html_bottom)
        return "".join(html_page)
    def process_chapter(self, bookname, chaptername_list):
        html_page = []
        html_title = '\n<title>' + bookname + ' 章节列表</title>'
        html_head = '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' + html_title + '\n<link rel="stylesheet" href="style.css">\n</head>\n<body class="page">\n<div class="list">\n'
        html_page.append(html_head)

        html_dt='<dt>'+bookname+' 章节列表</dt>\n'
        html_page.append(html_dt)

        for index,value in enumerate(chaptername_list):
            html_page.append('<dd><a href="' + str(index) + '.html">' + value + '</a></dd>')

        html_page.append('</div>\n</body>')
        return "".join(html_page)