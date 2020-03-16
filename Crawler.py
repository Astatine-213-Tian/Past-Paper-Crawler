from bs4 import BeautifulSoup
import requests

levels_dict = {"O-Level": "https://papers.gceguide.com/O%20Levels/", "AS & A-Level": "https://papers.gceguide.com/A%20Levels/", "IGCSE": "https://papers.gceguide.com/IGCSE/"}


def visit_level(level_url):  # Level_url is the url of selected level.
    subjects_dict = {}
    try:
        response = requests.get(level_url)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", class_="name"):
            if "error" not in link.get("href"):
                subject_name = link.get("href")
                subject_url = level_url + subject_name.replace(" ", "%20")
                subjects_dict[subject_name] = subject_url
        return subjects_dict
    except requests.exceptions.ConnectionError:
        return -1


def visit_subject(subject_url):  # Subject_url is the url of selected level.
    paper_dict = {}
    try:
        response = requests.get(subject_url)
        soup = BeautifulSoup(response.text,"html.parser")
        for link in soup.find_all("a", class_="name"):
            paper_year = link.get("href")
            paper_url = subject_url + "/" + paper_year
            paper_dict[paper_year] = paper_url
        return paper_dict
    except requests.exceptions.ConnectionError:
        return -1
