<template>
  <header class="header-nav">
    <RouterLink class="brand" to="/">
      <img class="brand-logo" src="/logo.png" alt="PaceFlow" />
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
        <div class="profile-wrap" ref="dropdownWrapRef">
          <button type="button" class="profile-trigger" @click.stop="toggleDropdown">
            <span class="profile-avatar">{{ userInitials }}</span>
            <span class="profile-name">{{ displayName }}</span>
            <span class="profile-chevron" :class="{ open: showDropdown }">▾</span>
          </button>

          <Transition name="dropdown">
            <div v-if="showDropdown" class="profile-dropdown">
              <RouterLink
                class="dropdown-item"
                :to="isSupplier ? '/supplier/mypage' : '/mypage'"
                @click="showDropdown = false"
              >
                <span>👤</span> 마이페이지
              </RouterLink>
              <button type="button" class="dropdown-item dropdown-logout" @click="handleLogout">
                <span>🚪</span> 로그아웃
              </button>
            </div>
          </Transition>
        </div>
      </template>
      <template v-else>
        <RouterLink class="ghost-button" to="/login?role=requester">로그인</RouterLink>
      </template>
    </div>
  </header>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authState, logoutUser } from "../api/authApi";

const router = useRouter();
const route = useRoute();
const navRef = ref(null);
const dropdownWrapRef = ref(null);
const showDropdown = ref(false);

const isSupplier = computed(() => authState.user?.role === "supplier");

const userInitials = computed(() => {
  const name = authState.user?.name || "";
  return name.slice(0, 2).toUpperCase();
});

const displayName = computed(() =>
  authState.user?.companyName || authState.user?.name || ""
);

const indicatorStyle = ref({ left: "0px", width: "0px", opacity: "0" });
const hoverPillStyle = ref({ left: "0px", width: "0px", top: "0px", height: "0px", opacity: "0" });

watch(
  () => route.path,
  () => { nextTick(updateIndicator); },
  { immediate: true },
);

watch(showDropdown, (val) => {
  if (val) {
    document.addEventListener("click", handleOutsideClick);
  } else {
    document.removeEventListener("click", handleOutsideClick);
  }
});

onUnmounted(() => {
  document.removeEventListener("click", handleOutsideClick);
});

function handleOutsideClick(e) {
  if (dropdownWrapRef.value && !dropdownWrapRef.value.contains(e.target)) {
    showDropdown.value = false;
  }
}

function toggleDropdown() {
  showDropdown.value = !showDropdown.value;
}

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
  showDropdown.value = false;
  await logoutUser();
  router.push("/");
}
</script>

<style scoped>
.brand-logo {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  object-fit: contain;
  flex-shrink: 0;
}

/* ── 프로필 드롭다운 ── */
.profile-wrap {
  position: relative;
}

.profile-trigger {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 42px;
  padding: 0 14px 0 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 999px;
  background: transparent;
  cursor: pointer;
  transition: background 0.15s;
}

.profile-trigger:hover {
  background: rgba(0, 0, 0, 0.05);
}

.profile-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1559e8;
  color: #fff;
  font-size: 11px;
  font-weight: 900;
  flex-shrink: 0;
}

.profile-name {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
  white-space: nowrap;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-chevron {
  font-size: 14px;
  color: #8fa3be;
  transition: transform 0.2s;
  display: inline-block;
}

.profile-chevron.open {
  transform: scaleY(-1);
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 160px;
  border: 1px solid #e2eaf5;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 12px 40px rgba(21, 55, 103, 0.14);
  overflow: hidden;
  z-index: 100;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 13px 16px;
  border: 0;
  background: transparent;
  font: inherit;
  font-size: 14px;
  font-weight: 700;
  color: #334155;
  cursor: pointer;
  text-align: left;
  text-decoration: none;
  transition: background 0.12s;
}

.dropdown-item:hover {
  background: #f5f8ff;
  color: #1559e8;
}

.dropdown-logout {
  border-top: 1px solid #f0f4fa;
  color: #e53e3e;
}

.dropdown-logout:hover {
  background: #fff5f5;
  color: #c53030;
}

/* 홈페이지에서 흰색 스타일 */
:global(.app-shell:has(.home-page)) .profile-trigger {
  border-color: rgba(255, 255, 255, 0.3);
}

:global(.app-shell:has(.home-page)) .profile-name {
  color: rgba(255, 255, 255, 0.9);
}

:global(.app-shell:has(.home-page)) .profile-chevron {
  color: rgba(255, 255, 255, 0.7);
}

:global(.app-shell:has(.home-page)) .profile-trigger:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 드롭다운 전환 애니메이션 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
