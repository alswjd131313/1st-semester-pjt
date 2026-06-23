<template>
  <div class="mypage">
    <div class="page-header">
      <h1>마이페이지</h1>
      <p class="page-sub">내 계정 정보와 활동 내역을 확인합니다.</p>
    </div>

    <!-- 프로필 카드 -->
    <section class="profile-card">
      <div class="profile-left">
        <div class="avatar-wrap">
          <div class="avatar" @click="fileInput?.click()">
            <img v-if="profileImage" :src="profileImage" class="avatar-img" alt="프로필 사진" />
            <span v-else class="avatar-letter">{{ initial }}</span>
          </div>
          <button class="avatar-edit-btn" type="button" title="사진 변경" @click.stop="fileInput?.click()">
            <svg width="12" height="12" viewBox="0 0 20 20" fill="none">
              <path d="M14.5 2.5l3 3L6 17H3v-3L14.5 2.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="handleImageUpload" />
        </div>

        <div class="profile-info">
          <h2 class="profile-name">{{ displayName }}</h2>
          <span class="role-badge">자재 요청자</span>
          <p class="profile-email">{{ profileEmail }}</p>
        </div>
      </div>
      <button class="btn-profile-edit" type="button" @click="openProfileModal">프로필 편집</button>
    </section>

    <!-- 문의 현황 -->
    <section class="mypage-card">
      <div class="card-header">
        <h2>문의 현황</h2>
        <RouterLink class="link-more" to="/inquiries">전체 보기 ›</RouterLink>
      </div>
      <div class="inq-stat-grid">
        <div class="inq-stat-card inq-stat-blue">
          <div class="inq-stat-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M9 12h6M9 16h4M5 4h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="inq-stat-label">전체 문의</span>
          <strong class="inq-stat-num">{{ inquiries.length }}<span class="inq-unit">건</span></strong>
        </div>
        <div class="inq-stat-card inq-stat-orange">
          <div class="inq-stat-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M12 8v4l3 3M12 3a9 9 0 100 18A9 9 0 0012 3z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="inq-stat-label">검토 중</span>
          <strong class="inq-stat-num">{{ pendingCount }}<span class="inq-unit">건</span></strong>
        </div>
        <div class="inq-stat-card inq-stat-green">
          <div class="inq-stat-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/>
              <path d="M8 12l3 3 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="inq-stat-label">수락됨</span>
          <strong class="inq-stat-num">{{ acceptedCount }}<span class="inq-unit">건</span></strong>
        </div>
        <div class="inq-stat-card inq-stat-red">
          <div class="inq-stat-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/>
              <path d="M9 9l6 6M15 9l-6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="inq-stat-label">거절됨</span>
          <strong class="inq-stat-num">{{ rejectedCount }}<span class="inq-unit">건</span></strong>
        </div>
      </div>
    </section>

    <!-- 커뮤니티 활동 -->
    <section class="mypage-card">
      <div class="card-header">
        <h2>내 커뮤니티 활동</h2>
        <RouterLink class="link-more" to="/community">전체 보기 ›</RouterLink>
      </div>
      <div class="comm-stat-row">
        <div class="comm-stat-item">
          <div class="comm-icon-wrap">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="comm-stat-label">작성한 글</span>
          <strong class="comm-stat-num">{{ myPosts.length }}<span class="comm-unit">개</span></strong>
        </div>
        <div class="comm-stat-divider"></div>
        <div class="comm-stat-item">
          <div class="comm-icon-wrap">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="comm-stat-label">받은 댓글</span>
          <strong class="comm-stat-num">{{ receivedComments }}<span class="comm-unit">개</span></strong>
        </div>
      </div>
    </section>

    <!-- 계정 설정 -->
    <section class="mypage-card">
      <h2 class="card-title">계정 설정</h2>
      <div class="setting-list">
        <div class="setting-item">
          <div>
            <strong>비밀번호 변경</strong>
            <p>현재 비밀번호를 새 비밀번호로 변경합니다.</p>
          </div>
          <button class="btn-outline-sm" @click="showPwModal = true">변경</button>
        </div>
        <div class="setting-item">
          <div>
            <strong>알림 설정</strong>
            <p>문의 상태 변경 시 이메일 알림을 수신합니다.</p>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="emailNotify" />
            <span class="toggle-track"><span class="toggle-thumb"></span></span>
          </label>
        </div>
      </div>
    </section>

    <!-- 로그아웃 -->
    <div class="logout-section">
      <button class="btn-logout" @click="logout">로그아웃</button>
    </div>

    <!-- 프로필 편집 모달 -->
    <div v-if="showProfileModal" class="modal-backdrop" @click.self="showProfileModal = false">
      <div class="modal">
        <h3>프로필 편집</h3>
        <div class="form-group">
          <label>이름 <span class="field-note">변경 불가</span></label>
          <input type="text" :value="displayName" disabled class="input-disabled" />
        </div>
        <div class="form-group">
          <label>이메일</label>
          <input type="email" v-model="editForm.email" placeholder="이메일을 입력하세요" />
        </div>
        <p v-if="profileSaveMsg" :class="profileSaveMsg.type === 'error' ? 'error-msg' : 'success-msg'">{{ profileSaveMsg.text }}</p>
        <div class="modal-actions">
          <button class="btn-primary" @click="saveProfile">저장</button>
          <button class="btn-ghost" @click="showProfileModal = false">취소</button>
        </div>
      </div>
    </div>

    <!-- 비밀번호 변경 모달 -->
    <div v-if="showPwModal" class="modal-backdrop" @click.self="showPwModal = false">
      <div class="modal">
        <h3>비밀번호 변경</h3>
        <div class="form-group">
          <label>현재 비밀번호</label>
          <input type="password" v-model="pw.current" />
        </div>
        <div class="form-group">
          <label>새 비밀번호</label>
          <input type="password" v-model="pw.next" />
        </div>
        <div class="form-group">
          <label>새 비밀번호 확인</label>
          <input type="password" v-model="pw.confirm" />
        </div>
        <p v-if="pwError" class="error-msg">{{ pwError }}</p>
        <div class="modal-actions">
          <button class="btn-primary" @click="changePw">변경</button>
          <button class="btn-ghost" @click="showPwModal = false">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { authState, logoutUser as authLogout } from "../api/authApi";
