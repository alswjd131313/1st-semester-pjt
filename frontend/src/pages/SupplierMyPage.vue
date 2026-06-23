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
            <svg width="11" height="11" viewBox="0 0 20 20" fill="none">
              <path d="M14.5 2.5l3 3L6 17H3v-3L14.5 2.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="handleImageUpload" />
        </div>

        <div class="profile-info">
          <h2 class="profile-name">{{ displayName }}</h2>
          <span class="role-badge">공급사</span>
          <p class="profile-email">{{ profileEmail }}</p>
          <p v-if="joinDate" class="profile-joindate">가입일 &nbsp;{{ joinDate }}</p>
        </div>
      </div>
      <button class="btn-profile-edit" type="button" @click="openProfileModal">프로필 편집</button>
    </section>

    <!-- 빠른 이동 -->
    <div class="quick-links">
      <RouterLink class="quick-card" :to="{ name: 'supplier-dashboard' }">
        <div class="ql-icon-box ql-blue">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="ql-text">
          <strong>문의 관리</strong>
          <p>접수된 문의를 확인하고 답변을 관리합니다.</p>
        </div>
        <span class="ql-chevron">›</span>
      </RouterLink>
      <RouterLink class="quick-card" :to="{ name: 'supplier-profile' }">
        <div class="ql-icon-box ql-orange">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="ql-text">
          <strong>취급 자재 관리</strong>
          <p>등록 자재를 추가/수정하고 상태를 관리합니다.</p>
        </div>
        <span class="ql-chevron">›</span>
      </RouterLink>
      <RouterLink class="quick-card" :to="{ name: 'inquiries' }">
        <div class="ql-icon-box ql-purple">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="ql-text">
          <strong>전체 문의 내역</strong>
          <p>모든 문의와 답변 이력을 확인합니다.</p>
        </div>
        <span class="ql-chevron">›</span>
      </RouterLink>
    </div>

    <!-- 공급 현황 -->
    <section class="mypage-card">
      <div class="card-header">
        <h2 class="card-title">공급 현황</h2>
        <div class="period-wrap">
          <span class="period-label">기간</span>
          <select class="period-select" v-model="statPeriod">
            <option value="30">최근 30일</option>
            <option value="90">최근 90일</option>
            <option value="180">최근 6개월</option>
            <option value="365">최근 1년</option>
          </select>
        </div>
      </div>
      <div class="supply-stat-grid">
        <div class="supply-stat-card">
          <div class="ssc-icon ssc-blue">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M9 12h6M9 16h4M5 4h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="ssc-info">
            <span class="ssc-label">등록 자재</span>
            <strong class="ssc-num">{{ materials.length }}<span class="ssc-unit">종</span></strong>
          </div>
        </div>
        <div class="supply-stat-card">
          <div class="ssc-icon ssc-orange">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="ssc-info">
            <span class="ssc-label">전체 문의</span>
            <strong class="ssc-num">{{ inquiries.length }}<span class="ssc-unit">건</span></strong>
          </div>
        </div>
        <div class="supply-stat-card">
          <div class="ssc-icon ssc-green">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M12 8v4l3 3M12 3a9 9 0 100 18A9 9 0 0012 3z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="ssc-info">
            <span class="ssc-label">검토 중</span>
            <strong class="ssc-num">{{ pendingCount }}<span class="ssc-unit">건</span></strong>
          </div>
        </div>
        <div class="supply-stat-card">
          <div class="ssc-icon ssc-purple">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/>
              <path d="M8 12l3 3 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="ssc-info">
            <span class="ssc-label">수락</span>
            <strong class="ssc-num">{{ acceptedCount }}<span class="ssc-unit">건</span></strong>
          </div>
        </div>
      </div>
      <p class="stat-note">* 통계는 최근 {{ statPeriod }}일 기준입니다.</p>
    </section>

    <!-- 최근 문의 & 내 자재 현황 -->
    <div class="two-col-grid">
      <section class="mypage-card">
        <div class="card-header">
          <h2>최근 문의</h2>
          <RouterLink class="link-more" :to="{ name: 'supplier-dashboard' }">전체 보기 ›</RouterLink>
        </div>
        <div v-if="recentInquiries.length === 0" class="empty-state">
          <svg class="empty-icon" width="40" height="40" viewBox="0 0 24 24" fill="none">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" stroke="#c0cce4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p>접수된 문의가 없습니다.</p>
          <small>새로운 문의가 접수되면 여기에 표시됩니다.</small>
          <RouterLink class="btn-go" :to="{ name: 'supplier-dashboard' }">문의 관리 바로가기</RouterLink>
        </div>
        <div v-else class="inquiry-list">
          <div
            v-for="inq in recentInquiries"
            :key="inq.id"
            class="inquiry-item"
            @click="router.push(`/dashboard/${inq.id}`)"
          >
            <div class="inq-row">
              <span class="inq-material">{{ inq.material_name ?? '자재' }}</span>
              <span :class="['inq-status', statusClass(inq.status)]">{{ statusLabel(inq.status) }}</span>
            </div>
            <span class="inq-date">{{ formatDate(inq.created_at) }}</span>
          </div>
        </div>
      </section>

      <section class="mypage-card">
        <div class="card-header">
          <h2>내 자재 현황</h2>
          <RouterLink class="link-more" :to="{ name: 'supplier-profile' }">전체 보기 ›</RouterLink>
        </div>
        <div v-if="materials.length === 0" class="empty-state">
          <svg class="empty-icon" width="40" height="40" viewBox="0 0 24 24" fill="none">
            <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" stroke="#c0cce4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p>등록된 자재가 없습니다.</p>
          <small>자재를 등록하여 더 많은 문의를 받아보세요.</small>
          <RouterLink class="btn-go" :to="{ name: 'supplier-profile' }">자재 등록하러 가기</RouterLink>
        </div>
        <div v-else class="material-list">
          <div v-for="mat in materials.slice(0, 5)" :key="mat.id" class="mat-item">
            <span class="mat-name">{{ mat.name ?? mat.material_name ?? '자재' }}</span>
          </div>
        </div>
      </section>
    </div>

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
            <strong>문의 알림</strong>
            <p>새 문의 접수 시 이메일 알림을 수신합니다.</p>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="emailNotify" />
            <span class="toggle-track"><span class="toggle-thumb"></span></span>
          </label>
        </div>
      </div>
    </section>

    <div class="logout-section">
      <button class="btn-logout" @click="logout">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
          <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        로그아웃
      </button>
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
        <div class="form-group">
          <label>회사명</label>
          <input type="text" v-model="editForm.companyName" placeholder="회사명을 입력하세요" />
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
import { getSupplierInquiries, getSupplierMaterials } from "../api/materialApi";

