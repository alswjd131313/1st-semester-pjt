<template>
  <header :class="['header-nav', { 'home-header': isHomeRoute }]">
    <RouterLink class="brand" to="/">
      <img class="brand-logo" src="/logo.png" alt="PaceFlow" />
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
        <NotificationBell :user="authState.user" />
        <div class="profile-wrap" ref="dropdownWrapRef">
          <button
            type="button"
            :class="['profile-trigger', { 'is-active': myPageRouteNames.includes(route.name) }]"
            @click.stop="toggleDropdown"
          >
            <span class="profile-avatar">
              <img v-if="profileImage" :src="profileImage" class="profile-avatar-img" alt="" />
              <span v-else>{{ userInitials }}</span>
            </span>
            <span class="profile-name">{{ displayName }}</span>
            <span class="profile-chevron" :class="{ open: showDropdown }">▾</span>
          </button>

          <Transition name="dropdown">
            <div v-if="showDropdown" class="profile-dropdown">
              <RouterLink
                class="dropdown-item"
                :to="{ name: isSupplier ? 'supplier-mypage' : 'mypage' }"
                @click="showDropdown = false"
              >
                <span>👤</span> 마이페이지
              </RouterLink>
              <RouterLink
                class="dropdown-item"
                :to="{ name: 'inquiries' }"
                @click="showDropdown = false"
              >
                <span>📋</span> {{ isSupplier ? "받은 요청" : "문의 내역" }}
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
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authState, getProfileImageUrl, logoutUser } from "../api/authApi";
import NotificationBell from "./NotificationBell.vue";

const router = useRouter();
const route = useRoute();
const isSupplier = computed(() => authState.user?.role === "supplier");
const isHomeRoute = computed(() => route.name === "home");
const inquiryRouteNames = ["inquiries", "inquiry-detail", "inquiry-edit"];
const myPageRouteNames = computed(() => [
  "mypage",
  "supplier-mypage",
  "supplier-materials",
  "supplier-profile",
  ...(!isSupplier.value ? inquiryRouteNames : []),
]);
const navItems = computed(() => [
  ...(isSupplier.value
    ? [
        {
          name: "supplier-materials",
          label: "자재 관리",
          activeRoutes: ["supplier-materials", "supplier-profile"],
        },
        {
          name: "inquiries",
          label: "문의 현황",
          activeRoutes: inquiryRouteNames,
        },
      ]
    : [{
        name: "material-request",
        label: "자재 요청",
        activeRoutes: ["material-request"],
      }]),
  ...(!isSupplier.value ? [{
      name: "recommendation",
      label: "추천 결과",
      activeRoutes: ["recommendation", "recommendation-detail", "price-trend"],
    }] : []),
  {
    name: "community",
    label: "커뮤니티",
    activeRoutes: ["community", "community-write", "community-edit", "community-detail"],
  },
]);
const dropdownWrapRef = ref(null);
const showDropdown = ref(false);

const userInitials = computed(() => {
  const name = authState.user?.name || authState.user?.companyName || "";
  return name.slice(0, 2).toUpperCase();
});

const displayName = computed(() =>
  authState.user?.name || authState.user?.companyName || ""
);

const profileImage = computed(() => getProfileImageUrl(authState.user) || null);

watch(showDropdown, (val) => {
  if (val) {
    document.addEventListener("click", handleOutsideClick);
  } else {
    document.removeEventListener("click", handleOutsideClick);
  }
});

onBeforeUnmount(() => {
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

.header-nav.home-header {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) auto minmax(260px, 1fr);
  align-items: center;
  min-height: 88px;
  padding: 18px clamp(56px, 4.4vw, 72px);
}

.header-nav.home-header .brand {
  justify-self: start;
}

.header-nav.home-header nav {
  justify-self: center;
  gap: 30px;
}

.header-nav.home-header .auth-actions {
  justify-self: end;
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
  border: 1px solid #d8e4f3;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
  color: #102a56;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
}

.profile-trigger:hover {
  border-color: #bcd0ee;
  background: #fff;
}

.profile-trigger.is-active {
  box-shadow: inset 0 0 0 2px rgba(21, 89, 232, 0.2);
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
  overflow: hidden;
}

.profile-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.profile-name {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  box-sizing: border-box;
  padding: 0 9px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 3px 10px rgba(15, 23, 42, 0.08);
  font-size: 14px;
  font-weight: 700;
  color: #102a56;
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

/* 홈페이지에서도 다른 페이지와 동일한 밝은 프로필 pill 유지 */
.header-nav.home-header .profile-trigger,
:global(.app-shell:has(.home-page)) .profile-trigger {
  border-color: rgba(216, 226, 240, 0.98) !important;
  background: #fff !important;
  box-shadow: 0 10px 28px rgba(8, 24, 54, 0.18) !important;
  color: #102a56 !important;
}

.header-nav.home-header .profile-name,
:global(.app-shell:has(.home-page)) .profile-name {
  color: #102a56;
  border-color: rgba(226, 232, 240, 0.95);
  background: #f8fafc;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.header-nav.home-header .profile-chevron,
:global(.app-shell:has(.home-page)) .profile-chevron {
  color: #94a3b8;
}

.header-nav.home-header .profile-trigger:hover,
:global(.app-shell:has(.home-page)) .profile-trigger:hover {
  border-color: #bcd0ee !important;
  background: #fff !important;
}

.header-nav.home-header :deep(.notification-trigger) {
  border-color: rgba(216, 226, 240, 0.98) !important;
  color: #40516b !important;
  background: #fff !important;
  box-shadow: 0 10px 28px rgba(8, 24, 54, 0.16) !important;
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

@media (max-width: 820px) {
  .header-nav.home-header {
    display: flex;
    min-height: auto;
    padding: 18px 20px;
  }

  .header-nav.home-header .brand,
  .header-nav.home-header nav,
  .header-nav.home-header .auth-actions {
    justify-self: auto;
  }

  .profile-wrap,
  .profile-trigger {
    width: 100%;
  }

  .profile-trigger {
    justify-content: center;
  }

  .profile-name {
    max-width: min(160px, 45vw);
  }
}
</style>
