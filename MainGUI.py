import time
import Crawler
import DownloadModule
from MenuFrames import *
from PaperInfo import Paper, Pair


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Past paper Crawler", size=(520, 565))

        self.preference_path = Cache.preference_directory()

        level_list = ["--- Select level ---", "IGCSE", "AS & A-Level", "O-Level"]
        self.type_dict = {"All types": "All types", "Question Paper": "qp", "Mark Scheme": "ms", "Examiner Report": "er", "Grade Threshold": "gt", "Specimen Paper": "sp", "other": "other"}
        self.subject_dict = {}  # A dictionary of subjects available return from Crawler. (key: subject name, value: subject url)
        self.paper_dict = {}  # A dictionary of papers available return from Crawler. (key: f_in name, [value]: paper ur)
        self.paired = True

        self.directory = ""  # Record the root folder the user choose to save the f_in
        self.year, self.season, self.num, self.region, self.type = "All years", "All seasons", "All papers", "All regions", "All types"  # Record the subject, season, num, region, chosen by the user

        self.pairs_info = {}  # Store the information of question paper and corresponding mark scheme
        self.files_info = {}  # Store the information of each individual f_in

        self.level_choice = wx.Choice(self, choices=level_list)  # Choosing the level
        self.level_choice.Bind(wx.EVT_CHOICE, self.level_chosen)

        self.subject_choice = wx.Choice(self, choices=[])  # Choosing the subject
        self.subject_choice.Bind(wx.EVT_CHOICE, self.subject_chosen)

        self.year_choice = wx.Choice(self, size=(90, -1))  # Choosing the year
        self.year_choice.Bind(wx.EVT_CHOICE, self.year_chosen)

        self.season_choice = wx.Choice(self, size=(90, -1))  # Choosing the season
        self.season_choice.Bind(wx.EVT_CHOICE, self.season_chosen)

        self.num_choice = wx.Choice(self, size=(90, -1))  # Choosing the paper number
        self.num_choice.Bind(wx.EVT_CHOICE, self.num_chosen)

        self.region_choice = wx.Choice(self, size=(90, -1))  # Choosing the region
        self.region_choice.Bind(wx.EVT_CHOICE, self.region_chosen)

        txt_filter = wx.StaticText(self, label="Filter:")
        self.style_choice = wx.Choice(self, size=(160, -1))  # Choosing the display style
        self.style_choice.Bind(wx.EVT_CHOICE, self.style_chosen)
        self.hint = wx.StaticText(self)

        download = wx.Button(self, label="Download", size=(60, -1))  # Download button
        self.Bind(wx.EVT_BUTTON, self.pre_download, download)

        self.type_choice = wx.Choice(self, size=(40, -1), choices=[key for key in self.type_dict])
        self.type_choice.Bind(wx.EVT_CHOICE, self.type_chosen)
        self.type_choice.Hide()

        self.paper_checklist = wx.CheckListBox(self)  # Check list box to display papers avaliable for downloading

        select_all = wx.Button(self, label="Select All", size=(60, -1))  # Select all button
        self.Bind(wx.EVT_BUTTON, self.select_all, select_all)

        config = Cache.load(self.preference_path)
        self.level_choice.SetSelection(config["Default level"])
        self.level_chosen(None)

        # Arranging boxes
        sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        sizer_filter = wx.BoxSizer(wx.HORIZONTAL)
        sizer_paper_checklist = wx.BoxSizer(wx.HORIZONTAL)
        sizer_hint = wx.BoxSizer(wx.HORIZONTAL)
        sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)

        sizer_top.Add(self.level_choice, proportion=1, flag= wx.RIGHT, border=15)
        sizer_top.Add(self.subject_choice, proportion=1, flag=wx.ALIGN_RIGHT)

        sizer_filter.Add(txt_filter, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL, border=10)
        sizer_filter.Add(self.year_choice, proportion=1, flag=wx.LEFT, border=10)
        sizer_filter.Add(self.season_choice, proportion=1, flag=wx.LEFT, border=10)
        sizer_filter.Add(self.num_choice, proportion=1, flag=wx.LEFT, border=10)
        sizer_filter.Add(self.region_choice, proportion=1, flag=wx.LEFT, border=10)

        sizer_paper_checklist.Add(self.paper_checklist, proportion=1, flag=wx.EXPAND)

        sizer_hint.Add(self.hint, proportion=0)

        sizer_bottom.Add(self.style_choice, proportion=1, flag=wx.ALIGN_LEFT)
        sizer_bottom.Add(self.type_choice, proportion=1, flag=wx.LEFT | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, border=5)
        sizer_bottom.Add(select_all, proportion=1, flag=wx.LEFT, border=15)
        sizer_bottom.Add(download, proportion=1, flag=wx.ALIGN_RIGHT | wx.LEFT, border=5)

        sizer_all = wx.BoxSizer(wx.VERTICAL)
        side_border = 25
        bottom_border = 12

        sizer_all.Add(sizer_top, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=side_border)
        sizer_all.AddSpacer(bottom_border)
        sizer_all.Add(sizer_filter, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=side_border)
        sizer_all.AddSpacer(bottom_border)
        sizer_all.Add(sizer_paper_checklist, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=side_border)
        sizer_all.AddSpacer(bottom_border)
        sizer_all.Add(sizer_hint, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=side_border)
        sizer_all.AddSpacer(bottom_border)
        sizer_all.Add(sizer_bottom, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=side_border)

        self.SetSizer(sizer_all)

        # initialize menu
        menu_bar = wx.MenuBar()
        menu = wx.Menu()

        self.about = wx.MenuItem(menu, wx.ID_ABOUT, "About Past Paper Crawler")
        self.Bind(wx.EVT_MENU, self.on_about, self.about)
        menu.Append(self.about)

        self.preferences = wx.MenuItem(menu, wx.ID_PREFERENCES, '&Preferences...\tCtrl+,')
        self.Bind(wx.EVT_MENU, self.on_preferences, self.preferences)
        menu.Append(self.preferences)

        # For different system
        if platform.system() == "Darwin":
            menu_bar.Append(menu, " ")
        else:
            menu_bar.Append(menu, "File")

        self.SetMenuBar(menu_bar)

    def on_about(self, event):
        about_frame = AboutFrame(self.rebind_about)
        about_frame.Show()
        self.Unbind(wx.EVT_MENU, self.about)

    def on_preferences(self, event):
        preferences_frame = PreferencesFrame(self.rebind_preferences)
        preferences_frame.Show()
        self.Unbind(wx.EVT_MENU, self.preferences)

    def rebind_about(self):
        self.Bind(wx.EVT_MENU, self.on_about, self.about)

    def rebind_preferences(self):
        self.Bind(wx.EVT_MENU, self.on_preferences, self.preferences)

    def init_choice(self):
        self.paper_checklist.Clear()
        self.year_choice.Clear()
        self.season_choice.Clear()
        self.num_choice.Clear()
        self.region_choice.Clear()
        self.pairs_info = {}
        self.files_info = {}

        self.year, self.season, self.num, self.region, self.type = "All years", "All seasons", "All papers", "All regions", "All types"  # Record the subject, season, num, region, chosen by the user

    def level_chosen(self, event):
        self.init_choice()
        self.subject_choice.Clear()
        if self.level_choice.GetSelection() == 0:
            return
        else:
            level = self.level_choice.GetStringSelection()  # Get level chosen

        # Cache
        cache_folder = Cache.customized_directory()
        cache_subject = os.path.join(cache_folder, "GCE Guide %s" % level)
        if not os.path.exists(cache_subject):
            self.subject_dict = Crawler.visit_level(Crawler.levels_dict[level])  # Return subject list
            if self.subject_dict == -1:  # Connection error
                wx.MessageBox("Please check your Internet connection and retry.", "Connection Error")
                self.level_choice.SetSelection(0)
                return
            else:
                Cache.store(self.subject_dict, cache_subject)
        else:
            self.subject_dict = Cache.load(cache_subject)

        subject_list = ["----- Select subject -----"] + [each for each in self.subject_dict]
        self.subject_choice.Set(subject_list)  # Update subject list
        self.subject_choice.SetSelection(0)

    def subject_chosen(self, event):
        self.init_choice()

        subject_index = self.subject_choice.GetSelection()  # Get subject chosen
        # If no subject is chosen
        if subject_index == 0:
            return
        else:
            subject = self.subject_choice.GetStringSelection()

        # Cache
        cache_folder = Cache.customized_directory()
        cache_paper = os.path.join(cache_folder, "GCE Guide %s" % subject)
        if not os.path.exists(cache_paper):
            subject_url = self.subject_dict[subject]
            self.paper_dict = Crawler.visit_subject(subject_url)  # Get paper list
            if self.paper_dict == -1:  # Connection error
                wx.MessageBox("Please check your Internet connection and retry.", "Connection Error")
                self.subject_choice.SetSelection(0)
                return
            else:
                Cache.store(self.paper_dict, cache_paper)
        else:
            self.paper_dict = Cache.load(cache_paper)

        years, nums, regions = [], [], []  # Store all exist year, paper number, and region

        files_info = {}
        for file, url in self.paper_dict.items():
            paper = Paper(file, url)
            files_info[file] = paper
            years.append(paper.year)
            nums.append(paper.num)
            regions.append(paper.region)

        year_list = ["All years"] + sorted(list(set(years)))
        season_list = ("All seasons", "March", "May/June", "November", "other")
        num_list = ["All papers"] + sorted(list(set(nums)))
        region_list = ["All regions"] + sorted(list(set(regions)))

        files_info = sorted(files_info.items(), key=lambda files_info: (files_info[1].year, files_info[1].season_sort))
        self.files_info = dict(files_info)

        qp, ms = [], []  # Store question paper and mark scheme for pairing
        for paper in self.files_info.values():
            if paper.year != "other" and int(paper.year) > 2004:
                if paper.type == "qp":
                    qp.append(paper)
                elif paper.type == "ms":
                    ms.append(paper)

        for i in range(len(qp)):
            for each in ms:
                if qp[i].year == each.year and qp[i].season == each.season and qp[i].num == each.num and qp[i].region == each.region:
                    pair = Pair(qp[i], each)
                    del each
                    self.pairs_info[pair.display()] = pair
                    break

        self.year_choice.Set(year_list)
        self.year_choice.SetSelection(0)
        self.season_choice.Set(season_list)
        self.season_choice.SetSelection(0)
        self.num_choice.Set(num_list)
        self.num_choice.SetSelection(0)
        self.region_choice.Set(region_list)
        self.region_choice.SetSelection(0)

        self.style_choice.Set(["Select All QP & MS in pairs", "Select all individual files"])
        self.style_choice.SetSelection(0)
        self.style_chosen(None)

        if self.paired:  # Display information according to the display style
            self.paper_checklist.Set([each for each in self.pairs_info])
        else:
            self.paper_checklist.Set([each for each in self.files_info])

    def year_chosen(self, event):  # when year is chosen
        self.year = self.year_choice.GetStringSelection()
        if self.paired:
            self.filter_pairs()
        else:
            self.filter_files()

    def season_chosen(self, event):  # when season is chosen
        self.season = self.season_choice.GetStringSelection()
        if self.paired:
            self.filter_pairs()
        else:
            self.filter_files()

    def num_chosen(self, event):  # when paper number is chosen
        self.num = self.num_choice.GetStringSelection()
        if self.paired:
            self.filter_pairs()
        else:
            self.filter_files()

    def region_chosen(self, event):  # when region is chosen
        self.region = self.region_choice.GetStringSelection()
        if self.paired:
            self.filter_pairs()
        else:
            self.filter_files()

    def type_chosen(self, event):
        self.type = self.type_dict[self.type_choice.GetStringSelection()]
        self.filter_files()

    def filter_files(self):  # filter individual files which meet the requirement
        to_filter = self.files_info.copy()
        if self.year != "All years":
            to_filter = {file_name: file_object for file_name, file_object in to_filter.items() if
                         file_object.year == self.year}
        if self.season != "All seasons":
            to_filter = {file_name: file_object for file_name, file_object in to_filter.items() if
                         file_object.season == self.season}
        if self.num != "All papers":
            to_filter = {file_name: file_object for file_name, file_object in to_filter.items() if
                         file_object.num == self.num}
        if self.region != "All regions":
            to_filter = {file_name: file_object for file_name, file_object in to_filter.items() if
                         file_object.region == self.region}
        if self.type != "All types":
            to_filter = {file_name: file_object for file_name, file_object in to_filter.items() if
                         file_object.type == self.type}

        self.files_list = [file for file in to_filter]
        self.paper_checklist.Set(self.files_list)

    def filter_pairs(self):  # filter paired files which meet the requirement
        to_filter = self.pairs_info.copy()
        if self.year != "All years":
            to_filter = {pair_name: pair_object for pair_name, pair_object in to_filter.items() if
                         pair_object.year == self.year}
        if self.season != "All seasons":
            to_filter = {pair_name: pair_object for pair_name, pair_object in to_filter.items() if
                         pair_object.season == self.season}
        if self.num != "All papers":
            to_filter = {pair_name: pair_object for pair_name, pair_object in to_filter.items() if
                         pair_object.num == self.num}
        if self.region != "All regions":
            to_filter = {pair_name: pair_object for pair_name, pair_object in to_filter.items() if
                         pair_object.region == self.region}

        self.paper_checklist.Set([pair for pair in to_filter])

    def style_chosen(self, event):  # when display style was chosen
        self.paired = True if self.style_choice.GetSelection() == 0 else False
        if self.paired:
            self.hint.SetLabel("Papers and answers before 2005 are omitted. ")
            self.type_choice.Hide()
            self.filter_pairs()
        else:
            self.hint.SetLabel("All files are shown. ")
            self.filter_files()
            self.type_choice.Show()

    def select_all(self, event):  # when select all is pressed
        if self.paired:
            if len(self.paper_checklist.GetCheckedItems()) != self.paper_checklist.GetCount():
                self.paper_checklist.SetCheckedItems(range(self.paper_checklist.GetCount()))
            else:
                for i in range(self.paper_checklist.GetCount()):
                    self.paper_checklist.Check(i, check=False)
        else:
            if len(self.paper_checklist.GetCheckedItems()) != self.paper_checklist.GetCount():
                self.paper_checklist.SetCheckedItems(range(self.paper_checklist.GetCount()))
            else:
                for i in range(self.paper_checklist.GetCount()):
                    self.paper_checklist.Check(i, check=False)

    def pre_download(self, event):
        config = Cache.load(self.preference_path)
        if config["Default path mode"]:
            folder_directory = config["Default path"]
            if not os.path.exists(folder_directory):
                wx.MessageBox("Default download path does not exist. \nPlease go to preference and reset the path.",
                              "Folder not found")
                return
        else:
            dlg = wx.DirDialog(self, "Choose the root folder for past paper")
            if dlg.ShowModal() == wx.ID_OK:
                folder_directory = dlg.GetPath()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return

        self.directory = os.path.join(folder_directory, self.subject_choice.GetStringSelection())
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        selected_paper = self.paper_checklist.GetCheckedStrings()
        if not selected_paper:
            return

        urls = []
        if self.paired:
            for each in selected_paper:
                urls.append(self.pairs_info[each].url[0])
                urls.append(self.pairs_info[each].url[1])
        else:
            for each in selected_paper:
                urls.append(self.files_info[each].url)

        self.download(urls)

    def download(self, urls):  # when download button is pressed
        total_files = len(urls)
        DownloadModule.download_thread(urls, self.directory)

        # Show progress
        progress_bar = wx.ProgressDialog("Progress", "Start downloading files", maximum=total_files, parent=self,
                                         style=wx.PD_CAN_ABORT)
        time.sleep(1)
        while DownloadModule.running:
            if progress_bar.WasCancelled():
                DownloadModule.control = 1
                progress_bar.Destroy()
                wx.MessageBox("Download is cancelled.")
                break

            status = DownloadModule.status
            progress_bar.Update(status['F'], "Finish downloading %d/%d files" % (status['F'], total_files))
            time.sleep(1)

        error_files = DownloadModule.failed_names
        # selected_paper = self.paper_checklist.GetCheckedItems()
        if error_files:
            progress_bar.Destroy()
            retry_frame = RetryFrame(self, error_files, self.call_back)
            retry_frame.ShowModal()

            # for each in selected_paper:
            #     if each not in error_files:
            #         self.paper_checklist.Check(each, check=False)
        else:
            progress_bar.Update(total_files)
            # for each in selected_paper:
            #     self.paper_checklist.Check(each, check=False)

    def call_back(self, value):  # Link with RetryFrame
        if value:
            retry_urls = [self.paper_dict[each] for each in value]
            self.download(retry_urls)


