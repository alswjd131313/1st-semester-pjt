import { createRouter, createWebHistory } from "vue-router";
import { isLoggedIn, hasRole } from "./api/authApi";

import HomePage from "./pages/HomePage.vue";
import LoginPage from "./pages/LoginPage.vue";
import SignupPage from "./pages/SignupPage.vue";
import MaterialRequestPage from "./pages/MaterialRequestPage.vue";
import RecommendationPage from "./pages/RecommendationPage.vue";
import RecommendationDetailPage from "./pages/RecommendationDetailPage.vue";
import DashboardPage from "./pages/DashboardPage.vue";
import InquiryDetailPage from "./pages/InquiryDetailPage.vue";
import InquiryEditPage from "./pages/InquiryEditPage.vue";
import SupplierDashboardPage from "./pages/SupplierDashboardPage.vue";
import SupplierProfilePage from "./pages/SupplierProfilePage.vue";
import MyPage from "./pages/MyPage.vue";
import SupplierMyPage from "./pages/SupplierMyPage.vue";
import SignupSuccessPage from "./pages/SignupSuccessPage.vue";
import PriceTrendPage from "./pages/PriceTrendPage.vue";
import CommunityPage from "./pages/CommunityPage.vue";
import CommunityWritePage from "./pages/CommunityWritePage.vue";
import CommunityDetailPage from "./pages/CommunityDetailPage.vue";
import CommunityProfilePage from "./pages/CommunityProfilePage.vue";

const routes = [
  { path: "/", name: "home", component: HomePage },
  { path: "/login", name: "login", component: LoginPage },
  { path: "/signup", name: "signup", component: SignupPage },

  // 자재 요청자
  {
    path: "/materials/request",
    name: "material-request",
    component: MaterialRequestPage,
    meta: { requiresAuth: true, role: "requester" },
  },
  {
    path: "/materials/recommendation",
    name: "recommendation",
    component: RecommendationPage,
  },
  {
    path: "/recommendations/:id",
    name: "recommendation-detail",
    component: RecommendationDetailPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/materials/:id/price-trend",
    name: "price-trend",
    component: PriceTrendPage,
    meta: { requiresAuth: true },
  },

  // 커뮤니티
  { path: "/community", name: "community", component: CommunityPage },
  {
    path: "/community/new",
    name: "community-write",
    component: CommunityWritePage,
    meta: { requiresAuth: true },
  },
  {
    path: "/community/:id/edit",
    name: "community-edit",
    component: CommunityWritePage,
    meta: { requiresAuth: true },
  },
  { path: "/community/:id", name: "community-detail", component: CommunityDetailPage },

  // 문의
  {
    path: "/inquiries",
    name: "inquiries",
    component: DashboardPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/inquiries/:id",
    name: "inquiry-detail",
    component: InquiryDetailPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/inquiries/:id/edit",
    name: "inquiry-edit",
    component: InquiryEditPage,
    meta: { requiresAuth: true },
  },

  { path: "/profile/:id", name: "community-profile", component: CommunityProfilePage },

  // 공급사
  {
    path: "/supplier/dashboard",
    name: "supplier-dashboard",
    component: SupplierDashboardPage,
    meta: { requiresAuth: true, role: "supplier" },
  },
  {
    path: "/supplier/profile",
    name: "supplier-profile",
    component: SupplierProfilePage,
    meta: { requiresAuth: true, role: "supplier" },
  },

  // 마이페이지
  {
    path: "/mypage",
    name: "mypage",
    component: MyPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/supplier/mypage",
    name: "supplier-mypage",
    component: SupplierMyPage,
    meta: { requiresAuth: true, role: "supplier" },
  },
  { path: "/signup-success", name: "signup-success", component: SignupSuccessPage },

  // 하위 호환 리다이렉트
  { path: "/request", redirect: "/materials/request" },
  { path: "/recommendations", redirect: "/materials/recommendation" },
  { path: "/dashboard", redirect: "/inquiries" },
  { path: "/dashboard/:id", redirect: (to) => `/inquiries/${to.params.id}` },
  { path: "/supplier-register", redirect: "/supplier/dashboard" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.name === "login" && isLoggedIn()) {
    return authRedirectPath();
  }

  if (!to.meta.requiresAuth) return true;

  const role = to.meta.role;

  if (!isLoggedIn()) {
    return { path: "/login", query: { role, redirect: to.fullPath } };
  }

  if (role && !hasRole(role)) {
    return { path: authRedirectPath(), query: { roleMismatch: role } };
  }

  return true;
});

function authRedirectPath() {
  return hasRole("supplier") ? "/supplier/dashboard" : "/materials/request";
}

export default router;
