<template>
  <section class="page-wrap">
    <div class="page-heading dashboard-heading">
      <div>
        <!-- <p class="eyebrow">{{ isSupplier ? "Supplier Requests" : "Dashboard" }}</p> -->
        <h1>{{ dashboardTitle }}</h1>
        <p>{{ dashboardDescription }}</p>
      </div>
    </div>

    <div class="inquiry-type-tabs" role="tablist" aria-label="문의 유형">
      <button type="button" :class="{ active: activeTab === 'supplier' }" @click="activeTab = 'supplier'">공급사 문의</button>
      <button type="button" :class="{ active: activeTab === 'community' }" @click="activeTab = 'community'">커뮤니티 대화 요청</button>
    </div>

    <div v-if="activeTab === 'supplier' && isSupplier" class="dashboard-stats">
      <article>
        <span>전체 요청</span>
        <strong>{{ roleInquiries.length }}건</strong>
      </article>
      <article>
        <span>협의 필요</span>
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
        <span>협의 필요</span>
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
        v-for="(inquiry, index) in displayedInquiries"
        :key="inquiry.id"
        class="inquiry-card"
        :class="{ 'supplier-card': isSupplier }"
      >
        <!-- ── 공급사 뷰 ── -->
        <template v-if="isSupplier">
          <div class="card-topline">
            <span class="inq-id-badge">{{ displayedInquiries.length - index }}</span>
            <span :class="['status-badge', inquiry.status]">{{ getStatusLabel(inquiry.status) }}</span>
            <span class="inq-time">{{ formatDate(inquiry.createdAt) }}</span>
          </div>

          <h2 class="inq-title">
            {{ getMaterialName(inquiry) }}<template v-if="getMaterialStandard(inquiry)"> / {{ getMaterialStandard(inquiry) }}</template>
          </h2>

          <div class="inq-info-grid">
            <div class="inq-info-item">
              <div class="inq-info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20 7H4c-.55 0-1 .45-1 1v8c0 .55.45 1 1 1h16c.55 0 1-.45 1-1V8c0-.55-.45-1-1-1zm-9-5h2v2h-2V2zm4 0h2v2h-2V2zm-8 0h2v2H7V2z"/></svg>
              </div>
              <div>
                <span class="inq-info-label">요청 수량</span>
                <strong class="inq-info-value">{{ getQuantity(inquiry) || "미입력" }}</strong>
              </div>
            </div>
            <div class="inq-info-item">
              <div class="inq-info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20 3h-1V1h-2v2H7V1H5v2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H4V8h16v13z"/></svg>
              </div>
              <div>
                <span class="inq-info-label">희망 납기</span>
                <strong class="inq-info-value">{{ inquiry.desiredDate || "미입력" }}</strong>
              </div>
            </div>
            <div class="inq-info-item">
              <div class="inq-info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
              </div>
              <div>
                <span class="inq-info-label">현장 위치</span>
                <strong class="inq-info-value">{{ getSiteAddress(inquiry) || "미입력" }}</strong>
              </div>
            </div>
          </div>

          <div class="inq-requester-row">
            <div class="inq-requester-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
              <span>요청자</span>
              <strong>{{ getRequesterName(inquiry) || "미입력" }}</strong>
            </div>
            <div class="inq-requester-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/></svg>
              <span>요청 일시</span>
              <strong>{{ formatDate(inquiry.createdAt) }}</strong>
            </div>
          </div>

          <p v-if="inquiry.message" class="inq-message">{{ inquiry.message }}</p>

          <div class="inquiry-footer supplier-footer">
            <label class="status-select-wrap" @click.stop>
              <span class="status-select-label">현재 상태</span>
              <div class="status-select-box">
                <select
                  :value="getSelectStatus(inquiry.status)"
                  :disabled="updatingInquiryId === inquiry.id"
                  @change="changeInquiryStatus(inquiry.id, $event.target.value)"
                >
                  <option value="pending">협의 필요</option>
                  <option value="accepted">납품 가능</option>
                  <option value="rejected">거절</option>
                </select>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" class="select-chevron"><path d="M7 10l5 5 5-5z"/></svg>
              </div>
            </label>
            <RouterLink class="btn-card-detail" :to="`/inquiries/${inquiry.id}`" @click.stop>상세 보기</RouterLink>
            <button
              type="button"
              class="btn-card-delete"
              :disabled="deletingInquiryId === inquiry.id"
              @click.stop="deleteInquiryForSupplier(inquiry.id)"
            >
              {{ deletingInquiryId === inquiry.id ? "삭제 중" : "삭제" }}
            </button>
          </div>
        </template>

        <!-- ── 요청자 뷰 ── -->
        <template v-else>
          <!-- 상단: ID 뱃지 + 상태 + 날짜 -->
          <div class="card-topline">
            <span class="inq-id-badge rq">{{ displayedInquiries.length - index }}</span>
            <span :class="['status-badge', inquiry.status]">{{ getStatusLabel(inquiry.status) }}</span>
            <span class="inq-time">{{ formatDate(inquiry.createdAt) }}</span>
          </div>

          <!-- 공급사 이름 + 자재 -->
          <h2 class="inq-title">{{ inquiry.supplier?.supplierName || "공급사 미지정" }}</h2>
          <p class="inq-subtitle">
            {{ inquiry.supplier?.materialName || getMaterialName(inquiry) }}<template v-if="inquiry.supplier?.standard || getMaterialStandard(inquiry)"> · {{ inquiry.supplier?.standard || getMaterialStandard(inquiry) }}</template>
          </p>

          <!-- 상태 타임라인 -->
          <div class="inq-timeline">
            <template v-for="(step, i) in inquirySteps" :key="step.key">
              <div class="tl-step">
                <div :class="['tl-circle', getStepState(inquiry.status, i)]">
                  <template v-if="getStepState(inquiry.status, i) === 'done'">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </template>
                  <template v-else-if="getStepState(inquiry.status, i) === 'active' && i === 0">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
                  </template>
                  <template v-else-if="getStepState(inquiry.status, i) === 'active' && i === 1">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                  </template>
                  <template v-else-if="getStepState(inquiry.status, i) === 'active' && i === 2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                  </template>
                  <template v-else-if="getStepState(inquiry.status, i) === 'rejected'">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                  </template>
                  <template v-else>
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                  </template>
                </div>
                <span :class="['tl-label', { 'tl-label-active': ['active','rejected'].includes(getStepState(inquiry.status, i)) }]">{{ step.label }}</span>
                <span class="tl-date">{{ getStepDate(inquiry, i) }}</span>
              </div>
              <div v-if="i < inquirySteps.length - 1" :class="['tl-connector', { filled: getStepState(inquiry.status, i) === 'done' }]" />
            </template>
          </div>

          <!-- 2×2 정보 그리드 -->
          <div class="inq-info-grid inq-info-grid-2x2">
            <div class="inq-info-item">
              <div class="inq-info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20 7H4c-.55 0-1 .45-1 1v8c0 .55.45 1 1 1h16c.55 0 1-.45 1-1V8c0-.55-.45-1-1-1zm-9-5h2v2h-2V2zm4 0h2v2h-2V2zm-8 0h2v2H7V2z"/></svg>
              </div>
              <div>
                <span class="inq-info-label">문의 수량</span>
                <strong class="inq-info-value">{{ getQuantity(inquiry) || "미입력" }}</strong>
              </div>
            </div>
            <div class="inq-info-item">
              <div class="inq-info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
              </div>
              <div>
                <span class="inq-info-label">담당자</span>
                <strong class="inq-info-value">{{ inquiry.requesterName || "미입력" }}</strong>
              </div>
            </div>
            <div class="inq-info-item">
              <div class="inq-info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20 3h-1V1h-2v2H7V1H5v2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H4V8h16v13z"/></svg>
              </div>
              <div>
                <span class="inq-info-label">희망 납기</span>
                <strong class="inq-info-value">{{ inquiry.desiredDate || "미입력" }}</strong>
              </div>
            </div>
            <div class="inq-info-item">
              <div class="inq-info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
              </div>
              <div>
                <span class="inq-info-label">연락처</span>
                <strong class="inq-info-value">{{ inquiry.contact || "미입력" }}</strong>
              </div>
            </div>
          </div>

          <!-- 요청 메모 -->
          <div v-if="inquiry.message" class="inq-memo-card">
            <p class="inq-memo-text">{{ inquiry.message }}</p>
          </div>

          <!-- 공급사 정보 -->
          <div class="inq-supplier-info-row">
            <div class="inq-supplier-left">
              <div class="inq-supplier-icon-box">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3L2 12h3v8h6v-5h2v5h6v-8h3L12 3z"/></svg>
              </div>
              <div class="inq-supplier-text">
                <span class="inq-supplier-name-val">{{ inquiry.supplier?.supplierName || "공급사 미지정" }}</span>
                <div class="inq-supplier-tags">
                  <span v-if="inquiry.supplier?.deliveryCount" class="supplier-tag">최근 납품 {{ inquiry.supplier.deliveryCount }}건</span>
                  <span v-if="getSupplierDistance(inquiry)" class="supplier-tag">거리 {{ getSupplierDistance(inquiry) }}</span>
                </div>
              </div>
            </div>
            <button type="button" class="btn-supplier-detail" @click.stop="openInquiry(inquiry.id)">공급사 상세 보기</button>
          </div>

          <!-- 하단 푸터 -->
          <div class="supplier-footer requester-footer">
            <div class="rq-footer-status">
              <span>상태 변경</span><br>
              <span>{{ formatDate(inquiry.statusUpdatedAt || inquiry.createdAt) }} ({{ getStatusLabel(inquiry.status) }})</span>
            </div>
            <RouterLink class="btn-detail-outline" :to="`/inquiries/${inquiry.id}`" @click.stop>상세 보기</RouterLink>
          </div>
        </template>
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

    <template v-if="activeTab === 'community'">
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
  hideSupplierInquiryForSupplier,
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
const deletingInquiryId = ref("");
const inquiryStatusFilter = ref("all");
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
const inquiryStatusFilters = [
  { value: "all", label: "전체", statuses: [] },
  { value: "waiting", label: "협의 필요", statuses: ["received", "pending", "reviewing"] },
  { value: "available", label: "납품 가능", statuses: ["quoted", "accepted"] },
  { value: "rejected", label: "거절", statuses: ["rejected", "unavailable"] },
];
const supplierActionStatuses = [
  { value: "pending", label: "협의 필요" },
  { value: "accepted", label: "납품 가능" },
  { value: "rejected", label: "거절" },
];

