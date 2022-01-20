import wx, wx.html2, requests, os, shutil
from sqlite3 import connect
from concurrent.futures import ThreadPoolExecutor
from book_core_V2 import BookCore, HtmlCore, EpubCore
class MainWindow(wx.Frame):
    def __init__(self, parent):
        self.w_title="小说爬取工具"
        wx.Frame.__init__(self, parent, -1, title = self.w_title)

        self.SetSize(self.FromDIP((925, 585)))
        self.main_panel = wx.Panel(self, -1)
        self.scale_factor = self.GetDPIScaleFactor()

        self.Center()
        self.init_controls()
        self.Bind_EVT()
    def init_controls(self):
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

        self.init_menu_bar()
        self.init_status_bar()
    def init_menu_bar(self):
        self.menu_bar = wx.MenuBar()
        self.about_menu = wx.Menu()
        self.tool_menu = wx.Menu()

        self.url_menuitem = wx.MenuItem(self.about_menu, 990, "项目地址(&U)", " 访问项目地址")
        self.check_menuitem = wx.MenuItem(self.about_menu, 810, "检查更新(&P)", " 检查程序更新")
        self.help_menuitem = wx.MenuItem(self.about_menu, 950, "使用帮助(&C)", " 显示使用帮助")
        self.about_menuitem = wx.MenuItem(self.about_menu, 960, "关于(&A)", " 显示程序相关信息")

        self.bookshelf_menuitem = wx.MenuItem(self.tool_menu, 970, "书架(&B)", " 显示收藏的小说")
        self.read_mode_menuitem = wx.MenuItem(self.tool_menu, 985, "阅读模式(&R)", " 进入阅读模式")
        self.strfilter_menuitem = wx.MenuItem(self.tool_menu, 994, "字符串过滤(&F)", " 编辑要过滤字符串")
        self.setting_menuitem = wx.MenuItem(self.tool_menu, 980, "首选项(&S)", " 编辑首选项")

        self.menu_bar.Append(self.tool_menu,"工具(&T)")
        self.menu_bar.Append(self.about_menu,"帮助(&H)")

        self.about_menu.Append(self.url_menuitem)
        self.about_menu.Append(self.check_menuitem)
        self.about_menu.AppendSeparator()
        self.about_menu.Append(self.help_menuitem)
        self.about_menu.Append(self.about_menuitem)
        self.tool_menu.Append(self.read_mode_menuitem)
        self.tool_menu.Append(self.bookshelf_menuitem)
        self.tool_menu.Append(self.strfilter_menuitem)
        self.tool_menu.AppendSeparator()
        self.tool_menu.Append(self.setting_menuitem)

        self.SetMenuBar(self.menu_bar)
    def init_status_bar(self):
        self.status_bar = wx.StatusBar(self, -1)
        self.status_bar.SetFieldsCount(3)
        self.status_bar.SetStatusWidths((200 * self.scale_factor, 500 * self.scale_factor, 250 * self.scale_factor))
        self.status_bar.SetStatusText(" 就绪",0)

        self.SetStatusBar(self.status_bar)
    def Bind_EVT(self):
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.search_book_button.Bind(wx.EVT_BUTTON,self.Load_search_window)
        self.get_book_button.Bind(wx.EVT_BUTTON,self.Load_parse_window)
        self.add_shelf_button.Bind(wx.EVT_BUTTON,self.Add_to_shelf)

        self.chapter_tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED,self.select_chapter_tree)
        self.auto_chapter_chkbox.Bind(wx.EVT_CHECKBOX,self.auto_chapter_change)

        self.about_menu.Bind(wx.EVT_MENU,self.menu_EVT)
        self.tool_menu.Bind(wx.EVT_MENU,self.menu_EVT)

        self.book_info_label.Bind(wx.EVT_RIGHT_DOWN, self.info_popup_menu)
        self.chapter_tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.tree_popup_menu)
    def menu_EVT(self, event):
        from platform import platform
        menuid = event.GetId()
        if menuid == 950:
            self.show_msgbox(self, "使用帮助", "使用帮助\n\n搜索小说：如果没有搜索到小说，请尝试切换搜索站点\n预览章节：双击树形框章节标题，可预览该章节内容\n爬取小说：可选择文件保存位置，程序默认使用多线程爬取方式，以提高爬取效率。\n如果遇到问题，请前往github提交issue。",wx.ICON_INFORMATION)
        elif menuid == 960:
            self.show_msgbox(self, "关于 小说爬取工具", "小说爬取工具 Version 1.33\n\n轻量级的小说爬取工具\nProgrammed by Scott Sloan\n平台：%s\n日期：2022-1-20" % platform(),wx.ICON_INFORMATION)
        elif menuid == 970:
            shelf_window.ShowWindowModal()
        elif menuid == 985:
            if parse_window.isworking:
                self.show_msgbox(self, "警告", "请等待爬取进程结束", style = wx.ICON_WARNING)
                return
            read_window = ReadWindow(self)
            read_window.Show()
            read_window.load_select_window()

        elif menuid == 980:
            if parse_window.isworking:
                self.show_msgbox(self, "警告", "请等待爬取进程结束", style = wx.ICON_WARNING)
                return
            set_window = SetWindow(self)
            set_window.ShowWindowModal()
        elif menuid == 990:
            from webbrowser import open
            open("https://github.com/ScottSloan/Book-Scraper")
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
        edit_menuitem = wx.MenuItem(tree_menu, 310, "删除章节(&D)")
        rename_menuitem = wx.MenuItem(tree_menu, 320, "重命名章节(&R)")
        tree_menu.Append(preview_menuitem)
        tree_menu.AppendSeparator()
        tree_menu.Append(edit_menuitem)
        tree_menu.Append(rename_menuitem)

        self.tree_menu_event = event
        self.Bind(wx.EVT_MENU, self.popup_menu_EVT)
        self.PopupMenu(tree_menu)
    def popup_menu_EVT(self, event):
        menuid = event.GetId()
        if menuid == 200:
            self.copy_to_cb()
        elif menuid == 300:
            self.select_chapter_tree(self.tree_menu_event)
        elif menuid == 310:
            self.remove_chapter_tree(self.tree_menu_event)
        elif menuid == 320:
            self.rename_chapter_tree(self.tree_menu_event)
    def OnClose(self, event):
        from sys import exit
        if parse_window.isworking:
            id = self.show_msgbox(self, "警告：", "爬取进程仍在进行，是否确认退出？", style = wx.ICON_WARNING | wx.YES_NO)
            if id == wx.ID_YES:
                for i in parse_window.task:
                    i.cancel()
                exit(0)
            else:
                return
        else:
            exit(0)
    def show_msgbox(self, parent, caption, message, style):
        dlg=wx.MessageDialog(parent, message, caption, style=style)
        evt=dlg.ShowModal()
        dlg.Destroy()
        return evt
    def Load_search_window(self, event):
        if parse_window.isworking:
            self.show_msgbox(self,"警告","请等待爬取进程结束",style=wx.ICON_WARNING)
            return
        search_window.ShowWindowModal()
    def Load_parse_window(self, event):
        if parse_window.isworking:
            self.show_msgbox(self,"警告","请等待爬取进程结束",style=wx.ICON_WARNING)
            return
        parse_window.ShowWindowModal()
        parse_window.file_name_textbox.SetValue(search_window.current_name)
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

        wx.CallLater(1, self.select_chapter)

        self.processing_window = ProcessingWindow(self)
        self.processing_window.ShowWindowModal()
    def remove_chapter_tree(self, event):
        item = event.GetItem()
        chapter_name = self.chapter_tree.GetItemText(item)

        index = search_window.chapter_titles.index(chapter_name)
        del search_window.chapter_titles[index]
        del search_window.chapter_urls[index]

        self.chapter_tree.Delete(item)

        self.book_chapter_label.SetLabel("目录 (共 %d 章)" % len(search_window.chapter_titles))
    def rename_chapter_tree(self, event):
        item = event.GetItem()
        value = self.chapter_tree.GetItemText(item)
        dlg = wx.TextEntryDialog(self, "重命名章节名：", "重命名", value)
        if dlg.ShowModal() == wx.ID_OK:
            self.chapter_tree.SetItemText(item, dlg.GetValue())

            index = search_window.chapter_titles.index(value)
            search_window.chapter_titles[index] = dlg.GetValue()
    def select_chapter(self):
        self.current_text = book_core.get_book_contents(self.current_chapter_url)
        self.set_contents_textbox()
    def set_contents_textbox(self):
        if self.auto_chapter:
            self.chapter_content_textbox.SetValue(self.current_text[0] + "\n\n" + self.current_text[1])
        else:
            self.chapter_content_textbox.SetValue(self.current_text[1])
        self.processing_window.Destroy()
    def auto_chapter_change(self, event):
        self.auto_chapter=self.auto_chapter_chkbox.GetValue()
        self.set_contents_textbox()
    def copy_to_cb(self):
        cb = wx.Clipboard()
        data = wx.TextDataObject()
        data.SetText((self.book_info_label.GetLabel()))
        cb.Open()
        cb.SetData(data)
        cb.Flush()
class SearchWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "搜索小说")
        self.SetSize(self.FromDIP((600, 380)))
        self.search_panel = wx.Panel(self, -1)
        self.Center()
        self.scale_factor = self.GetDPIScaleFactor()

        self.init_controls()
        self.Bind_EVT()
        self.init_search_result_listctrl()

        self.history_list = book_core.read_history()
        self.search_cb.Set(self.history_list)
    def init_controls(self):
        self.search_cb = wx.ComboBox(self.search_panel, -1)
        self.search_book_button = wx.Button(self.search_panel, -1, "搜索", size = self.FromDIP((90, 30)))
        self.source_list = book_core.website_list
        self.source_combobox = wx.ComboBox(self.search_panel, -1, choices = self.source_list, style = wx.CB_READONLY)
        self.source_combobox.SetSelection(0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.search_cb, 1, wx.ALL | wx.EXPAND, 10)
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
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.search_book_button.Bind(wx.EVT_BUTTON, self.search_book_EVT)
        self.search_result_listctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.select_search_result_listctrl)
        self.source_combobox.Bind(wx.EVT_COMBOBOX,self.source_combobox_EVT)
    def OnClose(self, event):
        self.Hide()
    def search_book_EVT(self, event):
        self.bookname = self.search_cb.GetValue()
        self.update_history()
        self.type = self.source_combobox.GetSelection()
        if not bool(self.bookname):
            main_window.show_msgbox(self, "警告", "搜索内容不能为空", style = wx.ICON_WARNING)
            return 0
        threadpool.submit(self.search_book)

        self.processing_window = ProcessingWindow(self)
        self.processing_window.ShowWindowModal()
    def update_history(self):
        if not self.bookname or self.history_list.count(self.bookname) != 0:
            return
        self.history_list.append(self.bookname)
        book_core.save_history(self.bookname)

        self.search_cb.Set(self.history_list)
        self.search_cb.SetValue(self.bookname)
    def search_book(self):
        self.search_result = book_core.search_book(self.bookname)
        wx.CallAfter(self.set_search_result_listctrl)
    def init_search_result_listctrl(self):
        self.search_result_listctrl.ClearAll()
        self.search_result_listctrl.InsertColumn(0, "序号", width = int(50 * self.scale_factor))
        self.search_result_listctrl.InsertColumn(1, "书名", width = int(250 * self.scale_factor))
        self.search_result_listctrl.InsertColumn(2, "作者", width = int(200 * self.scale_factor))
    def set_search_result_listctrl(self):
        self.init_search_result_listctrl()

        index = 0
        for i in self.search_result:
            self.search_result_listctrl.InsertItem(index,str(index+1))
            self.search_result_listctrl.SetItem(index,1,i)
            self.search_result_listctrl.SetItem(index,2,self.search_result[i][1])
            index += 1
    
        self.search_result_label.SetLabel("搜索结果 (共 %d 条)" % len(self.search_result))
        self.processing_window.Destroy()
    def select_search_result_listctrl(self,event):
        index = self.search_result_listctrl.GetFocusedItem()

        name = self.search_result_listctrl.GetItemText(index, 1)
        url = self.search_result[name][0]
        author = self.search_result_listctrl.GetItemText(index, 2)

        self.Hide()
        wx.CallLater(1, self.select_book, name, url, author, self.type)

        self.processing_window = ProcessingWindow(self)
        self.processing_window.ShowWindowModal()
    def select_book(self,name,url,author,type):
        self.current_name, self.current_url, self.current_author, self.type = name, url, author, type
        book_core.change_websites(self.type)
        main_window.SetTitle(main_window.w_title + " - " + name)
        main_window.book_address_textbox.SetValue(self.current_url)
        main_window.book_info_label.SetLabel("书名：%s         作者：%s" % (name,author))

        self.intro = book_core.get_book_info(url)
        chapter_info = book_core.get_book_chapters(url)

        self.chapter_titles = list(chapter_info.keys())
        self.chapter_urls = list(chapter_info.values())

        self.set_chapter_tree(name,self.chapter_titles)
        main_window.book_chapter_label.SetLabel("目录 (共 %d 章)" % len(self.chapter_titles))
        main_window.chapter_content_textbox.SetValue(self.intro)

        main_window.get_book_button.Enable(True)
        main_window.add_shelf_button.Enable(True)
        main_window.read_mode_menuitem.Enable(True)
        main_window.auto_chapter_chkbox.Enable(False)

        parse_window.has_cached = False

        self.processing_window.Destroy()
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
class ParseBookWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "爬取小说")
        self.SetSize(self.FromDIP((400, 220)))
        self.parse_panel = wx.Panel(self, -1)
        self.Center()

        self.init_controls()
        self.Bind_EVT()

        self.file_path_textbox.SetValue(os.getcwd())
        self.isworking = False
        self.has_cached = False
    def init_controls(self):
        self.file_path_label = wx.StaticText(self.parse_panel, -1, "保存目录")
        self.file_path_textbox = wx.TextCtrl(self.parse_panel, -1)
        self.browse_dir_button = wx.Button(self.parse_panel, -1, "浏览")

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.file_path_label, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        hbox1.Add(self.file_path_textbox, 1, wx.ALL, 10)
        hbox1.Add(self.browse_dir_button, 0, wx.ALL, 10)

        self.file_type_label = wx.StaticText(self.parse_panel,-1, "保存格式\\类型")
        file_type = ["*.epub", "*.txt", "*.html"]
        self.file_type_combobox = wx.ComboBox(self.parse_panel, -1, choices = file_type, style = wx.CB_READONLY)
        self.file_type_combobox.SetSelection(0)
        self.description_label = wx.StaticText(self.parse_panel, -1, "说明：epub 是目前最流行的一种电子书格式，支持章节列表显示。")

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.file_type_label, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 10)
        hbox2.Add(self.file_type_combobox, 0, wx.LEFT | wx.RIGHT, 10)

        self.file_name_label = wx.StaticText(self.parse_panel, -1, "文件名")
        self.file_name_textbox = wx.TextCtrl(self.parse_panel, -1)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.file_name_label, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        hbox3.Add(self.file_name_textbox, 2, wx.ALL, 10)
        hbox3.AddStretchSpacer(1)

        self.parse_button=wx.Button(self.parse_panel, -1, "开始爬取小说", size = self.FromDIP((120, 35)))

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox1, 0, wx.EXPAND, 0)
        vbox.Add(hbox2, 0, wx.EXPAND, 0)
        vbox.Add(self.description_label, 0, wx.LEFT | wx.TOP, 10)
        vbox.Add(hbox3, 0, wx.EXPAND, 0)
        vbox.Add(self.parse_button, 0, wx.LEFT| wx.RIGHT | wx.ALIGN_RIGHT, 10)

        self.parse_panel.SetSizer(vbox)
    def OnShow(self, event):
        self.file_name_textbox.SetValue(search_window.current_name)
    def OnClose(self, event):
        self.Hide()
    def Bind_EVT(self):
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SHOW, self.OnShow)

        self.parse_button.Bind(wx.EVT_BUTTON, self.parse_book_EVT)
        self.browse_dir_button.Bind(wx.EVT_BUTTON, self.browser_dir)
        self.file_type_combobox.Bind(wx.EVT_COMBOBOX, self.select_type_EVT)
    def browser_dir(self, event):
        dlg = wx.DirDialog(self, "选择保存目录")
        if dlg.ShowModal() == wx.ID_OK:
            save_path=dlg.GetPath()
            self.file_path_textbox.SetValue(save_path)
        dlg.Destroy()
    def parse_book_EVT(self, event):
        self.file_name = self.file_name_textbox.GetValue()
        self.file_path = self.file_path_textbox.GetValue()
        self.file_type = self.file_type_combobox.GetValue()
        self.isworking = True

        self.Hide()
        if self.has_cached:
            self.process_all_chapters()
        else:
            self.get_all_chapters()
    def select_type_EVT(self, event):
        item = event.GetString()
        if item == "*.epub":
            self.description_label.SetLabel("说明：epub 是目前最流行的一种电子书格式，支持章节列表显示。")
        elif item == "*.txt":
            self.description_label.SetLabel("说明：txt 是一种通用的文本格式。")
        elif item == "*.html":
            self.description_label.SetLabel("说明：将小说缓存到本地，稍后可用阅读模式浏览。")

        if item == "*.html":
            self.file_path_textbox.Enable(False)
            self.browse_dir_button.Enable(False)
            self.file_name_textbox.Enable(False)
        else:
            self.file_path_textbox.Enable(True)
            self.browse_dir_button.Enable(True)
            self.file_name_textbox.Enable(True)
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
            self.sort_list = list(self.content_dict.keys())
            self.sort_list.sort(reverse = False)
            self.process_all_chapters()
    def update_progress(self, chapter_name, index):
        progress = (self.count / len(search_window.chapter_urls)) * 100
        tip = "[进度]：%.2f %% 正在爬取：%s" % (progress, chapter_name)
        main_window.status_bar.SetStatusText(tip, 1)
        main_window.status_bar.SetStatusText("正在处理线程：%d" % index, 2)
    def process_all_chapters(self):
        if self.file_type == "*.epub":
            self.filetype_epub()
        elif self.file_type ==  "*.txt":
            self.filetype_txt()
        else:
            self.filetype_html()
        wx.CallAfter(self.process_finish)
    def process_finish(self):
        main_window.show_msgbox(main_window, "提示", '小说 "%s" 爬取完成' % search_window.current_name,style=wx.ICON_INFORMATION)
        main_window.status_bar.SetStatusText(" 就绪",0)
        main_window.status_bar.SetStatusText("", 1)
        main_window.status_bar.SetStatusText("", 2)
        self.isworking = False
        self.has_cached = True
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
    def filetype_html(self):
        base_path = os.path.join(os.getcwd(), "book_cache", self.file_name)
        os.makedirs(base_path)

        for index in self.sort_list:
            text = self.content_dict[index]

            isFirst = True if index == 0 else False
            isLast = True if index + 1 == len(search_window.chapter_urls) else False

            html_core.process_contents(os.path.join(base_path, "%s.html" % str(int(index) + 1)), text[0], text, int(index), isFirst, isLast)
        html_core.process_chapter(os.path.join(base_path, "contents.html"), self.file_name, search_window.chapter_titles)
        html_core.save_css(os.path.join(base_path, "style.css"))
class ShelfWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "书架")
        self.SetSize(self.FromDIP((740, 400)))
        self.shelf_panel = wx.Panel(self, -1)
        self.Center()

        self.init_controls()
        self.Bind_EVT()
        self.connect_db()

        self.processing_window = ProcessingWindow(self)
    def OnShow(self, event):
        self.connect_db()
        self.show_books()
    def OnClose(self, event):
        self.Hide()
        self.db.close()
    def Bind_EVT(self):
        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.book_shelf_LC.Bind(wx.EVT_LIST_ITEM_SELECTED,self.select_shelf_lc)
        self.select_buttton.Bind(wx.EVT_BUTTON, self.select_book)
        self.remove_buttton.Bind(wx.EVT_BUTTON, self.remove_book)
        self.remove_all_button.Bind(wx.EVT_BUTTON, self.drop_table)
    def init_controls(self):
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
        self.db = connect("book.db",check_same_thread=False)
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
        wx.CallLater(1, search_window.select_book, self.name, self.url, self.author, self.type)

        search_window.processing_window = ProcessingWindow(main_window)
        search_window.processing_window.ShowWindowModal()
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

        self.init_controls()
        self.Bind_EVT()

        self.current_size = 20
    def load_select_window(self):
        select_window = SelectWindow(self)
        select_window.ShowWindowModal()

        bookname = select_window.select_bookname

        if bookname != "":
            self.show_page(bookname)
    def init_controls(self):
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
        self.browser.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.page_loaded)

        self.Bind(wx.EVT_MENU, self.menu_evt)
    def page_loaded(self, event):
        title = self.browser.GetCurrentTitle()
        if str(title).find("章节列表") == -1 and title != "":
            self.browser.RunScript('''document.getElementById("text").style.fontSize = "%dpx";''' % self.current_size)
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
            self.current_size = 14
        if menuid == 140:
            self.browser.RunScript('''document.getElementById("text").style.fontSize = "20px";''')
            self.current_size = 20
        if menuid == 150:
            self.browser.RunScript('''document.getElementById("text").style.fontSize = "25px";''')
            self.current_size = 25
        if menuid == 160:
            dlg = wx.NumberEntryDialog(self, "设置字体大小(单位: px):", "", "自定义字体大小", self.current_size, 14, 25)
            if dlg.ShowModal() == wx.ID_OK:
                self.current_size = dlg.GetValue()
                self.browser.RunScript('''document.getElementById("text").style.fontSize = "%dpx";''' % self.current_size)
    def title_changed(self, event):
        self.SetTitle(self.browser.GetCurrentTitle())
    def show_page(self, bookname):
        self.base_path = os.path.join(os.getcwd(), "book_cache", bookname)

        self.open_path = os.path.join(self.base_path, "contents.html")
        self.browser.LoadURL("file://" + self.open_path)
