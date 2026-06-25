<template>
  <section class="page-wrap">
    <RouterLink class="inqd-back-link" to="/inquiries">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
      문의 목록으로 돌아가기
    </RouterLink>

    <p v-if="isLoading" class="loading-message">문의 상세 정보를 불러오는 중입니다.</p>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <template v-if="!isLoading && inquiry">

      <!-- ═══════════════ 공급사 뷰 ═══════════════ -->
      <template v-if="isSupplier">
        <div class="inqd-header">
          <div>
            <h1 class="inqd-title">문의 상세</h1>
            <p class="inqd-desc">고객사의 문의 요청 정보를 확인하고, 적절히 답변해 주세요.</p>
          </div>
          <div class="inqd-header-btns">
          </div>
        </div>

        <!-- 메인 카드 -->
        <div class="inqd-main-card">
          <div class="inqd-card-top">
            <div class="inqd-badges">
              <span class="inqd-rank">{{ inquiry.id }}</span>
              <span :class="['inqd-status-badge', inquiry.status]">{{ getStatusLabel(inquiry.status) }}</span>
              <span class="inqd-type-badge">{{ isUrgentInquiry(inquiry) ? "긴급 문의" : "일반 문의" }}</span>
            </div>
            <div class="inqd-status-btns" ref="statusRef">
              <button
                v-for="s in inquiryStatuses"
                :key="s.value"
                type="button"
                :class="['inqd-sbtn', `inqd-sbtn-${s.value}`, { active: isStatusGroupActive(inquiry.status, s.value) }]"
                :disabled="isUpdating"
                @click="changeInquiryStatus(s.value)"
              >{{ s.label }}</button>
            </div>
          </div>

          <h2 class="inqd-company">{{ requesterCompanyLabel }}</h2>
          <p class="inqd-material-line">
            {{ inquiry.requestMaterial?.materialName || "" }}<template v-if="inquiry.requestMaterial?.strengthGrade"> · {{ inquiry.requestMaterial.strengthGrade }}</template>
          </p>

          <div class="inqd-divider"></div>

          <div class="inqd-info-bar">
            <div class="inqd-info-item">
              <span>담당자</span>
              <strong>{{ inquiry.requesterName || "미입력" }}</strong>
            </div>
            <div class="inqd-info-item">
              <span>연락처</span>
              <strong>{{ inquiry.contact || "미입력" }}</strong>
            </div>
            <div class="inqd-info-item">
              <span>문의 생성</span>
              <strong>{{ formatDateTime(inquiry.createdAt) }}</strong>
            </div>
            <div class="inqd-info-item">
              <span>상태 변경</span>
              <strong>{{ formatDateTime(inquiry.statusUpdatedAt) }}</strong>
            </div>
          </div>
        </div>

        <!-- 2열 그리드 -->
        <div class="inqd-grid">
          <div class="inqd-grid-card">
            <h3 class="inqd-grid-title">요청 자재 정보</h3>
            <dl class="inqd-dl">
              <div><dt>자재명</dt><dd>{{ inquiry.requestMaterial?.materialName || "미입력" }}</dd></div>
              <div><dt>강도/규격</dt><dd>{{ inquiry.requestMaterial?.strengthGrade || "미입력" }}</dd></div>
              <div><dt>현장 주소</dt><dd>{{ inquiry.requestMaterial?.siteAddress || "미입력" }}</dd></div>
              <div><dt>필요 수량</dt><dd>{{ inquiry.quantity || "미입력" }}</dd></div>
            </dl>
          </div>
          <div class="inqd-grid-card">
            <h3 class="inqd-grid-title">납기 정보</h3>
            <dl class="inqd-dl">
              <div><dt>문의 생성일</dt><dd>{{ formatShortDate(inquiry.createdAt) }}</dd></div>
              <div><dt>희망 납기일</dt><dd>{{ inquiry.desiredDate || "미입력" }}</dd></div>
              <div v-if="inquiry.desiredDate"><dt>남은 기간</dt><dd :class="['inqd-dday', getDDay(inquiry.desiredDate) < 0 ? 'inqd-dday-over' : '']">{{ getDDayLabel(inquiry.desiredDate) }}</dd></div>
              <div><dt>긴급 여부</dt><dd>{{ isUrgentInquiry(inquiry) ? "긴급" : "일반" }}</dd></div>
              <div><dt>현재 상태</dt><dd class="inqd-status-val">{{ getStatusLabel(inquiry.status) }}</dd></div>
            </dl>
          </div>
        </div>

        <!-- 문의 메모 -->
        <div class="inqd-memo">
          <div class="inqd-memo-head">
            <span class="inqd-memo-icon">❝</span>
            <h3>문의 메모</h3>
          </div>
          <div class="inqd-memo-inner">
            <p class="inqd-memo-text">{{ inquiry.message || "별도 메모가 없습니다." }}</p>
            <p class="inqd-memo-footer">작성일 {{ formatDateTime(inquiry.createdAt) }}</p>
          </div>
        </div>
      </template>

      <!-- ═══════════════ 요청자 뷰 ═══════════════ -->
      <template v-else>
        <div class="inqd-header">
          <div>
            <h1 class="inqd-title">문의 상세</h1>
            <p class="inqd-desc">보낸 문의의 상세 정보와 현재 처리 상태를 확인합니다.</p>
          </div>
          <div class="inqd-header-btns">
            <RouterLink class="inqd-btn-change" :to="`/inquiries/${inquiry.id}/edit`">수정하기</RouterLink>
            <button type="button" class="inqd-btn-delete" @click="removeInquiry">삭제하기</button>
          </div>
        </div>

        <!-- 메인 카드 -->
        <div class="inqd-main-card">
          <div class="inqd-card-top">
            <div class="inqd-badges">
              <span class="inqd-rank inqd-rank-rq">{{ inquiry.id }}</span>
              <span :class="['inqd-status-badge', inquiry.status]">{{ getStatusLabel(inquiry.status) }}</span>
            </div>
          </div>

          <h2 class="inqd-company">{{ inquiry.supplier?.supplierName || "공급사 미지정" }}</h2>
          <p class="inqd-material-line">
            {{ inquiry.requestMaterial?.materialName || "" }}<template v-if="inquiry.requestMaterial?.strengthGrade"> · {{ inquiry.requestMaterial.strengthGrade }}</template>
          </p>

          <div class="inqd-divider"></div>

          <div class="inqd-info-bar">
            <div class="inqd-info-item">
              <span>담당자</span>
              <strong>{{ inquiry.requesterName || "미입력" }}</strong>
            </div>
            <div class="inqd-info-item">
              <span>연락처</span>
              <strong>{{ inquiry.contact || "미입력" }}</strong>
            </div>
            <div class="inqd-info-item">
              <span>문의 생성</span>
              <strong>{{ formatDateTime(inquiry.createdAt) }}</strong>
            </div>
            <div class="inqd-info-item">
              <span>상태 변경</span>
              <strong>{{ formatDateTime(inquiry.statusUpdatedAt) }}</strong>
            </div>
          </div>
        </div>

        <!-- 2열 그리드 -->
        <div class="inqd-grid">
          <div class="inqd-grid-card">
            <h3 class="inqd-grid-title">요청 자재 정보</h3>
            <dl class="inqd-dl">
              <div><dt>자재명</dt><dd>{{ inquiry.requestMaterial?.materialName || "미입력" }}</dd></div>
              <div><dt>강도/규격</dt><dd>{{ inquiry.requestMaterial?.strengthGrade || "미입력" }}</dd></div>
              <div><dt>현장 주소</dt><dd>{{ inquiry.requestMaterial?.siteAddress || "미입력" }}</dd></div>
              <div><dt>필요 수량</dt><dd>{{ inquiry.quantity || "미입력" }}</dd></div>
            </dl>
          </div>
          <div class="inqd-grid-card">
            <h3 class="inqd-grid-title">납기 정보</h3>
            <dl class="inqd-dl">
              <div><dt>문의 생성일</dt><dd>{{ formatShortDate(inquiry.createdAt) }}</dd></div>
              <div><dt>희망 납기일</dt><dd>{{ inquiry.desiredDate || "미입력" }}</dd></div>
              <div v-if="inquiry.desiredDate"><dt>남은 기간</dt><dd :class="['inqd-dday', getDDay(inquiry.desiredDate) < 0 ? 'inqd-dday-over' : '']">{{ getDDayLabel(inquiry.desiredDate) }}</dd></div>
              <div><dt>긴급 여부</dt><dd>일반</dd></div>
              <div><dt>현재 상태</dt><dd class="inqd-status-val">{{ getStatusLabel(inquiry.status) }}</dd></div>
            </dl>
          </div>
        </div>

        <!-- 문의 메모 -->
        <div class="inqd-memo">
          <div class="inqd-memo-head">
            <span class="inqd-memo-icon">❝</span>
            <h3>문의 메모</h3>
          </div>
          <div class="inqd-memo-inner">
            <p class="inqd-memo-text">{{ inquiry.message || "별도 메모가 없습니다." }}</p>
            <p class="inqd-memo-footer">작성일 {{ formatDateTime(inquiry.createdAt) }}</p>
          </div>
        </div>
      </template>
    </template>

    <div v-else-if="!isLoading" class="empty-state">
      <strong>문의 정보를 찾을 수 없습니다.</strong>
      <p>저장된 문의가 없거나 접근 권한이 없습니다.</p>
      <RouterLink class="primary-button" to="/inquiries">문의 내역으로 이동</RouterLink>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authState } from "../api/authApi";
