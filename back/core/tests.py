from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from .services.kakao_directions import get_driving_route


class KakaoDirectionsTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_missing_coordinates_returns_safe_status(self):
        result = get_driving_route(None, None, 37.5, 127.0)

        self.assertEqual(result["status"], "missing_coordinates")
        self.assertIsNone(result["distance_m"])

    @override_settings(KAKAO_REST_API_KEY="")
    def test_missing_api_key_returns_unavailable(self):
        result = get_driving_route(37.4, 127.1, 37.5, 127.0)

        self.assertEqual(result["status"], "api_unavailable")

    @override_settings(KAKAO_REST_API_KEY="test-key")
    @patch("core.services.kakao_directions.requests.get")
    def test_success_returns_distance_and_duration(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "routes": [
                {
                    "summary": {
                        "distance": 7400,
                        "duration": 1080,
                        "priority": "RECOMMEND",
                        "fare": {"taxi": 12000, "toll": 0},
                    }
                }
            ]
        }
        mock_get.return_value = response

        result = get_driving_route(37.4, 127.1, 37.5, 127.0)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["distance_m"], 7400)
        self.assertEqual(result["duration_sec"], 1080)
        request_kwargs = mock_get.call_args.kwargs
        self.assertEqual(request_kwargs["params"]["origin"], "127.1,37.4")
        self.assertNotIn("test-key", str(request_kwargs["params"]))

    @override_settings(KAKAO_REST_API_KEY="test-key")
    @patch("core.services.kakao_directions.requests.get")
    def test_permission_failure_does_not_raise(self, mock_get):
        response = Mock()
        response.status_code = 403
        mock_get.return_value = response

        result = get_driving_route(37.4, 127.1, 37.5, 127.0)

        self.assertEqual(result["status"], "api_unavailable")
        self.assertEqual(result["note"], "카카오 길찾기 권한 확인 필요")
