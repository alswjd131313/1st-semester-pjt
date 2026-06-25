<template>
  <main class="community-detail-page page-wrap">
    <RouterLink class="back-link" to="/community">← 커뮤니티 목록</RouterLink>
    <p v-if="loading" class="detail-state">게시글을 불러오는 중입니다.</p>
    <p v-else-if="errorMessage" class="detail-state error">{{ errorMessage }}</p>

    <template v-else-if="post">
      <article class="community-detail-card">
        <CommunityAuthorHeader
          :author="post.author"
          :owner="isPostOwner"
          @question="askQuestion"
          @profile="viewProfile"
          @report="showNotice('신고 접수 기능은 MVP 이후 제공됩니다.')"
          @edit="editPost"
          @delete="removePost"
        />
        <div class="detail-type-row">
          <span :class="['community-type', post.post_type]">{{ post.post_type_label }}</span>
          <time>{{ formatDate(post.created_at) }}</time>
        </div>
        <h1>{{ post.title }}</h1>
        <p class="detail-content">{{ post.content }}</p>
        <dl class="detail-meta">
          <div v-if="post.material_name"><dt>관련 자재</dt><dd>{{ post.material_name }}</dd></div>
          <div v-if="post.supplier_name"><dt>관련 공급사</dt><dd>{{ post.supplier_name }}</dd></div>
          <div v-if="post.region"><dt>지역</dt><dd>{{ post.region }}</dd></div>
          <div><dt>상태</dt><dd>{{ post.status || "정보 공유" }}</dd></div>
        </dl>
      </article>

      <section class="comment-section">
        <div class="comment-title"><h2>댓글 {{ post.comments?.length || 0 }}</h2></div>
        <div v-if="post.comments?.length" class="comment-list">
          <article v-for="comment in post.comments" :key="comment.id" class="comment-card">
            <div class="comment-card-head">
              <CommunityAuthorHeader :author="comment.author" :menu="false" />
              <div v-if="comment.is_owner && editingCommentId !== comment.id" class="comment-owner-actions">
                <button type="button" @click="startCommentEdit(comment)">수정</button>
                <button
                  type="button"
                  class="delete"
                  :disabled="deletingCommentId === comment.id"
                  @click="removeComment(comment)"
                >{{ deletingCommentId === comment.id ? '삭제 중' : '삭제' }}</button>
              </div>
            </div>
            <form v-if="editingCommentId === comment.id" class="comment-edit-form" @submit.prevent="saveCommentEdit(comment)">
              <textarea v-model="editCommentContent" required rows="3" aria-label="댓글 내용 수정"></textarea>
              <div>
                <button type="button" class="cancel" :disabled="savingCommentId === comment.id" @click="cancelCommentEdit">취소</button>
                <button type="submit" :disabled="savingCommentId === comment.id">
                  {{ savingCommentId === comment.id ? '저장 중' : '저장' }}
                </button>
              </div>
            </form>
            <p v-else>{{ comment.content }}</p>
            <time>{{ formatDate(comment.created_at) }}</time>
          </article>
        </div>
        <p v-else class="no-comments">아직 댓글이 없습니다. 첫 번째 경험을 나눠보세요.</p>

        <form v-if="loggedIn" class="comment-form" @submit.prevent="submitComment">
          <div class="comment-display-mode" role="radiogroup" aria-label="댓글 작성 방식">
            <label :class="{ active: commentDisplayMode === 'profile' }">
              <input v-model="commentDisplayMode" type="radio" value="profile" />
              실명으로 댓글
            </label>
            <label :class="{ active: commentDisplayMode === 'anonymous' }">
              <input v-model="commentDisplayMode" type="radio" value="anonymous" />
              익명으로 댓글
            </label>
          </div>
          <p class="comment-display-help">
            {{ commentDisplayMode === 'anonymous'
              ? 'PF 아바타와 익명 닉네임만 표시되며 실제 계정 정보는 공개되지 않습니다.'
              : '현재 로그인한 프로필 이름과 역할로 표시됩니다.' }}
          </p>
          <textarea v-model="commentContent" required rows="3" placeholder="현장 경험이나 답변을 남겨주세요."></textarea>
          <button type="submit" :disabled="commentSubmitting">{{ commentSubmitting ? "등록 중" : "댓글 등록" }}</button>
        </form>
        <RouterLink v-else class="login-comment" :to="{ path: '/login', query: { redirect: route.fullPath } }">로그인 후 댓글 작성</RouterLink>
      </section>
    </template>

    <p v-if="notice" class="community-toast" role="status">{{ notice }}</p>
    <CommunityQuestionModal v-if="questionOpen" :post="post" @close="questionOpen=false" @sent="handleSent" />
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authState, isLoggedIn } from "../api/authApi";
import {
  createCommunityComment,
  deleteCommunityComment,
  deleteCommunityPost,
  getCommunityPost,
  updateCommunityComment,
} from "../api/communityApi";
import { createNotification } from "../api/notificationApi";
import CommunityAuthorHeader from "../components/CommunityAuthorHeader.vue";
import CommunityQuestionModal from "../components/CommunityQuestionModal.vue";

