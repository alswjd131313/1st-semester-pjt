<template>
  <div class="community-author-header">
    <div class="community-author-avatar" :class="{ anonymous: author?.is_anonymous }">
      {{ author?.avatar_text || "PF" }}
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
import { ref } from "vue";

defineProps({
  author: { type: Object, default: () => ({}) },
  menu: { type: Boolean, default: true },
  owner: { type: Boolean, default: false },
});
const emit = defineEmits(["question", "profile", "report", "edit", "delete"]);
const open = ref(false);

function emitAction(action) {
  open.value = false;
  emit(action);
}
</script>

<style scoped>
.community-author-header { display:grid; grid-template-columns:42px minmax(0,1fr) auto; align-items:center; gap:11px; min-width:0; }
.community-author-avatar { display:grid; place-items:center; width:42px; height:42px; border-radius:14px; color:#fff; background:linear-gradient(135deg,#1559e8,#22a6f2); box-shadow:0 7px 18px rgba(21,89,232,.16); font-size:12px; font-weight:1000; line-height:1; }
.community-author-avatar.anonymous { background:linear-gradient(135deg,#263a60,#6c7e9d); }
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
