from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService


class VjudgeContestScrapper:
    
    def __init__(this, ignore, driver_path=""):
        this.chrome_driver_path = driver_path
        this.chrome_service = ChromeService(this.chrome_driver_path)
        this.ignore = ignore
    
    # Open the webpage
    def get_rank(this, contest_id):
        driver = webdriver.Chrome(service=this.chrome_service)
        url = "https://vjudge.net/contest/" + contest_id + "#rank"
        driver.get(url)
        
        driver.implicitly_wait(10)
        
        # get the table
        table = driver.find_element(By.ID, "contest-rank-table")
        rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
        
        rank = {}
        print("processing contest", contest_id)

        for row in rows:
            # only process rows with the same contest id
            if row.get_attribute("data-c") != contest_id:
                continue

            # get the username
            team_td = row.find_element(By.CLASS_NAME, "team.meta")
            team_link = team_td.find_element(By.TAG_NAME, "a")
            team_href = team_link.get_attribute("href")
            username = team_href.split("/")[-1]
            print("User:", username)
            if username in this.ignore:
                username = "pacha"
                # print("Ignored")
                # continue
            if username == "alexalvarez":
                username = "alexrm"

            # get the solved count
            solved_td = row.find_element(By.CLASS_NAME, "solved.meta")
            solved_count = solved_td.find_element(By.TAG_NAME, "span").text
            print(f"Solved: {solved_count}")

            # get the penalty minute
            penalty_td = row.find_element(By.CLASS_NAME, "penalty.meta")
            penalty_minute = penalty_td.find_element(By.CLASS_NAME, "minute").text
            print(f"Penalty Minute: {penalty_minute}")

            # add the user to the rank
            rank[username] = [int(solved_count), int(penalty_minute)]

        driver.quit()
        return rank
    
    def get_total_rank(this, contests_ids):
        total_rank = {}
        for contest_id in contests_ids:
            rank = this.get_rank(contest_id=contest_id)
            for key in rank:
                if key in total_rank:
                    total_rank[key][0] += rank[key][0]
                    total_rank[key][1] += rank[key][1]
                else:
                    total_rank[key] = rank[key]
        return sorted(total_rank.items(), key=lambda x: (-int(x[1][0]), int(x[1][1])))


if __name__ == "__main__":
    scrapper = VjudgeContestScrapper(
        ignore={"pacha2880", "donpeyote", "percebe", "eldorado", "elsabandija", "toborochi", "obi", "maestrito"},
        driver_path="chromedriver.exe"
    )
    contests = []
    with open("contests.txt", "r") as f:
        for line in f:
            contests.append(line.strip())
    rank = scrapper.get_total_rank(contests)
    
    with open("rank.txt", "w") as f:
        for r in rank:
            f.write(f"{r[0]} {r[1][0]} {r[1][1]}\n")