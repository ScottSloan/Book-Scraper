import wx
import wx.html2
import requests
import sys
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from book_core_V2 import *
fontsize = 10
class MainWindow(wx.Frame):
    def __init__(self, parent):
        self.w_title="小说爬取工具"
        wx.Frame.__init__(self, parent, -1, title = self.w_title)
        self.SetSize(self.FromDIP((925, 585)))
        self.main_panel = wx.Panel(self, -1)
        self.scale_factor = self.GetDPIScaleFactor()

        self.Center()
        self.Show_Controls()
        self.Bind_EVT()
    def Show_Controls(self):
        self.font = wx.Font()
        self.font.PointSize = fontsize
        self.font.FaceName = "微软雅黑"
        self.main_panel.SetFont(self.font)

        self.book_address_label = wx.StaticText(self.main_panel, -1, "小说地址")
        self.book_address_textbox = wx.TextCtrl(self.main_panel, -1)

        self.search_book_button = wx.Button(self.main_panel, -1, "搜索小说", size = self.FromDIP((90, 30)))
        self.get_book_button = wx.Button(self.main_panel, -1, "爬取小说", size = self.FromDIP((90, 30)))
        self.get_book_button.Enable(False)
        self.add_shelf_button = wx.Button(self.main_panel, -1, "收藏小说", size = self.FromDIP((90, 30)))
        self.add_shelf_button.Enable(False)

        self.auto_chapter_chkbox = wx.CheckBox(self.main_panel, -1, "自动添加章节标题")
        self.auto_chapter_chkbox.SetValue(True)
        self.auto_chapter_chkbox.Enable(False)
        self.auto_chapter = True

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.book_address_label, 0, wx.ALL | wx.ALIGN_CENTRE, 10)
        hbox1.Add(self.book_address_textbox, 1, wx.ALL | wx.EXPAND, 5)
        hbox1.Add(self.search_book_button, 0, wx.ALL, 5)
        hbox1.Add(self.get_book_button, 0, wx.ALL, 5)
        hbox1.Add(self.add_shelf_button, 0, wx.ALL, 5)
        hbox1.Add(self.auto_chapter_chkbox, 0, wx.ALL | wx.ALIGN_CENTRE, 5)

        self.book_chapter_label = wx.StaticText(self.main_panel, -1, "目录")
        self.book_info_label = wx.StaticText(self.main_panel, -1, "书名")

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.book_chapter_label, 1, wx.ALL, 10)
        hbox2.Add(self.book_info_label, 3, wx.ALL, 10)

        self.chapter_content_textbox = wx.TextCtrl(self.main_panel, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.chapter_tree = wx.TreeCtrl(self.main_panel, -1)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.chapter_tree, 1, wx.ALL & (~wx.TOP) | wx.EXPAND, 10)
        hbox3.Add(self.chapter_content_textbox, 3, wx.ALL & (~wx.TOP) | wx.EXPAND, 10)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox1, 0, wx.EXPAND, 0)
        vbox.Add(hbox2, 0, wx.EXPAND, 0)
        vbox.Add(hbox3, 1, wx.EXPAND, 0)

        self.main_panel.SetSizer(vbox)

        self.status_bar = wx.StatusBar(self, -1)
        self.status_bar.SetFieldsCount(3)
        self.status_bar.SetStatusWidths((200 * self.scale_factor, 500 * self.scale_factor, 250 * self.scale_factor))
        self.status_bar.SetStatusText(" 就绪",0)

        self.SetStatusBar(self.status_bar)

        self.menu_bar = wx.MenuBar()
        self.about_menu = wx.Menu()
        self.tool_menu = wx.Menu()

        self.url_menuitem = wx.MenuItem(self.about_menu, 990, "项目地址(&U)", " 访问项目地址")
        self.check_menuitem = wx.MenuItem(self.about_menu, 810, "检查更新(&P)", " 检查程序更新")
        self.help_menuitem = wx.MenuItem(self.about_menu, 950, "使用帮助(&C)", " 显示使用帮助")
        self.about_menuitem = wx.MenuItem(self.about_menu, 960, "关于(&A)", " 显示程序相关信息")

        self.bookshelf_menuitem = wx.MenuItem(self.tool_menu, 970, "书架(&B)", " 显示收藏的小说")
        self.read_mode_menuitem = wx.MenuItem(self.tool_menu, 985, "阅读模式(&R)", " 进入阅读模式")
        self.setting_menuitem = wx.MenuItem(self.tool_menu, 980, "首选项(&S)", " 编辑首选项")

        self.read_mode_menuitem.Enable(False)

        self.menu_bar.Append(self.tool_menu,"工具(&T)")
        self.menu_bar.Append(self.about_menu,"帮助(&H)")

        self.about_menu.Append(self.url_menuitem)
        self.about_menu.Append(self.check_menuitem)
        self.about_menu.AppendSeparator()
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

        self.book_info_label.Bind(wx.EVT_RIGHT_DOWN, self.info_popup_menu)
        self.chapter_tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.tree_popup_menu)
    def menu_EVT(self, event):
        import platform
        menuid = event.GetId()
        if menuid == 950:
            self.show_msgbox(self, "使用帮助", "使用帮助\n\n搜索小说：如果没有搜索到小说，请尝试切换搜索站点\n预览章节：双击树形框章节标题，可预览该章节内容\n爬取小说：可选择文件保存位置，程序默认使用多线程爬取方式，以提高爬取效率。\n如果遇到问题，请前往github提交issue。",wx.ICON_INFORMATION)
        elif menuid == 960:
            self.show_msgbox(self, "关于 小说爬取工具", "小说爬取工具 Version 1.32\n\n轻量级的小说爬取工具\nProgrammed by Scott Sloan\n平台：%s\n日期：2022-1-14" % platform.platform(),wx.ICON_INFORMATION)
        elif menuid == 970:
            shelf_window.ShowWindowModal()
        elif menuid == 985:
            if setbook_window.isworking:
                self.show_msgbox(self,"警告","请等待爬取进程结束",style=wx.ICON_WARNING)
                return
            read_window = ReadWindow(self)
            read_window.Show()
        elif menuid == 980:
            if setbook_window.isworking:
                self.show_msgbox(self,"警告","请等待爬取进程结束",style=wx.ICON_WARNING)
                return
            set_window = SetWindow(self)
            set_window.ShowWindowModal()
        elif menuid == 990:
            import webbrowser
            webbrowser.open("https://github.com/ScottSloan/Book-Scraper")
        elif menuid == 810:
            pass
    def info_popup_menu(self, event):
        info_menu = wx.Menu()

        copy_menuitem = wx.MenuItem(info_menu, 200, "复制信息(&C)")
        info_menu.Append(copy_menuitem)
        
        self.Bind(wx.EVT_MENU, self.popup_menu_EVT)
        self.PopupMenu(info_menu)
    def tree_popup_menu(self, event):
        tree_menu = wx.Menu()

        preview_menuitem = wx.MenuItem(tree_menu, 300, "预览章节内容(&V)")
        edit_menuitem = wx.MenuItem(tree_menu, 310, "编辑\\导出章节信息(&E)")
        tree_menu.Append(preview_menuitem)
        tree_menu.AppendSeparator()
        tree_menu.Append(edit_menuitem)

        self.tree_menu_event = event
        self.Bind(wx.EVT_MENU, self.popup_menu_EVT)
        self.PopupMenu(tree_menu)
    def popup_menu_EVT(self, event):
        menuid = event.GetId()
        if menuid == 200:
            cb = wx.Clipboard()
            data = wx.TextDataObject()
            data.SetText((self.book_info_label.GetLabel()))
            cb.Open()
            cb.SetData(data)
            cb.Flush()
        if menuid == 300:
            self.select_chapter_tree(self.tree_menu_event)
    def window_onclose(self, event):
        if setbook_window.isworking:
            id = self.show_msgbox(self, "警告：", "爬取进程仍在进行，是否确认退出？", style = wx.ICON_WARNING | wx.YES_NO)
            if id == wx.ID_YES:
                for i in setbook_window.task:
                    i.cancel()
                sys.exit(0)
            else:
                return
        else:
            sys.exit(0)
    def show_msgbox(self, parent, caption, message, style):
        dlg=wx.MessageDialog(parent, message, caption, style=style)
        evt=dlg.ShowModal()
        dlg.Destroy()
        return evt
    def Load_search_window(self, event):
        if setbook_window.isworking:
            self.show_msgbox(self,"警告","请等待爬取进程结束",style=wx.ICON_WARNING)
            return
        search_window.ShowWindowModal()
    def Load_setbook_window(self, event):
        if setbook_window.isworking:
            self.show_msgbox(self,"警告","请等待爬取进程结束",style=wx.ICON_WARNING)
            return
        setbook_window.ShowWindowModal()
        setbook_window.file_name_textbox.SetValue(search_window.current_name)
    def Add_to_shelf(self, event):
        info=(search_window.current_name, search_window.current_url, search_window.current_author, search_window.type)
        if shelf_window.add_book(info):
            self.show_msgbox(self, "提示", '小说 "%s" 已收藏' % info[0], style=wx.ICON_INFORMATION)
        else:
            self.show_msgbox(self, "警告", '小说 "%s" 已在书架中' % info[0], style=wx.ICON_WARNING)
    def select_chapter_tree(self, event):
        self.auto_chapter_chkbox.Enable(True)
        index = event.GetItem()

        self.current_chapter_title = self.chapter_tree.GetItemText(index)
        if self.current_chapter_title == search_window.current_name:
            self.chapter_content_textbox.SetValue(search_window.intro)
            self.auto_chapter_chkbox.Enable(False)
            return

        index2 = search_window.chapter_titles.index(self.current_chapter_title)
        self.current_chapter_url = search_window.chapter_urls[index2]

        wx.CallAfter(processing_window.Show)
        wx.CallLater(1, self.select_chapter)
    def select_chapter(self):
        self.current_text = book_core.get_book_contents(self.current_chapter_url)
        self.set_contents_textbox()
    def set_contents_textbox(self):
        if self.auto_chapter:
            self.chapter_content_textbox.SetValue(self.current_text[0] + "\n\n" + self.current_text[1])
        else:
            self.chapter_content_textbox.SetValue(self.current_text[1])
        processing_window.Hide()
    def auto_chapter_change(self, event):
        self.auto_chapter=self.auto_chapter_chkbox.GetValue()
        self.set_contents_textbox()
class SearchWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "搜索小说")
        self.SetSize(self.FromDIP((600, 380)))
        self.search_panel = wx.Panel(self, -1)
        self.Center()

        self.Show_Controls()
        self.Bind_EVT()
        self.init_search_result_listctrl()
    def Show_Controls(self):
        self.font=wx.Font()
        self.font.PointSize=fontsize
        self.font.FaceName="微软雅黑"
        self.search_panel.SetFont(self.font)

        self.search_textbox = wx.TextCtrl(self.search_panel, -1)
        self.search_book_button = wx.Button(self.search_panel, -1, "搜索", size = self.FromDIP((90, 30)))
        self.source_list = book_core.website_list
        self.source_combobox = wx.ComboBox(self.search_panel, -1, choices = self.source_list, style = wx.CB_READONLY)
        self.source_combobox.SetSelection(0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.search_textbox, 1, wx.ALL | wx.EXPAND, 10)
        hbox.Add(self.search_book_button, 0 ,wx.TOP | wx.BOTTOM, 10)
        hbox.Add(self.source_combobox, 0, wx.ALL | wx.ALIGN_CENTRE, 10)

        self.search_result_label = wx.StaticText(self.search_panel, -1, "搜索结果")

        self.search_result_listctrl = wx.ListCtrl(self.search_panel, -1, style = wx.LC_REPORT)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, 0, wx.EXPAND, 0)
        vbox.Add(self.search_result_label, 0, wx.LEFT | wx.RIGHT, 10)
        vbox.Add(self.search_result_listctrl, 1, wx.ALL | wx.EXPAND, 10)

        self.search_panel.SetSizer(vbox)
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
        wx.CallAfter(processing_window.Show)
        threadpool.submit(self.search_book)
    def search_book(self):
        self.search_result = book_core.search_book(self.bookname)
        if book_core.isFailed:
            main_window.show_msgbox(processing_window, "错误", "尝试从站点获取信息失败\n\n原因：%s" % book_core.error_info, style = wx.ICON_ERROR)
            processing_window.Hide()
            return
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
        processing_window.Show()
        wx.CallLater(1, self.select_book, name, url, author, self.type)
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
        processing_window.Hide()
    def set_chapter_tree(self,name,chapter_titles):
        main_window.chapter_tree.DeleteAllItems()
        root = main_window.chapter_tree.AddRoot(name)
        for i in chapter_titles:
            main_window.chapter_tree.AppendItem(root,i)
        main_window.chapter_tree.ExpandAll()
    def source_combobox_EVT(self,event):
        self.type = self.source_combobox.GetSelection()
        book_core.change_websites(self.type)
        self.init_search_result_listctrl()
        self.search_result_label.SetLabel("搜索结果")
class SetBookWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "爬取小说")
        self.SetSize(self.FromDIP((400, 200)))
        self.setbook_panel=wx.Panel(self, -1)
        self.Center()

        self.Show_Controls()
        self.Bind_EVT()
        self.file_path_textbox.SetValue(os.getcwd())
        self.isworking = False
    def Show_Controls(self):
        self.font = wx.Font()
        self.font.PointSize = fontsize
        self.font.FaceName = "微软雅黑"
        self.setbook_panel.SetFont(self.font)

        self.file_path_label = wx.StaticText(self.setbook_panel, -1, "保存目录")
        self.file_path_textbox = wx.TextCtrl(self.setbook_panel, -1)
        self.browse_dir_button = wx.Button(self.setbook_panel, -1, "浏览")

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.file_path_label, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        hbox1.Add(self.file_path_textbox, 1, wx.ALL, 10)
        hbox1.Add(self.browse_dir_button, 0, wx.ALL, 10)

        self.file_type_label = wx.StaticText(self.setbook_panel,-1, "保存格式")
        file_type = ["*.epub","*.txt"]
        self.file_type_combobox = wx.ComboBox(self.setbook_panel, -1, choices = file_type, style = wx.CB_READONLY)
        self.file_type_combobox.SetSelection(0)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.file_type_label, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 10)
        hbox2.Add(self.file_type_combobox, 0, wx.LEFT | wx.RIGHT, 10)

        self.file_name_label = wx.StaticText(self.setbook_panel, -1, "文件名   ")
        self.file_name_textbox = wx.TextCtrl(self.setbook_panel, -1)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.file_name_label, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        hbox3.Add(self.file_name_textbox, 2, wx.ALL, 10)
        hbox3.AddStretchSpacer(1)

        self.start_get_book_button=wx.Button(self.setbook_panel, -1, "开始爬取小说", size = self.FromDIP((120, 35)))

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox1, 0, wx.EXPAND, 0)
        vbox.Add(hbox2, 0, wx.EXPAND, 0)
        vbox.Add(hbox3, 0, wx.EXPAND, 0)
        vbox.Add(self.start_get_book_button, 0, wx.LEFT| wx.RIGHT | wx.ALIGN_RIGHT, 10)

        self.setbook_panel.SetSizer(vbox)
    def window_onshow(self, event):
        self.file_name_textbox.SetValue(search_window.current_name)
    def window_onclose(self, event):
        self.Hide()
    def Bind_EVT(self):
        self.Bind(wx.EVT_CLOSE, self.window_onclose)
        self.Bind(wx.EVT_SHOW, self.window_onshow)

        self.start_get_book_button.Bind(wx.EVT_BUTTON,self.start_get_book)
        self.browse_dir_button.Bind(wx.EVT_BUTTON,self.browser_dir)
    def browser_dir(self, event):
        dlg=wx.DirDialog(self,"选择保存目录")
        if dlg.ShowModal()==wx.ID_OK:
            save_path=dlg.GetPath()
            self.file_path_textbox.SetValue(save_path)
        dlg.Destroy()
    def start_get_book(self, event):
        self.file_name = self.file_name_textbox.GetValue()
        self.file_path = self.file_path_textbox.GetValue()
        self.file_type = self.file_type_combobox.GetValue()
        self.isworking = True

        self.Hide()
        self.get_all_chapters()
    def get_all_chapters(self):
        self.auto_chapter = main_window.auto_chapter_chkbox.GetValue()

        main_window.status_bar.SetStatusText(" 处理中",0)
        
        self.content_dict = {}
        self.count = 0

        self.task = [threadpool.submit(self.get_each_chapter, search_window.chapter_urls.index(i)) for i in search_window.chapter_urls]
    def get_each_chapter(self, index):
        chapter_name = search_window.chapter_titles[index]
        chapter_url = search_window.chapter_urls[index]

        text = book_core.get_book_contents(chapter_url)

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
        self.sort_list = list(self.content_dict.keys())
        self.sort_list.sort(reverse = False)
        if self.file_type == "*.epub":
            self.filetype_epub()
        else:
            self.filetype_txt()
        wx.CallAfter(self.process_finish)
    def process_finish(self):
        main_window.show_msgbox(main_window, "提示", '小说 "%s" 爬取完成' % search_window.current_name,style=wx.ICON_INFORMATION)
        main_window.status_bar.SetStatusText(" 就绪",0)
        main_window.status_bar.SetStatusText("", 1)
        main_window.status_bar.SetStatusText("", 2)
        self.content_dict.clear()
        self.isworking = False
    def filetype_txt(self):
        path = os.path.join(self.file_path, self.file_name + ".txt")
        file = open(path, "a", encoding = "utf-8")
        for index in self.sort_list:
            text = self.content_dict[index]
            if self.auto_chapter:
                file.write(text[0] + "\n\n" + text[1] + "\n\n")
            else:
                file.write(text[1] + "\n\n")
        file.close()
    def filetype_epub(self):
        path = os.path.join(self.file_path, self.file_name + ".epub")
        epub = EpubCore()
        epub.create_epub(path, search_window.current_name, search_window.current_author, search_window.chapter_titles)

        epub.create_chapters(self.sort_list, self.content_dict)
class ShelfWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "书架")
        self.SetSize(self.FromDIP((740, 400)))
        self.shelf_panel = wx.Panel(self, -1)
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

        self.book_shelf_LC=wx.ListCtrl(self.shelf_panel,-1,size=((700, 300)),style=wx.LC_REPORT)

        self.select_buttton = wx.Button(self.shelf_panel, -1, "查看选中小说", size=(120, 30))
        self.select_buttton.Enable(False)
        self.remove_buttton = wx.Button(self.shelf_panel, -1, "删除选中小说", size=(120, 30))
        self.remove_buttton.Enable(False)
        self.remove_all_button=wx.Button(self.shelf_panel,-1,"删除全部小说", size=(120,30))

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.remove_all_button, 0, wx.ALL & (~wx.TOP), 10)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.select_buttton, 0, wx.ALL & (~wx.TOP), 10)
        hbox.Add(self.remove_buttton, 0, wx.ALL & (~wx.TOP), 10)

        vbox= wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.book_shelf_LC, 1, wx.ALL | wx.EXPAND, 10)
        vbox.Add(hbox, 0, wx.EXPAND, 10)

        self.shelf_panel.SetSizer(vbox)
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
        processing_window.Show()
        self.Hide()
        wx.CallLater(1, search_window.select_book, self.name, self.url, self.author, self.type)
    def remove_book(self, event):
        self.book_shelf_LC.DeleteItem(self.index)
        self.cursor.execute("DELETE FROM book_shelf WHERE book_name = '%s' AND source = '%s'" % (self.name,self.type))
        self.db.commit()
class ReadWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "阅读模式")
        self.SetSize(self.FromDIP((800, 500)))
        self.browser_panel = wx.Panel(self, -1)
        self.Center()

        self.show_controls()
        self.Bind_EVT()
        self.show_page()
        self.current_size = 20
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
        self.font_s_menuitem = wx.MenuItem(self.set_menu, 130, "小(&S)", kind = wx.ITEM_RADIO)
        self.font_m_menuitem = wx.MenuItem(self.set_menu, 140, "中(&M)", kind = wx.ITEM_RADIO)
        self.font_b_menuitem = wx.MenuItem(self.set_menu, 150, "大(&B)", kind = wx.ITEM_RADIO)
        self.font_c_menuitem = wx.MenuItem(self.set_menu, 160, "自定义(&U)")

        self.menu_bar.Append(self.navi_menu,"导航(&N)")
        self.menu_bar.Append(self.set_menu, "字体设置(&F)")
        self.navi_menu.Append(self.chapter_menuitem)
        self.navi_menu.Append(self.prevous_menuitem)
        self.navi_menu.Append(self.next_menuitem)
        self.set_menu.Append(self.font_s_menuitem)
        self.set_menu.Append(self.font_m_menuitem)
        self.set_menu.Check(140, True)
        self.set_menu.Append(self.font_b_menuitem)
        self.set_menu.Append(self.font_c_menuitem)

        self.SetMenuBar(self.menu_bar)

        self.Status_Bar = wx.StatusBar(self, -1)
        self.Status_Bar.SetFieldsCount(2)
        self.Status_Bar.SetStatusWidths((200, 300))
        self.Status_Bar.SetStatusText(" 就绪", 0)
        self.SetStatusBar(self.Status_Bar)
    def Bind_EVT(self):
        self.browser.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, self.title_changed)
        self.Bind(wx.EVT_MENU, self.menu_evt)
    def menu_evt(self, event):
        menuid = event.GetId()
        if menuid == 100:
            self.browser.RunScript('''document.getElementById("p_con").click();''')
        if menuid == 110:
            self.browser.RunScript('''document.getElementById("p_u").click();''')
        if menuid == 120:
            self.browser.RunScript('''document.getElementById("p_d").click();''')
        if menuid == 130:
            self.browser.RunScript('''document.getElementById("text").style.fontSize = "14px";''')
        if menuid == 140:
            self.browser.RunScript('''document.getElementById("text").style.fontSize = "20px";''')
        if menuid == 150:
            self.browser.RunScript('''document.getElementById("text").style.fontSize = "25px";''')
        if menuid == 160:
            dlg = wx.NumberEntryDialog(self, "设置字体大小(单位: px):", "", "自定义字体大小", self.current_size, 14, 25)
            if dlg.ShowModal() == wx.ID_OK:
                self.current_size = dlg.GetValue()
                self.browser.RunScript('''document.getElementById("text").style.fontSize = "%dpx";''' % self.current_size)
    def title_changed(self, event):
        self.SetTitle(self.browser.GetCurrentTitle())
    def show_page(self):
        self.bookname = search_window.current_name
        self.base_path = os.path.join(os.getcwd(), "book_cache", self.bookname)

        if not os.path.exists(self.base_path):
            self.get_book_cache()
            pass
        else:
            self.open_path = os.path.join(self.base_path, "contents.html")
            self.browser.LoadURL("file://" + self.open_path)
    def get_book_cache(self):
        os.makedirs(self.base_path)
        html_core.save_css(os.path.join(self.base_path, "style.css"))
        self.process_chapter()
        self.count = 0
        self.Status_Bar.SetStatusText(" 处理中", 0)

        task = [threadpool.submit(self.process_each_chapter, search_window.chapter_urls.index(i)) for i in search_window.chapter_urls]
    def process_each_chapter(self, index):
        chapter_name = search_window.chapter_titles[index]
        chapter_url = search_window.chapter_urls[index]

        isFirst = True if index == 0 else False
        isLast = True if index + 1 == len(search_window.chapter_urls) else False

        text = book_core.get_book_contents(chapter_url)
        html_page = html_core.process_contents(chapter_name, text, index, isFirst, isLast)
        self.count += 1
        wx.CallAfter(self.update_progress, chapter_name)

        file_path = os.path.join(self.base_path, "%d.html" % index)
        with open (file_path, "w", encoding = "utf-8") as f:
            f.write(html_page)

        if self.count == len(search_window.chapter_urls):
            self.Status_Bar.SetStatusText(" 就绪", 0)
            self.Status_Bar.SetStatusText("", 1)
    def update_progress(self, chapter_name):
        progress = (self.count / len(search_window.chapter_urls)) * 100
        self.Status_Bar.SetStatusText("[进度]：%.2f %% 正在爬取：%s" % (progress, chapter_name), 1)
    def process_chapter(self):
        path = os.path.join(self.base_path, "contents.html")
        with open (path, "w", encoding = "utf-8") as f:
            f.write(html_core.process_chapter(self.bookname, search_window.chapter_titles))
        self.browser.LoadURL(path)