const dashboardTitle = computed(() =>
  authState.user?.role === "supplier" ? "문의 현황" : "내 문의 내역",
);

const isSupplier = computed(() => authState.user?.role === "supplier");
const dashboardDescription = computed(() =>
  isSupplier.value
    ? "받은 자재 문의와 커뮤니티 대화 요청을 구분해 확인하고 관리합니다."
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
  const latest = roleInquiries.value[0];
  return latest ? formatDate(latest.createdAt) : "없음";
});

onMounted(() => {
  loadInquiries();
  loadCommunityRequests();
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

async function deleteInquiryForSupplier(inquiryId) {
  const confirmed = window.confirm(
    "이 문의를 삭제하시겠습니까?\n공급자 화면에서만 삭제되며, 요청자 문의 내역은 유지됩니다.",
  );
  if (!confirmed) return;

  try {
    deletingInquiryId.value = inquiryId;
    errorMessage.value = "";
    await hideSupplierInquiryForSupplier(inquiryId);
    inquiries.value = inquiries.value.filter((inquiry) => inquiry.id !== inquiryId);
    window.alert("문의가 삭제되었습니다.");
  } catch {
    errorMessage.value = "문의 삭제에 실패했습니다.";
  } finally {
    deletingInquiryId.value = "";
  }
}

async function loadInquiries() {
  try {
    isLoading.value = true;
    errorMessage.value = "";
    inquiries.value = await getSupplierInquiries();
  } catch {
    errorMessage.value = "문의 내역을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.";
  } finally {
    isLoading.value = false;
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

function getSelectStatus(status) {
  if (["received", "pending", "reviewing"].includes(status)) return "pending";
  if (["quoted", "accepted"].includes(status)) return "accepted";
  if (["rejected", "unavailable"].includes(status)) return "rejected";
  return "pending";
}

const inquirySteps = [
  { key: "received", label: "문의 접수" },
  { key: "reviewing", label: "검토 중" },
  { key: "available", label: "견적 가능" },
  { key: "rejected", label: "거절" },
];

function getInquiryCurrentStep(status) {
  if (["received", "pending"].includes(status)) return 0;
  if (status === "reviewing") return 1;
  if (["quoted", "accepted"].includes(status)) return 2;
  if (["rejected", "unavailable"].includes(status)) return 3;
  return 0;
}

function getStepState(status, i) {
  const current = getInquiryCurrentStep(status);
  const isRejected = ["rejected", "unavailable"].includes(status);
  if (i < current) {
    if (isRejected && i === 2) return "pending";
    return "done";
  }
  if (i === current) return isRejected ? "rejected" : "active";
  return "pending";
}

function getStepDate(inquiry, stepIndex) {
  if (stepIndex === 0) return formatShortDate(inquiry.createdAt);
  return "-";
}

function formatShortDate(value) {
  if (!value) return "-";
  const d = new Date(value);
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${mm}.${dd} ${hh}:${min}`;
}

function getSupplierDistance(inquiry) {
  const dm = Number(inquiry.supplier?.routeDistanceM);
  if (Number.isFinite(dm) && dm > 0) return `${(dm / 1000).toFixed(1)}km`;
  return null;
}
</script>

<style scoped>
.supplier-status-filters{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 22px}.supplier-status-filters button{border:1px solid #d7e3f5;border-radius:999px;padding:9px 14px;color:#51627e;background:#fff;font-weight:800;cursor:pointer}.supplier-status-filters button.active{border-color:#1559e8;color:#1559e8;background:#edf4ff}.supplier-request-details dd{overflow-wrap:anywhere}
/* 공급사 카드 */
.supplier-card { cursor: default; }
.inq-id-badge { display:inline-flex;align-items:center;padding:4px 12px;border-radius:99px;background:#1559e8;color:#fff;font-size:12px;font-weight:800;font-family:ui-monospace,monospace;letter-spacing:.02em; }
.status-badge.received,.status-badge.pending,.status-badge.reviewing { background:#eef4ff;color:#1d4ed8;border-radius:99px;padding:4px 12px;font-size:12px;font-weight:800; }
.status-badge.quoted,.status-badge.accepted { background:#dcf8ed;color:#047857;border-radius:99px;padding:4px 12px;font-size:12px;font-weight:800; }
.status-badge.rejected,.status-badge.unavailable { background:#fee7e7;color:#b42318;border-radius:99px;padding:4px 12px;font-size:12px;font-weight:800; }
.inq-time { margin-left:auto;font-size:13px;color:#8492a8; }
.inq-title { font-size:20px;font-weight:900;color:#102a56;margin:14px 0 12px; }
.inq-info-grid { display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px; }
.inq-info-item { display:flex;align-items:center;gap:12px;background:#f5f8fd;border-radius:12px;padding:12px 14px; }
.inq-info-icon { display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:9px;background:#e8eef9;color:#1559e8;flex-shrink:0; }
.inq-info-label { display:block;font-size:11px;color:#8492a8;font-weight:600;margin-bottom:3px; }
.inq-info-value { display:block;font-size:14px;font-weight:800;color:#102a56;word-break:break-all; }
.inq-requester-row { display:flex;gap:24px;margin-bottom:10px;padding:8px 0; }
.inq-requester-item { display:flex;align-items:center;gap:6px;font-size:13px; }
.inq-requester-item svg { color:#94a3b8;flex-shrink:0; }
.inq-requester-item span { color:#8492a8; }
.inq-requester-item strong { color:#102a56;font-weight:700;margin-left:2px; }
.inq-message { font-size:14px;color:#51627e;margin:4px 0 0;padding:10px 14px;background:#f8f9fb;border-radius:8px; }
.supplier-footer { display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:16px;padding-top:14px;border-top:1px solid #eef2f8; }
.status-select-wrap { display:flex;align-items:center;gap:10px; }
.status-select-label { font-size:13px;font-weight:700;color:#65748d; }
.status-select-box { position:relative;display:flex;align-items:center; }
.status-select-box select { appearance:none;-webkit-appearance:none;border:1.5px solid #d7e3f5;border-radius:10px;padding:8px 36px 8px 14px;font-size:14px;font-weight:700;color:#1559e8;background:#edf4ff;cursor:pointer;min-width:110px; }
.status-select-box select:disabled { opacity:.6;cursor:default; }
.select-chevron { position:absolute;right:10px;pointer-events:none;color:#1559e8; }
.btn-card-detail { display:inline-flex;align-items:center;justify-content:center;padding:10px 24px;border-radius:10px;background:#1559e8;color:#fff;font-size:14px;font-weight:800;text-decoration:none; }
.btn-card-detail:hover { opacity:.88; }
.supplier-card .btn-card-detail { margin-left:auto; }
.btn-card-delete { display:inline-flex;align-items:center;justify-content:center;border:1px solid #fecaca;border-radius:10px;padding:10px 18px;color:#dc2626;background:#fff5f5;font-size:14px;font-weight:900;cursor:pointer;transition:background .15s,border-color .15s,opacity .15s; }
.btn-card-delete:hover { border-color:#fca5a5;background:#fee2e2; }
.btn-card-delete:disabled { cursor:default;opacity:.6; }
@media(max-width:700px){.inq-info-grid{grid-template-columns:1fr}.inq-requester-row{flex-direction:column;gap:8px}}
/* ── 요청자 카드 ── */
.inq-id-badge.rq { background:#1559e8; }
.inq-subtitle { font-size:13px;color:#8492a8;margin:-10px 0 14px;font-weight:500; }
/* 타임라인 */
.inq-timeline { display:flex;align-items:flex-start;margin:16px 0 18px; }
.tl-step { display:flex;flex-direction:column;align-items:center;gap:5px;min-width:64px; }
.tl-circle { width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0; }
.tl-circle.done { background:#1559e8; }
.tl-circle.active { background:#fff;border:2.5px solid #1559e8;color:#1559e8; }
.tl-circle.rejected { background:#ef4444;color:#fff; }
.tl-circle.pending { background:#e9eef6;color:#94a3b8; }
.tl-label { font-size:11px;font-weight:700;color:#8492a8;text-align:center;white-space:nowrap; }
.tl-label-active { color:#1559e8;font-weight:900; }
.tl-date { font-size:10px;color:#b0bac9;text-align:center;white-space:nowrap; }
.tl-connector { flex:1;height:2px;background:#e2e8f0;margin-top:17px;align-self:flex-start; }
.tl-connector.filled { background:#1559e8; }
/* 2×2 그리드 */
.inq-info-grid-2x2 { grid-template-columns:repeat(2,1fr) !important; }
/* 요청 메모 */
.inq-memo-card { border-radius:10px;padding:10px 14px;background:#f5f8fd;border:1px solid #e8eef9;margin-bottom:14px; }
.inq-memo-text { font-size:14px;color:#40506a;line-height:1.65;margin:0; }
/* 공급사 정보 */
.inq-supplier-info-row { display:flex;align-items:center;justify-content:space-between;gap:12px;background:#f5f8fd;border-radius:14px;padding:13px 15px;margin-bottom:4px; }
.inq-supplier-left { display:flex;align-items:center;gap:12px;min-width:0;flex:1; }
.inq-supplier-icon-box { display:flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:10px;background:#e8eef9;color:#1559e8;flex-shrink:0; }
.inq-supplier-text { display:flex;flex-direction:column;gap:5px;min-width:0; }
.inq-supplier-name-val { font-size:15px;font-weight:800;color:#102a56; }
.inq-supplier-tags { display:flex;flex-wrap:wrap;gap:6px; }
.supplier-tag { display:inline-flex;padding:3px 10px;border-radius:99px;background:#eef4ff;color:#1559e8;font-size:11px;font-weight:700; }
.btn-supplier-detail { flex-shrink:0;border:1.5px solid #1559e8;border-radius:10px;padding:9px 14px;background:#fff;color:#1559e8;font-size:13px;font-weight:800;cursor:pointer;white-space:nowrap; }
.btn-supplier-detail:hover { background:#edf4ff; }
/* 요청자 하단 */
.requester-footer { align-items:center; }
.rq-footer-status { font-size:12px;color:#8492a8;line-height:1.7; }
.rq-footer-status>span:first-child { font-weight:700;color:#65748d; }
.btn-detail-outline { display:inline-flex;align-items:center;justify-content:center;padding:10px 22px;border-radius:10px;background:#1559e8;color:#fff;font-size:14px;font-weight:800;text-decoration:none;white-space:nowrap; }
.btn-detail-outline:hover { opacity:.88; }
@media(max-width:700px){.inq-info-grid-2x2{grid-template-columns:1fr !important}.inq-supplier-info-row{flex-direction:column;align-items:flex-start}.btn-supplier-detail{align-self:stretch;text-align:center}}
.inquiry-type-tabs{display:flex;gap:8px;margin:22px 0}.inquiry-type-tabs button{border:1px solid #d7e3f5;border-radius:999px;padding:11px 17px;color:#51627e;background:#fff;font-weight:900;cursor:pointer}.inquiry-type-tabs button.active{border-color:#1559e8;color:#fff;background:#1559e8}.community-request-list{display:grid;gap:14px}.community-request-card{border:1px solid #dbe6f8;border-radius:22px;padding:22px;background:#fff;box-shadow:0 14px 40px rgba(31,61,115,.08)}.community-request-topline,.community-request-card footer{display:flex;align-items:center;justify-content:space-between;gap:12px}.community-request-topline>span:first-child{color:#1559e8;font-size:12px;font-weight:900}.community-request-status{border-radius:999px;padding:6px 10px;font-size:12px;font-weight:900}.community-request-status.pending{color:#9a5b00;background:#fff2cc}.community-request-status.confirmed{color:#047857;background:#dcf8ed}.community-request-status.rejected{color:#b42318;background:#fee7e7}.community-request-card h2{margin:14px 0 7px;color:#102a56;font-size:20px}.community-request-target{color:#65748d;font-size:13px}.community-request-message{border-radius:14px;padding:14px;color:#40506a;background:#f5f8fd;line-height:1.6}.community-request-card footer{margin-top:14px;color:#8492a8;font-size:12px}.community-request-card footer>a{color:#1559e8;font-weight:900}.community-request-actions{display:flex;gap:7px;margin-left:auto}.community-request-actions button{border:0;border-radius:9px;padding:8px 10px;color:#fff;background:#1559e8;cursor:pointer;font-weight:800}.community-request-actions .reject{color:#b42318;background:#fee7e7}@media(max-width:650px){.community-request-card footer{align-items:flex-start;flex-direction:column}.community-request-actions{margin-left:0}}
</style>
