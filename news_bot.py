import requests
import urllib.parse
import json
import os
from datetime import datetime

# 🔐 1. 깃허브 시크릿(환경변수) 불러오기
SLACK_URL = os.environ['SLACK_WEBHOOK_URL']
NAVER_ID = os.environ['NAVER_CLIENT_ID']
NAVER_SECRET = os.environ['NAVER_CLIENT_SECRET']

# 🔍 2. 뉴스 검색 함수
def get_news(keyword, count):
    enc_text = urllib.parse.quote(keyword)
    # sort='sim': 정확도순(주요뉴스), display=count: 설정한 개수만큼
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display={count}&sort=sim"
    
    headers = {
        "X-Naver-Client-Id": NAVER_ID,
        "X-Naver-Client-Secret": NAVER_SECRET
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('items', [])
        return []
    except:
        return []

# 🚀 3. 메인 실행 함수
def send_alert():
    # 날짜 표시 (예: 2026-02-10)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 📋 설정: 검색어 및 가져올 개수 (총 10건)
    search_configs = [
        ("제주 (렌터카 | 렌트카)", 3),  # 렌터카 3건
        ("제주 모빌리티", 1),          # 모빌리티 1건
        ("제주 쏘카", 1),              # 쏘카 1건
        ("제주 관광", 3),              # 관광 3건
        ("제주 공항", 1),              # 공항 1건
        ("제주 예보", 1)               # 날씨/예보 1건
    ]
    
    # 슬랙 메시지 제목
    full_message = f"📅 *{today} 제주 주요 뉴스 브리핑*\n"
    
    # 각 주제별로 뉴스 검색 및 메시지 추가
    for keyword, count in search_configs:
        news_items = get_news(keyword, count)
        
        # 소제목 꾸미기 (보기 좋게 다듬기)
        clean_title = keyword.replace(" (렌터카 | 렌트카)", " 렌터카")
        full_message += f"\n🔹 *{clean_title}*\n"
        
        if not news_items:
            full_message += "   (관련된 최신 뉴스가 없습니다.)\n"
            continue
            
        for item in news_items:
            # 제목의 HTML 태그(<b> 등) 제거
            title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
            link = item['link']
            full_message += f"• {title}\n  <{link}|기사 보기>\n"

    # 📨 4. 슬랙 전송
    payload = {"text": full_message}
    requests.post(SLACK_URL, data=json.dumps(payload))
    print("✅ 제주봇 뉴스 전송 완료")

if __name__ == "__main__":
    send_alert()
