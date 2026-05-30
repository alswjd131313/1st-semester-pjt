import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import { isLoggedIn, hasRole } from "../api/authApi";
import LoginPage from "../pages/LoginPage.vue";
import MaterialRequestPage from "../pages/MaterialRequestPage.vue";
import RecommendationPage from "../pages/RecommendationPage.vue";
import SupplierRegisterPage from "../pages/SupplierRegisterPage.vue";
import DashboardPage from "../pages/DashboardPage.vue";
import InquiryDetailPage from "../pages/InquiryDetailPage.vue";

const routes = [
  { path: "/", name: "home", component: HomePage },
  { path: "/login", name: "login", component: LoginPage },
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/dashboard/:inquiryId",
    name: "inquiry-detail",
    component: InquiryDetailPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/request",
    name: "request",
    component: MaterialRequestPage,
    meta: { requiresAuth: true, role: "requester" },
  },
  { path: "/recommendations", name: "recommendations", component: RecommendationPage },
  {
    path: "/supplier-register",
    name: "supplier-register",
    component: SupplierRegisterPage,
    meta: { requiresAuth: true, role: "supplier" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.name === "login" && isLoggedIn()) {
    return authRedirectPath();
  }

  if (!to.meta.requiresAuth) {
    return true;
  }

  const role = to.meta.role;

  if (!isLoggedIn()) {
    return {
      path: "/login",
      query: {
        role,
        redirect: to.fullPath,
      },
    };
  }

  if (role && !hasRole(role)) {
    return {
      path: authRedirectPath(),
      query: { roleMismatch: role },
    };
  }

  return true;
});

function authRedirectPath() {
  return hasRole("supplier") ? "/supplier-register" : "/request";
}

export default router;
