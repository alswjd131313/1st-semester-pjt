<template>
  <section class="page-wrap">
    <div class="page-heading dashboard-heading">
      <div>
        <p class="eyebrow">Inquiry Detail</p>
        <h1>문의 상세</h1>
        <p>
          저장된 문의의 요청 정보, 공급사 후보, 상태를 한 화면에서 확인합니다.
        </p>
      </div>
      <RouterLink class="secondary-button" to="/dashboard">문의 내역으로</RouterLink>
    </div>

    <p v-if="isLoading" class="loading-message">문의 상세 정보를 불러오는 중입니다.</p>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <div v-if="!isLoading && inquiry" class="detail-page-grid">
      <section class="detail-page-card primary-detail">
        <div class="card-topline">
          <span class="rank-badge">{{ inquiry.id }}</span>
          <span :class="['status-badge', inquiry.status]">
            {{ getStatusLabel(inquiry.status) }}
          </span>
          <span :class="['approval-badge', { warn: inquiry.supplier?.approvalRequired }]">
            {{ inquiry.supplier?.approvalRequired ? "승인 확인 필요" : "일반 문의" }}
          </span>
        </div>

        <h2>{{ inquiry.supplier?.supplierName || "공급사 미지정" }}</h2>
        <p class="material-line">
          {{ inquiry.supplier?.materialName || "자재 미지정" }}
          <span v-if="inquiry.supplier?.standard">· {{ inquiry.supplier.standard }}</span>
        </p>

        <div class="detail-note">
          <h3>문의 메모</h3>
          <p>{{ inquiry.message || "별도 문의 메모가 없습니다." }}</p>
        </div>

        <div v-if="isSupplier" class="status-actions detail-status-actions">
          <button
            v-for="status in inquiryStatuses"
            :key="status.value"
            type="button"
            :class="['status-action', { active: inquiry.status === status.value }]"
            :disabled="isUpdating"
            @click="changeInquiryStatus(status.value)"
          >
            {{ status.label }}
          </button>
        </div>
      </section>

      <section class="detail-page-card">
        <h2>문의 정보</h2>
        <dl class="detail-list">
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
          <div>
            <dt>문의 생성</dt>
            <dd>{{ formatDate(inquiry.createdAt) }}</dd>
          </div>
          <div>
            <dt>상태 변경</dt>
            <dd>{{ formatDate(inquiry.statusUpdatedAt) }}</dd>
          </div>
        </dl>
      </section>

      <section class="detail-page-card">
        <h2>공급사 후보</h2>
        <dl class="detail-list">
          <div>
            <dt>최근 단가</dt>
            <dd>{{ inquiry.supplier?.price || "확인 필요" }}</dd>
          </div>
          <div>
            <dt>거리</dt>
            <dd>{{ inquiry.supplier?.distanceKm ?? "확인 필요" }}km</dd>
          </div>
          <div>
            <dt>납품 이력</dt>
            <dd>{{ inquiry.supplier?.deliveryCount ?? 0 }}회</dd>
          </div>
          <div>
            <dt>최종 점수</dt>
            <dd>{{ inquiry.supplier?.totalScore ?? "-" }}점</dd>
          </div>
          <div v-if="inquiry.supplier?.serviceArea">
            <dt>납품 가능 지역</dt>
            <dd>{{ inquiry.supplier.serviceArea }}</dd>
          </div>
        </dl>
      </section>

      <section class="detail-page-card">
        <h2>요청 자재</h2>
        <dl class="detail-list">
          <div>
            <dt>자재명</dt>
            <dd>{{ inquiry.requestMaterial?.materialName || "미입력" }}</dd>
          </div>
          <div>
            <dt>강도/규격</dt>
            <dd>{{ inquiry.requestMaterial?.strengthGrade || "미입력" }}</dd>
          </div>
          <div>
            <dt>현장 주소</dt>
            <dd>{{ inquiry.requestMaterial?.siteAddress || "미입력" }}</dd>
          </div>
          <div>
            <dt>필요 수량</dt>
            <dd>{{ inquiry.requestMaterial?.requiredQuantity || "미입력" }}</dd>
          </div>
        </dl>
      </section>
    </div>

    <div v-else-if="!isLoading" class="empty-state">
      <strong>문의 정보를 찾을 수 없습니다.</strong>
      <p>저장된 mock 문의가 없거나 브라우저 저장 데이터가 초기화되었을 수 있습니다.</p>
      <RouterLink class="primary-button" to="/dashboard">문의 내역으로 이동</RouterLink>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { authState } from "../api/authApi";
import { getSupplierInquiry, updateSupplierInquiryStatus } from "../api/materialApi";

const route = useRoute();
const inquiry = ref(null);
const isLoading = ref(false);
const isUpdating = ref(false);
const errorMessage = ref("");
const inquiryStatuses = [
  { value: "received", label: "문의 접수" },
  { value: "reviewing", label: "확인 중" },
  { value: "quoted", label: "견적 가능" },
  { value: "unavailable", label: "불가" },
];

const isSupplier = computed(() => authState.user?.role === "supplier");

onMounted(loadInquiry);

async function changeInquiryStatus(status) {
  try {
    isUpdating.value = true;
    errorMessage.value = "";
    const updatedInquiry = await updateSupplierInquiryStatus(inquiry.value.id, status);
    if (updatedInquiry) {
      inquiry.value = updatedInquiry;
    }
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
    inquiry.value = await getSupplierInquiry(route.params.inquiryId);
  } catch {
    errorMessage.value = "문의 상세 정보를 불러오지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

function getStatusLabel(status) {
  return inquiryStatuses.find((item) => item.value === status)?.label || "문의 접수";
}

function formatDate(value) {
  if (!value) {
    return "날짜 없음";
  }

  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
</script>
