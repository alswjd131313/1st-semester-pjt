<template>
  <header class="header-nav">
    <RouterLink class="brand" to="/">
      <span class="brand-mark">PF</span>
      <span>
        <strong>PaceFlow</strong>
        <small>Keep Your Supply Moving</small>
      </span>
    </RouterLink>

    <nav>
      <RouterLink to="/request">자재 요청</RouterLink>
      <RouterLink to="/recommendations">추천 결과</RouterLink>
      <RouterLink to="/supplier-register">공급사 등록</RouterLink>
    </nav>

    <div class="auth-actions">
      <template v-if="authState.user">
        <span class="user-chip">
          {{ roleLabel }} · {{ authState.user.name }}
        </span>
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
import { useRouter } from "vue-router";
import { authState, logoutUser } from "../api/authApi";

const router = useRouter();

const roleLabel = computed(() =>
  authState.user?.role === "supplier" ? "공급사" : "요청자",
);

function handleLogout() {
  logoutUser();
  router.push("/");
}
</script>
