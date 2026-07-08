<template>
  <main class="profile-page page-wrap">
    <RouterLink class="back-link" to="/community">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
      커뮤니티로
    </RouterLink>

    <p v-if="loading" class="loading-message">프로필을 불러오는 중입니다.</p>

    <div v-else-if="errorMessage" class="empty-state">
      <strong>공개 프로필을 확인할 수 없습니다.</strong>
      <p>{{ errorMessage }}</p>
    </div>

    <template v-else-if="profile">
      <!-- 프로필 헤로 카드 -->
      <section class="profile-hero-card">
        <div class="profile-avatar-wrap">
          <div class="profile-avatar">
            <img
              v-if="resolvedProfileImage && !profileImageFailed"
              :src="resolvedProfileImage"
              class="profile-avatar-img"
              alt=""
              @error="profileImageFailed = true"
            />
            <DefaultBeaverAvatar v-else />
          </div>
          <div class="avatar-check-badge" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
          </div>
        </div>

        <div class="profile-hero-info">
          <h1>{{ profile.display_name }}</h1>
          <p class="profile-subtitle">
            {{ profile.role || "PaceFlow 사용자" }}<span v-if="profile.affiliation"> · {{ profile.affiliation }}</span>
          </p>
          <div class="profile-badges">
            <span class="profile-badge">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>
              실명 인증 완료
            </span>
            <span class="profile-badge">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
              현장 담당자
            </span>
          </div>
        </div>

        <div class="profile-meta-row">
          <div class="profile-meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="meta-icon"><path d="M20 3h-1V1h-2v2H7V1H5v2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H4V8h16v13z"/></svg>
            <span class="meta-label">가입일</span>
            <strong class="meta-value">{{ joinedLabel }}</strong>
          </div>
          <div class="profile-meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="meta-icon"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/></svg>
            <span class="meta-label">소속 회사</span>
            <strong class="meta-value">{{ profile.affiliation || "등록 정보 없음" }}</strong>
          </div>
          <div class="profile-meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="meta-icon"><path d="M20 6h-8l-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2z"/></svg>
            <span class="meta-label">등록 정보</span>
            <strong class="meta-value">{{ profile.project_name || "등록 정보 없음" }}</strong>
          </div>
        </div>
      </section>

      <!-- 주요 정보 -->
      <section class="profile-section">
        <h2>주요 정보</h2>
        <div class="info-grid">
          <div class="info-card">
            <div class="info-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
            </div>
            <div>
              <span class="info-label">역할 / 직무</span>
              <strong class="info-value">{{ profile.role || "PaceFlow 사용자" }}</strong>
            </div>
          </div>
          <div class="info-card">
            <div class="info-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/></svg>
            </div>
            <div>
              <span class="info-label">소속 회사</span>
              <strong class="info-value">{{ profile.affiliation || "등록 정보 없음" }}</strong>
            </div>
          </div>
          <div class="info-card">
            <div class="info-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20 6h-8l-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2z"/></svg>
            </div>
            <div>
              <span class="info-label">현장 / 프로젝트</span>
              <strong class="info-value">{{ profile.project_name || "등록 정보 없음" }}</strong>
            </div>
          </div>
          <div class="info-card">
            <div class="info-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.89 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
            </div>
            <div>
              <span class="info-label">실명 커뮤니티 글</span>
              <strong class="info-value">{{ profile.community_post_count ?? 0 }}건</strong>
            </div>
          </div>
        </div>
      </section>

      <!-- 활동 요약 -->
      <section class="profile-section">
        <h2>활동 요약</h2>
        <div class="activity-row">
          <div class="activity-item">
            <div class="activity-icon activity-icon-gray">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>
            </div>
            <div class="activity-info">
              <span class="activity-label">문의 경험</span>
              <strong class="activity-count">{{ profile.received_contact_request_count ?? 0 }}건</strong>
              <span class="activity-sub">최근 6개월 기준</span>
            </div>
          </div>
          <div class="activity-divider"></div>
          <div class="activity-item">
            <div class="activity-icon activity-icon-green">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
            </div>
            <div class="activity-info">
              <span class="activity-label">공급사 평가</span>
              <strong class="activity-count">{{ profile.supplier_review_count ?? 0 }}건</strong>
              <span class="activity-sub">평가 참여</span>
            </div>
          </div>
          <div class="activity-divider"></div>
          <div class="activity-item">
            <div class="activity-icon activity-icon-purple">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>
            </div>
            <div class="activity-info">
              <span class="activity-label">배지 획득</span>
              <strong class="activity-count">{{ profile.badge_count ?? 0 }}개</strong>
              <span class="activity-sub">총 획득 배지</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 하단 면책 -->
      <p class="profile-disclaimer">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>
        프로필 정보는 사용자가 공개한 정보로 표시됩니다.
      </p>
    </template>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { authState, getProfileImageUrl } from "../api/authApi";
import { getCommunityProfile } from "../api/communityApi";
import DefaultBeaverAvatar from "../components/DefaultBeaverAvatar.vue";

const route = useRoute();
const profile = ref(null);
const loading = ref(false);
const errorMessage = ref("");
const profileImageFailed = ref(false);