import { deleteSupplierInquiry, getSupplierInquiry, updateSupplierInquiryStatus } from "../api/materialApi";

const route = useRoute();
const router = useRouter();
const inquiry = ref(null);
const isLoading = ref(false);
const isUpdating = ref(false);
const errorMessage = ref("");
const statusRef = ref(null);

const statusLabels = {
  received: "협의 필요",
  pending: "협의 필요",
  reviewing: "협의 필요",
  quoted: "납품 가능",
  accepted: "납품 가능",
  need_more_info: "추가 확인 필요",
  rejected: "거절",
  unavailable: "거절",
};

const inquiryStatuses = [
  { value: "accepted", label: "납품 가능" },
  { value: "pending", label: "협의 필요" },
  { value: "rejected", label: "거절" },
];

const isSupplier = computed(() => authState.user?.role === "supplier");
const requesterCompanyLabel = computed(() =>
  inquiry.value?.requesterCompany
  || inquiry.value?.requesterName
  || "회사명 미등록",
);

onMounted(loadInquiry);

function scrollToStatus() {
  statusRef.value?.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function changeInquiryStatus(status) {
  try {
    isUpdating.value = true;
    errorMessage.value = "";
    const updated = await updateSupplierInquiryStatus(inquiry.value.id, status);
    if (updated) inquiry.value = updated;
  } catch {
    errorMessage.value = "문의 상태를 변경하지 못했습니다.";
  } finally {
    isUpdating.value = false;
  }
}

async function loadInquiry() {
  try {
    isLoading.value = true;
    errorMessage.value = "";
    inquiry.value = await getSupplierInquiry(route.params.id);
  } catch {
    errorMessage.value = "문의 상세 정보를 불러오지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

async function removeInquiry() {
  if (!window.confirm("이 문의를 삭제하시겠습니까?")) return;
  try {
    await deleteSupplierInquiry(inquiry.value.id);
    router.push("/inquiries");
  } catch {
    errorMessage.value = "삭제할 문의를 찾을 수 없습니다.";
  }
}

function getStatusLabel(status) {
  return statusLabels[status] || "협의 필요";
}

function isStatusGroupActive(currentStatus, actionStatus) {
  const groups = {
    pending: ["received", "pending", "reviewing"],
    accepted: ["quoted", "accepted"],
    rejected: ["rejected", "unavailable"],
  };
  return groups[actionStatus]?.includes(currentStatus) ?? false;
}

function isUrgentInquiry(inq) {
  return inq?.requestType === "urgent" || inq?.priority === "high" || String(inq?.id || "").startsWith("URG");
}

function formatDateTime(value) {
  if (!value) return "날짜 없음";
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatShortDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(value));
}

function getDDay(desiredDate) {
  if (!desiredDate) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(desiredDate);
  target.setHours(0, 0, 0, 0);
  return Math.round((target - today) / (1000 * 60 * 60 * 24));
}

function getDDayLabel(desiredDate) {
  const diff = getDDay(desiredDate);
  if (diff === null) return "-";
  if (diff > 0) return `D-${diff}일`;
  if (diff === 0) return "D-Day";
  return `D+${Math.abs(diff)}일`;
}
</script>

<style scoped>
/* 뒤로가기 */
.inqd-back-link { display:inline-flex;align-items:center;gap:6px;color:#1559e8;font-size:14px;font-weight:700;text-decoration:none;margin-bottom:20px;padding:4px 0;transition:opacity .15s; }
.inqd-back-link:hover { opacity:.7; }

/* 헤더 */
.inqd-header { display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:24px; }
.inqd-title { font-size:32px;font-weight:900;color:#102a56;margin:0 0 6px; }
.inqd-desc { color:#65748d;font-size:15px;margin:0; }
.inqd-header-btns { display:flex;gap:10px;flex-shrink:0;align-items:center; }
.inqd-btn-change { display:inline-flex;align-items:center;gap:6px;border:1.5px solid #d7e3f5;border-radius:10px;padding:11px 20px;background:#fff;color:#40506a;font-size:14px;font-weight:800;cursor:pointer;text-decoration:none;transition:border-color .15s,color .15s; }
.inqd-btn-change:hover { border-color:#1559e8;color:#1559e8; }
.inqd-btn-respond { display:inline-flex;align-items:center;gap:6px;border:none;border-radius:10px;padding:11px 22px;background:#1559e8;color:#fff;font-size:14px;font-weight:800;cursor:pointer;transition:opacity .15s; }
.inqd-btn-respond:hover { opacity:.88; }
.inqd-btn-delete { display:inline-flex;align-items:center;border:1.5px solid #fecaca;border-radius:10px;padding:11px 20px;background:#fff;color:#b42318;font-size:14px;font-weight:800;cursor:pointer;transition:background .15s; }
.inqd-btn-delete:hover { background:#fff5f5; }

/* 메인 카드 */
.inqd-main-card { background:#fff;border:1.5px solid #e2e8f3;border-radius:20px;padding:24px 28px;margin-bottom:16px;box-shadow:0 4px 24px rgba(16,42,86,.07); }
.inqd-card-top { display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:16px; }

/* 뱃지 영역 */
.inqd-badges { display:flex;align-items:center;gap:8px;flex-wrap:wrap; }
.inqd-rank { display:inline-flex;align-items:center;justify-content:center;min-width:32px;height:32px;border-radius:50%;background:#1559e8;color:#fff;font-size:13px;font-weight:900;padding:0 8px; }
.inqd-rank-rq { background:#1559e8; }
.inqd-status-badge { border-radius:99px;padding:5px 14px;font-size:12px;font-weight:800; }
.inqd-status-badge.received,.inqd-status-badge.pending,.inqd-status-badge.reviewing { background:#eef4ff;color:#1d4ed8; }
.inqd-status-badge.quoted,.inqd-status-badge.accepted { background:#dcf8ed;color:#047857; }
.inqd-status-badge.rejected,.inqd-status-badge.unavailable { background:#fee7e7;color:#b42318; }
.inqd-type-badge { background:#f5f8fd;color:#51627e;border-radius:99px;padding:5px 14px;font-size:12px;font-weight:700; }

/* 상태 변경 버튼 그룹 */
.inqd-status-btns { display:flex;gap:8px; }
.inqd-sbtn { border-radius:10px;padding:10px 18px;font-size:14px;font-weight:800;cursor:pointer;transition:background .15s,color .15s,border-color .15s,opacity .15s; }
.inqd-sbtn:disabled { opacity:.5;cursor:default; }
.inqd-sbtn-accepted { border:1.5px solid #1559e8;background:#fff;color:#1559e8; }
.inqd-sbtn-pending { border:1.5px solid #d7e3f5;background:#fff;color:#40506a; }
.inqd-sbtn-rejected { border:1.5px solid #fca5a5;background:#fff;color:#b42318; }
.inqd-sbtn.active { background:#1559e8;color:#fff;border-color:#1559e8; }
.inqd-sbtn-rejected.active { background:#b42318;border-color:#b42318; }
.inqd-sbtn:not(:disabled):not(.active):hover { opacity:.75; }

/* 업체명 + 자재 */
.inqd-company { font-size:26px;font-weight:900;color:#102a56;margin:0 0 6px; }
.inqd-material-line { font-size:15px;color:#65748d;margin:0; }

/* 구분선 */
.inqd-divider { height:1px;background:#eef2f8;margin:20px 0; }

/* 4열 정보 바 */
.inqd-info-bar { display:grid;grid-template-columns:repeat(4,1fr); }
.inqd-info-item { padding:10px 16px 10px 0;border-right:1px solid #eef2f8; }
.inqd-info-item:last-child { border-right:none; }
.inqd-info-item > span { display:block;font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:6px; }
.inqd-info-item > strong { display:block;font-size:14px;color:#102a56;font-weight:800; }

/* 2열 그리드 */
.inqd-grid { display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px; }
.inqd-grid-card { background:#fff;border:1.5px solid #e2e8f3;border-radius:20px;padding:22px 24px;box-shadow:0 4px 24px rgba(16,42,86,.07); }
.inqd-grid-title { font-size:17px;font-weight:900;color:#102a56;margin:0 0 16px; }
.inqd-dl { display:flex;flex-direction:column; }
.inqd-dl > div { display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f3f6fb; }
.inqd-dl > div:last-child { border-bottom:none; }
.inqd-dl dt { font-size:13px;color:#8492a8;font-weight:600; }
.inqd-dl dd { font-size:14px;color:#102a56;font-weight:700;text-align:right;max-width:60%;word-break:break-all; }
.inqd-dday { color:#1559e8;font-weight:900 !important; }
.inqd-dday-over { color:#b42318 !important; }
.inqd-status-val { color:#1559e8;font-weight:900 !important; }

/* 문의 메모 */
.inqd-memo { background:#fff;border:1.5px solid #e2e8f3;border-radius:20px;padding:24px 28px;box-shadow:0 4px 24px rgba(16,42,86,.07); }
.inqd-memo-head { display:flex;align-items:center;gap:10px;margin-bottom:14px; }
.inqd-memo-icon { font-size:28px;color:#c7d7f4;line-height:1;font-family:Georgia,serif; }
.inqd-memo-head h3 { font-size:16px;font-weight:900;color:#102a56;margin:0; }
.inqd-memo-inner { background:#f5f8fd;border:1px solid #e2e8f3;border-radius:14px;padding:18px 20px; }
.inqd-memo-text { font-size:15px;color:#40506a;line-height:1.8;margin:0 0 16px;white-space:pre-line; }
.inqd-memo-footer { font-size:12px;color:#94a3b8;text-align:right;margin:0; }

/* 반응형 */
@media(max-width:780px) {
  .inqd-header { flex-direction:column; }
  .inqd-card-top { flex-direction:column;align-items:flex-start; }
  .inqd-info-bar { grid-template-columns:repeat(2,1fr); }
  .inqd-info-item:nth-child(2) { border-right:none; }
  .inqd-info-item:nth-child(1),.inqd-info-item:nth-child(2) { border-bottom:1px solid #eef2f8; }
  .inqd-grid { grid-template-columns:1fr; }
  .inqd-status-btns { flex-wrap:wrap; }
}
</style>