import { getSupplierInquiries } from "../api/materialApi";
import { getCommunityPosts } from "../api/communityApi";

const router = useRouter();
const inquiries = ref([]);
const myPosts = ref([]);
const receivedComments = ref(0);
const emailNotify = ref(true);
const showPwModal = ref(false);
const showProfileModal = ref(false);
const pwError = ref("");
const profileSaveMsg = ref(null);
const pw = reactive({ current: "", next: "", confirm: "" });
const editForm = reactive({ email: "" });
const fileInput = ref(null);
const profileImage = ref(localStorage.getItem("paceflow_profile_img") || null);

const displayName = computed(() => authState.user?.name ?? authState.user?.email ?? "사용자");
const profileEmail = computed(() => localStorage.getItem("paceflow_profile_email") || authState.user?.email || "-");
const initial = computed(() => (displayName.value[0] ?? "U").toUpperCase());

const pendingCount = computed(() => inquiries.value.filter(i => i.status === "pending").length);
const acceptedCount = computed(() => inquiries.value.filter(i => i.status === "accepted").length);
const rejectedCount = computed(() => inquiries.value.filter(i => i.status === "rejected").length);

onMounted(async () => {
  try {
    inquiries.value = await getSupplierInquiries();
  } catch { /* pass */ }

  try {
    const all = await getCommunityPosts();
    const mine = all.filter(
      p => p.author?.profile_id === authState.user?.id
        || (!p.author?.is_anonymous && p.author?.display_name === authState.user?.name),
    );
    myPosts.value = mine;
    receivedComments.value = mine.reduce((sum, p) => sum + (p.comment_count ?? p.comments?.length ?? 0), 0);
  } catch { /* pass */ }
});

function openProfileModal() {
  editForm.email = profileEmail.value === "-" ? "" : profileEmail.value;
  profileSaveMsg.value = null;
  showProfileModal.value = true;
}

