<template>
  <section class="page-wrap">
    <div class="page-heading dashboard-heading">
      <div>
        <p class="eyebrow">{{ isSupplier ? "Supplier Requests" : "Dashboard" }}</p>
        <h1>{{ dashboardTitle }}</h1>
        <p>{{ dashboardDescription }}</p>
      </div>
    </div>

    <div v-if="!isSupplier" class="inquiry-type-tabs" role="tablist" aria-label="문의 유형">
      <button type="button" :class="{ active: activeTab === 'supplier' }" @click="activeTab = 'supplier'">공급사 문의</button>
      <button type="button" :class="{ active: activeTab === 'community' }" @click="activeTab = 'community'">커뮤니티 대화 요청</button>
    </div>

    <div v-if="activeTab === 'supplier' && isSupplier" class="dashboard-stats">
      <article>
        <span>받은 요청</span>
        <strong>{{ roleInquiries.length }}건</strong>
      </article>
      <article>
        <span>확인 대기</span>
        <strong>{{ waitingCount }}건</strong>
      </article>
      <article>
        <span>납품 가능</span>
        <strong>{{ availableCount }}건</strong>
      </article>
      <article>
        <span>거절</span>
        <strong>{{ rejectedCount }}건</strong>
      </article>
    </div>

    <div v-else-if="activeTab === 'supplier'" class="dashboard-stats">
      <article>
        <span>저장된 문의</span>
        <strong>{{ roleInquiries.length }}건</strong>
      </article>
      <article>
        <span>확인 대기</span>
        <strong>{{ waitingCount }}건</strong>
      </article>
      <article>
        <span>납품 가능</span>
        <strong>{{ availableCount }}건</strong>
      </article>
      <article>
        <span>거절</span>
        <strong>{{ rejectedCount }}건</strong>
      </article>
    </div>

    <div v-if="activeTab === 'supplier'" class="supplier-status-filters" aria-label="문의 상태 필터">
      <button
        v-for="filter in inquiryStatusFilters"
        :key="filter.value"
        type="button"
        :class="{ active: inquiryStatusFilter === filter.value }"
        @click="inquiryStatusFilter = filter.value"
      >
        {{ filter.label }}
      </button>
    </div>

    <p v-if="activeTab === 'supplier' && isLoading" class="loading-message">문의 내역을 불러오는 중입니다.</p>
    <p v-if="activeTab === 'supplier' && errorMessage" class="error-message">{{ errorMessage }}</p>

    <div v-if="activeTab === 'supplier' && !isLoading && displayedInquiries.length" class="inquiry-list">
      <article
        v-for="inquiry in displayedInquiries"
        :key="inquiry.id"
        class="inquiry-card"
        role="link"
        tabindex="0"
        @click="openInquiry(inquiry.id)"
        @keydown.enter="openInquiry(inquiry.id)"
      >
        <div class="card-topline">
          <span class="rank-badge">{{ inquiry.id }}</span>
          <span :class="['status-badge', inquiry.status]">
            {{ getStatusLabel(inquiry.status) }}
          </span>
          <span v-if="!isSupplier" :class="['approval-badge', { warn: inquiry.supplier?.approvalRequired }]">
            {{ inquiry.supplier?.approvalRequired ? "승인 확인 필요" : "일반 문의" }}
          </span>
          <span v-if="!isSupplier && isUrgentInquiry(inquiry)" class="urgent-badge">긴급 납품 요청</span>
        </div>

        <div class="inquiry-card-header">
          <div v-if="isSupplier">
            <h2>{{ getMaterialName(inquiry) }}</h2>
            <p v-if="getMaterialStandard(inquiry)" class="material-line">{{ getMaterialStandard(inquiry) }}</p>
          </div>
          <div v-else>
            <h2>{{ inquiry.supplier?.supplierName || "공급사 미지정" }}</h2>
            <p class="material-line">
              {{ inquiry.supplier?.materialName || "자재 미지정" }}
              <span v-if="inquiry.supplier?.standard">· {{ inquiry.supplier.standard }}</span>
            </p>
          </div>
          <span class="inquiry-date">
            {{ formatDate(isSupplier ? (inquiry.statusUpdatedAt || inquiry.createdAt) : inquiry.createdAt) }}
          </span>
        </div>

        <dl v-if="isSupplier" class="score-list supplier-request-details">
          <div v-if="getRequesterName(inquiry)">
            <dt>요청자</dt>
            <dd>{{ getRequesterName(inquiry) }}</dd>
          </div>
          <div v-if="getQuantity(inquiry)">
            <dt>요청 수량</dt>
            <dd>{{ getQuantity(inquiry) }}</dd>
          </div>
          <div v-if="inquiry.desiredDate">
            <dt>희망 납기</dt>
            <dd>{{ inquiry.desiredDate }}</dd>
          </div>
          <div v-if="getSiteAddress(inquiry)">
            <dt>현장 위치</dt>
            <dd>{{ getSiteAddress(inquiry) }}</dd>
          </div>
        </dl>

        <dl v-else class="score-list">
          <div>
            <dt>담당자</dt>
            <dd>{{ inquiry.requesterName }}</dd>
          </div>
          <div>
            <dt>연락처</dt>
            <dd>{{ inquiry.contact }}</dd>
          </div>
          <div>
            <dt>문의 수량</dt>
            <dd>{{ inquiry.quantity }}</dd>
          </div>
          <div>
            <dt>희망 납기</dt>
            <dd>{{ inquiry.desiredDate || "미입력" }}</dd>
          </div>
        </dl>

        <p v-if="inquiry.message" class="reason">{{ inquiry.message }}</p>

        <div v-if="!isSupplier && isUrgentInquiry(inquiry)" class="urgent-request-note">
          <strong>우선 확인 필요</strong>
          <span>재고 보유 여부, 최종 단가, 가능한 납품 시간을 빠르게 확인해야 하는 요청입니다.</span>
        </div>

        <div class="inquiry-footer">
          <span>
            {{ isSupplier ? "최근 상태 변경" : "상태 변경" }}:
            {{ formatDate(isSupplier ? (inquiry.statusUpdatedAt || inquiry.createdAt) : inquiry.statusUpdatedAt) }}
          </span>
          <div v-if="isSupplier" class="status-actions" aria-label="문의 상태 변경">
            <button
            v-for="status in supplierActionStatuses"
              :key="status.value"
              type="button"
              :class="['status-action', { active: isStatusGroupActive(inquiry.status, status.value) }]"
              :disabled="updatingInquiryId === inquiry.id"
              @click.stop="changeInquiryStatus(inquiry.id, status.value)"
            >
              {{ status.label }}
            </button>
          </div>
          <RouterLink class="secondary-button" :to="`/inquiries/${inquiry.id}`" @click.stop>
            상세 보기
          </RouterLink>
        </div>
      </article>
    </div>

    <div v-else-if="activeTab === 'supplier' && !isLoading" class="empty-state">
      <template v-if="isSupplier">
        <strong>{{ inquiryStatusFilter === "all" ? "아직 받은 요청이 없습니다." : "해당 상태의 요청이 없습니다." }}</strong>
        <p>요청자가 보낸 자재 문의가 접수되면 이곳에서 확인할 수 있습니다.</p>
      </template>
      <template v-else>
        <strong>아직 저장된 문의가 없습니다.</strong>
        <p>추천 결과에서 공급사 후보의 문의하기 버튼을 눌러 첫 문의를 저장해보세요.</p>
        <RouterLink class="primary-button" to="/recommendations">추천 결과 확인하기</RouterLink>
      </template>
    </div>

    <template v-if="!isSupplier && activeTab === 'community'">
      <p v-if="communityLoading" class="loading-message">커뮤니티 대화 요청을 불러오는 중입니다.</p>
      <p v-if="communityError" class="error-message">{{ communityError }}</p>
      <div v-if="!communityLoading && communityRequests.length" class="community-request-list">
        <article v-for="item in communityRequests" :key="item.id" class="community-request-card">
          <div class="community-request-topline">
            <span>{{ item.direction === 'sent' ? '보낸 질문' : '받은 질문' }}</span>
            <span :class="['community-request-status', item.status]">{{ item.status_label }}</span>
          </div>
          <h2>{{ item.post_title }}</h2>
          <p class="community-request-target">
            {{ item.direction === 'sent' ? '요청 대상' : '요청자' }} ·
            {{ item.direction === 'sent' ? item.target_display_name : item.requester_display_name }}
          </p>
          <p class="community-request-message">{{ item.message }}</p>
          <footer>
            <time>{{ formatDate(item.created_at) }}</time>
            <div v-if="item.direction === 'received' && item.status === 'pending'" class="community-request-actions">
              <button type="button" @click="changeCommunityStatus(item.id, 'confirmed')">확인 완료</button>
              <button type="button" class="reject" @click="changeCommunityStatus(item.id, 'rejected')">거절</button>
            </div>
            <RouterLink :to="`/community/${item.post}`">게시글 보기</RouterLink>
          </footer>
        </article>
      </div>
      <div v-else-if="!communityLoading" class="empty-state">
        <strong>커뮤니티 대화 요청이 없습니다.</strong>
        <p>커뮤니티 게시글의 ‘작성자에게 질문’에서 사례 관련 질문을 보낼 수 있습니다.</p>
        <RouterLink class="primary-button" to="/community">커뮤니티 보기</RouterLink>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { authState } from "../api/authApi";
