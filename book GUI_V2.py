import wx, os, sqlite3
import wx.html2
from concurrent.futures import ThreadPoolExecutor
from book_core_V2 import BookCore, HtmlCore
fontsize = 10
class MainWindow(wx.Frame):
    def __init__(self, parent):
        style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX)
        self.w_title="小说爬取工具"
        wx.Frame.__init__(self, parent, -1, title=self.w_title, size=(925,585), style=style)
        self.main_panel=wx.Panel(self,-1)

        self.Center()
        self.Show_Controls()
        self.Bind_EVT()
    def Show_Controls(self):
        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName="微软雅黑"
        self.main_panel.SetFont(self.font)

        self.book_address_label=wx.StaticText(self.main_panel, -1, "小说地址", pos=(10,15), size=(60,35))
        self.book_chapter_label=wx.StaticText(self.main_panel, -1, "目录", pos=(10,55), size=(150,30))
        self.book_info_label=wx.StaticText(self.main_panel, -1, "书名",pos=(245,55), size=(400,30))
     

        self.search_book_button=wx.Button(self.main_panel, -1, "搜索小说", pos=(470,10), size=(90,30))
        self.get_book_button=wx.Button(self.main_panel, -1, "爬取小说", pos=(570,10), size=(90,30))
        self.get_book_button.Enable(False)
        self.add_shelf_button=wx.Button(self.main_panel, -1, "收藏小说", pos=(670,10), size=(90,30))
        self.add_shelf_button.Enable(False)

        self.book_address_textbox=wx.TextCtrl(self.main_panel, -1, pos=(80, 12), size=(370, 28))
        self.chapter_content_textbox=wx.TextCtrl(self.main_panel, -1, pos=(245,85), size=(650,400), style=wx.TE_READONLY|wx.TE_MULTILINE)

        self.chapter_tree=wx.TreeCtrl(self.main_panel, -1, pos=(10,85), size=(220,400))

        self.auto_chapter_chkbox=wx.CheckBox(self.main_panel, -1, "自动添加章节标题", pos=(775,12), size=(150,30))
        self.auto_chapter_chkbox.SetValue(True)
        self.auto_chapter_chkbox.Enable(False)
        self.auto_chapter=True

        self.status_bar=wx.StatusBar(self,-1)
        self.status_bar.SetFieldsCount(3)
        self.status_bar.SetStatusWidths((200,500,250))
        self.status_bar.SetStatusText(" 就绪",0)

        self.SetStatusBar(self.status_bar)

        self.menu_bar=wx.MenuBar()
        self.about_menu=wx.Menu()
        self.tool_menu=wx.Menu()

        self.help_menuitem=wx.MenuItem(self.about_menu,950,"使用帮助(&C)"," 显示使用帮助")
        self.about_menuitem=wx.MenuItem(self.about_menu,960,"关于(&A)"," 显示程序相关信息")

        self.bookshelf_menuitem=wx.MenuItem(self.tool_menu,970,"书架(&B)"," 显示收藏的小说")
        self.read_mode_menuitem=wx.MenuItem(self.tool_menu,985,"阅读模式(&R)"," 进入阅读模式")
        self.setting_menuitem=wx.MenuItem(self.tool_menu,980,"首选项(&S)"," 编辑首选项")

        self.read_mode_menuitem.Enable(False)

        self.menu_bar.Append(self.tool_menu,"工具(&T)")
        self.menu_bar.Append(self.about_menu,"帮助(&H)")

        self.about_menu.Append(self.help_menuitem)
        self.about_menu.Append(self.about_menuitem)
        self.tool_menu.Append(self.read_mode_menuitem)
        self.tool_menu.Append(self.bookshelf_menuitem)
        self.tool_menu.AppendSeparator()
        self.tool_menu.Append(self.setting_menuitem)
        self.menu_bar.SetFont(self.font)

        self.SetMenuBar(self.menu_bar)
    def Bind_EVT(self):
        self.Bind(wx.EVT_CLOSE, self.window_onclose)

        self.search_book_button.Bind(wx.EVT_BUTTON,self.Load_search_window)
        self.get_book_button.Bind(wx.EVT_BUTTON,self.Load_setbook_window)
        self.add_shelf_button.Bind(wx.EVT_BUTTON,self.Add_to_shelf)

        self.chapter_tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED,self.select_chapter_tree)
        self.auto_chapter_chkbox.Bind(wx.EVT_CHECKBOX,self.auto_chapter_change)

        self.about_menu.Bind(wx.EVT_MENU,self.menu_EVT)
        self.tool_menu.Bind(wx.EVT_MENU,self.menu_EVT)
    def menu_EVT(self,event):
        import platform
        menuid = event.GetId()
        if menuid == 950:
            self.show_msgbox(self, "使用帮助", "使用帮助\n\n搜索小说：如果没有搜索到小说，请尝试切换搜索站点\n预览章节：双击树形框章节标题，可预览该章节内容\n爬取小说：可选择文件保存位置，程序默认使用多线程爬取方式，以提高爬取效率。\n如果遇到问题，请前往github提交issue。",wx.ICON_INFORMATION)
        elif menuid == 960:
            self.show_msgbox(self, "关于 小说爬取工具", "小说爬取工具 Version 1.31\n\n轻量级的小说爬取工具\nProgrammed by Scott Sloan\n平台：%s\n日期：2021-12-11\n项目地址：https://github.com/ScottSloan/Book-Scraper" % platform.platform(),wx.ICON_INFORMATION)
        elif menuid == 970:
            shelf_window.Show()
        elif menuid == 985:
            read_window = ReadWindow(main_window)
            read_window.Show()
        elif menuid == 980:
            set_window = SetWindow(main_window)
            set_window.Show()
    def window_onclose(self, event):
        import sys
        sys.exit()
    def show_msgbox(self, parent, caption, message, style):
        dlg=wx.MessageDialog(parent, message, caption, style=style)
        evt=dlg.ShowModal()
        dlg.Destroy()
        return evt
    def Load_search_window(self, event):
        if setbook_window.isworking:
            self.show_msgbox(self,"警告","请等待爬取进程结束",style=wx.ICON_WARNING)
            return
        bookname = self.book_address_textbox.GetValue()
        if not bookname.startswith("http") and bookname != "":
            search_window.Show()
            search_window.search_textbox.SetValue(bookname)
            search_window.search_book_EVT(0)
        else:
            search_window.Show()
    def Load_setbook_window(self, event):
        if setbook_window.isworking:
            self.show_msgbox(self,"警告","请等待爬取进程结束",style=wx.ICON_WARNING)
            return
        setbook_window.Show()
        setbook_window.file_name_textbox.SetValue(search_window.current_name)
    def Add_to_shelf(self, event):
        info=(search_window.current_name, search_window.current_url, search_window.current_author, search_window.type)
        if shelf_window.add_book(info):
            self.show_msgbox(self, "提示", '小说 "%s" 已收藏' % info[0], style=wx.ICON_INFORMATION)
        else:
            self.show_msgbox(self, "警告", '小说 "%s" 已在书架中' % info[0], style=wx.ICON_WARNING)
    def select_chapter_tree(self, event):
        self.auto_chapter_chkbox.Enable(True)
        index=self.chapter_tree.GetFocusedItem()

        self.current_chapter_title = self.chapter_tree.GetItemText(index)
        if self.current_chapter_title == search_window.current_name:
            print(search_window.intro)
            self.chapter_content_textbox.SetValue(search_window.intro)
            self.auto_chapter_chkbox.Enable(False)
            return

        index2 = search_window.chapter_titles.index(self.current_chapter_title)
        self.current_chapter_url=search_window.chapter_urls[index2]

        threadpool.submit(self.select_chapter)
    def select_chapter(self):
        self.current_text = book_core.get_book_contents(self.current_chapter_url)
        wx.CallAfter(self.set_contents_textbox)
    def set_contents_textbox(self):
        if self.auto_chapter:
            self.chapter_content_textbox.SetValue(self.current_text[0] + "\n\n" + self.current_text[1])
        else:
            self.chapter_content_textbox.SetValue(self.current_text[1])
    def auto_chapter_change(self, event):
        self.auto_chapter=self.auto_chapter_chkbox.GetValue()
        self.set_contents_textbox()