function saveProfile() {
  if (!editForm.email) { profileSaveMsg.value = { type: "error", text: "이메일을 입력하세요." }; return; }
  localStorage.setItem("paceflow_profile_email", editForm.email);
  if (authState.user) authState.user.email = editForm.email;
  profileSaveMsg.value = { type: "success", text: "프로필이 저장되었습니다." };
  setTimeout(() => { showProfileModal.value = false; profileSaveMsg.value = null; }, 1200);
}

async function logout() {
  await authLogout?.();
  router.push("/");
}

function changePw() {
  if (!pw.current || !pw.next) { pwError.value = "모든 항목을 입력하세요."; return; }
  if (pw.next !== pw.confirm) { pwError.value = "새 비밀번호가 일치하지 않습니다."; return; }
  pwError.value = "";
  showPwModal.value = false;
  Object.assign(pw, { current: "", next: "", confirm: "" });
}

async function handleImageUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const dataUrl = await resizeImage(file, 200);
  profileImage.value = dataUrl;
  localStorage.setItem("paceflow_profile_img", dataUrl);
  event.target.value = "";
}

function resizeImage(file, maxSize) {
  return new Promise((resolve) => {
    const canvas = document.createElement("canvas");
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      const ratio = Math.min(maxSize / img.width, maxSize / img.height, 1);
      canvas.width = img.width * ratio;
      canvas.height = img.height * ratio;
      canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      resolve(canvas.toDataURL("image/jpeg", 0.85));
    };
    img.src = url;
  });
}
</script>

