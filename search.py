import requests
from bs4 import BeautifulSoup

# --- 다중 검색 조건 설정 ---
SEARCH_TARGETS = [
    {"keyword": "ジョニーウォーカー ブラック 金キャップ 特級", "max_price": 4000},
    {"keyword": "ジョニーウォーカー ブラック 半金キャップ 特級", "max_price": 3000}
]

def search_yahoo_auction():
    print("=== 일본 야후 옥션 주류 카테고리 검색 시작 ===\n")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for target in SEARCH_TARGETS:
        keyword = target["keyword"]
        max_price = target["max_price"]
        
        print(f"▶ 검색어: {keyword} (상한가: {max_price}엔)")
        # 주류 카테고리(2084006720) 한정 파라미터 추가
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
            for idx, item in enumerate(found_items, 1):
                print(f"  {idx}. {item['title']}")
                print(f"     가격: {item['price']}엔")
                print(f"     링크: {item['link']}")
        else:
            print("현재 설정한 금액 이하의 매물이 없습니다.")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    search_yahoo_auction()
