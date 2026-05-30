<template>
  <section class="page-wrap">
    <div class="page-heading dashboard-heading">
      <div>
        <p class="eyebrow">Dashboard</p>
        <h1>{{ dashboardTitle }}</h1>
        <p>
          추천 결과에서 저장한 공급사 문의를 확인합니다. 실제 전송과 상태 변경은
          백엔드 API 연결 이후 확장할 수 있습니다.
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
        <span>최근 문의</span>
        <strong>{{ latestInquiryLabel }}</strong>
      </article>
      <article>
        <span>견적 가능</span>
        <strong>{{ quotedCount }}건</strong>
      </article>
    </div>

    <div v-if="inquiries.length" class="inquiry-list">
      <article v-for="inquiry in inquiries" :key="inquiry.id" class="inquiry-card">
        <div class="card-topline">
          <span class="rank-badge">{{ inquiry.id }}</span>
          <span :class="['status-badge', inquiry.status]">
            {{ getStatusLabel(inquiry.status) }}
          </span>
          <span :class="['approval-badge', { warn: inquiry.supplier?.approvalRequired }]">
            {{ inquiry.supplier?.approvalRequired ? "승인 확인 필요" : "일반 문의" }}
          </span>
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

        <div class="inquiry-footer">
          <span>상태 변경: {{ formatDate(inquiry.statusUpdatedAt) }}</span>
          <div v-if="isSupplier" class="status-actions" aria-label="문의 상태 변경">
            <button
              v-for="status in inquiryStatuses"
              :key="status.value"
              type="button"
              :class="['status-action', { active: inquiry.status === status.value }]"
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

    <div v-else class="empty-state">
      <strong>아직 저장된 문의가 없습니다.</strong>
      <p>추천 결과에서 공급사 후보의 문의하기 버튼을 눌러 첫 문의를 저장해보세요.</p>
      <RouterLink class="primary-button" to="/recommendations">추천 결과 확인하기</RouterLink>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { authState } from "../api/authApi";
import { getSupplierInquiries, updateSupplierInquiryStatus } from "../api/materialApi";

const inquiries = ref([]);
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

const latestInquiryLabel = computed(() => {
  const latest = inquiries.value[0];
  return latest ? formatDate(latest.createdAt) : "없음";
});

onMounted(async () => {
  inquiries.value = await getSupplierInquiries();
});

async function changeInquiryStatus(inquiryId, status) {
  const updatedInquiry = await updateSupplierInquiryStatus(inquiryId, status);
  if (!updatedInquiry) {
    return;
  }

  inquiries.value = inquiries.value.map((inquiry) =>
    inquiry.id === inquiryId ? updatedInquiry : inquiry,
  );
}

function getStatusLabel(status) {
  return inquiryStatuses.find((item) => item.value === status)?.label || "문의 접수";
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
