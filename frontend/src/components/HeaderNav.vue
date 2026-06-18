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
      <RouterLink v-if="!isSupplier" to="/request">자재 요청</RouterLink>
      <RouterLink to="/recommendations">추천 결과</RouterLink>
      <RouterLink v-if="!isRequester" to="/supplier-register">공급사 등록</RouterLink>
      <RouterLink to="/dashboard">문의 내역</RouterLink>
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
const isSupplier = computed(() => authState.user?.role === "supplier");
const isRequester = computed(() => authState.user?.role === "requester");

async function handleLogout() {
  await logoutUser();
  router.push("/");
}
</script>
