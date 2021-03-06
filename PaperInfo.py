import re


class Paper:
    def __init__(self, file_name, url):
        self.url = url
        self.season = "other"
        self.season_sort = 9
        self.year = "other"
        self.type = "other"
        self.num = "other"
        self.region = "other"

        pattern = re.compile(r'\d{4}_(\S)(\d{2})_(\S{2})_*(\w*).')  # Pattern for matching the f_in (subject code, season, year, paper number, region number
        match = re.match(pattern, file_name)

        if match:
            result = match.groups()

            if result[0] == "m":
                self.season = "March"
                self.season_sort = 0
            elif result[0] == "s":
                self.season = "May/June"
                self.season_sort = 1
            elif result[0] == "w":
                self.season = "November"
                self.season_sort = 2

            self.year = "20" + result[1]
            self.type = result[2]

            if result[3] and len(result[3]) <= 2:
                if len(result[3]) == 1:
                    self.num = "Paper " + result[3][0]
                elif result[3][0] == "0":
                    self.num = "Paper " + result[3][1]
                else:
                    self.num = "Paper " + result[3][0]
                    self.region = "Region " + result[3][1]


class Pair:  # Class for storing information of ms and qp in pairs
    def __init__(self, qp, ms):
        self.url = [qp.url, ms.url]
        self.year = qp.year
        self.season = qp.season
        self.num = qp.num
        self.region = qp.region if qp.region != "other" else ""

    def display(self):
        if self.region:
            return self.year + " " + self.season + " " + self.num + " " + self.region
        else:
            return self.year + " " + self.season + " " + self.num
