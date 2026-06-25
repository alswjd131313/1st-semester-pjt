from django.urls import path
from . import views

urlpatterns = [
    # 주소 검색 / 좌표 변환
    path("addresses/search/", views.search_addresses, name="address-search"),
    path("addresses/geocode/", views.geocode_address, name="address-geocode"),
    path("narajangteo/contracts/", views.narajangteo_contracts, name="narajangteo-contracts"),
    path("narajangteo/cached-contracts/", views.cached_narajangteo_contracts, name="narajangteo-cached-contracts"),
    path("routes/driving/", views.driving_route, name="driving-route"),

    # 자재 검색
    path("materials/", views.MaterialListView.as_view(), name="material-list"),
    path("materials/suggest/", views.material_suggestions, name="material-suggestions"),

    # 대체 공급사 추천 (핵심)
    path("materials/<int:material_id>/alternatives/", views.alternative_suppliers,name="alternatives"),

    # 단가 트렌드
    path("materials/<int:material_id>/price-trend/", views.price_trend, name="price-trend"),

    # 수요 등록
    path("demands/", views.DemandListCreateView.as_view(), name="demand-list-create"),
    path("demands/<int:pk>/", views.DemandDetailView.as_view(), name="demand-detail"),

    # 공급사 직접 등록 자재
    path("supplier-materials/", views.SupplierMaterialRegistrationListCreateView.as_view(), name="supplier-material-list-create"),
    path("supplier-materials/<int:pk>/", views.SupplierMaterialRegistrationDetailView.as_view(), name="supplier-material-detail"),
    path("supplier-materials/public/", views.PublicSupplierMaterialRegistrationListView.as_view(), name="supplier-material-public-list"),
    path("suppliers/map/", views.SupplierMapListView.as_view(), name="supplier-map-list"),

    # 커뮤니티 MVP
    path("community/posts/", views.CommunityPostListCreateView.as_view(), name="community-post-list-create"),
    path("community/posts/<int:pk>/", views.CommunityPostDetailView.as_view(), name="community-post-detail"),
    path("community/posts/<int:post_id>/comments/", views.CommunityCommentListCreateView.as_view(), name="community-comment-list-create"),
    path("community/comments/<int:pk>/", views.CommunityCommentDetailView.as_view(), name="community-comment-detail"),
    path("community/contact-requests/", views.CommunityContactRequestListCreateView.as_view(), name="community-contact-list-create"),
    path("community/contact-requests/<int:pk>/", views.CommunityContactRequestDetailView.as_view(), name="community-contact-detail"),
    path("community/profiles/<int:user_id>/", views.community_public_profile, name="community-public-profile"),

    # 공급사 문의
    path("inquiries/", views.SupplierInquiryListCreateView.as_view(), name="inquiry-list-create"),
    path("inquiries/<int:pk>/", views.SupplierInquiryDetailView.as_view(), name="inquiry-detail"),
    path("inquiries/<int:pk>/status/", views.SupplierInquiryStatusView.as_view(), name="inquiry-status"),
    path(
        "inquiries/<int:pk>/delete-for-supplier/",
        views.SupplierInquiryDeleteForSupplierView.as_view(),
        name="inquiry-delete-for-supplier",
    ),

    # 알림
    path("notifications/", views.NotificationListView.as_view(), name="notification-list"),
    path("notifications/unread-count/", views.NotificationUnreadCountView.as_view(), name="notification-unread-count"),
    path("notifications/<int:pk>/read/", views.NotificationMarkReadView.as_view(), name="notification-mark-read"),
    path("notifications/read-all/", views.NotificationMarkAllReadView.as_view(), name="notification-read-all"),
    path("notifications/<int:pk>/", views.NotificationDeleteView.as_view(), name="notification-delete"),
]
