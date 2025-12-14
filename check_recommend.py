import requests

BASE_URL = "http://localhost:8000/api/v2"
USER = {"username": "graph_user", "password": "password123"}

def check():
    print("🚀 추천 API 테스트 시작...")
    
    # 1. 로그인
    res = requests.post(f"{BASE_URL}/auth/login", json=USER)
    if res.status_code != 200:
        print(f"❌ 로그인 실패: {res.text}")
        return
    token = res.json()["access_token"]
    print("✅ 로그인 성공")

    # 2. 추천 요청
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/recommend", headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        print("\n📊 [추천 결과]")
        print(f"   - 메뉴 목록: {data.get('menus')}")
        print(f"   - 설명: {data.get('message')}")
        
        if "나가사키짬뽕" in str(data.get('menus')):
            print("\n🎉 성공! 나가사키짬뽕이 추천되었습니다.")
        else:
            print("\n⚠️ 실패: 원하는 메뉴가 안 나옴.")
    else:
        print(f"❌ API 오류: {res.text}")

if __name__ == "__main__":
    check()
