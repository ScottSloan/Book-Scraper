from parsel import Selector
from configparser import ConfigParser
from sqlite3 import connect
from requests import get, RequestException
from urllib.parse import quote
class BookCore:
    def __init__(self):
        self.set_dpi()
        self.read_config()
        self.read_strs()
        self.change_websites(0)
        self.get_websites_list()
    def get_html_page(self, url, encoding) -> str:
        for i in range(0, 3):
            try:
                header = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"}
                req = get(url = url, headers = header,proxies = self.get_ip(), timeout = 5)
                break
            except RequestException as e:
                if i == 3:
                    self.error_info = e
                    return "Error"
                continue
        req.encoding = encoding
        return req.text
    def get_book_chapters(self, url) -> dict:
        html = self.get_html_page(url, self.get_encoding(1))
        selector = Selector(html)

        chapter_titles = selector.css(self.result[11]).extract()
        chapter_urls = selector.css(self.result[12]).extract()
        
        chapter_titles = self.process_chapter_titles(chapter_titles)
        chapter_urls = self.process_chapter_urls(chapter_urls)

        chapter_info = dict(zip(chapter_titles, chapter_urls))
        return chapter_info
    def get_book_contents(self, url) -> list:
        html = self.get_html_page(url, self.get_encoding(2))
        selector = Selector(html)

        title = selector.css(self.result[13]).extract_first()
        contents = selector.css(self.result[14]).extract()
        contents = [i for i in contents if i != "\r\n\t\t"]

        contents_p = "\n".join(contents)

        for i in self.str_list:
            contents_p = contents_p.replace(i, "")

        return [title, contents_p]
    def get_book_info(self, url) -> str:
        html = self.get_html_page(url, self.get_encoding(1))
        selector = Selector(html)

        info=selector.css(self.result[9]).extract()
        intro=selector.css(self.result[10]).extract()

        return self.process_info(info + intro)
    def get_book_cover(self, url) -> bytes:
        html = self.get_html_page(url, self.get_encoding(1))
        selector = Selector(html)

        img_url = selector.css("div.book > div.info > div.cover > img::attr(src)").extract_first()

        req = get(img_url)
        with open("temp.jpg", "wb") as f:
            f.write(req.content)
    def process_chapter_urls(self, chapter_urls) -> list:
        if str(chapter_urls[0]).startswith("https") or str(chapter_urls[0]).startswith("http"):
            return chapter_urls
        else:
            return ["http://" + self.result[2] + i for i in chapter_urls if i != "javascript:dd_show()"]
    def process_info(self, info) -> str:
        processed = info
        text = ["????????????", ",", "????????????", "????????????>>"] 
        for i in text:
            if i in processed:
                processed.remove(i)
        return "\n".join(processed)
    def process_chapter_titles(self, chapter_titles) -> list:
        remove_str = '<<---??????????????????--->>'
        temp = list(chapter_titles)
        if temp.count(remove_str) != 0:
            temp.remove(remove_str)
        return temp
    def search_book(self, bookname) -> dict:
        encoding = self.get_encoding(0)
        search_url = self.result[4] + quote (bookname, encoding=encoding)

        html = self.get_html_page(search_url, encoding)
        selector = Selector(html)

        result_names = selector.css(self.result[5]).extract()
        result_urls = selector.css(self.result[6]).extract()
        result_authors = selector.css(self.result[7]).extract()

        result_urls = self.process_urls(result_urls)
        result_authors = self.process_authors(result_authors)

        return dict(zip(result_names,list(zip(result_urls,result_authors))))
    def process_urls(self, result_urls) -> list:
        if not bool(len(result_urls)) or str(result_urls[0]).startswith("https") or str(result_urls[0]).startswith("http"):
            return result_urls
        else:
            return ["https://" + self.result[2] + i for i in result_urls]
    def process_authors(self, result_authors) -> list:
        if not bool(len(result_authors)) or not str(result_authors[0]).startswith("??????"):
            return result_authors
        return [i[3:] for i in result_authors]
    def change_websites(self, type):
        self.result = self.sql_query("*", type)
    def sql_query(self, args, type):
        self.db = connect("book.db", check_same_thread = False)
        self.cursor = self.db.cursor()
        self.cursor.execute('''SELECT %s FROM book_websites WHERE id=%d''' % (args, type))
        return self.cursor.fetchone()
    def get_encoding(self, index) -> str:
        return self.result[3].split(" | ")[index]
    def get_websites_list(self):
        self.cursor.execute('''SELECT website,baseurl FROM book_websites''')
        result = self.cursor.fetchall()
        self.website_list = []
        for index,value in enumerate(result):
            self.website_list.append("%d.%s (%s)" % (index + 1, value[0], value[1]))
    def get_ip(self) -> dict:
        if not self.proxy_ip:
            return {}
        else:
            return {"https":self.ip_addres}
    def read_config(self):
        self.config = ConfigParser()
        self.config.read("config.ini", encoding = "utf-8")

        self.proxy_ip = bool(int(self.config.get("proxy_ip","proxy_ip")))
        self.ip_addres = self.config.get("proxy_ip","ip_address")
        self.thread_amounts = int(self.config.get("thread_pool","thread_amounts"))
    def save_config(self, ip_type, ip_address, thread_amounts):
        self.config.set("proxy_ip", "proxy_ip", str(ip_type))
        self.config.set("proxy_ip", "ip_address", ip_address)
        self.config.set("thread_pool", "thread_amounts", str(thread_amounts))
        self.save_conf()
        self.read_config()
    def set_dpi(self):
        from platform import platform
        if platform().startswith("Windows-10"):
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(2)
    def read_conf(self, section) -> list:
        return self.config.options(section)
    def read_strs(self):
        self.str_list = self.config.options("string")
    def add_conf(self, section, option):
        self.config.set(section, "%s" % option, "")
        self.save_conf()
    def remove_conf(self, section, option):
        self.config.remove_option(section, option)
        self.save_conf()
    def save_conf(self):
        with open("config.ini", "w", encoding = "utf-8") as f:
            self.config.write(f)    
    def clear_history(self):
        self.config.remove_section("history")
        self.config.add_section("history")
        self.save_conf()
