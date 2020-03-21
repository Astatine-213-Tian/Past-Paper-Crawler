import pickle
import platform
import os
import getpass
import wx


def store(content, directory):
    with open(directory, "wb") as f:
        encrypt_data = pickle.dumps(content)
        pickle.dump(encrypt_data, f)


def load(directory):
    with open(directory, "rb") as f:
        data = pickle.load(f)
        data = pickle.loads(data)
    return data


def cache_folder():
    path = os.getcwd()
    if platform.system() == "Darwin":
        cache_path = path + "/Cache"
    else:
        cache_path = "C:\\Users\\" + getpass.getuser() + "\\AppData\\Local\\Temp\\Teresa.PastPaperCrawler"

    if not os.path.exists(cache_path):
        os.mkdir(cache_path)

    return cache_path


def customized_directory():
    customized_path = os.path.join(cache_folder(), "Customized")

    if not os.path.exists(customized_path):
        os.mkdir(customized_path)

    return customized_path


def preference_directory():
    preference_path = os.path.join(cache_folder(), "preference-config")

    if not os.path.exists(preference_path):
        # Default setting
        setting = {"Default path mode": False, "Default path": "", "Paper folder mode": True, "Skip exist file": True}
        store(setting, preference_path)

    return preference_path