class SearchWindow(wx.Frame):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE  & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX) | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, -1, "搜索小说", size=(600,380), style=style)
        self.search_panel=wx.Panel(self,-1)
        self.Center()

        self.Show_Controls()
        self.Bind_EVT()
        self.init_search_result_listctrl()
    def Show_Controls(self):
        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName="微软雅黑"
        self.search_panel.SetFont(self.font)

        self.search_result_label=wx.StaticText(self.search_panel,-1,"搜索结果",pos=(10,50),size=(100,30))
        self.search_book_button=wx.Button(self.search_panel,-1,"搜索",pos=(270,10),size=(90,30))
        self.search_textbox=wx.TextCtrl(self.search_panel,-1,pos=(10,10),size=(250,30))

        self.source_list=book_core.website_list
        self.source_combobox=wx.ComboBox(self.search_panel,-1,choices=self.source_list,pos=(370,12),size=(200,30),style=wx.CB_READONLY)
        self.source_combobox.SetSelection(0)

        self.search_result_listctrl=wx.ListCtrl(self.search_panel,-1,pos=(10,80),size=(550,250),style=wx.LC_REPORT)
    def Bind_EVT(self):
        self.Bind(wx.EVT_CLOSE,self.Window_OnClose)
        self.search_book_button.Bind(wx.EVT_BUTTON, self.search_book_EVT)
        self.search_result_listctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.select_search_result_listctrl)
        self.source_combobox.Bind(wx.EVT_COMBOBOX,self.source_combobox_EVT)
    def Window_OnClose(self, event):
        self.Hide()
    def search_book_EVT(self,event):
        self.bookname=self.search_textbox.GetValue()
        self.type=self.source_combobox.GetSelection()
        if self.bookname == "":
            main_window.show_msgbox(self,"警告","搜索内容不能为空",style=wx.ICON_WARNING)
            return 0
        processing_window.Show()
        threadpool.submit(self.search_book)
    def search_book(self):
        self.search_result = book_core.search_book(self.bookname)
        wx.CallAfter(self.set_search_result_listctrl)
    def init_search_result_listctrl(self):
        self.search_result_listctrl.ClearAll()
        self.search_result_listctrl.InsertColumn(0,"序号",width=50)
        self.search_result_listctrl.InsertColumn(1,"书名",width=250)
        self.search_result_listctrl.InsertColumn(2,"作者",width=200)
    def set_search_result_listctrl(self):
        self.init_search_result_listctrl()
        index = 0
        for i in self.search_result:
            self.search_result_listctrl.InsertItem(index,str(index+1))
            self.search_result_listctrl.SetItem(index,1,i)
            self.search_result_listctrl.SetItem(index,2,self.search_result[i][1])
            index += 1
        self.search_result_label.SetLabel("搜索结果 (共 %d 条)" % len(self.search_result))
        processing_window.Hide()
    def select_search_result_listctrl(self,event):
        index=self.search_result_listctrl.GetFocusedItem()

        name=self.search_result_listctrl.GetItemText(index,1)
        url=self.search_result[name][0]
        author=self.search_result_listctrl.GetItemText(index,2)

        self.Hide()
        wx.CallAfter(self.select_book,name,url,author,self.type)
    def select_book(self,name,url,author,type):
        self.current_name,self.current_url,self.current_author,self.type=name,url,author,type
        book_core.change_websites(self.type)
        main_window.SetTitle(main_window.w_title + " - " + name)
        main_window.book_address_textbox.SetValue(self.current_url)
        main_window.book_info_label.SetLabel("书名：%s         作者：%s" % (name,author))

        self.intro=book_core.get_book_info(url)
        chapter_info=book_core.get_book_chapters(url)

        self.chapter_titles=list(chapter_info.keys())
        self.chapter_urls=list(chapter_info.values())

        self.set_chapter_tree(name,self.chapter_titles)
        main_window.book_chapter_label.SetLabel("目录 (共 %d 章)" % len(self.chapter_titles))
        main_window.chapter_content_textbox.SetValue(self.intro)

        main_window.get_book_button.Enable(True)
        main_window.add_shelf_button.Enable(True)
        main_window.read_mode_menuitem.Enable(True)
        main_window.auto_chapter_chkbox.Enable(False)
    def set_chapter_tree(self,name,chapter_titles):
        main_window.chapter_tree.DeleteAllItems()
        root=main_window.chapter_tree.AddRoot(name)
        for i in chapter_titles:
            main_window.chapter_tree.AppendItem(root,i)
        main_window.chapter_tree.ExpandAll()
    def source_combobox_EVT(self,event):
        self.type = self.source_combobox.GetSelection()
        book_core.change_websites(self.type)
        self.init_search_result_listctrl()
        self.search_result_label.SetLabel("搜索结果")
