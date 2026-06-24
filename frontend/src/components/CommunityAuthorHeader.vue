<template>
  <div class="community-author-header">
    <div
      class="community-author-avatar"
      :class="{
        anonymous: author?.is_anonymous,
        'default-user': !author?.is_anonymous && !resolvedProfileImage,
      }"
    >
      <img v-if="author?.is_anonymous" src="/basic_profile.png" class="avatar-img" alt="" />
      <img v-else-if="resolvedProfileImage" :src="resolvedProfileImage" class="avatar-img" alt="" />
      <span v-else class="default-user-avatar" aria-hidden="true">
        <svg viewBox="0 0 48 48">
          <ellipse cx="24" cy="45" rx="18" ry="12" fill="#8b5838" />
          <circle cx="11.5" cy="14" r="4" fill="#70432d" />
          <circle cx="36.5" cy="14" r="4" fill="#70432d" />
          <circle cx="11.5" cy="14" r="2" fill="#bd8058" />
          <circle cx="36.5" cy="14" r="2" fill="#bd8058" />
          <path d="M7.5 25.5C7.5 13.6 14.2 7 24 7s16.5 6.6 16.5 18.5c0 11.2-6.6 18-16.5 18s-16.5-6.8-16.5-18z" fill="#a96f43" />
          <circle cx="17.5" cy="23" r="1.7" fill="#263a50" />
          <circle cx="30.5" cy="23" r="1.7" fill="#263a50" />
          <ellipse cx="24" cy="31" rx="10" ry="7.7" fill="#d8a575" />
          <ellipse cx="24" cy="27.5" rx="4.5" ry="3.2" fill="#4d3027" />
          <path d="M24 30v3.2M24 32.8c-1.7 1.6-3.7 1.8-5.4.4M24 32.8c1.7 1.6 3.7 1.8 5.4.4" fill="none" stroke="#704329" stroke-width="1.4" stroke-linecap="round" />
          <rect x="20.5" y="34.5" width="3.5" height="5.5" rx="1" fill="#fff9e9" />
          <rect x="24" y="34.5" width="3.5" height="5.5" rx="1" fill="#fff9e9" />
        </svg>
      </span>
    </div>
    <div class="community-author-copy">
      <strong>{{ author?.display_name || "PaceFlow 사용자" }}</strong>
      <span>
        {{ author?.role || "PaceFlow 사용자" }}
        <template v-if="author?.affiliation"> · {{ author.affiliation }}</template>
      </span>
    </div>
    <div v-if="menu" class="community-more-wrap">
      <button type="button" class="community-more-button" aria-label="게시글 메뉴" @click.stop="open = !open">•••</button>
      <div v-if="open" class="community-more-menu" @click.stop>
        <button v-if="owner" type="button" @click="emitAction('edit')">수정하기</button>
        <button v-if="owner" type="button" class="delete" @click="emitAction('delete')">삭제하기</button>
        <button v-if="!owner" type="button" @click="emitAction('question')">작성자에게 질문</button>
        <button v-if="!author?.is_anonymous" type="button" @click="emitAction('profile')">프로필 보기</button>
        <button v-if="!owner" type="button" class="report" @click="emitAction('report')">신고하기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { authState } from "../api/authApi";

const props = defineProps({
  author: { type: Object, default: () => ({}) },
  menu: { type: Boolean, default: true },
  owner: { type: Boolean, default: false },
});
const emit = defineEmits(["question", "profile", "report", "edit", "delete"]);
const open = ref(false);

const resolvedProfileImage = computed(() => {
  if (!props.author || props.author.is_anonymous) return null;
  if (props.author.profile_id != null && props.author.profile_id === authState.user?.id) {
    return localStorage.getItem("paceflow_profile_img") || null;
  }
  return null;
});

function emitAction(action) {
  open.value = false;
  emit(action);
}
</script>

<style scoped>
.community-author-header { display:grid; grid-template-columns:42px minmax(0,1fr) auto; align-items:center; gap:11px; min-width:0; }
.community-author-avatar { display:grid; place-items:center; width:42px; height:42px; border-radius:14px; color:#fff; background:linear-gradient(135deg,#1559e8,#22a6f2); box-shadow:0 7px 18px rgba(21,89,232,.16); font-size:12px; font-weight:1000; line-height:1; overflow:hidden; }
.community-author-avatar:not(.anonymous) { border-radius:50%; }
.community-author-avatar.default-user { background:#eaf3ff; box-shadow:inset 0 0 0 1px rgba(93,143,207,.2),0 5px 14px rgba(21,89,232,.11); }
.community-author-avatar.anonymous { background:linear-gradient(135deg,#263a60,#6c7e9d); }
.avatar-img { width:100%; height:100%; object-fit:cover; border-radius:14px; }
.community-author-avatar:not(.anonymous) .avatar-img { border-radius:50%; }
.default-user-avatar { display:grid; width:100%; height:100%; place-items:center; }
.default-user-avatar svg { width:40px; height:40px; }
.community-author-copy { min-width:0; flex:1; }
.community-author-copy strong,.community-author-copy span { display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.community-author-copy strong { color:#102a56; font-size:14px; line-height:1.35; }
.community-author-copy span { margin-top:3px; color:#71809a; font-size:12px; line-height:1.4; }
.community-more-wrap { position:relative; }
.community-more-button { width:34px; height:34px; border:0; border-radius:10px; color:#71809a; background:#f4f7fc; cursor:pointer; font-weight:900; letter-spacing:1px; }
.community-more-menu { position:absolute; top:40px; right:0; z-index:20; width:160px; overflow:hidden; border:1px solid #dbe6f8; border-radius:13px; background:#fff; box-shadow:0 16px 40px rgba(16,42,86,.16); }
.community-more-menu button { display:block; width:100%; border:0; padding:11px 13px; color:#334155; background:#fff; text-align:left; cursor:pointer; font-weight:700; }
.community-more-menu button:hover { background:#f3f7ff; color:#1559e8; }
.community-more-menu .report { color:#c24141; }
.community-more-menu .delete { color:#b42318; }
</style>
