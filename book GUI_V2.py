import wx, os, sqlite3
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from book_core_V2 import BookCore
fontsize=10
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

        self.book_address_label=wx.StaticText(self.main_panel, -1, "小说地址", pos=(10,15), size=(60,35))
        self.book_address_label.SetFont(self.font)
        self.book_chapter_label=wx.StaticText(self.main_panel, -1, "目录", pos=(10,55), size=(150,30))
        self.book_chapter_label.SetFont(self.font)
        self.book_info_label=wx.StaticText(self.main_panel, -1, "书名",pos=(245,55), size=(400,30))
        self.book_info_label.SetFont(self.font)

        self.search_book_button=wx.Button(self.main_panel, -1, "搜索小说", pos=(480,10), size=(90,30))
        self.search_book_button.SetFont(self.font)
        self.get_book_button=wx.Button(self.main_panel, -1, "爬取小说", pos=(580,10), size=(90,30))
        self.get_book_button.SetFont(self.font)
        self.get_book_button.Enable(False)
        self.add_shelf_button=wx.Button(self.main_panel, -1, "收藏小说", pos=(680,10), size=(90,30))
        self.add_shelf_button.SetFont(self.font)
        self.add_shelf_button.Enable(False)

        self.book_address_textbox=wx.TextCtrl(self.main_panel, -1, pos=(80,12), size=(380,28))
        self.book_address_textbox.SetFont(self.font)
        self.chapter_content_textbox=wx.TextCtrl(self.main_panel, -1, pos=(245,85), size=(650,400), style=wx.TE_READONLY|wx.TE_MULTILINE)
        self.chapter_content_textbox.SetFont(self.font)

        self.chapter_tree=wx.TreeCtrl(self.main_panel, -1, pos=(10,85), size=(220,400))
        self.chapter_tree.SetFont(self.font)

        self.auto_chapter_chkbox=wx.CheckBox(self.main_panel, -1, "自动添加章节名", pos=(785,12), size=(150,30))
        self.auto_chapter_chkbox.SetValue(True)
        self.auto_chapter_chkbox.SetFont(self.font)
        self.auto_chapter_chkbox.Enable(False)
        self.auto_chapter=True

        self.status_bar=wx.StatusBar(self,-1)
        self.status_bar.SetFieldsCount(3)
        self.status_bar.SetStatusWidths((200,500,250))
        self.status_bar.SetStatusText(" 就绪",0)
        self.status_bar.SetFont(self.font)

        self.SetStatusBar(self.status_bar)

        self.menu_bar=wx.MenuBar()
        self.about_menu=wx.Menu()
        self.tool_menu=wx.Menu()

        self.help_menuitem=wx.MenuItem(self.about_menu,950,"使用帮助(&C)"," 显示使用帮助")
        self.about_menuitem=wx.MenuItem(self.about_menu,960,"关于(&A)"," 显示程序相关信息")

        self.bookshelf_menuitem=wx.MenuItem(self.tool_menu,970,"书架(&B)"," 显示收藏的小说")

        self.menu_bar.Append(self.tool_menu,"工具(&T)")
        self.menu_bar.Append(self.about_menu,"帮助(&H)")

        self.about_menu.Append(self.help_menuitem)
        self.about_menu.Append(self.about_menuitem)
        self.tool_menu.Append(self.bookshelf_menuitem)
        self.tool_menu.AppendSeparator()

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
        menuid=event.GetId()
        if menuid==950:
            self.show_msgbox(self,"使用帮助","使用帮助\n\n搜索小说时，如果没有找到你想要的小说，或小说没有更新，请尝试切换搜索来源。\n点击目录列表框，可预览该章节内容\n爬取小说时，可设置保存文件类型以及保存位置，程序默认使用多线程爬取方式，以提高爬取效率。\n如果遇到问题，请前往github提交issue。",wx.ICON_INFORMATION)
        elif menuid==960:
            self.show_msgbox(self,"关于 小说爬取工具","小说爬取工具 Version 1.30\n\n轻量级的小说爬取工具\nProgrammed by Scott Sloan\n平台：%s\n日期：2021-12-4" % platform.platform(),wx.ICON_INFORMATION)
        elif menuid==970:
            shelf_window.Show()
    def window_onclose(self, event):
        import sys
        sys.exit()
    def show_msgbox(self, parent, caption, message, style):
        dlg=wx.MessageDialog(parent, message, caption, style=style)
        evt=dlg.ShowModal()
        dlg.Destroy()
        return evt
    def Load_search_window(self, event):
        bookname=self.book_address_textbox.GetValue()
        if not bookname.startswith("http") and bookname!="":
            search_window.Show()
            search_window.search_textbox.SetValue(bookname)
            search_window.search_book_EVT(0)
        else:
            search_window.Show()
    def Load_setbook_window(self, event):
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

        self.current_chapter_title=self.chapter_tree.GetItemText(index)

        index2=search_window.chapter_titles.index(self.current_chapter_title)
        self.current_chapter_url=search_window.chapter_urls[index2]

        select_thread=Thread(target=self.select_chapter_thread)
        select_thread.start()
    def select_chapter_thread(self):
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
        style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX)
        wx.Frame.__init__(self, parent, -1, "搜索小说", size=((600,380)), style=style)
        self.search_panel=wx.Panel(self,-1)
        self.Center()

        self.Show_Controls()
        self.Bind_EVT()
        self.init_search_result_listctrl()
    def Show_Controls(self):
        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName="微软雅黑"

        self.search_result_label=wx.StaticText(self.search_panel,-1,"搜索结果",pos=(10,50),size=(100,30))
        self.search_result_label.SetFont(self.font)

        self.search_book_button=wx.Button(self.search_panel,-1,"搜索",pos=(270,10),size=(90,30))
        self.search_book_button.SetFont(self.font)

        self.search_textbox=wx.TextCtrl(self.search_panel,-1,pos=(10,10),size=(250,30))
        self.search_textbox.SetFont(self.font)

        self.source_list=book_core.website_list
        self.source_combobox=wx.ComboBox(self.search_panel,-1,choices=self.source_list,pos=(370,12),size=(200,30),style=wx.CB_READONLY)
        self.source_combobox.SetSelection(0)
        self.source_combobox.SetFont(self.font)

        self.search_result_listctrl=wx.ListCtrl(self.search_panel,-1,pos=(10,80),size=(550,250),style=wx.LC_REPORT)
        self.search_result_listctrl.SetFont(self.font)
    def Bind_EVT(self):
        self.Bind(wx.EVT_CLOSE,self.Window_OnClose)

        self.search_book_button.Bind(wx.EVT_BUTTON,self.search_book_EVT)

        self.search_result_listctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.select_search_result_listctrl)

        self.source_combobox.Bind(wx.EVT_COMBOBOX,self.source_combobox_EVT)
    def Window_OnClose(self, event):
        self.Hide()
    def search_book_EVT(self,event):
        self.bookname=self.search_textbox.GetValue()
        self.type=self.source_combobox.GetSelection()
        if self.bookname=="":
            main_window.show_msgbox(self,"警告","搜索内容不能为空",style=wx.ICON_WARNING)
            return 0
        search_thread=Thread(target=self.search_book_thread)
        search_thread.start()
    def search_book_thread(self):
        self.search_result = book_core.search_book(self.bookname)
        wx.CallAfter(self.set_search_result_listctrl, self.search_result)
    def init_search_result_listctrl(self):
        self.search_result_listctrl.ClearAll()
        self.search_result_listctrl.InsertColumn(0,"序号",width=50)
        self.search_result_listctrl.InsertColumn(1,"书名",width=250)
        self.search_result_listctrl.InsertColumn(2,"作者",width=200)
    def set_search_result_listctrl(self,search_result):
        self.init_search_result_listctrl()
        index=0
        for i in search_result:
            self.search_result_listctrl.InsertItem(index,str(index+1))
            self.search_result_listctrl.SetItem(index,1,i)
            self.search_result_listctrl.SetItem(index,2,search_result[i][1])
            index += 1
        self.search_result_label.SetLabel("搜索结果 (共 %d 条)" % len(search_result))
    def select_search_result_listctrl(self,event):
        index=self.search_result_listctrl.GetFocusedItem()

        name=self.search_result_listctrl.GetItemText(index,1)
        url=self.search_result[name][0]
        author=self.search_result_listctrl.GetItemText(index,2)

        self.Hide()
        wx.CallAfter(self.select_book,name,url,author,self.type)
    def select_book(self,name,url,author,type):
        self.current_name,self.current_url,self.current_author,self.type=name,url,author,type

        intro=book_core.get_book_info(url)
        chapter_info=book_core.get_book_chapters(url)

        self.chapter_titles=list(chapter_info.keys())
        self.chapter_urls=list(chapter_info.values())

        self.set_chapter_tree(name,self.chapter_titles)
        main_window.SetTitle(main_window.w_title + " - " + name)
        main_window.book_address_textbox.SetValue(self.current_url)
        main_window.book_info_label.SetLabel("书名：%s         作者：%s" % (name,author))
        main_window.book_chapter_label.SetLabel("目录 (共 %d 章)" % len(self.chapter_titles))
        main_window.chapter_content_textbox.SetValue(intro)

        main_window.get_book_button.Enable(True)
        main_window.add_shelf_button.Enable(True)
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
        style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX)
        wx.Frame.__init__(self, parent, -1, "爬取小说", size=(460, 230), style=style)
        self.setbook_panel=wx.Panel(self, -1)
        self.Center()

        self.Show_Controls()
        self.Bind_EVT()
        self.file_path_textbox.SetValue(os.getcwd())
    def Show_Controls(self):
        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName="微软雅黑"

        self.file_path_label=wx.StaticText(self.setbook_panel,-1,"保存目录：",pos=(10,12),size=(80,30))
        self.file_path_label.SetFont(self.font)
        self.file_type_label=wx.StaticText(self.setbook_panel,-1,"保存格式：",pos=(10,54),size=(80,30))
        self.file_type_label.SetFont(self.font)
        self.file_name_label=wx.StaticText(self.setbook_panel,-1,"文件名：",pos=(10,96),size=(80,30))
        self.file_name_label.SetFont(self.font)

        self.browse_dir_button=wx.Button(self.setbook_panel,-1,"浏览",pos=(340,10),size=(90,30))
        self.browse_dir_button.SetFont(self.font)
        self.start_get_book_button=wx.Button(self.setbook_panel,-1,"开始爬取小说",pos=(310,140),size=(120,35))
        self.start_get_book_button.SetFont(self.font)

        self.file_path_textbox=wx.TextCtrl(self.setbook_panel,-1,pos=(90,10),size=(230,30))
        self.file_path_textbox.SetFont(self.font)
        self.file_name_textbox=wx.TextCtrl(self.setbook_panel,-1,pos=(90,90),size=(230,30))
        self.file_name_textbox.SetFont(self.font)

        file_type=["*.txt"]
        self.file_type_combobox=wx.ComboBox(self.setbook_panel,-1,choices=file_type,pos=(90,50),size=(100,30),style=wx.CB_READONLY)
        self.file_type_combobox.SetSelection(0)
        self.file_type_combobox.SetFont(self.font)
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

        self.Hide()
        self.get_all_chapters()
    def get_all_chapters(self):
        self.auto_chapter=main_window.auto_chapter_chkbox.GetValue()

        main_window.status_bar.SetStatusText(" 处理中",0)
        
        self.content_dict={}
        self.count=0

        thread = ThreadPoolExecutor(max_workers=10)
        task=[thread.submit(self.get_each_chapter, search_window.chapter_urls.index(i)) for i in search_window.chapter_urls]
    def get_each_chapter(self, index):
        chapter_name = search_window.chapter_titles[index]
        chapter_url = search_window.chapter_urls[index]

        text=book_core.get_book_contents(chapter_url)

        self.content_dict[index]=text
        self.count+=1
        
        wx.CallAfter(self.update_progress, chapter_name, index)

        if self.count==len(search_window.chapter_urls):
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
        main_window.show_msgbox(main_window, "提示", '小说 %s 爬取完成' % search_window.current_name,style=wx.ICON_INFORMATION)
        main_window.status_bar.SetStatusText(" 就绪",0)
        main_window.status_bar.SetStatusText("", 1)
        main_window.status_bar.SetStatusText("", 2)
