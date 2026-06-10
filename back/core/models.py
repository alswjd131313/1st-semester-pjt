from django.db import models
from django.core.validators import MinValueValidator


# ──────────────────────────────────────────
# 1. 자재 마스터
# ──────────────────────────────────────────

class Material(models.Model):
    """
    자재 마스터 테이블.
    KS 규격 단위로 레코드를 관리한다.
    예) 철근 / KS D 3504 / SD400 / D10
    """

    CATEGORY_CHOICES = [
        ("structural",     "구조재"),
        ("non_structural", "비구조재"),
    ]

    name       = models.CharField(max_length=100, verbose_name="자재명")
    ks_code    = models.CharField(max_length=50,  verbose_name="KS 규격 번호")   # 예: KS D 3504
    ks_grade   = models.CharField(max_length=50,  verbose_name="KS 등급",   blank=True)  # 예: SD400
    diameter   = models.CharField(max_length=20,  verbose_name="규격(직경)", blank=True)  # 예: D10
    category   = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="structural",
        verbose_name="시공 분류",
    )
    is_seismic = models.BooleanField(default=False, verbose_name="내진 구조 적용 가능")
    is_weldable = models.BooleanField(default=False, verbose_name="용접 시공 가능")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "materials"
        unique_together = ("ks_code", "ks_grade", "diameter")
        verbose_name = "자재"
        verbose_name_plural = "자재 목록"

    def __str__(self):
        return f"{self.name} {self.ks_grade} {self.diameter}".strip()


# ──────────────────────────────────────────
# 2. 물성치 (자재별 1:1)
# ──────────────────────────────────────────

class MaterialSpec(models.Model):
    """
    자재별 물성치 테이블.
    KS 규격 문서(KS D 3504 등)에서 직접 추출해 수동 적재한다.
    동등성 필터링의 핵심 데이터.
    """

    material = models.OneToOneField(
        Material,
        on_delete=models.CASCADE,
        related_name="spec",
        verbose_name="자재",
    )

    # 항복강도 (MPa)
    yield_strength_min = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="항복강도 최솟값 (MPa)",
        validators=[MinValueValidator(0)],
    )
    yield_strength_max = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="항복강도 최댓값 (MPa)",
        null=True, blank=True,
    )

    # 인장강도 (MPa)
    tensile_strength_min = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="인장강도 최솟값 (MPa)",
        validators=[MinValueValidator(0)],
    )

    # 연신율 (%)
    elongation_min = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name="연신율 최솟값 (%)",
        validators=[MinValueValidator(0)],
    )

    # 탄소당량 (상한)
    carbon_equivalent_max = models.DecimalField(
        max_digits=5, decimal_places=3,
        verbose_name="탄소당량 최댓값",
        null=True, blank=True,
    )

    source = models.CharField(
        max_length=200,
        verbose_name="출처 규격 문서",
        blank=True,
    )  # 예: KS D 3504:2022

    class Meta:
        db_table = "material_specs"
        verbose_name = "물성치"

    def __str__(self):
        return f"{self.material} 물성치"


# ──────────────────────────────────────────
# 3. 국제 규격 매핑 (자재별 1:1)
# ──────────────────────────────────────────

class RegulationMapping(models.Model):
    """
    KS ↔ ASTM ↔ JIS 동등 규격 매핑.
    국제 규격 대체재 포함 여부 및 감리 승인 필요 여부를 관리한다.
    """

    material = models.OneToOneField(
        Material,
        on_delete=models.CASCADE,
        related_name="regulation",
        verbose_name="자재",
    )

    astm_code = models.CharField(
        max_length=50, blank=True,
        verbose_name="동등 ASTM 규격",
    )  # 예: A615 Gr60

    jis_code = models.CharField(
        max_length=50, blank=True,
        verbose_name="동등 JIS 규격",
    )  # 예: SD390

    requires_approval = models.BooleanField(
        default=False,
        verbose_name="감리 승인 필요",
    )

    approval_reason = models.TextField(
        blank=True,
        verbose_name="승인 필요 사유",
    )  # 예: "SD500 이상 강도 상향 — 구조 재계산 필요"

    class Meta:
        db_table = "regulation_mappings"
        verbose_name = "국제 규격 매핑"

    def __str__(self):
        return f"{self.material} 규격 매핑"


