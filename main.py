import time
import requests
from dotenv import load_dotenv

from crawler.student_meal import run_student_meal
from crawler.faculty_meal import run_faculty_meal
from crawler.dorm_meal import run_dorm_meal
from crawler.scholarship_notice import run_scholarship_notice
from crawler.academic_notice import run_academic_notice
from crawler.hankyong_notice import run_hankyong_notice
from crawler.academic_schedule import run_academic_schedule

def clear_cache():
    print("\n✅ 캐시 삭제 요청 시작")

    endpoints = [
        "academic-notices",
        "academic-schedule",
        "student-meals",
        "faculty-meals",
        "dorm-meals",
        "hankyong-notices",
        "scholarship-notices"
    ]

    server_url = "http://211.188.57.74:8080"

    for endpoint in endpoints:
        try:
            url = f"{server_url}/api/{endpoint}/clear-cache"
            response = requests.post(url)
            if response.status_code == 200:
                print(f"✅ {endpoint} 캐시 삭제 성공")
            else:
                print(f"⚠️ {endpoint} 캐시 삭제 실패 - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} 캐시 삭제 오류: {e}")

def main():
    load_dotenv(dotenv_path="/root/hknu_scraper/.env")  # .env 파일 로딩

    jobs = [
        ("학생식당", run_student_meal),
        ("교직원식당", run_faculty_meal),
        ("기숙사식당", run_dorm_meal),
        ("장학공지", run_scholarship_notice),
        ("학사공지", run_academic_notice),
        ("한경공지", run_hankyong_notice),
        ("학사일정", run_academic_schedule)
    ]
    # 크롤링 실행
    for name, job in jobs:
        try:
            print(f"\n✅ [{name}] 실행 시작")
            job()
            time.sleep(5)
        except Exception as e:
            print(f"❌ [{name}] 오류 발생: {e}")

    # 캐시 삭제 요청
    clear_cache()

if __name__ == "__main__":
    main()