class ShelfWindow(wx.Frame):
    def __init__(self, parent):
        style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX)
        wx.Frame.__init__(self, parent, -1, "书架", size=(740, 400),style=style)
        self.shelf_panel=wx.Panel(self, -1)
        self.Center()

        self.Show_Controls()
        self.Bind_EVT()
        self.connect_db()
    def Window_OnShow(self, event):
        self.connect_db()
        self.show_books()
    def wWindow_OnClose(self, event):
        self.Hide()
        self.db.close()
    def Bind_EVT(self):
        self.Bind(wx.EVT_SHOW, self.Window_OnShow)
        self.Bind(wx.EVT_CLOSE, self.wWindow_OnClose)

        self.book_shelf_LC.Bind(wx.EVT_LIST_ITEM_SELECTED,self.select_shelf_lc)
        self.select_buttton.Bind(wx.EVT_BUTTON, self.select_book)
        self.remove_buttton.Bind(wx.EVT_BUTTON, self.remove_book)
    def Show_Controls(self):
        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName = "微软雅黑"

        self.select_buttton = wx.Button(self.shelf_panel, -1, "查看选中小说", pos=(460, 320), size=(120, 30))
        self.select_buttton.SetFont(self.font)
        self.select_buttton.Enable(False)
        self.remove_buttton = wx.Button(self.shelf_panel, -1, "删除选中小说", pos=(590, 320), size=(120, 30))
        self.remove_buttton.SetFont(self.font)
        self.remove_buttton.Enable(False)

        self.book_shelf_LC=wx.ListCtrl(self.shelf_panel,-1,pos=((10,10)),size=((700, 300)),style=wx.LC_REPORT)
        self.book_shelf_LC.SetFont(self.font)
    def connect_db(self):
        self.db = sqlite3.connect("book.db",check_same_thread=False)
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT * FROM book_shelf")
        self.result = self.cursor.fetchall()
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
        self.book_shelf_LC.ClearAll()
        self.book_shelf_LC.InsertColumn(0,"序号",width=50)
        self.book_shelf_LC.InsertColumn(1,"书名",width=150)
        self.book_shelf_LC.InsertColumn(2,"作者",width=100)
        self.book_shelf_LC.InsertColumn(3,"来源",width=200)
        self.book_shelf_LC.InsertColumn(4,"地址",width=200)

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
        search_window.select_book(self.name, self.url, self.author, self.type)
    def remove_book(self, event):
        self.book_shelf_LC.DeleteItem(self.index)
        self.cursor.execute("DELETE FROM book WHERE book_name = '%s' AND source = '%s'" % (self.name,self.type))
        self.db.commit()
if __name__=="__main__":
    app=wx.App()
    book_core=BookCore()
    main_window=MainWindow(None)
    search_window=SearchWindow(main_window)
    setbook_window=SetBookWindow(main_window)
    shelf_window=ShelfWindow(main_window)
    main_window.Show()
    app.MainLoop()