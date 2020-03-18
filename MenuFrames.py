import wx
import os
import platform
import subprocess
import Cache


class AboutFrame(wx.Frame):
    def __init__(self, call):
        wx.Frame.__init__(self, None, -1, size=(300, 160), style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        title = wx.StaticText(self, label="Past Paper Crawler")
        title_font = wx.Font(wx.FontInfo(13).Bold().FaceName("Arial"))
        title.SetFont(title_font)

        version = wx.StaticText(self, label="Version 1.3.0")
        team = wx.StaticText(self, label="Made by Teresa, John, Ethan, and Peter")
        maintenance = wx.StaticText(self, label="Currently maintained by Teresa")
        thanks = wx.StaticText(self, label="Inspired by Past Paper Crawler created by Raymond")

        content_font = wx.Font(wx.FontInfo(10))
        version.SetFont(content_font)
        team.SetFont(content_font)
        maintenance.SetFont(content_font)
        thanks.SetFont(content_font)

        bottom_border = 10
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title, flag=wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, border=bottom_border | bottom_border)
        sizer.Add(version, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=bottom_border)
        sizer.Add(team, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=bottom_border)
        sizer.Add(maintenance, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=bottom_border)
        sizer.Add(thanks, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=bottom_border)

        self.SetSizer(sizer)

        self.call = call
        self.Bind(wx.EVT_CLOSE, self.on_close, self)

    def on_close(self, event):
        self.Destroy()
        self.call()


class PreferencesFrame(wx.Frame):
    def __init__(self, call):
        wx.Frame.__init__(self, None, style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX, size=(400, 485))
        self.init_UI()
        self.call = call
        self.Bind(wx.EVT_CLOSE, self.on_close, self)

    def init_UI(self):
        preference = wx.Notebook(self)
        preference.AddPage(GeneralPanel(preference), "General")
        preference.AddPage(CachePanel(preference), "Cache")
        self.Show()

    def on_close(self, event):
        self.Destroy()
        self.call()


class GeneralPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.config_path = Cache.preference_directory()
        self.current_setting = Cache.load(self.config_path)

        hint_txt = wx.StaticText(self, label="Download path:")
        self.default_directory = wx.StaticText(self, label="")
        ask_radio_button = wx.RadioButton(self, label="Ask every time")
        default_radio_button = wx.RadioButton(self, label="Use default path")
        if self.current_setting["Default path mode"]:
            default_radio_button.SetValue(True)
            self.default_directory.SetLabel(self.current_setting["Default path"])
        else:
            ask_radio_button.SetValue(True)

        self.Bind(wx.EVT_RADIOBUTTON, self.on_radio_button)

        change_button = wx.Button(self, label="change", size=(65, -1))
        self.Bind(wx.EVT_BUTTON, self.on_change_path, change_button)

        set_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        set_path_sizer.Add(default_radio_button, flag=wx.ALIGN_CENTER_VERTICAL)
        set_path_sizer.Add(change_button, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=5)

        border = 10

        general_sizer = wx.BoxSizer(wx.VERTICAL)
        general_sizer.Add(hint_txt, flag=wx.LEFT | wx.TOP, border=border)
        general_sizer.AddSpacer(5)
        general_sizer.Add(ask_radio_button, flag=wx.LEFT, border=border)
        general_sizer.AddSpacer(3)
        general_sizer.Add(set_path_sizer, flag=wx.LEFT, border=border)
        general_sizer.AddSpacer(2)
        general_sizer.Add(self.default_directory, flag=wx.LEFT, border=25)
        self.SetSizer(general_sizer)

    def on_radio_button(self, event):
        choice = event.GetEventObject()
        if choice.GetLabel() == "Use default path":
            self.current_setting["Default path mode"] = True
        else:
            self.current_setting["Default path mode"] = False
        Cache.store(self.current_setting, self.config_path)

    def on_change_path(self, event):
        dlg = wx.DirDialog(self, "Choose the default folder for past paper")
        if dlg.ShowModal() == wx.ID_OK:
            folder_directory = dlg.GetPath()
            self.current_setting["Default path"] = folder_directory
            self.default_directory.SetLabel(folder_directory)
            Cache.store(self.current_setting, self.config_path)
            dlg.Destroy()
        else:
            dlg.Destroy()
            return


class CachePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        explain_txt = wx.StaticText(self, label="Past Paper Crawler caches viewed web pages to memory \nand disk to boost efficiency.")
        hint_txt = wx.StaticText(self, label="Current cache on the disk:")
        open_button = wx.Button(self, label="open folder")
        self.Bind(wx.EVT_BUTTON, self.on_open, open_button)

        self.cache_folder = Cache.customized_directory()
        cache_list = sorted([file for file in os.listdir(self.cache_folder) if not file.startswith(".")])
        self.cache_checklist = wx.CheckListBox(self, choices=cache_list, size=(0, 295))

        open_cache_sizer = wx.BoxSizer(wx.HORIZONTAL)
        open_cache_sizer.Add(hint_txt, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        open_cache_sizer.Add(open_button, flag=wx.ALIGN_CENTER_VERTICAL)

        select_all_button = wx.Button(self, label="Select all")
        self.Bind(wx.EVT_BUTTON, self.on_select_all, select_all_button)
        remove_button = wx.Button(self, label="Remove")
        self.Bind(wx.EVT_BUTTON, self.on_remove, remove_button)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(select_all_button)
        button_sizer.Add(remove_button, flag=wx.LEFT, border=8)

        cache_sizer = wx.BoxSizer(wx.VERTICAL)
        cache_sizer.Add(explain_txt, flag=wx.ALL, border=10)
        cache_sizer.Add(open_cache_sizer, flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)
        cache_sizer.Add(self.cache_checklist, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
                        border=10)
        cache_sizer.Add(button_sizer, flag=wx.ALIGN_RIGHT | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)
        self.SetSizer(cache_sizer)

    def on_open(self, event):
        if platform.system() == "Darwin":
            subprocess.call(["open", self.cache_folder])
        else:
            subprocess.Popen("explorer %s" % self.cache_folder)
            
    def on_select_all(self, event):
        if len(self.cache_checklist.GetCheckedItems()) != self.cache_checklist.GetCount():
            self.cache_checklist.SetCheckedItems(range(self.cache_checklist.GetCount()))
        else:
            for i in range(self.cache_checklist.GetCount()):
                self.cache_checklist.Check(i, check=False)
    
    def on_remove(self, event):
        for file in self.cache_checklist.GetCheckedStrings():
            path = os.path.join(self.cache_folder, file)
            os.remove(path)

        # Update cache list
        cache_list = sorted([file for file in os.listdir(self.cache_folder) if not file.startswith(".")])
        self.cache_checklist.Set(cache_list)


if __name__ == '__main__':
    app = wx.App()
    frame = PreferencesFrame(None)
    frame.Show()
    app.MainLoop()