import {
  filterInquiriesForUser,
  getSupplierInquiries,
  updateSupplierInquiryStatus,
} from "../api/materialApi";
import { getCommunityContactRequests, updateCommunityContactRequest } from "../api/communityApi";

const inquiries = ref([]);
const router = useRouter();
const activeTab = ref("supplier");
const communityRequests = ref([]);
const communityLoading = ref(false);
const communityError = ref("");
const isLoading = ref(false);
const errorMessage = ref("");
const updatingInquiryId = ref("");
const inquiryStatusFilter = ref("all");
const statusLabels = {
  received: "확인 대기",
  pending: "확인 대기",
  reviewing: "확인 대기",
  quoted: "납품 가능",
  accepted: "납품 가능",
  need_more_info: "추가 확인 필요",
  rejected: "거절",
  unavailable: "거절",
};
const inquiryStatusFilters = [
  { value: "all", label: "전체", statuses: [] },
  { value: "waiting", label: "확인 대기", statuses: ["received", "pending", "reviewing"] },
  { value: "available", label: "납품 가능", statuses: ["quoted", "accepted"] },
  { value: "rejected", label: "거절", statuses: ["rejected", "unavailable"] },
];
const supplierActionStatuses = [
  { value: "pending", label: "확인 대기" },
  { value: "accepted", label: "납품 가능" },
  { value: "rejected", label: "거절" },
];

