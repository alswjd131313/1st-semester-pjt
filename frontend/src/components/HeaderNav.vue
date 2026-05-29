<template>
  <header class="header">
    <RouterLink class="brand" to="/">
      <span class="brand-mark">≋</span>
      <span>
        <strong>PaceFlow</strong>
        <small>Keep Your Supply Moving</small>
      </span>
    </RouterLink>

    <nav class="nav">
      <RouterLink to="/">홈</RouterLink>
      <RouterLink to="/request">자재 요청</RouterLink>
      <RouterLink to="/nearby-suppliers">주변 공급사</RouterLink>
      <RouterLink to="/recommendations">추천 결과</RouterLink>
      <RouterLink to="/supplier-register">공급사 등록</RouterLink>
    </nav>

    <div class="auth-nav">
      <template v-if="authState.user">
        <span>{{ authState.user.companyName }}</span>
        <button type="button" @click="handleLogout">로그아웃</button>
      </template>
      <RouterLink v-else class="login-link" to="/login?role=requester">로그인</RouterLink>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from "vue-router";
import { authState, logout } from "../api/authApi";

const router = useRouter();

function handleLogout() {
  logout();
  router.push("/");
}
</script>
