import os
import json
import requests
import xml.etree.ElementTree as ET

# ===== [설정 영역] 원하시는 조건으로 변경하세요 =====
TARGET_REGIONS = ["경기도 구리시", "경기도 하남시"]  # 관심 지역
MAX_PRICE = 1000000000  # 최고 가격 (예: 10억 원 이하)
MIN_PRICE = 200000000   # 최저 가격 (예: 2억 원 이상)

# 공공데이터포럼 디코딩 API Key (GitHub Secrets에 등록하여 사용)
API_KEY = os.environ.get("ONBID_API_KEY", "")

def fetch_onbid_data():
    """온비드 공매물건 API 호출 예시 (공공데이터포럼 온비드 공매물건 조회서비스 API 사용)"""
    url = "http://apis.data.go.kr/1230000/OnbidBaseInfoService/getOnbidBaseInfo"
    params = {
        'serviceKey': API_KEY,
        'numOfRows': '100',
        'pageNo': '1',
        'dpslMthdCd': '01', # 처분방식 (매각)
        'ctgrLrgClssCd': '01', # 카테고리 (주거용)
    }

    listings = []
    
    try:
        if API_KEY:
            res = requests.get(url, params=params, timeout=10)
            # xml 응답 파싱
            root = ET.fromstring(res.text)
            for item in root.findall('.//item'):
                goods_nm = item.findtext('CLTR_NM', '')     # 물건명
                addr = item.findtext('LNM_ADRS', '')         # 주소
                appraisal_price = int(item.findtext('DPSL_MTD_PRC', '0') or 0) # 감정가/최저입찰가
                link = f"https://www.onbid.co.kr"
                
                # 아파트 키워드 및 지역/가격 조건 검증
                if "아파트" in goods_nm and MIN_PRICE <= appraisal_price <= MAX_PRICE:
                    if any(region in addr for region in TARGET_REGIONS):
                        listings.append({
                            "title": goods_nm,
                            "address": addr,
                            "price": appraisal_price,
                            "price_text": f"{appraisal_price:,}원",
                            "source": "온비드 공매",
                            "link": link
                        })
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")

    # API 키가 없거나 테스트용 샘플 데이터 생성
    if not listings:
        print("API 결과가 없거나 설정되지 않아 테스트용 샘플 데이터를 생성합니다.")
        listings = [
            {
                "title": "서울특별시 송파구 가락동 OO아파트 101동 502호",
                "address": "서울특별시 송파구 송파대로 123",
                "price": 850000000,
                "price_text": "850,000,000원",
                "source": "법원 경매 / 온비드",
                "link": "https://www.onbid.co.kr"
            },
            {
                "title": "경기도 성남시 분당구 정자동 OO아파트 203동 1201호",
                "address": "경기도 성남시 분당구 정자일로 45",
                "price": 620000000,
                "price_text": "620,000,000원",
                "source": "법원 경매 / 온비드",
                "link": "https://www.onbid.co.kr"
            }
        ]

    return listings

def save_json(data):
    os.makedirs("data", exist_ok=True)
    with open("data/listings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"총 {len(data)}건의 매물 데이터가 data/listings.json 에 저장되었습니다.")

if __name__ == "__main__":
    data = fetch_onbid_data()
    save_json(data)
