<template>
  <main class="community-page page-wrap">
    <header class="community-hero">
      <div>
        <p class="eyebrow">PaceFlow Community</p>
        <h1>커뮤니티</h1>
        <p>자재 수급 정보와 대체 자재 사용 경험을 공유하세요.</p>
      </div>
      <RouterLink class="community-write-button" to="/community/new">글쓰기</RouterLink>
    </header>

    <nav class="community-tabs" aria-label="커뮤니티 게시글 유형">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        type="button"
        :class="{ active: activeType === tab.value }"
        @click="activeType = tab.value"
      >{{ tab.label }}</button>
    </nav>

    <p v-if="loading" class="community-state">게시글을 불러오는 중입니다.</p>
    <p v-else-if="errorMessage" class="community-state error">{{ errorMessage }}</p>

    <section v-else-if="posts.length" class="community-grid">
      <article v-for="post in posts" :key="post.id" class="community-card" @click="openPost(post.id)">
        <CommunityAuthorHeader
          :author="post.author"
          :owner="post.is_owner"
          @question="askQuestion(post)"
          @profile="viewProfile(post)"
          @report="showReportNotice"
          @edit="editPost(post)"
          @delete="removePost(post)"
        />
        <div class="community-card-type-row">
          <span :class="['community-type', post.post_type]">{{ post.post_type_label }}</span>
          <time>{{ formatDate(post.created_at) }}</time>
        </div>
        <h2>{{ post.title }}</h2>
        <p class="community-preview">{{ post.content }}</p>
        <dl class="community-meta">
          <div v-if="post.material_name"><dt>자재</dt><dd>{{ post.material_name }}</dd></div>
          <div v-if="post.supplier_name"><dt>공급사</dt><dd>{{ post.supplier_name }}</dd></div>
          <div v-if="post.region"><dt>지역</dt><dd>{{ post.region }}</dd></div>
        </dl>
        <footer>
          <span class="community-status">{{ post.status || "정보 공유" }}</span>
          <span>댓글 {{ post.comment_count }}개</span>
        </footer>
      </article>
    </section>

    <section v-else class="community-empty">
      <strong>아직 등록된 게시글이 없습니다.</strong>
      <p>첫 번째 자재 수급 경험을 공유해보세요.</p>
      <RouterLink to="/community/new">글쓰기</RouterLink>
    </section>

    <p v-if="notice" class="community-toast" role="status">{{ notice }}</p>
    <CommunityQuestionModal
      v-if="questionPost"
      :post="questionPost"
      @close="questionPost = null"
      @sent="handleSent"
    />
  </main>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { isLoggedIn } from "../api/authApi";
import { deleteCommunityPost, getCommunityPosts } from "../api/communityApi";
import CommunityAuthorHeader from "../components/CommunityAuthorHeader.vue";
import CommunityQuestionModal from "../components/CommunityQuestionModal.vue";

const router = useRouter();
const tabs = [
  { value: "", label: "전체" },
  { value: "substitute_review", label: "대체 자재 후기" },
  { value: "supplier_review", label: "공급사 후기" },
  { value: "field_question", label: "현장 질문" },
];
const activeType = ref("");
const posts = ref([]);
const loading = ref(false);
const errorMessage = ref("");
const questionPost = ref(null);
const notice = ref("");

onMounted(loadPosts);
watch(activeType, loadPosts);