<style scoped>
.mypage {
  max-width: 760px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

.page-header { margin-bottom: 32px; }
.page-header h1 { font-size: 28px; font-weight: 800; color: #102a56; margin: 0 0 4px; }
.page-sub { color: #71809a; font-size: 15px; margin: 0; }

/* ── 프로필 카드 ── */
.profile-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 20px;
}

.profile-left { display: flex; align-items: center; gap: 20px; }

.avatar-wrap { position: relative; flex-shrink: 0; }

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, #1559e8, #22a6f2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(21, 89, 232, 0.25);
}

.avatar-letter { font-size: 28px; font-weight: 800; }

.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.avatar-edit-btn {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #1559e8;
  color: #fff;
  border: 2.5px solid #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.profile-info { display: flex; flex-direction: column; gap: 5px; }

.profile-name { font-size: 22px; font-weight: 800; color: #102a56; margin: 0; }

.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  background: #e8f0fe;
  color: #1559e8;
  font-size: 12px;
  font-weight: 700;
  width: fit-content;
}

.profile-email { font-size: 13px; color: #71809a; margin: 0; }

.btn-profile-edit {
  border: 1px solid #dde7f7;
  background: #fff;
  color: #4b6380;
  border-radius: 10px;
  padding: 9px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: border-color 0.15s, color 0.15s;
}
.btn-profile-edit:hover { border-color: #1559e8; color: #1559e8; }

/* ── 공통 카드 ── */
.mypage-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
}
.card-header h2 { font-size: 17px; font-weight: 700; color: #102a56; margin: 0; }
.card-title { font-size: 17px; font-weight: 700; color: #102a56; margin: 0 0 22px; }
.link-more { font-size: 13px; color: #1559e8; text-decoration: none; font-weight: 600; }

/* ── 문의 현황 4-카드 그리드 ── */
.inq-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.inq-stat-card {
  border-radius: 14px;
  padding: 18px 16px 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.inq-stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.inq-stat-label {
  font-size: 13px;
  font-weight: 600;
  color: #71809a;
}

.inq-stat-num {
  font-size: 24px;
  font-weight: 800;
  color: #102a56;
  line-height: 1;
}

.inq-unit {
  font-size: 14px;
  font-weight: 600;
  margin-left: 2px;
}

.inq-stat-blue { background: #eff4ff; }
.inq-stat-blue .inq-stat-icon { background: #dce8fd; color: #1559e8; }
.inq-stat-blue .inq-stat-num { color: #1559e8; }

.inq-stat-orange { background: #fff8ee; }
.inq-stat-orange .inq-stat-icon { background: #fde9c3; color: #d97706; }
.inq-stat-orange .inq-stat-num { color: #b45309; }

.inq-stat-green { background: #f0fdf4; }
.inq-stat-green .inq-stat-icon { background: #bbf7d0; color: #16a34a; }
.inq-stat-green .inq-stat-num { color: #15803d; }

.inq-stat-red { background: #fff1f2; }
.inq-stat-red .inq-stat-icon { background: #fecdd3; color: #e11d48; }
.inq-stat-red .inq-stat-num { color: #be123c; }

/* ── 커뮤니티 활동 ── */
.comm-stat-row {
  display: flex;
  align-items: center;
  gap: 0;
}

.comm-stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px 0;
}

.comm-stat-divider {
  width: 1px;
  height: 80px;
  background: #f0f4fa;
  flex-shrink: 0;
}

.comm-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #f0f4fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7a93b8;
}

.comm-stat-label {
  font-size: 14px;
  font-weight: 600;
  color: #71809a;
}

.comm-stat-num {
  font-size: 28px;
  font-weight: 800;
  color: #102a56;
  line-height: 1;
}

.comm-unit {
  font-size: 15px;
  font-weight: 600;
  margin-left: 2px;
}

/* ── 계정 설정 ── */
.setting-list { display: flex; flex-direction: column; }
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 0;
  border-bottom: 1px solid #f5f8fc;
}
.setting-item:last-child { border-bottom: none; }
.setting-item strong { font-size: 15px; color: #102a56; font-weight: 700; }
.setting-item p { font-size: 13px; color: #71809a; margin: 4px 0 0; }

.btn-outline-sm {
  border: 1px solid #dde7f7;
  background: none;
  border-radius: 8px;
  padding: 8px 20px;
  font-size: 14px;
  color: #4b6380;
  cursor: pointer;
  font-weight: 600;
}

.toggle { display: flex; align-items: center; cursor: pointer; }
.toggle input { display: none; }
.toggle-track { width: 48px; height: 26px; background: #dde7f7; border-radius: 999px; position: relative; transition: background 0.2s; }
.toggle input:checked + .toggle-track { background: #1559e8; }
.toggle-thumb { position: absolute; top: 3px; left: 3px; width: 20px; height: 20px; background: #fff; border-radius: 50%; transition: transform 0.2s; box-shadow: 0 1px 4px rgba(0,0,0,0.18); }
.toggle input:checked + .toggle-track .toggle-thumb { transform: translateX(22px); }

/* ── 로그아웃 ── */
.logout-section { text-align: center; margin-top: 8px; }
.btn-logout {
  background: none;
  border: 1.5px solid #fca5a5;
  color: #dc2626;
  border-radius: 12px;
  padding: 14px 60px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-logout:hover { background: #fff5f5; }

/* ── 모달 ── */
.modal-backdrop { position: fixed; inset: 0; background: rgba(10,20,50,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: 20px; padding: 36px; width: 420px; max-width: 90vw; }
.modal h3 { font-size: 20px; font-weight: 700; color: #102a56; margin: 0 0 24px; }
.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.form-group label { font-size: 13px; font-weight: 600; color: #4b6380; display: flex; align-items: center; gap: 6px; }
.field-note { font-size: 11px; font-weight: 500; color: #aab4c4; background: #f5f8fc; padding: 1px 6px; border-radius: 4px; }
.form-group input { border: 1px solid #dde7f7; border-radius: 8px; padding: 10px 14px; font-size: 15px; outline: none; width: 100%; box-sizing: border-box; }
.form-group input:focus { border-color: #1559e8; }
.input-disabled { background: #f8fafc; color: #aab4c4; cursor: not-allowed; }
.success-msg { font-size: 14px; color: #059669; margin: 8px 0; }
.error-msg { font-size: 14px; color: #dc2626; margin: 8px 0; }
.modal-actions { display: flex; gap: 12px; margin-top: 8px; }
.btn-primary { background: #1559e8; color: #fff; border: none; border-radius: 10px; padding: 10px 24px; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn-ghost { background: none; border: 1px solid #dde7f7; border-radius: 10px; padding: 10px 20px; font-size: 15px; color: #71809a; cursor: pointer; }

/* ── 반응형 ── */
@media (max-width: 600px) {
  .inq-stat-grid { grid-template-columns: repeat(2, 1fr); }
  .profile-card { flex-direction: column; align-items: flex-start; }
  .btn-profile-edit { align-self: flex-end; }
}
</style>
