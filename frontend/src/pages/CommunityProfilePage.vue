<template>
  <main class="profile-page page-wrap">
    <RouterLink class="back-link" to="/community">← 커뮤니티로</RouterLink>
    <p v-if="loading" class="loading-message">프로필을 불러오는 중입니다.</p>
    <div v-else-if="errorMessage" class="empty-state">
      <strong>공개 프로필을 확인할 수 없습니다.</strong>
      <p>{{ errorMessage }}</p>
    </div>

    <template v-else-if="profile">
      <section class="profile-hero">
        <div class="profile-avatar" aria-hidden="true">{{ profile.avatar_text || initials }}</div>
        <div>
          <p class="eyebrow">PaceFlow Profile</p>
          <h1>{{ profile.display_name }}</h1>
          <p>{{ profile.role }}<template v-if="profile.affiliation"> · {{ profile.affiliation }}</template></p>
        </div>
      </section>

      <section class="profile-grid">
        <article><span>소속/회사</span><strong>{{ profile.affiliation || "등록 정보 없음" }}</strong></article>
        <article><span>역할/직무</span><strong>{{ profile.role || "PaceFlow 사용자" }}</strong></article>
        <article><span>현장/프로젝트</span><strong>{{ profile.project_name || "등록 정보 없음" }}</strong></article>
        <article><span>실명 커뮤니티 글</span><strong>{{ profile.community_post_count }}건</strong></article>
        <article><span>공개 글로 받은 대화 요청</span><strong>{{ profile.received_contact_request_count }}건</strong></article>
      </section>
    </template>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { getCommunityProfile } from "../api/communityApi";

const route = useRoute();
const profile = ref(null);
const loading = ref(false);
const errorMessage = ref("");
const initials = computed(() => (profile.value?.display_name || "PF").slice(0, 2).toUpperCase());

onMounted(loadProfile);
watch(() => route.params.id, loadProfile);

async function loadProfile() {
  try {
    loading.value = true;
    errorMessage.value = "";
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
.profile-page{max-width:900px}.back-link{display:inline-block;margin-bottom:22px;color:#1559e8;text-decoration:none;font-weight:900}.profile-hero{display:flex;align-items:center;gap:24px;border:1px solid #dbe6f8;border-radius:28px;padding:clamp(24px,5vw,42px);background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(231,241,255,.92));box-shadow:0 20px 60px rgba(31,61,115,.1)}.profile-avatar{display:grid;flex:0 0 auto;place-items:center;width:88px;height:88px;border-radius:28px;color:#fff;background:linear-gradient(135deg,#1559e8,#22a6f2);box-shadow:0 14px 30px rgba(21,89,232,.22);font-size:24px;font-weight:1000}.profile-hero .eyebrow{margin-bottom:8px}.profile-hero h1{font-size:clamp(34px,5vw,52px)}.profile-hero div>p:last-child{margin:10px 0 0;color:#65748d}.profile-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:18px}.profile-grid article{display:grid;gap:7px;border:1px solid #dbe6f8;border-radius:19px;padding:20px;background:#fff}.profile-grid span{color:#8492a8;font-size:12px}.profile-grid strong{color:#18365f;font-size:17px}.profile-grid article:nth-last-child(1){grid-column:1/-1}@media(max-width:650px){.profile-hero{align-items:flex-start;flex-direction:column}.profile-grid{grid-template-columns:1fr}.profile-grid article:nth-last-child(1){grid-column:auto}}
</style>