class HtmlCore:
    def save_css(self, path):
        css = '.page {background-color: #E9FAFF; font-family: ????????????; }\n.list {overflow: hidden; margin: 0 auto 10px;}\n.list dt {font-size: 18px; line-height: 36px; text-align: center; background: #C3DFEA; overflow: hidden;}\n.list dd {zoom: 1; padding: 0 10px; border-bottom: 1px dashed #CCC; float: left; width: 250px;}\n.list dd a {font-size: 16px; line-height: 36px; white-space: nowrap; color: #2a779d;}\n.list dd a:link {text-decoration: none;}\n.content h1 {font-size: 24px ; font-weight: 400; text-align: center ; color: #CC3300 ; line-height: 40px ;margin: 20px; border-bottom: 1px dashed #CCC;}\n.content p {font-size: 20px ;border-bottom: 1px dashed #CCC; margin: 20px;}\n.pagedown {padding: 0; background: #d4eaf2; height: 40px ; line-height: 40px ; margin-bottom: 10px ;text-align: center;}\n.pagedown a {font-size: 16px; padding: 10px ; line-height: 30px;}\n.pagedown a:link {text-decoration: none;}\n.pagedown .p_contents {color: #2a779d; background-size: 90px;}\n.pagedown .p_up {color: #2a779d; background-size: 90px;}\n.pagedown .p_down {color: #2a779d; background-size: 90px;}'
        with open(path, "w", encoding = "utf-8") as file:
            file.write(css)
    def process_contents(self, path, chapter_name, text, index, isFirst, isLast):
        html_page = []
        html_title = '\n<title>' + chapter_name + '</title>'
        html_head = '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' + html_title + '\n<link rel="stylesheet" href="style.css">\n</head>\n<body class="page">\n<div class="content">'
        html_page.append(html_head)

        content_lines = str(text[1]).replace("\n","\n<br /><br />\n")
        html_body = '<h1>' + chapter_name + '</h1>\n'+'<p id="text">' + content_lines + '</p>\n'
        html_page.append(html_body)

        previous_c = '<a href="' + str(index)+'.html" id="p_u" class="p_up">?????????</a>\n'
        next_c = '<a href="' + str(index + 2) +'.html" id="p_d" class="p_down">?????????</a>\n'
        if isFirst :
            previous_c = ""
        elif isLast:
            next_c = ""

        html_bottom = '</div>\n<div class="pagedown">\n<a href="contents.html" id="p_con" class="p_contents" >??????</a>\n' + previous_c + next_c + '</div>\n</body>\n</html>'

        html_page.append(html_bottom)

        self.save_to_file(path, "".join(html_page))
    def process_chapter(self, path, bookname, chaptername_list):
        html_page = []
        html_title = '\n<title>' + bookname + ' ????????????</title>'
        html_head = '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' + html_title + '\n<link rel="stylesheet" href="style.css">\n</head>\n<body class="page">\n<div class="list">\n'
        html_page.append(html_head)

        html_dt='<dt>'+bookname+' ????????????</dt>\n'
        html_page.append(html_dt)

        for index,value in enumerate(chaptername_list):
            html_page.append('<dd><a href="' + str(index + 1) + '.html">' + value + '</a></dd>\n')

        html_page.append('</div>\n</body>')

        self.save_to_file(path, "".join(html_page))
    def save_to_file(self, path, text):
        with open(path, "a", encoding = "utf-8") as f:
            f.write(text)
