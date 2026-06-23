import hashlib
import logging

import requests
from django.conf import settings
from django.core.cache import cache


KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"
ROUTE_CACHE_SECONDS = 30 * 60
logger = logging.getLogger(__name__)


def _route_result(
    status,
    note,
    *,
    distance_m=None,
    duration_sec=None,
    route_summary=None,
    route_path=None,
):
    return {
        "distance_m": distance_m,
        "duration_sec": duration_sec,
        "route_summary": route_summary or {},
        "route_path": route_path or [],
        "status": status,
        "note": note,
    }


def _is_valid_coordinate(latitude, longitude):
    try:
        lat = float(latitude)
        lng = float(longitude)
    except (TypeError, ValueError):
        return False
    return -90 <= lat <= 90 and -180 <= lng <= 180


def get_driving_route(
    origin_lat,
    origin_lng,
    destination_lat,
    destination_lng,
    *,
    timeout=5,
    include_path=False,
):
    """카카오 자동차 길찾기의 거리·예상시간과 선택적 경로 좌표를 반환한다."""

    if not (
        _is_valid_coordinate(origin_lat, origin_lng)
        and _is_valid_coordinate(destination_lat, destination_lng)
    ):
        return _route_result("unavailable", "위치 정보 확인 필요")

    api_key = settings.KAKAO_REST_API_KEY
    if not api_key:
        return _route_result("unavailable", "카카오 길찾기 설정 확인 필요")

    coordinates = (
        round(float(origin_lat), 5),
        round(float(origin_lng), 5),
        round(float(destination_lat), 5),
        round(float(destination_lng), 5),
    )
    cache_digest = hashlib.sha256(repr(coordinates).encode()).hexdigest()[:24]
    cache_key = f"paceflow:kakao-route:{'path' if include_path else 'summary'}:{cache_digest}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        response = requests.get(
            KAKAO_DIRECTIONS_URL,
            headers={"Authorization": f"KakaoAK {api_key}"},
            params={
                "origin": f"{coordinates[1]},{coordinates[0]}",
                "destination": f"{coordinates[3]},{coordinates[2]}",
                "priority": "RECOMMEND",
                "summary": "false" if include_path else "true",
            },
            timeout=timeout,
        )
    except requests.RequestException as exc:
        logger.warning("Kakao directions request failed: %s", exc.__class__.__name__)
        return _route_result("failed", "거리 정보 확인 필요")

    if response.status_code in (401, 403):
        logger.warning("Kakao directions unavailable: HTTP %s", response.status_code)
        return _route_result("unavailable", "카카오 길찾기 권한 확인 필요")
    if response.status_code != 200:
        logger.warning("Kakao directions failed: HTTP %s", response.status_code)
        return _route_result("failed", "거리 정보 확인 필요")

    try:
        payload = response.json()
        route = (payload.get("routes") or [])[0]
        summary = route.get("summary") or {}
        distance_m = int(summary["distance"])
        duration_sec = int(summary["duration"])
    except (ValueError, TypeError, KeyError, IndexError):
        return _route_result("failed", "차량 경로를 확인할 수 없습니다.")

    if distance_m < 0 or duration_sec < 0:
        return _route_result("failed", "차량 경로를 확인할 수 없습니다.")

    route_path = []
    if include_path:
        for section in route.get("sections") or []:
            for road in section.get("roads") or []:
                vertexes = road.get("vertexes") or []
                for index in range(0, len(vertexes) - 1, 2):
                    try:
                        longitude = float(vertexes[index])
                        latitude = float(vertexes[index + 1])
                    except (TypeError, ValueError):
                        continue
                    point = {"lat": latitude, "lng": longitude}
                    if not route_path or route_path[-1] != point:
                        route_path.append(point)

        if len(route_path) < 2:
            return _route_result("failed", "차량 경로선을 확인할 수 없습니다.")

    result = _route_result(
        "success",
        "카카오 차량 경로 기준",
        distance_m=distance_m,
        duration_sec=duration_sec,
        route_summary={
            "priority": summary.get("priority"),
            "fare": summary.get("fare") or {},
        },
        route_path=route_path,
    )
    cache.set(cache_key, result, ROUTE_CACHE_SECONDS)
    return result
