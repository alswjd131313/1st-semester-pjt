from unittest.mock import Mock, patch
from datetime import date
from decimal import Decimal

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings

from .models import CategoryContractHistory, Material, Supplier, SupplyHistory
from .services.kakao_directions import get_driving_route
from .views import calculate_category_experience_score


class CategoryContractHistoryTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="테스트 공급사",
            business_no="test-category-supplier",
        )
        self.material = Material.objects.create(
            name="단열재",
            ks_code="KS TEST",
            ks_grade="XPS II",
            diameter="50T",
            material_group="insulation",
            material_subtype="xps",
        )

    def test_category_history_does_not_change_exact_material_history(self):
        SupplyHistory.objects.create(
            supplier=self.supplier,
            material=self.material,
            contract_date=date(2025, 6, 1),
            unit_price=Decimal("1000.00"),
        )
        CategoryContractHistory.objects.create(
            supplier=self.supplier,
            material_category="insulation",
            contract_date=date(2025, 6, 5),
            contract_name="PF보드 단열재 구입",
            unit_price=Decimal("5000000.00"),
            mapping_reason="두께 미확정",
            external_id="test-category-contract-1",
        )

        exact_histories = SupplyHistory.objects.filter(material=self.material)
        self.assertEqual(exact_histories.count(), 1)
        self.assertEqual(exact_histories.get().unit_price, Decimal("1000.00"))
        self.assertEqual(self.supplier.category_contract_histories.count(), 1)

    def test_category_experience_score_is_capped_at_five(self):
        self.assertEqual(calculate_category_experience_score(0), 0)
        self.assertEqual(calculate_category_experience_score(3), 3)
        self.assertEqual(calculate_category_experience_score(12), 5)

    def test_collector_saves_held_contract_only_as_category_history(self):
        from scripts.collect_narajangteo import save_category_history

        item = {
            "cntrctNm": "PF보드 단열재 구입",
            "cntrctCnclsDate": "2025-06-05",
            "thtmCntrctAmt": "5000000",
            "cntrctNo": "TEST-CONTRACT-001",
        }
        created, error = save_category_history(
            self.supplier,
            "insulation",
            "단열재",
            "두께 미확정",
            item,
        )
        duplicated, duplicate_error = save_category_history(
            self.supplier,
            "insulation",
            "단열재",
            "두께 미확정",
            item,
        )

        self.assertTrue(created)
        self.assertEqual(error, "")
        self.assertFalse(duplicated)
        self.assertEqual(duplicate_error, "")
        self.assertEqual(CategoryContractHistory.objects.count(), 1)
        self.assertEqual(SupplyHistory.objects.count(), 0)

    def test_fep_conduit_is_held_instead_of_representative_mapping(self):
        from scripts.collect_narajangteo import choose_materials

        rigid = Material.objects.create(
            name="전선관",
            ks_code="KS C IEC 61386-1",
            ks_grade="경질 합성수지관",
            diameter="16C",
            material_group="electrical_conduit",
            material_subtype="rigid_conduit",
        )
        item = {
            "cntrctNm": "부산항 신항 상부시설 축조공사 지급자재 FEP전선관 구매",
        }

        matched = choose_materials([rigid], item, "전선관")

        self.assertEqual(matched, [])
        self.assertEqual(item["_paceflow_hold_reason"], "전선관 종류에 일치하는 내부 Material 없음")
        self.assertNotEqual(item.get("_paceflow_match_basis"), "대표 규격 매핑")

    def test_cd_conduit_requires_explicit_type_and_size(self):
        from scripts.collect_narajangteo import choose_materials

        cd_16 = Material.objects.create(
            name="전선관",
            ks_code="KS C IEC 61386-1",
            ks_grade="CD관",
            diameter="16CD",
            material_group="electrical_conduit",
            material_subtype="cd_conduit",
        )
        item = {"cntrctPrdctNm": "CD관 16mm 구매"}

        matched = choose_materials([cd_16], item, "전선관")

        self.assertEqual(matched, [cd_16])
        self.assertEqual(item["_paceflow_match_basis"], "전선관 명시 규격 매핑: CD관 16CD")


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
