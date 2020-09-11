from bs4 import BeautifulSoup
import requests
import aiohttp
import asyncio

levels_dict = {"O-Level": "https://papers.gceguide.com/O%20Levels/",
               "AS & A-Level": "https://papers.gceguide.com/A%20Levels/", "IGCSE": "https://papers.gceguide.com/IGCSE/"}

failed_flag = False


def visit_level(level_url):  # Level_url is the url of selected level.
    subjects_dict = {}
    try:
        response = requests.get(level_url)
    except requests.exceptions.ConnectionError:
        return -1
    else:
        soup = BeautifulSoup(response.text, "lxml")
        for link in soup.find_all("a", class_="name"):
            if "error" not in link.get("href"):
                subject_name = link.get("href")
                subject_url = level_url + subject_name.replace(" ", "%20")
                subjects_dict[subject_name] = subject_url
        return subjects_dict


async def find_file(url, session):
    global failed_flag
    print(url, 'start')
    counter = 0
    while True:
        try:
            r = await session.get(url)
            html = await r.text()
            break
        except aiohttp.client_exceptions.ClientConnectorError:
            failed_flag = True
            return
        except asyncio.TimeoutError:
            counter += 1
            print(url, 'retry %d' % counter)
            if counter == 8:
                failed_flag = True
                return

    print(url, 'finished')
    file_info = {}
    soup = BeautifulSoup(html, "lxml")
    file_list = soup.find('ul', class_='paperslist')
    for link in file_list.find_all('li'):
        if link['class'][0] == 'file':
            paper_name = link.a.get("href")
            paper_url = url + "/" + paper_name
            file_info[paper_name] = paper_url
    # print('finished parsing')
    return file_info

paper_dict = {}


async def subject_loop(loop, urls):
    conn = aiohttp.TCPConnector(ssl=False)
    timeout = aiohttp.ClientTimeout(total=4)
    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
        print('\nAsync Crawling...')
        tasks = [loop.create_task(find_file(url, session)) for url in urls]
        finished, unfinished = await asyncio.wait(tasks)
        print(unfinished)
        results = [f.result() for f in finished]
        print(results)
        if failed_flag:
            return

        print('\nAnalysing...')
        for info in results:
            # print(count, title, url)
            paper_dict.update(info)


def visit_subject(subject_url):
    counter = 0
    while True:
        try:
            response = requests.get(subject_url, timeout=4)
            break
        except requests.exceptions.ConnectTimeout or requests.exceptions.ReadTimeout:
            counter += 1
            print(subject_url, counter)
            if counter == 5:
                return -1
        except requests.exceptions.ConnectionError:
            return -1
    soup = BeautifulSoup(response.text, "lxml")
    dir_urls = []
    file_list = soup.find('ul', class_='paperslist')
    for link in file_list.find_all('li'):
        if link['class'][0] == 'dir':
            dir_urls.append(subject_url + '/' + link.a.get('href'))
        elif link['class'][0] == 'file':
            paper_name = link.a.get("href")
            paper_url = subject_url + "/" + paper_name
            paper_dict[paper_name] = paper_url

    if dir_urls:
        # print(dir_urls)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(subject_loop(loop, dir_urls))

    if failed_flag:
        return -1
    return paper_dict


if __name__ == '__main__':
    visit_subject('https://papers.gceguide.com/A%20Levels/Accounting%20(9706)')
