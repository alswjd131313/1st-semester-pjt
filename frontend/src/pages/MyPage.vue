<template>
  <div class="mypage">
    <div class="page-header">
      <h1>마이페이지</h1>
      <p class="page-sub">내 계정 정보와 활동 내역을 확인합니다.</p>
    </div>

    <!-- 프로필 요약 -->
    <section class="profile-summary">
      <div class="avatar">{{ initial }}</div>
      <div class="profile-info">
        <strong>{{ displayName }}</strong>
        <p>{{ roleLabel }}</p>
        <span class="email">{{ authState.user?.email ?? '-' }}</span>
      </div>
      <RouterLink class="btn-outline" to="/supplier/profile" v-if="isSupplier">공급사 프로필 편집</RouterLink>
    </section>

    <!-- 최근 문의 -->
    <section class="mypage-card">
      <div class="card-header">
        <h2>최근 문의</h2>
        <RouterLink class="link-more" to="/inquiries">전체 보기</RouterLink>
      </div>
      <div v-if="recentInquiries.length === 0" class="empty-state">문의 내역이 없습니다.</div>
      <div v-else class="inquiry-list">
        <div
          v-for="inq in recentInquiries"
          :key="inq.id"
          class="inquiry-item"
          @click="router.push(`/inquiries/${inq.id}`)"
        >
          <div class="inq-row">
            <span class="inq-material">{{ inq.material_name ?? '자재' }}</span>
            <span :class="['inq-status', statusClass(inq.status)]">{{ statusLabel(inq.status) }}</span>
          </div>
          <span class="inq-date">{{ formatDate(inq.created_at) }}</span>
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

const router = useRouter();
const inquiries = ref([]);
const emailNotify = ref(true);
const showPwModal = ref(false);
const pwError = ref("");
const pw = reactive({ current: "", next: "", confirm: "" });

const isSupplier = computed(() => authState.user?.role === "supplier");
const displayName = computed(() => authState.user?.username ?? authState.user?.email ?? "사용자");
const roleLabel = computed(() => isSupplier.value ? "공급사" : "자재 요청자");
const initial = computed(() => (displayName.value[0] ?? "U").toUpperCase());

const recentInquiries = computed(() => inquiries.value.slice(0, 5));

onMounted(async () => {
  try {
    inquiries.value = await getSupplierInquiries();
  } catch {
    // pass
  }
});

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
  max-width: 720px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

.page-header { margin-bottom: 36px; }
.page-header h1 { font-size: 28px; font-weight: 700; color: #102a56; margin: 0 0 4px; }
.page-sub { color: #71809a; font-size: 15px; margin: 0; }

.profile-summary {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #1559e8;
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-info { flex: 1; }
.profile-info strong { font-size: 18px; font-weight: 700; color: #102a56; }
.profile-info p { font-size: 14px; color: #71809a; margin: 2px 0 4px; }
.email { font-size: 13px; color: #aab4c4; }

.btn-outline {
  border: 1px solid #1559e8;
  color: #1559e8;
  background: none;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 14px;
  text-decoration: none;
  white-space: nowrap;
}

.mypage-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.card-header h2 { font-size: 18px; font-weight: 700; color: #102a56; margin: 0; }
.card-title { font-size: 18px; font-weight: 700; color: #102a56; margin: 0 0 20px; }
.link-more { font-size: 14px; color: #1559e8; text-decoration: none; }

.empty-state { text-align: center; color: #aab4c4; padding: 28px; font-size: 15px; }

.inquiry-list { display: flex; flex-direction: column; gap: 12px; }
.inquiry-item {
  border: 1px solid #f0f4fa;
  border-radius: 10px;
  padding: 14px 18px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.inquiry-item:hover { border-color: #1559e8; }
.inq-row { display: flex; align-items: center; gap: 12px; }
.inq-material { font-weight: 600; font-size: 15px; color: #102a56; }
.inq-status { font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 999px; }
.status-pending { background: #fef9ec; color: #b45309; }
.status-accepted { background: #ecfdf5; color: #059669; }
.status-rejected { background: #fef2f2; color: #dc2626; }
.inq-date { font-size: 13px; color: #aab4c4; }

.setting-list { display: flex; flex-direction: column; gap: 0; }
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 0;
  border-bottom: 1px solid #f0f4fa;
}
.setting-item:last-child { border-bottom: none; }
.setting-item strong { font-size: 15px; color: #102a56; }
.setting-item p { font-size: 13px; color: #71809a; margin: 4px 0 0; }
.btn-outline-sm {
  border: 1px solid #dde7f7;
  background: none;
  border-radius: 8px;
  padding: 7px 18px;
  font-size: 14px;
  color: #4b6380;
  cursor: pointer;
}

.toggle { display: flex; align-items: center; cursor: pointer; }
.toggle input { display: none; }
.toggle-track {
  width: 44px;
  height: 24px;
  background: #dde7f7;
  border-radius: 999px;
  position: relative;
  transition: background 0.2s;
}
.toggle input:checked + .toggle-track { background: #1559e8; }
.toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.2s;
}
.toggle input:checked + .toggle-track .toggle-thumb { transform: translateX(20px); }

.logout-section { text-align: center; }
.btn-logout {
  background: none;
  border: 1px solid #fca5a5;
  color: #dc2626;
  border-radius: 10px;
  padding: 12px 40px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 20, 50, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal {
  background: #fff;
  border-radius: 20px;
  padding: 36px;
  width: 420px;
  max-width: 90vw;
}
.modal h3 { font-size: 20px; font-weight: 700; color: #102a56; margin: 0 0 24px; }

.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.form-group label { font-size: 13px; font-weight: 600; color: #4b6380; }
.form-group input {
  border: 1px solid #dde7f7;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 15px;
  outline: none;
}
.form-group input:focus { border-color: #1559e8; }

.error-msg { font-size: 14px; color: #dc2626; margin: 8px 0; }

.modal-actions { display: flex; gap: 12px; margin-top: 8px; }
.btn-primary {
  background: #1559e8;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 10px 24px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.btn-ghost {
  background: none;
  border: 1px solid #dde7f7;
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 15px;
  color: #71809a;
  cursor: pointer;
}
</style>
