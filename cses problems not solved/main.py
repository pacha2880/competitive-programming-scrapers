import os
import sys
import csv
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://cses.fi"
START_URL = "https://cses.fi/problemset"
FINAL_CSV = "cses_unsolved_sorted.csv"

def parse_detail_counts(text):
    m = re.search(r"(\d+)\s*/\s*(\d+)", text.replace("\xa0", " "))
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))

def is_solved(task_li):
    score = task_li.find("span", class_="task-score")
    return bool(score and "full" in score.get("class", []))

def extract_task(task_li):
    a = task_li.find("a", href=True)
    detail = task_li.find("span", class_="detail")
    title = (a.get_text(strip=True) if a else "").strip()
    href = urljoin(BASE, a["href"]) if a else ""
    solved, total = parse_detail_counts(detail.get_text(" ", strip=True) if detail else "")
    return {"title": title, "url": href, "solved_count": solved, "solved": is_solved(task_li)}

def get_session():
    phpsessid = os.getenv("CSES_PHPSESSID", "").strip()
    if not phpsessid:
        print("ERROR: Define la variable de entorno CSES_PHPSESSID con tu cookie PHPSESSID.", file=sys.stderr)
        sys.exit(1)
    s = requests.Session()
    s.headers.update({"User-Agent": "CSES-Scraper/1.0", "Referer": START_URL})
    s.cookies.set("PHPSESSID", phpsessid, domain="cses.fi", path="/", secure=True)
    return s

def main():
    sess = get_session()
    resp = sess.get(START_URL, timeout=20)
    if resp.status_code != 200:
        print(f"ERROR HTTP {resp.status_code}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "html.parser")
    tasks = soup.select("li.task")

    # Filtrar no resueltos
    unsolved = []
    for li in tasks:
        t = extract_task(li)
        if not t["solved"] and isinstance(t["solved_count"], int):
            unsolved.append((t["title"], t["solved_count"], t["url"]))

    # Ordenar desc por cantidad de resoluciones
    unsolved.sort(key=lambda x: x[1], reverse=True)

    # Escribir CSV final
    with open(FINAL_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["problema", "personas_que_lo_resolvieron", "link"])
        for title, sc, link in unsolved:
            w.writerow([title, sc, link])
            print(f"[WRITE] {title} | {sc} | {link}")

    print(f"[DONE] CSV ordenado guardado en: {FINAL_CSV}")

if __name__ == "__main__":
    main()
