import os
import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

TOP_N = 100  # 数量上限
DATA_DIR = "data"
URL = "https://stackoverflow.com/questions"
PERIOD_URLS = {"hot": "?tab=Hot", "active": "?tab=Active", "newest": "?tab=Newest"}
API_URL = "https://api.stackexchange.com/2.3/questions"

# 提取数字
def get_number(text):
    result = re.search(r"[\d,.]+", text.replace(",", ""))
    return int(float(result.group().replace(",", ""))) if result else 0

# 请求网页
def get_questions(period):
    response = requests.get(URL + PERIOD_URLS[period], headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("div.s-post-summary")
    data = []

    # 解析问题
    for row in rows[:TOP_N]:
        link = row.select_one("h3 a")
        if link is None:
            continue
        stats = row.select("div.s-post-summary--stats-item")
        tags = row.select("a.s-tag")
        excerpt = row.select_one("div.s-post-summary--content-excerpt")
        data.append({
            "period": period,
            "title": link.get_text(" ", strip=True),
            "description": excerpt.get_text(" ", strip=True) if excerpt else "",
            "tags": " ".join(tag.get_text(strip=True) for tag in tags),
            "votes": get_number(stats[0].get_text(" ", strip=True)) if len(stats) > 0 else 0,
            "answers": get_number(stats[1].get_text(" ", strip=True)) if len(stats) > 1 else 0,
            "views": get_number(stats[2].get_text(" ", strip=True)) if len(stats) > 2 else 0,
            "url": "https://stackoverflow.com" + link.get("href", ""),
        })
    return data

# 网页受限时使用接口
def get_questions_api(period):
    params = {"order": "desc", "sort": "hot", "site": "stackoverflow", "pagesize": TOP_N}
    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()
    data = []
    for item in response.json().get("items", [])[:TOP_N]:
        data.append({
            "period": period,
            "title": item.get("title", ""),
            "description": "",
            "tags": " ".join(item.get("tags", [])),
            "votes": item.get("score", 0),
            "answers": item.get("answer_count", 0),
            "views": item.get("view_count", 0),
            "url": item.get("link", ""),
        })
    return data

# 保存数据
def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    all_data = []
    for period in PERIOD_URLS:
        try:
            print("正在爬取", period)
            try:
                all_data.extend(get_questions(period))
            except requests.HTTPError:
                all_data.extend(get_questions_api(period))
            time.sleep(2)
        except requests.RequestException as error:
            print("爬取失败", period, error)
    result = pd.DataFrame(all_data)
    result.to_csv(os.path.join(DATA_DIR, "stackoverflow_questions.csv"), index=False, encoding="utf-8-sig")
    print("保存数据", len(result))


if __name__ == "__main__":
    main()
