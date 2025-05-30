import requests
import pymysql
import hashlib
from bs4 import BeautifulSoup
import urllib3
import datetime
import os
from dotenv import load_dotenv

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# .env 로드
load_dotenv()

def clean_date(date_str):
    try:
        dt = datetime.datetime.strptime(date_str.strip(), "%Y.%m.%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str.strip()

def generate_hash(title, link):
    return hashlib.sha256(f"{title}_{link}".encode("utf-8")).hexdigest()

def run_academic_notice():
    print("📢 한경국립대학교 학사공지")
    print("=" * 30)

    base_url = "https://www.hknu.ac.kr/bbs/kor/70/artclList.do"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # .env에서 DB 연결 정보 불러오기
    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT hash FROM academic_notices")
    existing_hashes = set(row[0] for row in cursor.fetchall())

    page = 1
    empty_count = 0
    MAX_EMPTY = 3
    new_notices = []

    while True:
        print(f"📄 페이지 {page} 수집 중...")

        data = {
            "layout": "6b6f7240403536324040666e637431",  # 학사공지 layout
            "page": str(page),
            "srchColumn": "",
            "srchWrd": "",
            "bbsClSeq": "",
            "bbsOpenWrdSeq": "",
            "rgsBgndeStr": "",
            "rgsEnddeStr": "",
            "isViewMine": "false"
        }

        try:
            res = requests.post(base_url, headers=headers, data=data, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 실패: {e}")
            break

        if "board-table" not in res.text:
            print("🛑 공지 테이블 없음 또는 마지막 페이지 도달")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.board-table tbody tr")

        if not rows:
            break

        added = 0

        for row in rows:
            title_tag = row.select_one("td.td-subject a")
            date_tag = row.select_one("td.td-date")
            author_tag = row.select_one("td.td-write")

            if not title_tag or not date_tag:
                continue

            title = ' '.join(title_tag.text.split())
            href = "https://www.hknu.ac.kr" + title_tag['href']
            date = clean_date(date_tag.get_text(strip=True))
            author = author_tag.get_text(strip=True) if author_tag else "작성자 없음"
            hash_value = generate_hash(title, href)

            if hash_value in existing_hashes:
                continue

            print(f"📌 {title} | {date} | {author}")
            new_notices.append((title, date, author, href, hash_value))
            added += 1

        if added == 0:
            empty_count += 1
        else:
            empty_count = 0

        if empty_count >= MAX_EMPTY:
            print(f"🛑 {MAX_EMPTY}페이지 연속으로 새로운 공지가 없어 종료합니다.")
            break

        page += 1

    if new_notices:
        sql = """
        INSERT INTO academic_notices (title, notice_date, author, link, hash)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(sql, new_notices)
        conn.commit()
        print(f"✅ {len(new_notices)}건의 새 공지를 저장했습니다.")
    else:
        print("✅ 새로운 공지가 없습니다.")

    cursor.close()
    conn.close()