const resolvedProfileImage = computed(() => {
  const image = getProfileImageUrl(profile.value);
  if (image) return image;
  if (profile.value?.id != null && profile.value.id === authState.user?.id) {
    return getProfileImageUrl(authState.user) || "";
  }
  return "";
});

const joinedLabel = computed(() => {
  const raw = profile.value?.joined_at || profile.value?.date_joined;
  if (!raw) return "---";
  const d = new Date(raw);
  if (isNaN(d.getTime())) return "---";
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}`;
});

onMounted(loadProfile);
watch(() => route.params.id, loadProfile);

async function loadProfile() {
  try {
    loading.value = true;
    errorMessage.value = "";
    profileImageFailed.value = false;
    profile.value = await getCommunityProfile(route.params.id);
  } catch {
    profile.value = null;
    errorMessage.value = "실명으로 공개된 커뮤니티 작성자만 프로필을 볼 수 있습니다.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.profile-page { max-width: 820px; padding-top: clamp(32px, 5vw, 56px); padding-bottom: 72px; }

/* Back Link */
.back-link { display: inline-flex; align-items: center; gap: 5px; margin-bottom: 24px; color: var(--color-primary, #1d66eb); text-decoration: none; font-size: 14px; font-weight: 700; }
.back-link:hover { opacity: .75; }

/* Hero Card */
.profile-hero-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 28px 32px 0; margin-bottom: 20px; overflow: hidden; }
.profile-avatar-wrap { position: relative; width: 110px; height: 110px; margin-bottom: 16px; }
.profile-avatar { width: 110px; height: 110px; border-radius: 50%; background: #eaf3ff; box-shadow: inset 0 0 0 1px rgba(93,143,207,.2), 0 10px 24px rgba(21,89,232,.14); display: flex; align-items: center; justify-content: center; overflow: hidden; }
.profile-avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.avatar-check-badge { position: absolute; bottom: 4px; right: 4px; width: 24px; height: 24px; border-radius: 50%; background: #1d66eb; border: 2px solid #fff; display: flex; align-items: center; justify-content: center; }
.profile-hero-info { padding-bottom: 20px; }
.profile-hero-info h1 { font-size: 30px; font-weight: 900; color: #1e293b; margin: 0 0 6px; }
.profile-subtitle { font-size: 15px; color: #64748b; margin: 0 0 14px; }
.profile-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.profile-badge { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border: 1.5px solid #bfdbfe; border-radius: 99px; font-size: 12.5px; font-weight: 600; color: #1d66eb; background: #eff6ff; }
.profile-meta-row { display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid #f1f5f9; margin: 0 -32px; }
.profile-meta-item { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; padding: 18px 24px; }
.profile-meta-item + .profile-meta-item { border-left: 1px solid #f1f5f9; }
.meta-icon { color: #94a3b8; }
.meta-label { font-size: 11px; color: #94a3b8; font-weight: 600; }
.meta-value { font-size: 15px; font-weight: 800; color: #1e293b; }

/* Sections */
.profile-section { background: #fff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 24px 28px; margin-bottom: 16px; }
.profile-section h2 { font-size: 17px; font-weight: 800; color: #1e293b; margin: 0 0 16px; }

/* Info Grid */
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.info-card { display: flex; align-items: center; gap: 14px; padding: 16px; border: 1px solid #f1f5f9; border-radius: 12px; background: #fafbfc; }
.info-icon-wrap { width: 40px; height: 40px; border-radius: 10px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: #64748b; }
.info-label { font-size: 11px; color: #94a3b8; font-weight: 600; display: block; margin-bottom: 3px; }
.info-value { font-size: 15px; font-weight: 800; color: #1e293b; display: block; }

/* Activity Row */
.activity-row { display: flex; align-items: center; gap: 0; }
.activity-item { flex: 1; display: flex; align-items: center; gap: 16px; padding: 8px 16px 8px 0; }
.activity-item:first-child { padding-left: 0; }
.activity-divider { width: 1px; height: 56px; background: #f1f5f9; flex-shrink: 0; }
.activity-icon { width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.activity-icon-gray { background: #f1f5f9; color: #64748b; }
.activity-icon-green { background: #dcfce7; color: #16a34a; }
.activity-icon-purple { background: #ede9fe; color: #7c3aed; }
.activity-info { display: flex; flex-direction: column; gap: 2px; }
.activity-label { font-size: 12px; color: #94a3b8; font-weight: 600; }
.activity-count { font-size: 22px; font-weight: 900; color: #1e293b; line-height: 1.1; }
.activity-sub { font-size: 11px; color: #94a3b8; }

/* Disclaimer */
.profile-disclaimer { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #94a3b8; text-align: center; justify-content: center; margin-top: 8px; }
.profile-disclaimer svg { color: #cbd5e1; }

@media (max-width: 600px) {
  .profile-hero-card { padding: 20px 20px 0; }
  .profile-meta-row { grid-template-columns: 1fr; margin: 0 -20px; }
  .profile-meta-item + .profile-meta-item { border-left: none; border-top: 1px solid #f1f5f9; }
  .info-grid { grid-template-columns: 1fr; }
  .activity-row { flex-direction: column; align-items: flex-start; gap: 16px; }
  .activity-divider { width: 100%; height: 1px; }
}
</style>
