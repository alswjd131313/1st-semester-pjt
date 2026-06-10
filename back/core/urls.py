from django.urls import path
from . import views

urlpatterns = [
    # 주소 검색 / 좌표 변환
    path("addresses/search/", views.search_addresses, name="address-search"),
    path("addresses/geocode/", views.geocode_address, name="address-geocode"),

    # 자재 검색
    path("materials/", views.MaterialListView.as_view(), name="material-list"),

    # 대체 공급사 추천 (핵심)
    path("materials/<int:material_id>/alternatives/", views.alternative_suppliers,name="alternatives"),

    # 단가 트렌드
    path("materials/<int:material_id>/price-trend/", views.price_trend, name="price-trend"),

    # 수요 등록
    path("demands/", views.DemandCreateView.as_view(), name="demand-create"),
]