const router = useRouter();
const inquiries = ref([]);
const materials = ref([]);
const emailNotify = ref(true);
const showPwModal = ref(false);
const showProfileModal = ref(false);
const pwError = ref("");
const profileSaveMsg = ref(null);
const statPeriod = ref("30");
const pw = reactive({ current: "", next: "", confirm: "" });
const editForm = reactive({ email: "", companyName: "" });

const displayName = computed(() => authState.user?.name ?? authState.user?.companyName ?? authState.user?.email ?? "공급사");
const initial = computed(() => (displayName.value[0] ?? "S").toUpperCase());
const fileInput = ref(null);
const profileImage = ref(localStorage.getItem("paceflow_profile_img") || null);
const profileEmail = computed(() => localStorage.getItem("paceflow_profile_email") || authState.user?.email || "-");

const joinDate = computed(() => {
  const d = authState.user?.date_joined;
  if (!d) return null;
  const dt = new Date(d);
  return `${dt.getFullYear()}.${String(dt.getMonth() + 1).padStart(2, "0")}.${String(dt.getDate()).padStart(2, "0")}`;
});

const pendingCount = computed(() => inquiries.value.filter(i => i.status === "pending").length);
const acceptedCount = computed(() => inquiries.value.filter(i => i.status === "accepted").length);
const recentInquiries = computed(() => inquiries.value.slice(0, 5));