const route = useRoute();
const router = useRouter();
const post = ref(null);
const loading = ref(false);
const errorMessage = ref("");
const commentContent = ref("");
const commentDisplayMode = ref("profile");
const commentSubmitting = ref(false);
const editingCommentId = ref(null);
const editCommentContent = ref("");
const savingCommentId = ref(null);
const deletingCommentId = ref(null);
const questionOpen = ref(false);
const notice = ref("");
const loggedIn = isLoggedIn();
const isPostOwner = computed(() => Boolean(
  post.value?.is_owner
  || (
    authState.user?.id != null
    && post.value?.author?.profile_id != null
    && Number(authState.user.id) === Number(post.value.author.profile_id)
  ),
));

onMounted(loadPost);

async function loadPost() {
  try {
    loading.value = true;
    post.value = await getCommunityPost(route.params.id);
  } catch {
    errorMessage.value = "게시글을 찾을 수 없습니다.";
  } finally {
    loading.value = false;
  }
}

async function submitComment() {
  try {
    commentSubmitting.value = true;
    const comment = await createCommunityComment(
      post.value.id,
      commentContent.value.trim(),
      commentDisplayMode.value,
    );
    post.value.comments = [...(post.value.comments || []), comment];
    post.value.comment_count = post.value.comments.length;
    createCommentNotification(comment);
    commentContent.value = "";
  } catch {
    showNotice("댓글을 등록하지 못했습니다.");
  } finally {
    commentSubmitting.value = false;
  }
}

function createCommentNotification(comment) {
  const postAuthor = post.value?.author;
  if (post.value?.is_owner || !postAuthor?.profile_id || !postAuthor?.account_role) return;

  const commenterName = comment.author?.display_name || "커뮤니티 사용자";
  createNotification({
    recipient_user_id: postAuthor.profile_id,
    recipient_role: postAuthor.account_role,
    recipient_key: `user:${postAuthor.profile_id}`,
    type: "community_comment_created",
    title: "게시글에 새 댓글이 달렸습니다.",
    message: `${commenterName}님이 ‘${post.value.title}’ 게시글에 댓글을 남겼습니다.`,
    target_path: `/community/${post.value.id}`,
    event_key: `community-comment:${comment.id}`,
  });
}

function startCommentEdit(comment) {
  editingCommentId.value = comment.id;
  editCommentContent.value = comment.content;
}

function cancelCommentEdit() {
  editingCommentId.value = null;
  editCommentContent.value = "";
}

async function saveCommentEdit(comment) {
  const content = editCommentContent.value.trim();
  if (!content) return;
  try {
    savingCommentId.value = comment.id;
    const updated = await updateCommunityComment(comment.id, content);
    post.value.comments = post.value.comments.map((item) => item.id === comment.id ? updated : item);
    cancelCommentEdit();
  } catch {
    showNotice("댓글을 수정하지 못했습니다.");
  } finally {
    savingCommentId.value = null;
  }
}

async function removeComment(comment) {
  if (!window.confirm("이 댓글을 삭제하시겠습니까?")) return;
  try {
    deletingCommentId.value = comment.id;
    await deleteCommunityComment(comment.id);
    post.value.comments = post.value.comments.filter((item) => item.id !== comment.id);
    post.value.comment_count = post.value.comments.length;
    if (editingCommentId.value === comment.id) cancelCommentEdit();
  } catch {
    showNotice("댓글을 삭제하지 못했습니다.");
  } finally {
    deletingCommentId.value = null;
  }
}

function askQuestion() {
  if (!loggedIn) {
    router.push({ path: "/login", query: { redirect: route.fullPath } });
    return;
  }
  questionOpen.value = true;
}

function viewProfile() {
  if (post.value?.author?.profile_id && !post.value?.author?.is_anonymous) {
    router.push(`/profile/${post.value.author.profile_id}`);
    return;
  }
  showNotice("공개 프로필 정보를 확인할 수 없습니다.");
}

function editPost() {
  if (!isPostOwner.value) {
    showNotice("작성자 본인만 게시글을 수정할 수 있습니다.");
    return;
  }
  router.push(`/community/${post.value.id}/edit`);
}

async function removePost() {
  if (!isPostOwner.value) {
    showNotice("작성자 본인만 게시글을 삭제할 수 있습니다.");
    return;
  }
  if (!window.confirm("이 게시글을 삭제하시겠습니까?")) return;
  try {
    await deleteCommunityPost(post.value.id);
    window.alert("게시글이 삭제되었습니다.");
    router.push("/community");
  } catch {
    showNotice("게시글을 삭제하지 못했습니다.");
  }
}

function handleSent(message) {
  questionOpen.value = false;
  showNotice(message);
}