const dashboardTitle = computed(() =>
  authState.user?.role === "supplier" ? "받은 요청" : "내 문의 내역",
);

const isSupplier = computed(() => authState.user?.role === "supplier");
const dashboardDescription = computed(() =>
  isSupplier.value
    ? "요청자가 보낸 자재 문의를 확인하고 상태를 관리합니다."
    : "내가 보낸 공급사 문의와 커뮤니티 대화 요청을 확인하고 후속 상태를 관리합니다.",
);
const roleInquiries = computed(() => filterInquiriesForUser(inquiries.value, authState.user));
const displayedInquiries = computed(() => {
  if (inquiryStatusFilter.value === "all") {
    return roleInquiries.value;
  }
  const filter = inquiryStatusFilters.find((item) => item.value === inquiryStatusFilter.value);
  return roleInquiries.value.filter((inquiry) => filter?.statuses.includes(inquiry.status));
});

function openInquiry(inquiryId) {
  router.push(`/inquiries/${inquiryId}`);
}

const waitingCount = computed(
  () => roleInquiries.value.filter((inquiry) => ["received", "pending", "reviewing"].includes(inquiry.status)).length,
);

const availableCount = computed(
  () => roleInquiries.value.filter((inquiry) => ["quoted", "accepted"].includes(inquiry.status)).length,
);

const rejectedCount = computed(
  () => roleInquiries.value.filter((inquiry) => ["rejected", "unavailable"].includes(inquiry.status)).length,
);

const latestInquiryLabel = computed(() => {
  const latest = inquiries.value[0];
  return latest ? formatDate(latest.createdAt) : "없음";
});

onMounted(() => {
  loadInquiries();
  if (!isSupplier.value) loadCommunityRequests();
});

async function loadCommunityRequests() {
  try {
    communityLoading.value = true;
    communityError.value = "";
    communityRequests.value = await getCommunityContactRequests();
  } catch {
    communityError.value = "커뮤니티 대화 요청을 불러오지 못했습니다.";
  } finally {
    communityLoading.value = false;
  }
}

async function changeCommunityStatus(requestId, status) {
  try {
    const updated = await updateCommunityContactRequest(requestId, status);
    communityRequests.value = communityRequests.value.map((item) => item.id === requestId ? updated : item);
  } catch {
    communityError.value = "대화 요청 상태를 변경하지 못했습니다.";
  }
}