class SetBookWindow(wx.Frame):
    def __init__(self, parent):
        style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX) | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, -1, "爬取小说", size=(460, 230), style=style)
        self.setbook_panel=wx.Panel(self, -1)
        self.Center()

        self.Show_Controls()
        self.Bind_EVT()
        self.file_path_textbox.SetValue(os.getcwd())
        self.isworking = False
    def Show_Controls(self):
        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName="微软雅黑"
        self.setbook_panel.SetFont(self.font)

        self.file_path_label=wx.StaticText(self.setbook_panel,-1,"保存目录：",pos=(10,12),size=(80,30))
        self.file_type_label=wx.StaticText(self.setbook_panel,-1,"保存格式：",pos=(10,54),size=(80,30))
        self.file_name_label=wx.StaticText(self.setbook_panel,-1,"文件名：",pos=(10,96),size=(80,30))

        self.browse_dir_button=wx.Button(self.setbook_panel,-1,"浏览",pos=(340,10),size=(90,30))
        self.start_get_book_button=wx.Button(self.setbook_panel,-1,"开始爬取小说",pos=(310,140),size=(120,35))

        self.file_path_textbox=wx.TextCtrl(self.setbook_panel,-1,pos=(90,10),size=(230,30))
        self.file_name_textbox=wx.TextCtrl(self.setbook_panel,-1,pos=(90,90),size=(230,30))

        file_type=["*.txt"]
        self.file_type_combobox=wx.ComboBox(self.setbook_panel,-1,choices=file_type,pos=(90,50),size=(100,30),style=wx.CB_READONLY)
        self.file_type_combobox.SetSelection(0)
    def window_onclose(self, event):
        self.Hide()
    def Bind_EVT(self):
        self.Bind(wx.EVT_CLOSE,self.window_onclose)

        self.start_get_book_button.Bind(wx.EVT_BUTTON,self.start_get_book)
        self.browse_dir_button.Bind(wx.EVT_BUTTON,self.browser_dir)
    def browser_dir(self,event):
        dlg=wx.DirDialog(self,"选择保存目录")
        if dlg.ShowModal()==wx.ID_OK:
            save_path=dlg.GetPath()
            self.file_path_textbox.SetValue(save_path)
        dlg.Destroy()
    def start_get_book(self, event):
        self.file_name = self.file_name_textbox.GetValue()
        self.file_path = self.file_path_textbox.GetValue()
        self.full_path = os.path.join(self.file_path, self.file_name + ".txt")
        self.isworking = True

        self.Hide()
        self.get_all_chapters()
    def get_all_chapters(self):
        self.auto_chapter = main_window.auto_chapter_chkbox.GetValue()

        main_window.status_bar.SetStatusText(" 处理中",0)
        
        self.content_dict = {}
        self.count = 0

        task = [threadpool.submit(self.get_each_chapter, search_window.chapter_urls.index(i)) for i in search_window.chapter_urls]
    def get_each_chapter(self, index):
        chapter_name = search_window.chapter_titles[index]
        chapter_url = search_window.chapter_urls[index]

        text=book_core.get_book_contents(chapter_url)

        self.content_dict[index] = text
        self.count += 1
        
        wx.CallAfter(self.update_progress, chapter_name, index)

        if self.count == len(search_window.chapter_urls):
            self.process_all_chapters()
    def update_progress(self, chapter_name, index):
        progress = (self.count/len(search_window.chapter_urls)) * 100
        tip = "[进度]：%.2f %% 正在爬取：%s" % (progress, chapter_name)
        main_window.status_bar.SetStatusText(tip,1)
        main_window.status_bar.SetStatusText("正在处理线程：%d" % index,2)
    def process_all_chapters(self):
        sort_list = list(self.content_dict.keys())
        sort_list.sort(reverse = False)

        file=open(self.full_path, "a", encoding = "utf-8")
        for index in sort_list:
            text = self.content_dict[index]
            if self.auto_chapter:
                file.write(text[0] + "\n\n" + text[1] + "\n\n")
            else:
                file.write(text[1] + "\n\n")
        file.close()
        wx.CallAfter(self.process_finish)
    def process_finish(self):
        main_window.show_msgbox(main_window, "提示", '小说 "%s" 爬取完成' % search_window.current_name,style=wx.ICON_INFORMATION)
        main_window.status_bar.SetStatusText(" 就绪",0)
        main_window.status_bar.SetStatusText("", 1)
        main_window.status_bar.SetStatusText("", 2)
        self.content_dict.clear()
        self.isworking = False