class SetWindow(wx.Dialog):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX)  & (~wx.RESIZE_BORDER) | wx.FRAME_FLOAT_ON_PARENT
        wx.Dialog.__init__(self, parent, -1, title = "首选项", style = style)
        self.SetSize(self.FromDIP((400,365)))
        self.set_panel = wx.Panel(self, -1)
        self.Center()

        self.show_controls()
        self.Bind_EVT()
        book_core.read_config()
    def show_controls(self):
        self.font = wx.Font()
        self.font.PointSize = fontsize
        self.font.FaceName = "微软雅黑"

        self.ip_box = wx.StaticBox(self.set_panel, -1, "代理 IP 设置")
        self.ip_box.SetFont(self.font)

        self.disable_ip_rad = wx.RadioButton(self.ip_box, -1, "禁用代理 IP")
        self.disable_ip_rad.SetValue(True)
        self.cust_ip_rad = wx.RadioButton(self.ip_box, -1, "自定义代理 IP ")

        self.ip_port_label = wx.StaticText(self.ip_box, -1, "代理 IP 地址(仅支持 HTTPS)：")

        self.ip_port_tc = wx.TextCtrl(self.ip_box, -1)
        self.test_button = wx.Button(self.ip_box, -1, "测试", size = self.FromDIP((90,30)))
        self.test_button.Enable(False)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.disable_ip_rad, 0, wx.ALL & (~wx.BOTTOM), 10)
        hbox1.Add(self.cust_ip_rad, 0, wx.RIGHT | wx.TOP, 10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.ip_port_tc, 1, wx.EXPAND | wx.LEFT, 10)
        hbox2.Add(self.test_button, 0, wx.LEFT, 10)

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(hbox1, 0, wx.EXPAND, 0)
        vbox1.Add(self.ip_port_label, 0, wx.LEFT | wx.TOP, 10)
        vbox1.Add(hbox2, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        sbox = wx.StaticBoxSizer(self.ip_box)
        sbox.Add(vbox1, 1, wx.EXPAND, 0)

        self.thread_box = wx.StaticBox(self.set_panel, -1, "线程池设置")
        self.thread_box.SetFont(self.font)
        self.thread_label = wx.StaticText(self.thread_box, -1, "线程数：10")
        self.thread_slider = wx.Slider(self.thread_box, -1, 10, 1, 32, style = wx.SL_AUTOTICKS | wx.SL_MIN_MAX_LABELS)
        self.change_thread(0)

        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox2.Add(self.thread_label, 0, wx.TOP | wx.LEFT, 10)
        vbox2.Add(self.thread_slider, 0, wx.ALL | wx.EXPAND, 10)

        sbox2 = wx.StaticBoxSizer(self.thread_box, wx.VERTICAL)
        sbox2.Add(vbox2, 0, wx.EXPAND, 0)

        self.ok_button = wx.Button(self.set_panel, -1, "确定", size = self.FromDIP((90,30)))
        self.ok_button.SetFont(self.font)
        self.cancel_button = wx.Button(self.set_panel, -1, "取消",size = self.FromDIP((90,30)))
        self.cancel_button.SetFont(self.font)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(self.ok_button, 0, wx.ALL, 10)
        hbox3.Add(self.cancel_button, 0, wx.ALL, 10)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(sbox, 0, wx.EXPAND | wx.ALL, 10)
        vbox.Add(sbox2, 0, wx.EXPAND | wx.ALL & (~wx.BOTTOM), 10)
        vbox.Add(hbox3, 0, wx.EXPAND, 0)
        self.set_panel.SetSizer(vbox)
    def Bind_EVT(self):
        self.Bind(wx.EVT_SHOW, self.window_onshow)
        self.thread_slider.Bind(wx.EVT_SLIDER, self.change_thread)

        self.disable_ip_rad.Bind(wx.EVT_RADIOBUTTON, self.disable_ip)
        self.cust_ip_rad.Bind(wx.EVT_RADIOBUTTON, self.cust_ip)

        self.ok_button.Bind(wx.EVT_BUTTON, self.save_change)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.close_window)
        self.test_button.Bind(wx.EVT_BUTTON, self.test_ip)
    def close_window(self, event):
        self.Close()
    def window_onshow(self, event):
        self.ip_type = book_core.ip_type
        if self.ip_type == 0:
            self.disable_ip(0)
            self.disable_ip_rad.SetValue(True)
        elif self.ip_type == 1:
            self.cust_ip(0)
            self.cust_ip_rad.SetValue(True)

        self.ip_port_tc.SetValue(book_core.ip_addres)

        self.thread_value = book_core.thread_amounts
        self.thread_slider.SetValue(self.thread_value)
        self.change_thread(0)
    def disable_ip(self, event):
        self.ip_type = 0
        self.ip_port_label.Enable(False)
        self.ip_port_tc.Enable(False)
        self.test_button.Enable(False)
    def cust_ip(self, event):
        self.ip_type = 1
        self.ip_port_label.Enable(True)
        self.ip_port_tc.Enable(True)
        self.test_button.Enable(True)
    def change_thread(self, event):
        self.thread_value = self.thread_slider.GetValue()
        self.thread_label.SetLabel("线程数：%d" % self.thread_value)
    def save_change(self, event):
        threadpool._max_workers = self.thread_value
        book_core.save_config(self.ip_type, self.ip_port_tc.GetValue(), self.thread_value)
        self.Close()
    def test_ip(self, event):
        threadpool.submit(self.visit_website)
    def visit_website(self):
        try:
            page = requests.get(url = "https://www.baidu.com", proxies = {"https":self.ip_port_tc.GetValue()}, timeout = 5)
            if page.text.find("搜索"):
                main_window.show_msgbox(self, "提示", "测试成功\n\n状态码：%d\n响应时间：%.2f 秒" % (page.status_code, page.elapsed.total_seconds()), style = wx.ICON_INFORMATION)
        except requests.RequestException as e:
            main_window.show_msgbox(self, "提示", "测试失败\n\n原因：%s" % e, style = wx.ICON_ERROR)
class EditWindow(wx.Dialog):
    pass
class ProcessingWindow(wx.Frame):
    def __init__(self, parent):
        style = wx.CAPTION
        wx.Frame.__init__(self, parent, -1, "处理中", style = style)
        self.SetSize(self.FromDIP((200, 80)))
        self.processing_panel=wx.Panel(self, -1)
        self.Center()

        self.font = wx.Font()
        self.font.PointSize = fontsize
        self.font.FaceName = "微软雅黑"

        self.processing_label = wx.StaticText(self.processing_panel, -1, "正在处理中，请稍候")
        self.processing_label.SetFont(self.font)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.processing_label, 0, wx.ALL, 10)

        self.processing_panel.SetSizer(vbox)
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