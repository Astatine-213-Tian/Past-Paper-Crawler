import pickle
import platform
import os
import getpass


def store(content, directory):
    with open(directory, "wb") as f:
        encrypt_data = pickle.dumps(content)
        pickle.dump(encrypt_data, f)


def load(directory):
    with open(directory, "rb") as f:
        data = pickle.load(f)
        data = pickle.loads(data)
    return data


def get_cache_directory():
    path = os.getcwd()
    if platform.system() == "Darwin":
        cache_path = "/Users/" + path.split("/")[2] + "/Library/Caches/Teresa.PastPaperCrawler"
    else:
        cache_path = "C:\\Users\\" + getpass.getuser() + "\\AppData\\Local\\Temp\\Teresa.PastPaperCrawler"

    if not os.path.exists(cache_path):
        os.mkdir(cache_path)

    return cache_path