class ShelfWindow(wx.Frame):
    def __init__(self, parent):
        style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX) | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, -1, "书架", size=(740, 400),style=style)
        self.shelf_panel=wx.Panel(self, -1)
        self.Center()

        self.Show_Controls()
        self.Bind_EVT()
        self.connect_db()
    def Window_OnShow(self, event):
        self.connect_db()
        self.show_books()
    def Window_OnClose(self, event):
        self.Hide()
        self.db.close()
    def Bind_EVT(self):
        self.Bind(wx.EVT_SHOW, self.Window_OnShow)
        self.Bind(wx.EVT_CLOSE, self.Window_OnClose)

        self.book_shelf_LC.Bind(wx.EVT_LIST_ITEM_SELECTED,self.select_shelf_lc)
        self.select_buttton.Bind(wx.EVT_BUTTON, self.select_book)
        self.remove_buttton.Bind(wx.EVT_BUTTON, self.remove_book)
        self.remove_all_button.Bind(wx.EVT_BUTTON, self.drop_table)
    def Show_Controls(self):
        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName = "微软雅黑"
        self.shelf_panel.SetFont(self.font)

        self.select_buttton = wx.Button(self.shelf_panel, -1, "查看选中小说", pos=(460, 320), size=(120, 30))
        self.select_buttton.Enable(False)
        self.remove_buttton = wx.Button(self.shelf_panel, -1, "删除选中小说", pos=(590, 320), size=(120, 30))
        self.remove_buttton.Enable(False)
        self.remove_all_button=wx.Button(self.shelf_panel,-1,"删除全部小说",pos=(10,320),size=(120,30))

        self.book_shelf_LC=wx.ListCtrl(self.shelf_panel,-1,pos=((10,10)),size=((700, 300)),style=wx.LC_REPORT)
    def connect_db(self):
        self.db = sqlite3.connect("book.db",check_same_thread=False)
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT * FROM book_shelf")
        self.result = self.cursor.fetchall()
    def init_listctrl(self):
        self.book_shelf_LC.ClearAll()
        self.book_shelf_LC.InsertColumn(0,"序号",width=50)
        self.book_shelf_LC.InsertColumn(1,"书名",width=150)
        self.book_shelf_LC.InsertColumn(2,"作者",width=100)
        self.book_shelf_LC.InsertColumn(3,"来源",width=200)
        self.book_shelf_LC.InsertColumn(4,"地址",width=200)
    def drop_table(self, event):
        self.cursor.execute('''DROP TABLE "book_shelf"''')
        self.cursor.execute('''CREATE TABLE "book_shelf" ("id"	INTEGER,"name"	TEXT,"url"	TEXT,"author"	TEXT,"type"	INTEGER,PRIMARY KEY("id" AUTOINCREMENT))''')
        self.db.commit()
        self.init_listctrl()
    def add_book(self, info):
        self.connect_db()
        if not self.check_same(info[0], info[3]):
            return False
        self.cursor.execute("INSERT INTO book_shelf (name,url,author,type) VALUES('%s','%s','%s',%d)" % info)
        self.db.commit()
        return True
    def check_same(self, name, type):
        self.cursor.execute("SELECT name FROM book_shelf WHERE name='%s' AND type=%d" % (name, type))
        result = self.cursor.fetchone()
        if result != None:
            return False
        else:
            return True
    def show_books(self):
        self.init_listctrl()
        for index,value in enumerate(self.result):
            self.book_shelf_LC.InsertItem(index,str(value[0]))
            self.book_shelf_LC.SetItem(index,1,value[1])
            self.book_shelf_LC.SetItem(index,2,value[3])
            self.book_shelf_LC.SetItem(index,3,search_window.source_list[value[4]])
            self.book_shelf_LC.SetItem(index,4,value[2])
    def select_shelf_lc(self, event):
        self.index=self.book_shelf_LC.GetFocusedItem()
        self.name=self.book_shelf_LC.GetItemText(self.index,1)
        self.author=self.book_shelf_LC.GetItemText(self.index,2)
        self.url=self.book_shelf_LC.GetItemText(self.index,4)
        self.type=search_window.source_list.index(self.book_shelf_LC.GetItemText(self.index,3))

        self.select_buttton.Enable(True)
        self.remove_buttton.Enable(True)
    def select_book(self, event):
        self.Hide()
        processing_window.Show()
        wx.CallAfter(search_window.select_book, self.name, self.url, self.author, self.type)
    def remove_book(self, event):
        self.book_shelf_LC.DeleteItem(self.index)
        self.cursor.execute("DELETE FROM book WHERE book_name = '%s' AND source = '%s'" % (self.name,self.type))
        self.db.commit()