class RetryFrame(wx.Dialog):  # New frame to display f_in that need to retry
    def __init__(self, parent, retry_files, call):
        wx.Dialog.__init__(self, parent, size=(300, 355))
        hint = wx.StaticText(self, label="Failed to download:")
        self.retry_file = wx.CheckListBox(self, size=(-1, 250), choices=retry_files)
        self.retry_file.SetCheckedItems(range(len(retry_files)))
        retry_button = wx.Button(self, size=(75, -1), label="Retry")
        self.Bind(wx.EVT_BUTTON, self.retry, retry_button)

        retry_sizer = wx.BoxSizer(wx.VERTICAL)
        retry_sizer.AddSpacer(10)
        retry_sizer.Add(hint, flag=wx.LEFT, border=15)
        retry_sizer.AddSpacer(10)
        retry_sizer.Add(self.retry_file, flag=wx.RIGHT|wx.LEFT|wx.EXPAND, border=15)
        retry_sizer.AddSpacer(10)
        retry_sizer.Add(retry_button, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=15)
        retry_sizer.AddSpacer(3)
        self.SetSizer(retry_sizer)

        self.call = call

        self.code = self.GetReturnCode()
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        self.EndModal(self.code)

    def retry(self, event):
        self.EndModal(self.code)
        self.call(self.retry_file.GetCheckedStrings())


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
