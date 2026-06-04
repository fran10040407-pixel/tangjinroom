import requests
from bs4 import BeautifulSoup

# --- 다중 검색 조건 설정 ---
# keyword: 야후 옥션에서 검색될 일본어 키워드
# max_price: 해당 키워드의 상한 금액 (엔)
SEARCH_TARGETS = [
    {"keyword": "ジョニーウォーカー ブラック 金キャップ 特級", "max_price": 4000},
    {"keyword": "ジョニーウォーカー ブラック 半金キャップ 特級", "max_price": 3000}
]# 추가는 이곳에........

def search_yahoo_auction():
    print("=== 일본 야후 옥션 다중 조건 검색 시작 ===\n")
    
    # 봇(Bot) 차단을 막기 위한 일반 사용자 위장 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 설정한 여러 검색 조건을 순서대로 실행
    for target in SEARCH_TARGETS:
        keyword = target["keyword"]
        max_price = target["max_price"]
        
        print(f"▶ 검색어: {keyword} (상한가: {max_price}엔)")
        url = f"https://auctions.yahoo.co.jp/search/search?p={keyword}"
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        items = soup.find_all("li", class_="Product")
        found_items = []
        
        for item in items:
            try:
                title = item.find("a", class_="Product__titleLink").text.strip()
                price_str = item.find("span", class_="Product__priceValue").text.strip()
                
                # 가격에서 숫자만 추출
                price = int(''.join(filter(str.isdigit, price_str)))
                link = item.find("a", class_="Product__titleLink")["href"]
                
                # 상한 금액 이하인지 확인
                if price <= max_price:
                    found_items.append({"title": title, "price": price, "link": link})
            except Exception as e:
                continue

        # 개별 조건에 대한 결과 출력
        if found_items:
            print(f"🎉 조건에 맞는 매물을 {len(found_items)}개 찾았습니다!")
            for idx, item in enumerate(found_items, 1):
                print(f"  {idx}. {item['title']}")
                print(f"     가격: {item['price']}엔")
                print(f"     링크: {item['link']}")
        else:
            print("현재 설정한 금액 이하의 매물이 없습니다.")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    search_yahoo_auction()