class ReadWindow(wx.Frame):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, -1, "Read", size=(800, 500), style=style)
        self.browser_panel = wx.Panel(self, -1)
        self.Center()

        self.show_controls()
        self.Bind_EVT()
        self.show_page()
    def show_controls(self):
        self.browser = wx.html2.WebView.New(self.browser_panel, -1)
        hbox = wx.BoxSizer()
        hbox.Add(self.browser, 1, wx.EXPAND | wx.ALL)
        self.browser_panel.SetSizer(hbox)

        self.menu_bar = wx.MenuBar()
        self.navi_menu = wx.Menu()
        self.set_menu = wx.Menu()
        self.chapter_menuitem = wx.MenuItem(self.navi_menu, 100, "目录(&C)")
        self.prevous_menuitem = wx.MenuItem(self.navi_menu, 110, "上一章(&P)")
        self.next_menuitem = wx.MenuItem(self.navi_menu, 120, "下一章(&N)")
        self.font_menuitem = wx.MenuItem(self.set_menu, 130, "字体设置(&F)")


        self.menu_bar.Append(self.navi_menu,"导航(&N)")
        self.menu_bar.Append(self.set_menu, "设置(&S)")
        self.navi_menu.Append(self.chapter_menuitem)
        self.navi_menu.Append(self.prevous_menuitem)
        self.navi_menu.Append(self.next_menuitem)
        self.set_menu.Append(self.font_menuitem)

        self.SetMenuBar(self.menu_bar)
    def Bind_EVT(self):
        self.browser.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, self.title_changed)
    def title_changed(self, event):
        self.SetTitle(self.browser.GetCurrentTitle())
    def show_page(self):
        self.bookname = search_window.current_name
        self.base_path = os.path.join(os.getcwd(), "book_cache", self.bookname)

        if not os.path.exists(self.base_path):
            self.get_book_cache()
        else:
            self.open_path = os.path.join(self.base_path, "contents.html")
            self.browser.LoadURL(self.open_path)
    def get_book_cache(self):
        os.makedirs(self.base_path)
        processing_window.Show()
        html_core.save_css(os.path.join(self.base_path, "style.css"))
        self.process_chapter()
        self.count = 0

        task = [threadpool.submit(self.process_each_chapter, search_window.chapter_urls.index(i)) for i in search_window.chapter_urls]
    def process_each_chapter(self, index):
        self.count += 1
        chapter_name = search_window.chapter_titles[index]
        chapter_url = search_window.chapter_urls[index]

        isFirst = True if self.count == 1 else False
        isLast = True if self.count == len(search_window.chapter_urls) else False

        text = book_core.get_book_contents(chapter_url)
        html_page = html_core.process_contents(chapter_name, text, index, isFirst, isLast)

        file_path = os.path.join(self.base_path, "%d.html" % index)
        with open (file_path, "w", encoding = "utf-8") as f:
            f.write(html_page)

        if isLast:
            processing_window.Hide()
    def process_chapter(self):
        path = os.path.join(self.base_path, "contents.html")
        with open (path, "w", encoding = "utf-8") as f:
            f.write(html_core.process_chapter(self.bookname, search_window.chapter_titles))
        self.browser.LoadURL(path)
