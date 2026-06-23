<template>
  <main class="community-form-page page-wrap">
    <header>
      <RouterLink to="/community">← 커뮤니티</RouterLink>
      <p class="eyebrow">Share Field Knowledge</p>
      <h1>{{ isEditing ? "게시글 수정" : "글쓰기" }}</h1>
      <p>{{ isEditing ? "작성한 게시글 내용을 수정합니다." : "자재 수급 경험과 현장 질문을 다른 실무자와 공유하세요." }}</p>
    </header>

    <form class="community-form-card" @submit.prevent="submitPost">
      <fieldset>
        <legend>작성자 표시 방식</legend>
        <label :class="{ selected: form.display_mode === 'profile' }">
          <input v-model="form.display_mode" type="radio" value="profile" />
          <span><strong>실명/프로필로 작성</strong><small>{{ profileSummary }}</small></span>
        </label>
        <label :class="{ selected: form.display_mode === 'anonymous' }">
          <input v-model="form.display_mode" type="radio" value="anonymous" />
          <span><strong>익명으로 작성</strong><small>PF 기본 아바타와 자동 생성 닉네임으로 표시됩니다.</small></span>
        </label>
      </fieldset>

      <div class="form-grid">
        <label>게시글 유형
          <select v-model="form.post_type" required>
            <option value="substitute_review">대체 자재 후기</option>
            <option value="supplier_review">공급사 후기</option>
            <option value="field_question">현장 질문</option>
          </select>
        </label>
        <label>상태
          <input v-model="form.status" placeholder="예: 승인 검토 완료, 답변 대기" />
        </label>
        <label class="wide">제목
          <input v-model="form.title" required maxlength="200" placeholder="공유할 경험이나 질문을 입력하세요" />
        </label>
        <label>관련 자재명
          <input v-model="form.material_name" placeholder="예: 철근 SD400 D13" />
        </label>
        <label>관련 공급사명
          <input v-model="form.supplier_name" placeholder="공급사 후기인 경우 입력" />
        </label>
        <label class="wide">지역
          <input v-model="form.region" placeholder="예: 서울 마포구" />
        </label>
        <label class="wide">내용
          <textarea v-model="form.content" required rows="10" placeholder="검토 과정, 확인한 기준, 결과를 구체적으로 공유해주세요."></textarea>
        </label>
      </div>

      <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
      <div class="form-actions">
        <RouterLink to="/community">취소</RouterLink>
        <button type="submit" :disabled="submitting">{{ submitting ? "저장 중" : isEditing ? "수정 완료" : "게시글 등록" }}</button>
      </div>
    </form>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authState } from "../api/authApi";
import { createCommunityPost, getCommunityPost, updateCommunityPost } from "../api/communityApi";

const route = useRoute();
const router = useRouter();
const submitting = ref(false);
const errorMessage = ref("");
const form = reactive({
  display_mode: "profile",
  post_type: "substitute_review",
  title: "",
  content: "",
  material_name: "",
  supplier_name: "",
  region: "",
  status: "",
});
const profileSummary = computed(() => {
  const user = authState.user;
  return [user?.name || "PaceFlow 사용자", user?.roleLabel, user?.companyName].filter(Boolean).join(" · ");
});
const isEditing = computed(() => route.name === "community-edit");

onMounted(async () => {
  if (!isEditing.value) return;
  try {
    const post = await getCommunityPost(route.params.id);
    if (!post.is_owner) {
      router.replace(`/community/${post.id}`);
      return;
    }
    Object.assign(form, {
      display_mode: post.display_mode,
      post_type: post.post_type,
      title: post.title,
      content: post.content,
      material_name: post.material_name,
      supplier_name: post.supplier_name,
      region: post.region,
      status: post.status,
    });
  } catch {
    errorMessage.value = "수정할 게시글을 불러오지 못했습니다.";
  }
});

async function submitPost() {
  try {
    submitting.value = true;
    errorMessage.value = "";
    const post = isEditing.value
      ? await updateCommunityPost(route.params.id, form)
      : await createCommunityPost(form);
    router.push(`/community/${post.id}`);
  } catch (error) {
    errorMessage.value = error?.response?.status === 401
      ? "로그인 후 게시글을 작성할 수 있습니다."
      : "게시글을 등록하지 못했습니다. 입력 내용을 확인해주세요.";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.community-form-page { max-width:980px; padding-top:38px; padding-bottom:80px; }
.community-form-page header>a { color:#1559e8; text-decoration:none; font-weight:900; }.community-form-page header h1{margin:8px 0;color:#102a56;font-size:44px}.community-form-page header>p:last-child{color:#65748d}
.community-form-card { margin-top:24px; border:1px solid #dbe6f8; border-radius:28px; padding:30px; background:#fff; box-shadow:0 20px 60px rgba(31,61,115,.1); }
fieldset { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:0 0 25px; border:0; padding:0; } legend{grid-column:1/-1;margin-bottom:10px;color:#102a56;font-weight:1000} fieldset label{display:flex;gap:10px;border:1px solid #dbe6f8;border-radius:16px;padding:15px;cursor:pointer}fieldset label.selected{border-color:#1559e8;background:#f3f7ff}fieldset span,fieldset strong,fieldset small{display:block}fieldset small{margin-top:4px;color:#71809a;line-height:1.4}
.form-grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }.form-grid label{display:grid;gap:8px;color:#334155;font-size:13px;font-weight:900}.form-grid .wide{grid-column:1/-1}.form-grid input,.form-grid select,.form-grid textarea{width:100%;box-sizing:border-box;border:1px solid #cddbf0;border-radius:13px;padding:13px 14px;background:#fbfdff;font:inherit}.form-grid textarea{resize:vertical;line-height:1.7}
.form-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:24px}.form-actions a,.form-actions button{border:0;border-radius:13px;padding:13px 20px;text-decoration:none;font-weight:900}.form-actions a{color:#51627e;background:#eef3fa}.form-actions button{color:#fff;background:#1559e8;cursor:pointer}.form-actions button:disabled{opacity:.5}.form-error{color:#c24141}
@media(max-width:650px){.community-form-card{padding:20px}fieldset,.form-grid{grid-template-columns:1fr}.form-grid .wide{grid-column:auto}}
</style>
