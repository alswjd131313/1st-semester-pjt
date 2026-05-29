import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import MaterialRequestPage from "../pages/MaterialRequestPage.vue";
import RecommendationPage from "../pages/RecommendationPage.vue";
import SupplierRegisterPage from "../pages/SupplierRegisterPage.vue";
import LoginPage from "../pages/LoginPage.vue";
import NearbySuppliersPage from "../pages/NearbySuppliersPage.vue";

const routes = [
  { path: "/", name: "home", component: HomePage },
  { path: "/request", name: "request", component: MaterialRequestPage },
  { path: "/recommendations", name: "recommendations", component: RecommendationPage },
  { path: "/nearby-suppliers", name: "nearby-suppliers", component: NearbySuppliersPage },
  { path: "/login", name: "login", component: LoginPage },
  { path: "/supplier-register", name: "supplier-register", component: SupplierRegisterPage },
];

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});