class SetWindow(wx.Frame):
    def __init__(self, parent):
        style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX) | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, -1, title = "首选项", size = (400, 380), style = style)
        self.set_panel = wx.Panel(self, -1)
        self.Center()

        self.show_controls()
        self.Bind_EVT()
        book_core.read_config()
    def show_controls(self):
        self.font = wx.Font()
        self.font.PointSize = fontsize
        self.font.FaceName = "微软雅黑"

        self.ip_box = wx.StaticBox(self.set_panel, -1, "代理 IP 设置", size=(360,170), pos = (10,10))
        self.ip_box.SetFont(self.font)
        self.disable_ip_rad = wx.RadioButton(self.ip_box, -1, "禁用代理 IP", pos=(10, 25))
        self.use_ippool_rad = wx.RadioButton(self.ip_box, -1, "使用代理 IP 池", pos=(120,25))
        self.use_ippool_rad.SetValue(True)
        self.cust_ip_rad = wx.RadioButton(self.ip_box, -1, "自定义代理 IP ", pos=(245,25))
        self.ip_label = wx.StaticText(self.ip_box, -1, "代理IP数：10", pos=(10, 55))
        self.ip_slider = wx.Slider(self.ip_box, -1, 10, 10, 100, size =(320, 50), pos = (10,85), style = wx.SL_AUTOTICKS | wx.SL_MIN_MAX_LABELS | wx.SL_HORIZONTAL)
        
        self.ip_slider.SetTickFreq(10)
        self.ip_port_label = wx.StaticText(self.ip_box, -1, "代理 IP 地址：", pos=(10,133))
        self.ip_port_tc = wx.TextCtrl(self.ip_box, -1, size=(180,30),pos=(100,130))
        self.change_ip(0)
        self.use_ippool(0)

        self.thread_box = wx.StaticBox(self.set_panel, -1, "线程池设置", size=(360,100), pos = (10,190))
        self.thread_box.SetFont(self.font)
        self.thread_label = wx.StaticText(self.thread_box, -1, "线程数：10", pos=(10, 25))
        self.thread_slider = wx.Slider(self.thread_box, -1, 10, 1, 32, size =(320, 50), pos = (10,50), style = wx.SL_AUTOTICKS | wx.SL_MIN_MAX_LABELS)
        self.change_thread(0)

        self.ok_button = wx.Button(self.set_panel, -1, "确定", size = (90,30), pos=(180,300))
        self.ok_button.SetFont(self.font)
        self.cancel_button = wx.Button(self.set_panel, -1, "取消",size = (90,30), pos=(280,300))
        self.cancel_button.SetFont(self.font)
    def Bind_EVT(self):
        self.Bind(wx.EVT_SHOW, self.window_onshow)
        self.ip_slider.Bind(wx.EVT_SLIDER, self.change_ip)
        self.thread_slider.Bind(wx.EVT_SLIDER, self.change_thread)

        self.disable_ip_rad.Bind(wx.EVT_RADIOBUTTON, self.disable_ip)
        self.use_ippool_rad.Bind(wx.EVT_RADIOBUTTON, self.use_ippool)
        self.cust_ip_rad.Bind(wx.EVT_RADIOBUTTON, self.cust_ip)

        self.ok_button.Bind(wx.EVT_BUTTON, self.save_change)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.close_window)
    def close_window(self, event):
        self.Close()
    def window_onshow(self, event):
        self.ip_type = book_core.ip_type
        if self.ip_type == 0:
            self.disable_ip(0)
            self.disable_ip_rad.SetValue(True)
        elif self.ip_type == 1:
            self.use_ippool(0)
            self.use_ippool_rad.SetValue(True)
        elif self.ip_type == 2:
            self.cust_ip(0)
            self.cust_ip_rad.SetValue(True)
        self.ip_value = book_core.ip_amounts
        self.ip_slider.SetValue(self.ip_value)
        self.change_ip(0)
        self.ip_port_tc.SetValue(book_core.ip_addres)

        self.thread_value = book_core.thread_amounts
        self.thread_slider.SetValue(self.thread_value)
        self.change_thread(0)
    def disable_ip(self, event):
        self.ip_type = 0
        self.ip_label.Enable(False)
        self.ip_slider.Enable(False)
        self.ip_port_label.Enable(False)
        self.ip_port_tc.Enable(False)
    def use_ippool(self, event):
        self.ip_type = 1
        self.ip_label.Enable(True)
        self.ip_slider.Enable(True)
        self.ip_port_label.Enable(False)
        self.ip_port_tc.Enable(False)
    def cust_ip(self, event):
        self.ip_type = 2
        self.ip_label.Enable(False)
        self.ip_slider.Enable(False)
        self.ip_port_label.Enable(True)
        self.ip_port_tc.Enable(True)
    def change_ip(self, event):
        self.ip_value = round(self.ip_slider.GetValue() / 10) * 10
        self.ip_slider.SetValue(self.ip_value)
        self.ip_label.SetLabel("代理 IP 数：%d" % self.ip_value)
    def change_thread(self, event):
        self.thread_value = self.thread_slider.GetValue()
        self.thread_label.SetLabel("线程数：%d" % self.thread_value)
    def save_change(self, event):
        book_core.save_config(self.ip_type, self.ip_value, self.ip_port_tc.GetValue(), self.thread_value)
        self.Close()
class ProcessingWindow(wx.Frame):
    def __init__(self, parent):
        style=wx.CAPTION | wx.STAY_ON_TOP
        wx.Frame.__init__(self, parent, -1, "处理中", size=(200,80), style=style)
        self.processing_panel=wx.Panel(self, -1)
        self.Center()

        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName="微软雅黑"

        self.processing_label=wx.StaticText(self.processing_panel,-1,"正在处理中，请稍候",pos=(10,10),size=(120,30))
        self.processing_label.SetFont(self.font)
if __name__ == "__main__":
    app = wx.App()
    book_core = BookCore()
    threadpool = ThreadPoolExecutor(max_workers = book_core.thread_amounts)
    html_core = HtmlCore()
    main_window = MainWindow(None)
    search_window = SearchWindow(main_window)
    setbook_window = SetBookWindow(main_window)
    shelf_window = ShelfWindow(main_window)
    processing_window = ProcessingWindow(None)
    main_window.Show()
    app.MainLoop()