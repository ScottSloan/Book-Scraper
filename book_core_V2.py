import parsel, sqlite3, cloudscraper
from urllib.parse import quote
class BookCore:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(browser = {"browser":"chrome", "desktop":False, "platform":"android"}, delay = 5)
        self.change_websites(0)
        self.get_websites_list()
        self.get_proxy_ip()
    def get_html_page(self, url, encoding):
        while True:
            try:
                req = self.scraper.get(url = url, proxies = self.random_ip(), timeout=3)
                break
            except:
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

        return [title,"\n".join(contents)]
    def get_book_info(self, url):
        html=self.get_html_page(url, self.get_encoding(1))
        selector=parsel.Selector(html)

        info=selector.css(self.result[8]).extract()
        intro=selector.css(self.result[9]).extract()
        info_processed="\n".join(info + intro)

        return info_processed
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
        if not result_authors[0].startswith("作者"):
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
        html=self.scraper.get("http://www.ip3366.net/")
        html.encoding="gbk"

        selector=parsel.Selector(html.text)

        self.ip=selector.css("#list > table > tbody > tr > td:nth-child(1) ::text").extract()
        self.port=selector.css("#list > table > tbody > tr > td:nth-child(2) ::text").extract()
        self.type=selector.css("#list > table > tbody > tr > td:nth-child(4) ::text").extract()
    def random_ip(self):
        import random
        index = random.randint(0, 9)
        return {self.type[index].lower():self.ip[index] + ":" +self.port[index]}