function showNotice(message) {
  notice.value = message;
  window.setTimeout(() => { notice.value = ""; }, 4500);
}

function formatDate(value) {
  return new Intl.DateTimeFormat("ko-KR", { year:"numeric", month:"short", day:"numeric", hour:"2-digit", minute:"2-digit" }).format(new Date(value));
}
</script>

<style scoped>
.community-detail-page{max-width:980px;padding-top:36px;padding-bottom:80px}.back-link{display:inline-block;margin-bottom:18px;color:#1559e8;text-decoration:none;font-weight:900}.community-detail-card,.comment-section{border:1px solid #dbe6f8;border-radius:28px;padding:30px;background:#fff;box-shadow:0 18px 50px rgba(31,61,115,.08)}.detail-type-row{display:flex;justify-content:space-between;align-items:center;margin-top:24px}.detail-type-row time,.comment-list time{color:#8b99ad;font-size:12px}.community-type{border-radius:999px;padding:7px 10px;font-size:12px;font-weight:900}.community-type.substitute_review{color:#047857;background:#dff8ef}.community-type.supplier_review{color:#1559e8;background:#e7efff}.community-type.field_question{color:#7c3aed;background:#f1eaff}.community-detail-card h1{margin:18px 0;color:#102a56;font-size:clamp(30px,4vw,46px);line-height:1.25}.detail-content{margin:0;color:#40506a;font-size:17px;line-height:1.9;white-space:pre-wrap}.detail-meta{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:30px 0 0;border-radius:18px;padding:18px;background:#f5f8fd}.detail-meta div{display:grid;gap:4px}.detail-meta dt{color:#8492a8;font-size:12px}.detail-meta dd{margin:0;color:#18365f;font-weight:900}.comment-section{margin-top:18px}.comment-title h2{margin:0 0 18px;color:#102a56}.comment-list{display:grid;gap:12px}.comment-list article{border:1px solid #e4ebf6;border-radius:17px;padding:16px}.comment-card-head{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:12px}.comment-owner-actions{display:flex;gap:5px}.comment-owner-actions button{border:0;border-radius:8px;padding:7px 9px;color:#52637b;background:#f1f5f9;cursor:pointer;font-size:12px;font-weight:800}.comment-owner-actions button:hover{color:#1559e8;background:#eaf1ff}.comment-owner-actions .delete{color:#b42318}.comment-owner-actions .delete:hover{color:#b42318;background:#fff0ee}.comment-owner-actions button:disabled{cursor:not-allowed;opacity:.6}.comment-list article>p{margin:13px 0;color:#40506a;line-height:1.7}.comment-edit-form{display:grid;gap:9px;margin:13px 0 8px}.comment-edit-form textarea{width:100%;box-sizing:border-box;border:1px solid #9eb9e6;border-radius:12px;padding:11px 12px;resize:vertical;color:#334155;background:#fbfdff;font:inherit;line-height:1.6;outline:0}.comment-edit-form textarea:focus{border-color:#1559e8;box-shadow:0 0 0 3px rgba(21,89,232,.1)}.comment-edit-form>div{display:flex;justify-content:flex-end;gap:7px}.comment-edit-form button{border:0;border-radius:9px;padding:8px 12px;color:#fff;background:#1559e8;cursor:pointer;font-weight:800}.comment-edit-form button.cancel{color:#52637b;background:#edf2f7}.comment-edit-form button:disabled{cursor:not-allowed;opacity:.6}.comment-form{display:grid;gap:10px;margin-top:18px;border-top:1px solid #edf2fa;padding-top:18px}.comment-display-mode{display:flex;flex-wrap:wrap;gap:8px}.comment-display-mode label{display:flex;align-items:center;gap:7px;border:1px solid #d7e3f5;border-radius:999px;padding:9px 13px;color:#5d6c83;background:#fff;cursor:pointer;font-size:13px;font-weight:900}.comment-display-mode label.active{border-color:#1559e8;color:#1559e8;background:#f1f6ff}.comment-display-mode input{accent-color:#1559e8}.comment-display-help{margin:0;color:#7a899e;font-size:12px;line-height:1.5}.comment-form textarea{border:1px solid #cddbf0;border-radius:14px;padding:13px;resize:vertical;font:inherit}.comment-form button,.login-comment{justify-self:end;border:0;border-radius:12px;padding:12px 17px;color:#fff;background:#1559e8;text-decoration:none;font-weight:900;cursor:pointer}.no-comments{color:#71809a}.detail-state{padding:50px;text-align:center}.detail-state.error{color:#c24141}.community-toast{position:fixed;right:24px;bottom:24px;z-index:900;max-width:420px;border-radius:15px;padding:14px 18px;color:#fff;background:#102a56;box-shadow:0 16px 40px rgba(0,0,0,.2)}
@media(max-width:650px){.community-detail-card,.comment-section{padding:20px}.detail-meta{grid-template-columns:1fr}}
</style>
