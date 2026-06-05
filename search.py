import requests
import re
import datetime
from bs4 import BeautifulSoup

# --- 텔레그램 봇 설정 ---
TELEGRAM_TOKEN = '8943457065:AAGDqMYtX-ZglWavdSB1P3f7w3EctJB975o'
TELEGRAM_CHAT_ID = '-1004505085448'

# --- 다중 검색 조건 설정 ---
SEARCH_TARGETS = [
    {"keyword": "ジョニーウォーカー ブラック 金キャップ 特級", "max_price": 4000},
    {"keyword": "ジョニーウォーカー ブラックラベル 黒金キャップ", "max_price": 3000}
]

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True  # 긴 링크 미리보기 방지
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("텔레그램 메시지를 성공적으로 보냈습니다.")
        else:
            print(f"텔레그램 메시지 전송 실패: {response.text}")
    except Exception as e:
        print(f"텔레그램 전송 중 에러 발생: {e}")

def search_yahoo_auction():
    print("=== 일본 야후 옥션 주류 카테고리 검색 시작 ===\n")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # 현재 한국 시간(KST) 계산
    now_kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    current_hour = now_kst.hour
    
    # 실행 시간에 따른 마감 임박 기준 설정
    if 17 <= current_hour <= 19:
        max_hours = 6  # 저녁 6시 실행 시 자정까지 (6시간)
        time_label = "저녁 6시 기준 (자정 마감 임박)"
    elif 7 <= current_hour <= 9:
        max_hours = 48  # 아침 8시 실행 시 48시간 이내
        time_label = "아침 8시 기준 (48시간 이내)"
    else:
        max_hours = 48  # 기타 수동 실행 시 기본 48시간
        time_label = "수동 실행 기준 (48시간 이내)"

    print(f"⏰ 현재 한국 시간: {now_kst.strftime('%Y-%m-%d %H:%M')}")
    print(f"🎯 적용 필터: {time_label}\n")

    message_content = ""

    for target in SEARCH_TARGETS:
        keyword = target["keyword"]
        max_price = target["max_price"]
        
        print(f"▶ 검색어: {keyword} (상한가: {max_price}엔)")
        url = f"https://auctions.yahoo.co.jp/search/search?p={keyword}&auccat=2084006720"
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        items = soup.find_all("li", class_="Product")
        found_items = []
        
        for item in items:
            try:
                title = item.find("a", class_="Product__titleLink").text.strip()
                price_str = item.find("span", class_="Product__priceValue").text.strip()
                price = int(''.join(filter(str.isdigit, price_str)))
                link = item.find("a", class_="Product__titleLink")["href"]
                
                # 1. 4병 이상 묶음 매물 확인 (4本, 5本, 10本 등 패턴 매칭)
                is_bundle_4_or_more = False
                bundle_match = re.search(r'([4-9]|\d{2,})本', title)
                if bundle_match:
                    is_bundle_4_or_more = True

                # 2. 남은 시간 파싱 (残り1日, 6時間, 30分 등)
                time_str = ""
                time_elem = item.find(class_=re.compile("Product__time"))
                if time_elem:
                    time_str = time_elem.text.strip()
                
                remaining_hours = 999
                if "日" in time_str:
                    days = int(re.search(r'\d+', time_str).group())
                    remaining_hours = days * 24
                elif "時間" in time_str:
                    remaining_hours = int(re.search(r'\d+', time_str).group())
                elif "分" in time_str:
                    remaining_hours = 1

                # 조건 체크: (가격 만족 혹은 4병 이상) 이고 (남은 시간 기준 만족)
                if (price <= max_price or is_bundle_4_or_more) and (remaining_hours <= max_hours):
                    label = " [4병이상묶음]" if is_bundle_4_or_more else ""
                    found_items.append({
                        "title": title, 
                        "price": price, 
                        "link": link, 
                        "time": time_str,
                        "label": label
                    })
            except Exception as e:
                continue

        if found_items:
            print(f"🎉 조건에 맞는 매물을 {len(found_items)}개 찾았습니다!")
            message_content += f"\n[{keyword}]\n"
            
            chunk_size = 4
            total_chunks = ((len(found_items) - 1) // chunk_size) + 1
            
            for i in range(0, len(found_items), chunk_size):
                chunk = found_items[i:i+chunk_size]
                current_page = (i // chunk_size) + 1
                chunk_message = f"[{keyword} 알림 ({current_page}/{total_chunks})]\n"
                
                for idx, item in enumerate(chunk, i + 1):
                    chunk_message += f"{idx}. {item['price']}엔{item['label']} ({item['time']})\n{item['link']}\n\n"
                
                send_telegram_message(chunk_message)
                
            for idx, item in enumerate(found_items, 1):
                print(f"  {idx}. {item['title']}")
                print(f"     가격: {item['price']}엔 | 남은시간: {item['time']}")
        else:
            print("현재 조건(가격/묶음/마감시간)을 만족하는 매물이 없습니다.")
        print("-" * 50 + "\n")

    if not message_content:
        print("전송할 새 매물이 없습니다.")

if __name__ == "__main__":
    search_yahoo_auction()
