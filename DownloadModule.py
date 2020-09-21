import threading
import ssl
import urllib.request as rq
import urllib.error
import time
import os

ssl._create_default_https_context = ssl._create_unverified_context
forge_agent_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

all_tasks = []
error_flags = []  # 0: Normal. 1: Download finished. 2: Download Error. 8: Internet connection Error

# Final flags for external packages
running = False
control = 0  # 0: Normal. 1: Ask for shut down.
status = {}
failed_names = []


def _download_single(url, to, id):
    """
    Download a URL f_in to a dir.
    :param url: URL to download from.
    :param to: Full directory. Includes f_in and its suffix. e.g. ./files/9709_s16_ms_21.pdf
    :return: None
    """
    if os.path.exists(to):
        error_flags[id] = 1
        return

    try:
        request = rq.Request(url=url, headers=forge_agent_header)
        info = rq.urlopen(request).read()

    except urllib.error.URLError as e:
        print(url, 'urllib error')
        error_flags[id] = 2
        return

    except Exception as e:
        print(url, e)
        error_flags[id] = 2
        return

    with open(to, "wb") as file:
        print(url, 'writing')
        file.write(info)

    error_flags[id] = 1


class DownloadTask():
    def __init__(self, url, to_dir, id):

        if not to_dir.endswith("/"):
            to_dir += "/"

        self.url = url
        self.file_loc = to_dir + url.split("/")[-1]
        self.status = "Q"  # Status: Q - Queueing; D - Downloading; T - Timeout; R - timeout Retry; E - Error; F - Finished
        self.failed_count = 0
        self.trial_start = 0  # Time stamp of trial start
        self.id = id
        self.thread = None

    def download(self):
        if self.status == "Q":
            self.status = "D"
        elif self.status == "T":
            self.status = "R"
        else:
            return

        self.trial_start = time.time()

        self.thread = threading.Thread(target=_download_single, args=(self.url, self.file_loc, self.id))
        self.thread.setDaemon(True)
        self.thread.start()

    def update_status(self, flag):
        """
        Status flow of a document:

        |<- Queueing ->|  <---- Download ----->  | <-----  Task closed ----->  |
        |              |                         |                             |

                                            <Successful>
        [Q] -----------> [D] --------------->--------------->------|
                                     |                             |
                                     | <Unsuccessful>              |
                                     v                             |
            |----------------------<--                             |
            v                        ^                             v
            |                        |                             -->-----> [F*]
            |                        |    <Failed >= 5 times>      ^
            |                        |-->------------------>[E*]   |
            |                        |                             |
            |                        | <Unsuccessful>              |
            v                        |                             |
           [T]----------> [R]---->-------------------------->------|
                                         <Successful>


        *: Task finished. Close task.


        :param flag:
        :return:
        """
        max_attempts = 5

        if flag == 0:
            pass
        elif flag == 1:
            self.status = "F"
        elif flag == 2:
            self.failed_count += 1
            if self.status == "D":
                self.status = "T"

            elif self.status == "R":
                if self.failed_count >= max_attempts:  # Mark as failed if failed five times.
                    self.status = "E"
                else:
                    self.status = "T"  # Mark as time out and try again.


def statistics(update_global=True):
    """
    Current statistics of the download.
    :param update_global: To update the global variable.
    :return: <Dict> information of downloading task. See the Task Class for explainations.
    """
    info = {
        "Q": 0,
        "D": 0,
        "T": 0,
        "R": 0,
        "E": 0,
        "F": 0
    }

    for task in all_tasks:
        info[task.status] += 1

    global status
    if update_global:
        status = info
    else:
        status = {}

    return info


def download(urls, to_dir, threads=10, timeout=10):
    """
    Download multiple URLs at the same time.

    :param urls: [Array of String] URLs to download. e.g. [.../9709_s16_ms_21.pdf, .../9709_s16_ms_22.pdf]
    :param to_dir: String, directory to download e.g. "./9709/"
    :param threads: Number of files downloading at the same time
    :param timeout: [int] Time in seconds for timeout. When timeout a new same thread will be started.
    :return: [Array of String] Failed files
    """

    # Constant Parameters
    refresh_time = 0.1

    # Setup
    global all_tasks, error_flags
    all_tasks = []
    error_flags = []
    for count in range(len(urls)):
        all_tasks.append(DownloadTask(urls[count], to_dir, count))
        error_flags.append(False)

    # Final flags
    global running, status, failed_names, control
    running = True
    status = {}
    failed_names = []

    # Main
    while statistics()["E"] + statistics()["F"] < len(urls):

        # Start tasks
        for task in all_tasks:
            info = statistics()
            running = info["D"] + info["R"]

            if running >= threads:  # Max threads reached
                break

            if task.status == "F" or task.status == "E":  # Ended tasks
                continue
            elif info["Q"] > 0:  # Prioritize untested tasks
                if task.status == "R":
                    continue
            task.download()

        # Timeout check
        for count in range(len(all_tasks)):
            if time.time() - all_tasks[count].trial_start > timeout and \
                    (all_tasks[count].status == "D" or all_tasks[count].status == "R"):
                error_flags[count] = 2

        # Clear flags
        for count in range(len(error_flags)):
            all_tasks[count].update_status(error_flags[count])
            error_flags[count] = 0  # Reset flag

        # External order check
        if control == 1:
            for count in range(len(all_tasks)):
                if all_tasks[count].status != "F":
                    all_tasks[count].status = "E"

        control = 0  # Reset the flag

        # print(time.strftime("%H:%M:%S", time.localtime()), statistics())
        time.sleep(refresh_time)

    failed = []
    for task in all_tasks:
        if task.status == "E":
            failed.append(task.url.split("/")[-1])

    failed_names = failed
    running = False


def download_thread(urls, to_dir, threads=10, timeout=10):
    the_thread = threading.Thread(target=download, args=(urls, to_dir, threads, timeout))
    the_thread.start()