class SetWindow(wx.Dialog):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.MINIMIZE_BOX)  & (~wx.RESIZE_BORDER) | wx.FRAME_FLOAT_ON_PARENT
        wx.Dialog.__init__(self, parent, -1, title = "首选项", style = style)
        self.SetSize(self.FromDIP((400,365)))
        self.set_panel = wx.Panel(self, -1)
        self.Center()

        self.init_controls()
        self.Bind_EVT()
        book_core.read_config()
    def init_controls(self):
        self.ip_box = wx.StaticBox(self.set_panel, -1, "代理 IP 设置")

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
        self.thread_label = wx.StaticText(self.thread_box, -1, "线程数：10")
        self.thread_slider = wx.Slider(self.thread_box, -1, 10, 1, 32, style = wx.SL_AUTOTICKS | wx.SL_MIN_MAX_LABELS)
        self.change_thread(0)

        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox2.Add(self.thread_label, 0, wx.TOP | wx.LEFT, 10)
        vbox2.Add(self.thread_slider, 0, wx.ALL | wx.EXPAND, 10)

        sbox2 = wx.StaticBoxSizer(self.thread_box, wx.VERTICAL)
        sbox2.Add(vbox2, 0, wx.EXPAND, 0)

        self.ok_button = wx.Button(self.set_panel, -1, "确定", size = self.FromDIP((90,30)))
        self.cancel_button = wx.Button(self.set_panel, -1, "取消",size = self.FromDIP((90,30)))

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
        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.thread_slider.Bind(wx.EVT_SLIDER, self.change_thread)

        self.disable_ip_rad.Bind(wx.EVT_RADIOBUTTON, self.disable_ip)
        self.cust_ip_rad.Bind(wx.EVT_RADIOBUTTON, self.cust_ip)

        self.ok_button.Bind(wx.EVT_BUTTON, self.save_change)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.OnClose)
        self.test_button.Bind(wx.EVT_BUTTON, self.test_ip)
    def OnClose(self, event):
        self.Destroy()
    def OnShow(self, event):
        self.proxy_ip = book_core.proxy_ip
        if not self.proxy_ip:
            self.disable_ip(0)
            self.disable_ip_rad.SetValue(True)
        else:
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
        self.Destroy()
    def test_ip(self, event):
        threadpool.submit(self.visit_website)
    def visit_website(self):
        try:
            page = requests.get(url = "https://www.baidu.com", proxies = {"https":self.ip_port_tc.GetValue()}, timeout = 5)
            if page.text.find("搜索"):
                main_window.show_msgbox(self, "提示", "测试成功\n\n状态码：%d\n响应时间：%.2f 秒" % (page.status_code, page.elapsed.total_seconds()), style = wx.ICON_INFORMATION)
        except requests.RequestException as e:
            main_window.show_msgbox(self, "提示", "测试失败\n\n原因：%s" % e, style = wx.ICON_ERROR)
class ProcessingWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "处理中")
        self.SetSize(self.FromDIP((200, 80)))
        self.processing_panel = wx.Panel(self, -1)
        self.EnableCloseButton(False)
        self.Center()

        self.processing_label = wx.StaticText(self.processing_panel, -1, "正在处理中，请稍候")

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.processing_label, 0, wx.ALL, 10)

        self.processing_panel.SetSizer(vbox)
class StrFilterWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "字符串过滤")
class SelectWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "选择小说")
        self.SetSize(self.FromDIP((400, 250)))
        self.select_panel = wx.Panel(self, -1)

        self.init_controls()
        self.Bind_EVT()

        self.select_bookname = ""
    def init_controls(self):
        self.str_label = wx.StaticText(self.select_panel, -1, "选择要阅读的小说")

        self.select_listbox = wx.ListBox(self.select_panel, -1, size = self.FromDIP((400, 120)))

        self.select_button = wx.Button(self.select_panel, -1, "选择", size = self.FromDIP((80, 30)))
        self.select_button.Enable(False)
        self.remove_button = wx.Button(self.select_panel, -1, "删除", size = self.FromDIP((80, 30)))
        self.remove_button.Enable(False)
        self.help_button = wx.Button(self.select_panel, -1, "帮助", size = self.FromDIP((80, 30)))

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.help_button, 0, wx.LEFT, 10)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.select_button, 0, wx.LEFT, 10)
        hbox.Add(self.remove_button, 0, wx.LEFT | wx.RIGHT, 10)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.str_label, 0, wx.ALL, 10)
        vbox.Add(self.select_listbox, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        vbox.Add(hbox, 0, wx.TOP | wx.EXPAND, 10)

        self.select_panel.SetSizer(vbox)
    def Bind_EVT(self):
        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.select_listbox.Bind(wx.EVT_LISTBOX, self.select_list_EVT)

        self.select_button.Bind(wx.EVT_BUTTON, self.select_button_EVT)
        self.remove_button.Bind(wx.EVT_BUTTON, self.remove_button_EVT)
    def OnShow(self, event):
        self.select_listbox.Set([dirname for dirpath, dirname, filename in os.walk("book_cache") if dirname != []][0])
    def OnClose(self, event):
        self.select_bookname = ""
        self.Destroy()
    def select_list_EVT(self, event):
        self.select_button.Enable(True)
        self.remove_button.Enable(True)

        self.select_bookname = event.GetString()
    def select_button_EVT(self, event):
        self.Destroy()
    def remove_button_EVT(self, event):
        dlg = main_window.show_msgbox(self, "删除小说缓存", '是否确实要删除 "%s"？\n\n删除后需重新缓存' % self.select_bookname, style = wx.YES_NO | wx.ICON_WARNING)

        if dlg == wx.ID_YES:
            dir_path = os.path.join(os.getcwd(), "book_cache", self.select_bookname)
            shutil.rmtree(dir_path)

            self.OnShow(0)
if __name__ == "__main__":
    app = wx.App()
    book_core = BookCore()
    threadpool = ThreadPoolExecutor(max_workers = book_core.thread_amounts)
    html_core = HtmlCore()

    main_window = MainWindow(None)
    search_window = SearchWindow(main_window)
    parse_window = ParseBookWindow(main_window)
    shelf_window = ShelfWindow(main_window)

    main_window.Show()
    app.MainLoop()