async function loadPosts() {
  try {
    loading.value = true;
    errorMessage.value = "";
    posts.value = await getCommunityPosts(activeType.value);
  } catch {
    errorMessage.value = "커뮤니티 게시글을 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

function openPost(id) {
  router.push(`/community/${id}`);
}

function askQuestion(post) {
  if (!isLoggedIn()) {
    router.push({ path: "/login", query: { redirect: `/community/${post.id}` } });
    return;
  }
  questionPost.value = post;
}

function viewProfile(post) {
  if (post.author?.profile_id && !post.author?.is_anonymous) {
    router.push(`/profile/${post.author.profile_id}`);
    return;
  }
  showNotice("공개 프로필 정보를 확인할 수 없습니다.");
}

function showReportNotice() {
  showNotice("신고 접수 기능은 MVP 이후 제공됩니다.");
}

function editPost(post) {
  router.push(`/community/${post.id}/edit`);
}

async function removePost(post) {
  if (!window.confirm("이 게시글을 삭제하시겠습니까?")) return;
  try {
    await deleteCommunityPost(post.id);
    posts.value = posts.value.filter((item) => item.id !== post.id);
    showNotice("게시글이 삭제되었습니다.");
  } catch {
    showNotice("게시글을 삭제하지 못했습니다.");
  }
}

function handleSent(message) {
  questionPost.value = null;
  showNotice(message);
}

function showNotice(message) {
  notice.value = message;
  window.setTimeout(() => { notice.value = ""; }, 4500);
}

function formatDate(value) {
  const date = new Date(value);
  const elapsedMs = Date.now() - date.getTime();
  const minutes = Math.max(0, Math.floor(elapsedMs / 60000));
  if (minutes < 1) return "방금 전";
  if (minutes < 60) return `${minutes}분 전`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}일 전`;
  return new Intl.DateTimeFormat("ko-KR", { month: "short", day: "numeric" }).format(date);
}
</script>

<style scoped>
.community-page { padding-top:clamp(36px,6vw,64px); padding-bottom:72px; }
.community-hero { display:flex; align-items:flex-end; justify-content:space-between; gap:32px; margin-bottom:24px; padding:4px 2px 22px; border-bottom:1px solid #dbe6f8; }
.community-hero .eyebrow { margin-bottom:12px; color:#1d66eb; }
.community-hero h1 { margin:0; color:#102a56; font-size:clamp(36px,5vw,64px); line-height:1.08; letter-spacing:0; }
.community-hero div>p:last-child { max-width:700px; margin:14px 0 0; color:#65748d; font-size:16px; line-height:1.7; }
.community-write-button { display:inline-flex; min-height:46px; align-items:center; justify-content:center; border-radius:999px; padding:0 22px; color:#fff; background:linear-gradient(135deg,#1559e8,#1f8df2); box-shadow:0 10px 24px rgba(21,89,232,.2); text-decoration:none; font-weight:900; white-space:nowrap; transition:transform .18s,box-shadow .18s; }
.community-write-button:hover { transform:translateY(-2px); box-shadow:0 14px 30px rgba(21,89,232,.26); }
.community-tabs { display:flex; flex-wrap:wrap; gap:9px; margin:0 0 20px; }
.community-tabs button { border:1px solid #d7e3f5; border-radius:999px; padding:10px 16px; color:#51627e; background:rgba(255,255,255,.82); cursor:pointer; font-weight:800; transition:border-color .18s,color .18s,background .18s; }
.community-tabs button:hover { border-color:#9ebbea; color:#1559e8; background:#f5f8ff; }
.community-tabs button.active { border-color:#1559e8; color:#fff; background:#1559e8; }
.community-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:17px; }
.community-card { display:flex; min-height:348px; flex-direction:column; border:1px solid #dbe6f8; border-radius:22px; padding:19px; background:#fff; box-shadow:0 14px 38px rgba(31,61,115,.075); cursor:pointer; transition:transform .18s,box-shadow .18s; }
.community-card:hover { transform:translateY(-4px); box-shadow:0 24px 60px rgba(31,61,115,.14); }
.community-card-type-row { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-top:16px; }
.community-card-type-row time { color:#8b99ad; font-size:12px; }
.community-type { border-radius:999px; padding:6px 9px; font-size:12px; font-weight:900; }
.community-type.substitute_review { color:#047857; background:#dff8ef; }
.community-type.supplier_review { color:#1559e8; background:#e7efff; }
.community-type.field_question { color:#7c3aed; background:#f1eaff; }
.community-card h2 { margin:13px 0 8px; color:#102a56; font-size:19px; line-height:1.42; letter-spacing:-.02em; }
.community-preview { display:-webkit-box; overflow:hidden; margin:0 0 14px; color:#5e6c83; line-height:1.68; -webkit-line-clamp:4; -webkit-box-orient:vertical; }
.community-meta { display:grid; gap:7px; margin:auto 0 15px; border-radius:13px; padding:10px 11px; background:#f7f9fd; }
.community-meta div { display:grid; grid-template-columns:48px minmax(0,1fr); gap:8px; font-size:13px; line-height:1.4; }
.community-meta dt { color:#8b99ad; }.community-meta dd { margin:0; color:#334155; font-weight:800; }
.community-card footer { display:flex; align-items:center; justify-content:space-between; gap:18px; border-top:1px solid #edf2fa; padding-top:13px; color:#77869c; font-size:12px; }
.community-status { color:#1559e8; font-weight:900; }
.community-state,.community-empty { border-radius:22px; padding:50px; background:#fff; color:#65748d; text-align:center; }.community-state.error{color:#c24141}.community-empty strong{display:block;color:#102a56;font-size:20px}.community-empty a{display:inline-block;margin-top:14px;color:#1559e8;font-weight:900}
.community-toast { position:fixed; right:24px; bottom:24px; z-index:900; max-width:420px; border-radius:15px; padding:14px 18px; color:#fff; background:#102a56; box-shadow:0 16px 40px rgba(0,0,0,.2); }
@media (max-width:1000px){.community-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:650px){.community-hero{align-items:flex-start;flex-direction:column;gap:20px;padding:0 0 22px}.community-write-button{align-self:stretch}.community-grid{grid-template-columns:1fr}.community-card{min-height:0}}
</style>