onMounted(async () => {
  try {
    [inquiries.value, materials.value] = await Promise.all([
      getSupplierInquiries(),
      getSupplierMaterials(),
    ]);
  } catch { /* pass */ }
});

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

function openProfileModal() {
  editForm.email = profileEmail.value === "-" ? "" : profileEmail.value;
  editForm.companyName = authState.user?.companyName ?? "";
  profileSaveMsg.value = null;
  showProfileModal.value = true;
}

function saveProfile() {
  if (!editForm.email) { profileSaveMsg.value = { type: "error", text: "이메일을 입력하세요." }; return; }
  localStorage.setItem("paceflow_profile_email", editForm.email);
  if (authState.user) {
    authState.user.email = editForm.email;
    if (editForm.companyName) authState.user.companyName = editForm.companyName;
  }
  profileSaveMsg.value = { type: "success", text: "프로필이 저장되었습니다." };
  setTimeout(() => { showProfileModal.value = false; profileSaveMsg.value = null; }, 1200);
}

function statusLabel(s) {
  return { pending: "검토 중", accepted: "수락", rejected: "거절" }[s] ?? s;
}
function statusClass(s) {
  return { pending: "status-pending", accepted: "status-accepted", rejected: "status-rejected" }[s] ?? "";
}
function formatDate(d) {
  if (!d) return "";
  return new Date(d).toLocaleDateString("ko-KR", { year: "numeric", month: "short", day: "numeric" });
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
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.profile-info { display: flex; flex-direction: column; gap: 4px; }
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
.profile-joindate { font-size: 13px; color: #aab4c4; margin: 0; }

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

/* ── 빠른 이동 ── */
.quick-links {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.quick-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 16px;
  padding: 18px 20px;
  text-decoration: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.quick-card:hover { border-color: #1559e8; box-shadow: 0 4px 12px rgba(21, 89, 232, 0.08); }

.ql-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ql-blue { background: #eff4ff; color: #1559e8; }
.ql-orange { background: #fff8ee; color: #d97706; }
.ql-purple { background: #f5f0ff; color: #7c3aed; }

.ql-text { flex: 1; }
.ql-text strong { font-size: 14px; color: #102a56; font-weight: 700; display: block; margin-bottom: 2px; }
.ql-text p { font-size: 12px; color: #71809a; margin: 0; line-height: 1.4; }

.ql-chevron { font-size: 18px; color: #aab4c4; flex-shrink: 0; }

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

/* ── 기간 선택 ── */
.period-wrap { display: flex; align-items: center; gap: 8px; }
.period-label { font-size: 13px; color: #71809a; }
.period-select {
  border: 1px solid #dde7f7;
  border-radius: 8px;
  padding: 5px 10px;
  font-size: 13px;
  color: #102a56;
  background: #fff;
  cursor: pointer;
  outline: none;
}

/* ── 공급 현황 4-카드 ── */
.supply-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 14px;
}

.supply-stat-card {
  border: 1px solid #f0f4fa;
  border-radius: 14px;
  padding: 18px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.ssc-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ssc-blue { background: #eff4ff; color: #1559e8; }
.ssc-orange { background: #fff8ee; color: #d97706; }
.ssc-green { background: #f0fdf4; color: #16a34a; }
.ssc-purple { background: #f5f0ff; color: #7c3aed; }

.ssc-info { display: flex; flex-direction: column; gap: 2px; }
.ssc-label { font-size: 12px; color: #71809a; font-weight: 600; }
.ssc-num { font-size: 22px; font-weight: 800; color: #102a56; line-height: 1.2; }
.ssc-unit { font-size: 13px; font-weight: 600; margin-left: 1px; }

.stat-note { font-size: 12px; color: #aab4c4; margin: 0; }

/* ── 2-컬럼 그리드 ── */
.two-col-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}
.two-col-grid .mypage-card { margin-bottom: 0; }

/* ── 빈 상태 ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 28px 0;
  text-align: center;
}
.empty-icon { opacity: 0.6; }
.empty-state p { font-size: 14px; color: #71809a; margin: 0; font-weight: 600; }
.empty-state small { font-size: 12px; color: #aab4c4; }
.btn-go {
  margin-top: 4px;
  border: 1px solid #1559e8;
  color: #1559e8;
  background: none;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-go:hover { background: #eff4ff; }

/* ── 최근 문의 리스트 ── */
.inquiry-list { display: flex; flex-direction: column; gap: 10px; }
.inquiry-item {
  border: 1px solid #f0f4fa;
  border-radius: 10px;
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: border-color 0.12s;
}
.inquiry-item:hover { border-color: #1559e8; }
.inq-row { display: flex; align-items: center; gap: 10px; }
.inq-material { font-weight: 600; font-size: 14px; color: #102a56; }
.inq-status { font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 999px; }
.status-pending { background: #fef9ec; color: #b45309; }
.status-accepted { background: #ecfdf5; color: #059669; }
.status-rejected { background: #fef2f2; color: #dc2626; }
.inq-date { font-size: 12px; color: #aab4c4; }

/* ── 자재 리스트 ── */
.material-list { display: flex; flex-direction: column; gap: 8px; }
.mat-item { padding: 10px 0; border-bottom: 1px solid #f5f8fc; }
.mat-item:last-child { border-bottom: none; }
.mat-name { font-size: 14px; color: #102a56; font-weight: 600; }

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
.toggle-thumb { position: absolute; top: 3px; left: 3px; width: 20px; height: 20px; background: #fff; border-radius: 50%; transition: transform 0.2s; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.18); }
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
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background 0.15s;
}
.btn-logout:hover { background: #fff5f5; }

/* ── 모달 ── */
.modal-backdrop { position: fixed; inset: 0; background: rgba(10, 20, 50, 0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: 20px; padding: 36px; width: 420px; max-width: 90vw; }
.modal h3 { font-size: 20px; font-weight: 700; color: #102a56; margin: 0 0 24px; }
.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.form-group label { font-size: 13px; font-weight: 600; color: #4b6380; display: flex; align-items: center; gap: 6px; }
.field-note { font-size: 11px; font-weight: 500; color: #aab4c4; background: #f5f8fc; padding: 1px 6px; border-radius: 4px; }
.form-group input { border: 1px solid #dde7f7; border-radius: 8px; padding: 10px 14px; font-size: 15px; outline: none; width: 100%; box-sizing: border-box; }
.form-group input:focus { border-color: #1559e8; }
.input-disabled { background: #f8fafc; color: #aab4c4; cursor: not-allowed; }
.error-msg { font-size: 14px; color: #dc2626; margin: 8px 0; }
.success-msg { font-size: 14px; color: #059669; margin: 8px 0; }
.modal-actions { display: flex; gap: 12px; margin-top: 8px; }
.btn-primary { background: #1559e8; color: #fff; border: none; border-radius: 10px; padding: 10px 24px; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn-ghost { background: none; border: 1px solid #dde7f7; border-radius: 10px; padding: 10px 20px; font-size: 15px; color: #71809a; cursor: pointer; }

/* ── 반응형 ── */
@media (max-width: 680px) {
  .quick-links { grid-template-columns: 1fr; }
  .two-col-grid { grid-template-columns: 1fr; }
  .supply-stat-grid { grid-template-columns: repeat(2, 1fr); }
  .profile-card { flex-direction: column; align-items: flex-start; }
}
</style>
