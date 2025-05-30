# HKNU Scraper

한경국립대학교 공지사항 및 식단표 크롤러 프로젝트입니다.

## 크롤러 종류

### 📌 식단표
- 학생식당: `student_meal.py`
- 교직원식당: `faculty_meal.py`
- 기숙사식당: `dorm_meal.py`

### 📌 공지사항
- 장학공지: `scholarship_notice.py`
- 학사공지: `academic_notice.py`
- 한경공지: `hankyong_notice.py`
- 학사일정: `academic_schedule.py`

## 실행 방법
```bash
1. scp -r ./crawler root@211.188.57.74:/root/hknu_scraper/ # (Local → Server)
2. python main.py(server)

