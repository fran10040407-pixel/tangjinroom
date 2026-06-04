import requests
import json
from bs4 import BeautifulSoup

# --- 다중 검색 조건 설정 ---
SEARCH_TARGETS = [
    {"keyword": "ジョニーウォーカー ブラック 金キャップ 特級", "max_price": 4000},
    {"keyword": "ジョニーウォーカー ブラックラベル 黒金キャップ", "max_price": 3000}
]

def send_kakao_message(text):
    try:
        with open("kakao_token.json", "r") as fp:
            tokens = json.load(fp)
            access_token = tokens["access_token"]
    except FileNotFoundError:
        print("카카오 토큰 파일이 없습니다.")
        return

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://auctions.yahoo.co.jp/",
                "mobile_web_url": "https://auctions.yahoo.co.jp/"
            }
        })
    }
    response = requests.post(url, headers=headers, data=data)
    if response.json().get('result_code') == 0:
        print("카카오톡 메시지를 성공적으로 보냈습니다.")
    else:
        print(f"카카오톡 메시지 전송 실패: {response.text}")

def search_yahoo_auction():
    print("=== 일본 야후 옥션 주류 카테고리 검색 시작 ===\n")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

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
                
                if price <= max_price:
                    found_items.append({"title": title, "price": price, "link": link})
                except Exception as e:
                    continue

        if found_items:
            print(f"🎉 조건에 맞는 매물을 {len(found_items)}개 찾았습니다!")
            
            # 카카오톡 글자 수 제한(400자)을 넘지 않도록 4개씩 나누어 전송
            chunk_size = 4
            total_chunks = ((len(found_items) - 1) // chunk_size) + 1
            
            for i in range(0, len(found_items), chunk_size):
                chunk = found_items[i:i+chunk_size]
                current_page = (i // chunk_size) + 1
                message_content = f"[{keyword} 알림 ({current_page}/{total_chunks})]\n"
                
                for idx, item in enumerate(chunk, i + 1):
                    message_content += f"{idx}. {item['price']}엔\n{item['link']}\n"
                
                send_kakao_message(message_content)
                
            for idx, item in enumerate(found_items, 1):
                print(f"  {idx}. {item['title']}")
                print(f"     가격: {item['price']}엔")
                print(f"     링크: {item['link']}")
        else:
            print("현재 설정한 금액 이하의 매물이 없습니다.")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    search_yahoo_auction()
