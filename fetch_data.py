import os
import json
import requests
import xml.etree.ElementTree as ET

# ===== [수집 및 검색 조건 설정] =====
TARGET_REGIONS = ["하남", "서울", "성남", "경기"]
MAX_PRICE = 1000000000  # 최고가 (10억 원)
MIN_PRICE = 100000000   # 최저가 (1억 원)

API_KEY = os.environ.get("ONBID_API_KEY", "")

def fetch_onbid_data():
    listings = []

    # 1. 공공데이터포럼 API 키가 등록된 경우 실제 API 호출
    if API_KEY:
        try:
            url = "http://apis.data.go.kr/1230000/OnbidBaseInfoService/getOnbidBaseInfo"
            params = {
                'serviceKey': API_KEY,
                'numOfRows': '100',
                'pageNo': '1',
                'dpslMthdCd': '01',
                'ctgrLrgClssCd': '01',
            }
            res = requests.get(url, params=params, timeout=10)
            root = ET.fromstring(res.text)
            for item in root.findall('.//item'):
                goods_nm = item.findtext('CLTR_NM', '')
                addr = item.findtext('LNM_ADRS', '')
                appraisal_price = int(item.findtext('DPSL_MTD_PRC', '0') or 0)
                
                if "아파트" in goods_nm and MIN_PRICE <= appraisal_price <= MAX_PRICE:
                    if any(region in addr for region in TARGET_REGIONS):
                        listings.append({
                            "title": goods_nm,
                            "address": addr,
                            "price": appraisal_price,
                            "price_text": f"{appraisal_price:,}원",
                            "source": "온비드 공매",
                            "link": "https://www.onbid.co.kr"
                        })
        except Exception as e:
            print(f"API 호출 실패: {e}")

    # 2. 실제 API 결과가 없거나 키 미등록 시 (하남 포함 테스트 샘플 데이터)
    if not listings:
        print("하남 및 지정 지역 샘플 데이터를 생성합니다.")
        listings = [
            {
                "title": "경기도 하남시 망월동 미사강변 OO아파트 104동 1202호",
                "address": "경기도 하남시 미사강변서로 25",
                "price": 750000000,
                "price_text": "750,000,000원",
                "source": "온비드 공매",
                "link": "https://www.onbid.co.kr"
            },
            {
                "title": "경기도 하남시 신장동 OO아파트 201동 503호",
                "address": "경기도 하남시 신장대로 100",
                "price": 580000000,
                "price_text": "580,000,000원",
                "source": "법원 경매 / 온비드",
                "link": "https://www.onbid.co.kr"
            },
            {
                "title": "서울특별시 송파구 가락동 OO아파트 101동 502호",
                "address": "서울특별시 송파구 송파대로 123",
                "price": 850000000,
                "price_text": "850,000,000원",
                "source": "온비드 공매",
                "link": "https://www.onbid.co.kr"
            },
            {
                "title": "경기도 성남시 분당구 정자동 OO아파트 203동 1201호",
                "address": "경기도 성남시 분당구 정자일로 45",
                "price": 620000000,
                "price_text": "620,000,000원",
                "source": "온비드 공매",
                "link": "https://www.onbid.co.kr"
            }
        ]

    return listings

def save_json(data):
    os.makedirs("data", exist_ok=True)
    with open("data/listings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"총 {len(data)}건의 매물 데이터가 저장되었습니다.")

if __name__ == "__main__":
    data = fetch_onbid_data()
    save_json(data)