# ──────────────────────────────────────────
# 4. 공급사
# ──────────────────────────────────────────

class Supplier(models.Model):
    """
    공급사 마스터.
    나라장터 낙찰 이력에서 자동 수집되며,
    도로명주소 API로 위경도를 변환해 적재한다.
    """

    SOURCE_CHOICES = [
        ("narajangteo", "나라장터"),
        ("manual",      "수동 입력"),
    ]

    name        = models.CharField(max_length=200, verbose_name="업체명")
    business_no = models.CharField(
        max_length=20, unique=True, blank=True,
        verbose_name="사업자등록번호",
    )
    address     = models.TextField(verbose_name="주소", blank=True)
    latitude    = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        verbose_name="위도",
    )
    longitude   = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        verbose_name="경도",
    )
    phone       = models.CharField(max_length=30, blank=True, verbose_name="연락처")
    source      = models.CharField(
        max_length=20, choices=SOURCE_CHOICES,
        default="narajangteo",
        verbose_name="데이터 출처",
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "suppliers"
        verbose_name = "공급사"
        verbose_name_plural = "공급사 목록"

    def __str__(self):
        return self.name

    @property
    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None


# ──────────────────────────────────────────
# 5. 납품 이력
# ──────────────────────────────────────────

class SupplyHistory(models.Model):
    """
    나라장터 계약/낙찰 이력.
    공급사별 자재 취급 실적 및 단가 추이의 원천 데이터.
    신뢰도 점수(납품 횟수)와 단가 트렌드 차트에 활용된다.
    """

    supplier      = models.ForeignKey(
        Supplier, on_delete=models.CASCADE,
        related_name="supply_histories",
        verbose_name="공급사",
    )
    material      = models.ForeignKey(
        Material, on_delete=models.CASCADE,
        related_name="supply_histories",
        verbose_name="자재",
    )
    contract_date = models.DateField(verbose_name="계약 체결일")
    unit_price    = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name="단가 (원)",
        validators=[MinValueValidator(0)],
    )
    quantity      = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True, blank=True,
        verbose_name="수량",
        validators=[MinValueValidator(0)],
    )
    raw_data      = models.JSONField(
        default=dict, blank=True,
        verbose_name="나라장터 원본 응답",
    )
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "supply_history"
        ordering = ["-contract_date"]
        verbose_name = "납품 이력"
        verbose_name_plural = "납품 이력 목록"

    def __str__(self):
        return f"{self.supplier} / {self.material} / {self.contract_date}"


# ──────────────────────────────────────────
# 6. 수요 등록 (시공사)
# ──────────────────────────────────────────

class Demand(models.Model):
    """
    시공사의 긴급 자재 수요 등록.
    MVP에서는 내부 집계 용도. 추후 공급사 알림 연동 예정.
    """

    site_name  = models.CharField(max_length=200, verbose_name="현장명")
    site_lat   = models.DecimalField(
        max_digits=9, decimal_places=6,
        verbose_name="현장 위도",
    )
    site_lng   = models.DecimalField(
        max_digits=9, decimal_places=6,
        verbose_name="현장 경도",
    )
    material   = models.ForeignKey(
        Material, on_delete=models.SET_NULL,
        null=True, related_name="demands",
        verbose_name="필요 자재",
    )
    quantity   = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name="필요 수량 (kg)",
        validators=[MinValueValidator(0)],
    )
    deadline   = models.DateField(verbose_name="납기 기한")
    memo       = models.TextField(blank=True, verbose_name="메모")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "demands"
        ordering = ["-created_at"]
        verbose_name = "수요 등록"

    def __str__(self):
        return f"{self.site_name} / {self.material} / {self.deadline}"