import requests
import json

BASE = "http://localhost:8000/api/v1"

# ── 자재 목록 조회
print("=== 자재 목록 ===")
res = requests.get(f"{BASE}/materials/")
print(json.dumps(res.json(), ensure_ascii=False, indent=2))

# ── 대체 공급사 추천
print("\n=== 대체 공급사 추천 ===")
res = requests.post(
    f"{BASE}/materials/1/alternatives/",
    json={
        "site_lat": 37.5447,
        "site_lng": 127.0558,
        "is_seismic": True
    }
)
print(json.dumps(res.json(), ensure_ascii=False, indent=2))