async function changeInquiryStatus(inquiryId, status) {
  try {
    updatingInquiryId.value = inquiryId;
    errorMessage.value = "";
    const updatedInquiry = await updateSupplierInquiryStatus(inquiryId, status);
    if (!updatedInquiry) {
      return;
    }

    inquiries.value = inquiries.value.map((inquiry) =>
      inquiry.id === inquiryId ? updatedInquiry : inquiry,
    );
  } catch {
    errorMessage.value = "문의 상태를 변경하지 못했습니다. 잠시 후 다시 시도해주세요.";
  } finally {
    updatingInquiryId.value = "";
  }
}

async function loadInquiries() {
  try {
    isLoading.value = true;
    errorMessage.value = "";
    inquiries.value = await getSupplierInquiries();
  } catch {
    errorMessage.value = "문의 내역을 불러오지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

function getStatusLabel(status) {
  return statusLabels[status] || "확인 대기";
}

function isStatusGroupActive(currentStatus, actionStatus) {
  const groups = {
    pending: ["received", "pending", "reviewing"],
    accepted: ["quoted", "accepted"],
    rejected: ["rejected", "unavailable"],
  };
  return groups[actionStatus]?.includes(currentStatus) || false;
}

function getMaterialName(inquiry) {
  return inquiry.requestMaterial?.materialName || inquiry.supplier?.materialName || inquiry.material_name || "요청 자재";
}

function getMaterialStandard(inquiry) {
  return inquiry.requestMaterial?.strengthGrade || inquiry.supplier?.standard || inquiry.standard || inquiry.spec || "";
}

function getQuantity(inquiry) {
  return inquiry.quantity || inquiry.requestMaterial?.requiredQuantity || "";
}

function getSiteAddress(inquiry) {
  return inquiry.requestMaterial?.siteAddress || inquiry.siteAddress || inquiry.site_address || "";
}

function getRequesterName(inquiry) {
  return inquiry.requesterCompany || inquiry.companyName || inquiry.requesterName || "";
}

function isUrgentInquiry(inquiry) {
  return inquiry?.requestType === "urgent" || inquiry?.priority === "high" || String(inquiry?.id || "").startsWith("URG");
}

function formatDate(value) {
  if (!value) {
    return "날짜 없음";
  }

  return new Intl.DateTimeFormat("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
</script>

<style scoped>
.supplier-status-filters{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 22px}.supplier-status-filters button{border:1px solid #d7e3f5;border-radius:999px;padding:9px 14px;color:#51627e;background:#fff;font-weight:800;cursor:pointer}.supplier-status-filters button.active{border-color:#1559e8;color:#1559e8;background:#edf4ff}.supplier-request-details dd{overflow-wrap:anywhere}
.inquiry-type-tabs{display:flex;gap:8px;margin:22px 0}.inquiry-type-tabs button{border:1px solid #d7e3f5;border-radius:999px;padding:11px 17px;color:#51627e;background:#fff;font-weight:900;cursor:pointer}.inquiry-type-tabs button.active{border-color:#1559e8;color:#fff;background:#1559e8}.community-request-list{display:grid;gap:14px}.community-request-card{border:1px solid #dbe6f8;border-radius:22px;padding:22px;background:#fff;box-shadow:0 14px 40px rgba(31,61,115,.08)}.community-request-topline,.community-request-card footer{display:flex;align-items:center;justify-content:space-between;gap:12px}.community-request-topline>span:first-child{color:#1559e8;font-size:12px;font-weight:900}.community-request-status{border-radius:999px;padding:6px 10px;font-size:12px;font-weight:900}.community-request-status.pending{color:#9a5b00;background:#fff2cc}.community-request-status.confirmed{color:#047857;background:#dcf8ed}.community-request-status.rejected{color:#b42318;background:#fee7e7}.community-request-card h2{margin:14px 0 7px;color:#102a56;font-size:20px}.community-request-target{color:#65748d;font-size:13px}.community-request-message{border-radius:14px;padding:14px;color:#40506a;background:#f5f8fd;line-height:1.6}.community-request-card footer{margin-top:14px;color:#8492a8;font-size:12px}.community-request-card footer>a{color:#1559e8;font-weight:900}.community-request-actions{display:flex;gap:7px;margin-left:auto}.community-request-actions button{border:0;border-radius:9px;padding:8px 10px;color:#fff;background:#1559e8;cursor:pointer;font-weight:800}.community-request-actions .reject{color:#b42318;background:#fee7e7}@media(max-width:650px){.community-request-card footer{align-items:flex-start;flex-direction:column}.community-request-actions{margin-left:0}}
</style>
