<template>
  <header class="header-nav">
    <RouterLink class="brand" to="/">
      <span class="brand-mark">PF</span>
      <span>
        <strong>PaceFlow</strong>
        <small>Keep Your Supply Moving</small>
      </span>
    </RouterLink>

    <nav aria-label="주요 메뉴">
      <RouterLink
        v-for="item in navItems"
        :key="item.name"
        :to="{ name: item.name }"
        :class="{ 'is-active': item.activeRoutes.includes(route.name) }"
      >{{ item.label }}</RouterLink>
    </nav>

    <div class="auth-actions">
      <template v-if="authState.user">
        <RouterLink
          :class="['user-chip', { 'is-active': myPageRouteNames.includes(route.name) }]"
          :to="{ name: isSupplier ? 'supplier-mypage' : 'mypage' }"
        >
          마이페이지
        </RouterLink>
        <button type="button" class="ghost-button" @click="handleLogout">로그아웃</button>
      </template>
      <template v-else>
        <RouterLink class="ghost-button" to="/login?role=requester">로그인</RouterLink>
      </template>
    </div>
  </header>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authState, logoutUser } from "../api/authApi";

const router = useRouter();
const route = useRoute();

const isSupplier = computed(() => authState.user?.role === "supplier");
const myPageRouteNames = ["mypage", "supplier-mypage", "supplier-profile"];
const navItems = computed(() => [
  ...(isSupplier.value
    ? [{
        name: "supplier-dashboard",
        label: "공급사 대시보드",
        activeRoutes: ["supplier-dashboard", "supplier-profile"],
      }]
    : [{
        name: "material-request",
        label: "자재 요청",
        activeRoutes: ["material-request"],
      }]),
  {
    name: "recommendation",
    label: "추천 결과",
    activeRoutes: ["recommendation", "recommendation-detail", "price-trend"],
  },
  {
    name: "inquiries",
    label: "문의 내역",
    activeRoutes: ["inquiries", "inquiry-detail"],
  },
]);

async function handleLogout() {
  await logoutUser();
  router.push("/");
}
</script>
