<template>
  <section class="page-wrap">
    <div class="page-heading dashboard-heading">
      <div>
        <p class="eyebrow">Dashboard</p>
        <h1>{{ dashboardTitle }}</h1>
        <p>
          추천 결과에서 저장한 공급사 문의를 확인하고, 견적 가능 여부와 후속 상태를
          역할별로 관리합니다.
        </p>
      </div>
      <RouterLink class="primary-button" to="/recommendations">추천 결과로 이동</RouterLink>
    </div>

    <div class="dashboard-stats">
      <article>
        <span>저장된 문의</span>
        <strong>{{ inquiries.length }}건</strong>
      </article>
      <article>
        <span>감리 승인 확인</span>
        <strong>{{ approvalCount }}건</strong>
      </article>
      <article>
        <span>긴급 요청</span>
        <strong>{{ urgentCount }}건</strong>
      </article>
      <article>
        <span>견적 가능</span>
        <strong>{{ quotedCount }}건</strong>
      </article>
    </div>

    <p v-if="isLoading" class="loading-message">문의 내역을 불러오는 중입니다.</p>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <div v-if="!isLoading && inquiries.length" class="inquiry-list">
      <article v-for="inquiry in inquiries" :key="inquiry.id" class="inquiry-card">
        <div class="card-topline">
          <span class="rank-badge">{{ inquiry.id }}</span>
          <span :class="['status-badge', inquiry.status]">
            {{ getStatusLabel(inquiry.status) }}
          </span>
          <span :class="['approval-badge', { warn: inquiry.supplier?.approvalRequired }]">
            {{ inquiry.supplier?.approvalRequired ? "승인 확인 필요" : "일반 문의" }}
          </span>
          <span v-if="isUrgentInquiry(inquiry)" class="urgent-badge">긴급 납품 요청</span>
        </div>

        <div class="inquiry-card-header">
          <div>
            <h2>{{ inquiry.supplier?.supplierName || "공급사 미지정" }}</h2>
            <p class="material-line">
              {{ inquiry.supplier?.materialName || "자재 미지정" }}
              <span v-if="inquiry.supplier?.standard">· {{ inquiry.supplier.standard }}</span>
            </p>
          </div>
          <span class="inquiry-date">{{ formatDate(inquiry.createdAt) }}</span>
        </div>

        <dl class="score-list">
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

        <div v-if="isUrgentInquiry(inquiry)" class="urgent-request-note">
          <strong>우선 확인 필요</strong>
          <span>재고 보유 여부, 최종 단가, 가능한 납품 시간을 빠르게 확인해야 하는 요청입니다.</span>
        </div>

        <div class="inquiry-footer">
          <span>상태 변경: {{ formatDate(inquiry.statusUpdatedAt) }}</span>
          <div v-if="isSupplier" class="status-actions" aria-label="문의 상태 변경">
            <button
              v-for="status in inquiryStatuses"
              :key="status.value"
              type="button"
              :class="['status-action', { active: inquiry.status === status.value }]"
              :disabled="updatingInquiryId === inquiry.id"
              @click="changeInquiryStatus(inquiry.id, status.value)"
            >
              {{ status.label }}
            </button>
          </div>
          <RouterLink class="secondary-button" :to="`/dashboard/${inquiry.id}`">
            상세 보기
          </RouterLink>
        </div>
      </article>
    </div>

    <div v-else-if="!isLoading" class="empty-state">
      <strong>아직 저장된 문의가 없습니다.</strong>
      <p>추천 결과에서 공급사 후보의 문의하기 버튼을 눌러 첫 문의를 저장해보세요.</p>
      <RouterLink class="primary-button" to="/recommendations">추천 결과 확인하기</RouterLink>
    </div>
  </section>
      <StandardEvidencePanel />
</template>

<script setup>
import StandardEvidencePanel from '../components/StandardEvidencePanel.vue'
import { computed, onMounted, ref } from "vue";
import { authState } from "../api/authApi";
import { getSupplierInquiries, updateSupplierInquiryStatus } from "../api/materialApi";

const inquiries = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");
const updatingInquiryId = ref("");
const inquiryStatuses = [
  { value: "received", label: "문의 접수" },
  { value: "reviewing", label: "확인 중" },
  { value: "quoted", label: "견적 가능" },
  { value: "unavailable", label: "불가" },
];

const dashboardTitle = computed(() =>
  authState.user?.role === "supplier" ? "공급사 문의 내역" : "내 문의 내역",
);

const isSupplier = computed(() => authState.user?.role === "supplier");

const approvalCount = computed(
  () => inquiries.value.filter((inquiry) => inquiry.supplier?.approvalRequired).length,
);

const quotedCount = computed(
  () => inquiries.value.filter((inquiry) => inquiry.status === "quoted").length,
);

const urgentCount = computed(
  () => inquiries.value.filter((inquiry) => isUrgentInquiry(inquiry)).length,
);

const latestInquiryLabel = computed(() => {
  const latest = inquiries.value[0];
  return latest ? formatDate(latest.createdAt) : "없음";
});

onMounted(loadInquiries);

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
  return inquiryStatuses.find((item) => item.value === status)?.label || "문의 접수";
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