class EpubCore:
    def create_epub(self, path, name, author, chapters):
        from zipfile import ZipFile
        self.zfile = ZipFile(path, "a")

        self.save_mimetype()
        self.save_container()
        self.save_content(name, author, chapters)
        self.save_toc(name, author, chapters)
        self.save_css()   
    def create_chapters(self, sort_list, content_dict):
        for index in sort_list:
            text = content_dict[index]
            self.save_each_chapter(text[0], text[1], index + 1)
    def create_navpoint(self, index, title) -> str:
        navpoint = '''    <navPoint id="chapter%d" playOrder="%d">\n      <navLabel>\n        <text>%s</text>\n      </navLabel>\n      <content src="Text/chapter%d.html"/>\n    </navPoint>''' % (index, index, title, index)
        return navpoint
    def save_mimetype(self):
        mimetype = '''application/epub+zip'''

        self.zfile.writestr("mimetype", mimetype)
    def save_container(self):
        container = '''<?xml version="1.0" encoding="UTF-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n    <rootfiles>\n        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n   </rootfiles>\n</container>'''
        
        self.zfile.writestr("META-INF\\container.xml", container)
    def save_content(self, name, author, chapters):
        chapter_count = len(chapters) + 1
        metadata_head = '''<?xml version="1.0"  encoding="UTF-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="PrimaryID">\n  <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">\n'''
        metadata_body = '''    <dc:title>%s</dc:title>\n    <dc:creator opf:role="aut">%s</dc:creator>\n    <dc:publisher>Book Scraper</dc:publisher>\n    <dc:description/>\n''' % (name, author)
        metadata_body2 = '''    <dc:coverage/>\n    <dc:source/>\n    <dc:type>[type]</dc:type>\n    <dc:language>zh-CN</dc:language>\n    <meta name="Sigil version" content="0.9.7"/>\n  </metadata>\n'''

        mainifest_head = '''  <manifest>\n    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n    <item id="main.css" href="Style/main.css" media-type="text/css"/>\n'''
        mainifest_body = ['    <item id="chapter%d" href="Text/chapter%d.html" media-type="application/xhtml+xml"/>' % (i, i) for i in range(1, chapter_count)]

        spine_head = '''\n  </manifest>\n  <spine toc="ncx">\n'''
        spine_body = ['    <itemref idref="chapter%d" linear="yes"/>' % i for i in range(1, chapter_count)]

        bottom = '''\n  </spine>\n</package>'''

        page = metadata_head + metadata_body + metadata_body2 + mainifest_head + "\n".join(mainifest_body) + spine_head + "\n".join(spine_body) + bottom

        self.zfile.writestr("OEBPS\\content.opf", page)
    def save_toc(self, name, author, chapters):
        meta_head = '''<?xml version="1.0" encoding="utf-8" ?>\n<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"\n "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd"><ncx version="2005-1" xml:lang="en-US" xmlns="http://www.daisy.org/z3986/2005/ncx/">\n  <head>\n    <!-- The following four metadata items are required for all\n        NCX documents, including those conforming to the relaxed\n        constraints of OPS 2.0 -->    <meta content="51037e82-03ff-11dd-9fbb-0018f369440e" name="dtb:uid"/>\n    <meta content="1" name="dtb:depth"/>\n    <meta content="0" name="dtb:totalPageCount"/>\n    <meta content="0" name="dtb:maxPageNumber"/>\n'''

        doc = '''  </head>\n  <docTitle>\n    <text>%s</text>\n  </docTitle>\n  <docAuthor>\n    <text>%s</text>\n  </docAuthor>\n  <navMap>\n''' % (name, author)

        nav = [self.create_navpoint(index + 1, value) for index, value in enumerate(chapters)]

        bottom = '''\n  </navMap>\n</ncx>'''

        page = meta_head + doc + "\n".join(nav) + bottom

        self.zfile.writestr("OEBPS\\toc.ncx", page)
    def save_each_chapter(self, title, content, index):
        head = '''<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"\n  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n\n<meta content="??????????????????????????????????????????" name="right"/>\n\n'''
        h_title = '''<title>%s</title>\n<link href="../Style/main.css" type="text/css" rel="stylesheet"/>\n</head>\n<body>\n<div>''' % title

        content = str(content).splitlines()
        content = [str(i).strip() for i in content]
        body = '''\n<h3><span class="chaptertitle">%s</span></h3>\n<p>''' % title + "</p>\n<p>".join(content)
        bottom = '''</p>\n</div>\n</body>\n</html>'''

        page = head + h_title + body + bottom

        self.zfile.writestr("OEBPS\\Text\\chapter%d.html" % index, page)
    def save_css(self):
        css = '''h3 {\n    line-height: 130%;\n    text-align: right;\n    font-weight: bold;\n    font-size: 1.4em;\n    font-family: "ht","????????????","??????","MYing Hei S","MYing Hei T","TBGothic","zw",sans-serif;\n	border-right:4px solid #696969;\n	padding-top:2.5em;\n    padding-right:0.5em;\n	padding-bottom:0.1em;\n	margin-top:-2em;\n    margin-bottom: 1.5em;\n    color:#696969;\n}\n\nbody {\n	line-height: 125%;\n	text-align: justify;\n	font-size: 97%;\n}\n\ndiv {\n	line-height: 125%;\n	text-align: justify;\n	\n}\n\np {\n	text-align: justify;\n	text-indent: 2em;\n	font-family:"ht","????????????","??????","MYing Hei S","MYing Hei T","TBGothic","zw",sans-serif;\n    font-size: 1em;\n    margin-top: 0.2em;\n    margin-bottom: 0.2em;\n    line-height: 1.4em;;\n}'''
        
        self.zfile.writestr("OEBPS\\Style\\main.css", css)