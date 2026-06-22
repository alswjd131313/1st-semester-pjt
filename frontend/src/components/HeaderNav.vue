<template>
  <header class="header-nav">
    <RouterLink class="brand" to="/">
      <span class="brand-mark">PF</span>
      <span>
        <strong>PaceFlow</strong>
        <small>Keep Your Supply Moving</small>
      </span>
    </RouterLink>

    <nav ref="navRef" @mouseleave="onNavLeave">
      <RouterLink
        v-if="!isSupplier"
        to="/materials/request"
        @mouseenter="onLinkHover"
      >자재 요청</RouterLink>
      <RouterLink
        to="/materials/recommendation"
        @mouseenter="onLinkHover"
      >추천 결과</RouterLink>
      <RouterLink
        v-if="isSupplier"
        to="/supplier/dashboard"
        @mouseenter="onLinkHover"
      >공급사 대시보드</RouterLink>
      <RouterLink
        to="/inquiries"
        @mouseenter="onLinkHover"
      >문의 내역</RouterLink>

      <span class="nav-hover-pill" :style="hoverPillStyle" aria-hidden="true"></span>
      <span class="nav-indicator" :style="indicatorStyle" aria-hidden="true"></span>
    </nav>

    <div class="auth-actions">
      <template v-if="authState.user">
        <RouterLink class="user-chip" :to="isSupplier ? '/supplier/mypage' : '/mypage'">
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
import { computed, nextTick, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authState, logoutUser } from "../api/authApi";

const router = useRouter();
const route = useRoute();
const navRef = ref(null);

const isSupplier = computed(() => authState.user?.role === "supplier");

const indicatorStyle = ref({ left: "0px", width: "0px", opacity: "0" });
const hoverPillStyle = ref({ left: "0px", width: "0px", top: "0px", height: "0px", opacity: "0" });

watch(
  () => route.path,
  () => { nextTick(updateIndicator); },
  { immediate: true },
);

function updateIndicator() {
  if (!navRef.value) return;
  const active = navRef.value.querySelector(".router-link-active");
  if (!active) {
    indicatorStyle.value = { ...indicatorStyle.value, opacity: "0" };
    return;
  }
  const navRect = navRef.value.getBoundingClientRect();
  const linkRect = active.getBoundingClientRect();
  indicatorStyle.value = {
    left: linkRect.left - navRect.left + "px",
    width: linkRect.width + "px",
    opacity: "1",
  };
}

function onLinkHover(e) {
  if (!navRef.value) return;
  const navRect = navRef.value.getBoundingClientRect();
  const linkRect = e.currentTarget.getBoundingClientRect();
  hoverPillStyle.value = {
    left: linkRect.left - navRect.left - 10 + "px",
    width: linkRect.width + 20 + "px",
    top: linkRect.top - navRect.top - 6 + "px",
    height: linkRect.height + 12 + "px",
    opacity: "1",
  };
}

function onNavLeave() {
  hoverPillStyle.value = { ...hoverPillStyle.value, opacity: "0" };
}

async function handleLogout() {
  await logoutUser();
  router.push("/");
}
</script>
