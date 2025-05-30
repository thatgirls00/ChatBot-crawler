import urllib3
import requests
from bs4 import BeautifulSoup
import pymysql
import hashlib
from datetime import datetime
import re
import os
from dotenv import load_dotenv

# .env 로드
load_dotenv(dotenv_path="/root/hknu_scraper/.env")

def clean_menu_text(text):
    text = text.strip()
    text = re.sub(r"^-+", "", text)  # 앞 하이픈 제거
    text = text.replace("(통합)", "")
    return text.strip()

def run_dorm_meal():
    print("🍽️ 한경국립대학교 기숙사식당 식단표")
    print("=" * 30)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = "https://dormitory.hknu.ac.kr/bbs/board.php?bo_table=foodplan&h_flag=2"
    response = requests.get(url, verify=False)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="zp_schedule")
    meals = []

    if table:
        rows = table.find_all("tr")
        for row in rows:
            tds = row.find_all("td")
            for td in tds:
                date_tag = td.find("span", class_="caldate")
                menu_ul = td.find("ul", class_="plan")

                if date_tag and menu_ul:
                    date_text = date_tag.get_text(strip=True)
                    try:
                        date_obj = datetime.strptime(date_text[:10], "%Y.%m.%d")
                        date_formatted = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        date_formatted = date_text

                    menu_items = [
                        clean_menu_text(li.get_text())
                        for li in menu_ul.find_all("li")
                        if li.get_text(strip=True)
                    ]
                    menu_text = "\n".join(menu_items)

                    hash_val = hashlib.sha256((date_formatted + menu_text).encode("utf-8")).hexdigest()

                    meals.append({
                        "date": date_formatted,
                        "menu": menu_text,
                        "hash": hash_val
                    })

    # .env 기반 정보 사용
    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4"
    )

    new_meals = []
    with conn.cursor() as cursor:
        cursor.execute("SELECT hash FROM dorm_meals")
        existing_hashes = {row[0] for row in cursor.fetchall()}

        sql = """
        INSERT INTO dorm_meals (meal_date, meal_time, menu, hash)
        SELECT %s, %s, %s, %s FROM DUAL
        WHERE NOT EXISTS (
            SELECT 1 FROM dorm_meals WHERE hash = %s
        )
        """

        for meal in meals:
            if meal["hash"] in existing_hashes:
                continue
            new_meals.append(meal)
            cursor.execute(sql, (
                meal["date"], "", meal["menu"],
                meal["hash"], meal["hash"]
            ))

    conn.commit()
    conn.close()

    # 출력 결과
    if new_meals:
        for meal in new_meals:
            print(f"📅 날짜: {meal['date']}")
            print("🍽️ 메뉴:")
            print(meal['menu'])
            print("-" * 30)
        print(f"✅ {len(new_meals)}건의 새 식단을 저장했습니다.")
    else:
        print("✅ 새로운 식단이 없습니다.")