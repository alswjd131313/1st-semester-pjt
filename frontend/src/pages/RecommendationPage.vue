<template>
  <section class="page-wrap">
    <div class="page-heading">
      <p class="eyebrow">Step 2</p>
      <h1>추천 결과</h1>
      <p>
        본 추천 결과는 자재 규격, 가격, 거리, 과거 납품 이력을 기반으로 산출됩니다.
        실제 재고와 납품 가능 여부는 공급사에 직접 문의해야 합니다.
      </p>
    </div>

    <div v-if="request" class="summary-card">
      <strong>{{ request.materialName }} {{ request.strengthGrade }}</strong>
      <span>현장 위치: {{ request.siteAddress || "미입력" }}</span>
      <span>필요 수량: {{ request.requiredQuantity || "미입력" }}</span>
      <span>{{ request.isUrgent ? "긴급 요청" : "일반 요청" }}</span>
    </div>

    <section class="recommendation-toolbar" aria-label="추천 결과 필터와 정렬">
      <div>
        <strong>{{ filteredRecommendations.length }}개 후보</strong>
        <span>{{ activeFilterLabel }}</span>
      </div>

      <label>
        정렬 기준
        <select v-model="sortOption">
          <option value="score">최종 점수 높은순</option>
          <option value="distance">거리 가까운순</option>
          <option value="price">단가 낮은순</option>
          <option value="delivery">납품 이력 많은순</option>
        </select>
      </label>

      <div class="filter-toggles">
        <label>
          <input v-model="hideApprovalRequired" type="checkbox" />
          감리 승인 필요 제외
        </label>
        <label>
          <input v-model="registeredOnly" type="checkbox" />
          등록 공급사만 보기
        </label>
      </div>

      <button type="button" class="secondary-button" @click="resetFilters">초기화</button>
    </section>

    <div class="recommendation-grid">
      <article
        v-for="(item, index) in filteredRecommendations"
        :key="`${item.supplierName}-${item.materialName}-${item.standard}`"
        class="recommendation-card"
      >
        <div class="card-topline">
          <span class="rank-badge">{{ index + 1 }}순위</span>
          <span v-if="item.isRegisteredSupplier" class="source-badge">등록 공급사</span>
          <span :class="['approval-badge', { warn: item.approvalRequired }]">
            {{ item.approvalRequired ? "감리 승인 필요" : "승인 리스크 낮음" }}
          </span>
        </div>

        <h2>{{ item.supplierName }}</h2>
        <p class="material-line">{{ item.materialName }} · {{ item.standard }}</p>

        <dl class="score-list">
          <div>
            <dt>최근 단가</dt>
            <dd>{{ item.price }}</dd>
          </div>
          <div>
            <dt>거리</dt>
            <dd>{{ item.distanceKm }}km</dd>
          </div>
          <div>
            <dt>납품 이력</dt>
            <dd>{{ item.deliveryCount }}회</dd>
          </div>
          <div>
            <dt>최종 점수</dt>
            <dd>{{ item.totalScore }}점</dd>
          </div>
        </dl>

        <div v-if="item.contact || item.serviceArea" class="supplier-meta">
          <span v-if="item.contact">연락처 {{ item.contact }}</span>
          <span v-if="item.serviceArea">납품 가능 {{ item.serviceArea }}</span>
        </div>

        <div class="score-bars">
          <span>가격 {{ item.priceScore }}</span>
          <span>거리 {{ item.distanceScore }}</span>
          <span>신뢰도 {{ item.reliabilityScore }}</span>
        </div>

        <p class="reason">{{ item.reason }}</p>

        <div class="card-actions">
          <button type="button" class="secondary-button" @click="openDetail(item)">상세 보기</button>
          <button type="button" class="primary-button" @click="openInquiry(item)">문의하기</button>
        </div>
      </article>
    </div>

    <div v-if="!filteredRecommendations.length" class="empty-state">
      <strong>조건에 맞는 추천 후보가 없습니다.</strong>
      <p>필터를 줄이거나 초기화한 뒤 다시 확인해보세요.</p>
      <button type="button" class="primary-button" @click="resetFilters">필터 초기화</button>
    </div>

    <Teleport to="body">
      <div
        v-if="selectedRecommendation"
        class="modal-backdrop"
        role="presentation"
        @click.self="closeDetail"
      >
        <section
          class="detail-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="recommendation-detail-title"
        >
          <div class="modal-header">
            <div>
              <p class="eyebrow">Recommendation Detail</p>
              <h2 id="recommendation-detail-title">
                {{ selectedRecommendation.supplierName }}
              </h2>
              <span>{{ selectedRecommendation.materialName }} · {{ selectedRecommendation.standard }}</span>
            </div>
            <button type="button" class="icon-button" aria-label="상세 닫기" @click="closeDetail">
              ×
            </button>
          </div>

          <div class="detail-score-panel">
            <div>
              <span>최종 점수</span>
              <strong>{{ selectedRecommendation.totalScore }}점</strong>
            </div>
            <p>
              가격, 거리, 과거 납품 이력을 기준으로 문의 우선순위를 산출했습니다.
            </p>
          </div>

          <div class="detail-grid">
            <article>
              <h3>공급 조건</h3>
              <dl class="detail-list">
                <div>
                  <dt>최근 단가</dt>
                  <dd>{{ selectedRecommendation.price }}</dd>
                </div>
                <div>
                  <dt>현장 거리</dt>
                  <dd>{{ selectedRecommendation.distanceKm }}km</dd>
                </div>
                <div>
                  <dt>납품 이력</dt>
                  <dd>{{ selectedRecommendation.deliveryCount }}회</dd>
                </div>
                <div v-if="selectedRecommendation.contact">
                  <dt>연락처</dt>
                  <dd>{{ selectedRecommendation.contact }}</dd>
                </div>
                <div v-if="selectedRecommendation.serviceArea">
                  <dt>납품 가능 지역</dt>
                  <dd>{{ selectedRecommendation.serviceArea }}</dd>
                </div>
              </dl>
            </article>

            <article>
              <h3>점수 분석</h3>
              <div class="score-breakdown">
                <div>
                  <span>가격 점수</span>
                  <strong>{{ selectedRecommendation.priceScore }}</strong>
                  <meter min="0" max="100" :value="selectedRecommendation.priceScore" />
                </div>
                <div>
                  <span>거리 점수</span>
                  <strong>{{ selectedRecommendation.distanceScore }}</strong>
                  <meter min="0" max="100" :value="selectedRecommendation.distanceScore" />
                </div>
                <div>
                  <span>신뢰도 점수</span>
                  <strong>{{ selectedRecommendation.reliabilityScore }}</strong>
                  <meter min="0" max="100" :value="selectedRecommendation.reliabilityScore" />
                </div>
              </div>
            </article>
          </div>

          <div class="detail-note">
            <h3>추천 이유</h3>
            <p>{{ selectedRecommendation.reason }}</p>
          </div>

          <div :class="['approval-note', { warn: selectedRecommendation.approvalRequired }]">
            <strong>
              {{ selectedRecommendation.approvalRequired ? "감리 승인 확인 필요" : "승인 리스크 낮음" }}
            </strong>
            <p>
              {{
                selectedRecommendation.approvalRequired
                  ? "국제 규격 또는 강도 상향 자재는 구조 검토와 감리 승인 여부를 확인해야 합니다."
                  : "동일 규격 기준으로 우선 검토 가능한 후보입니다. 최종 납품 가능 여부는 공급사 문의가 필요합니다."
              }}
            </p>
          </div>

          <div class="modal-actions">
            <button type="button" class="secondary-button" @click="closeDetail">닫기</button>
            <button type="button" class="primary-button" @click="openInquiry(selectedRecommendation)">
              문의하기
            </button>
          </div>
        </section>
      </div>
    </Teleport>

    <Teleport to="body">
      <div
        v-if="selectedInquirySupplier"
        class="modal-backdrop"
        role="presentation"
        @click.self="closeInquiry"
      >
        <section
          class="detail-modal inquiry-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="supplier-inquiry-title"
        >
          <div class="modal-header">
            <div>
              <p class="eyebrow">Supplier Inquiry</p>
              <h2 id="supplier-inquiry-title">공급사 문의하기</h2>
              <span>
                {{ selectedInquirySupplier.supplierName }} ·
                {{ selectedInquirySupplier.materialName }}
                {{ selectedInquirySupplier.standard }}
              </span>
            </div>
            <button type="button" class="icon-button" aria-label="문의 닫기" @click="closeInquiry">
              ×
            </button>
          </div>

          <div class="inquiry-summary">
            <strong>문의 전 확인</strong>
            <p>
              PaceFlow는 문의 우선순위를 추천합니다. 실제 재고, 견적, 납품 가능 여부는
              공급사 확인 후 확정됩니다.
            </p>
          </div>

          <form class="inquiry-form" @submit.prevent="submitInquiry">
            <label>
              담당자명
              <input v-model.trim="inquiryForm.requesterName" type="text" placeholder="예: 김현장" required />
            </label>
            <label>
              연락처
              <input v-model.trim="inquiryForm.contact" type="tel" placeholder="예: 010-1234-5678" required />
            </label>
            <label>
              문의 수량
              <input v-model.trim="inquiryForm.quantity" type="text" placeholder="예: 50톤" required />
            </label>
            <label>
              희망 납기
              <input v-model="inquiryForm.desiredDate" type="date" />
            </label>
            <label class="full-field">
              문의 메모
              <textarea
                v-model.trim="inquiryForm.message"
                rows="4"
                placeholder="현장 조건, 하차 가능 시간, 대체 가능 범위 등을 남겨주세요."
              />
            </label>

            <p v-if="inquiryStatus" class="success-message">{{ inquiryStatus }}</p>

            <div class="modal-actions full-field">
              <button type="button" class="secondary-button" @click="closeInquiry">취소</button>
              <button type="submit" class="primary-button">문의 저장하기</button>
            </div>
          </form>
        </section>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import {
  createSupplierInquiry,
  getLatestMaterialRequest,
  getRecommendations,
} from "../api/materialApi";

const route = useRoute();
const request = ref(null);
const recommendations = ref([]);
const selectedRecommendation = ref(null);
const selectedInquirySupplier = ref(null);
const inquiryStatus = ref("");
const sortOption = ref("score");
const hideApprovalRequired = ref(false);
const registeredOnly = ref(false);
const inquiryForm = reactive({
  requesterName: "",
  contact: "",
  quantity: "",
  desiredDate: "",
  message: "",
});

onMounted(async () => {
  request.value = await getLatestMaterialRequest();
  recommendations.value = await getRecommendations(route.query.requestId);
});

const filteredRecommendations = computed(() => {
  return recommendations.value
    .filter((item) => !hideApprovalRequired.value || !item.approvalRequired)
    .filter((item) => !registeredOnly.value || item.isRegisteredSupplier)
    .slice()
    .sort((a, b) => compareRecommendations(a, b));
});

const activeFilterLabel = computed(() => {
  const filters = [];

  if (hideApprovalRequired.value) {
    filters.push("승인 리스크 제외");
  }

  if (registeredOnly.value) {
    filters.push("등록 공급사");
  }

  return filters.length ? filters.join(" · ") : "전체 후보를 표시 중입니다.";
});

function compareRecommendations(a, b) {
  if (sortOption.value === "distance") {
    return Number(a.distanceKm) - Number(b.distanceKm);
  }

  if (sortOption.value === "price") {
    return parsePrice(a.price) - parsePrice(b.price);
  }

  if (sortOption.value === "delivery") {
    return Number(b.deliveryCount || 0) - Number(a.deliveryCount || 0);
  }

  return Number(b.totalScore || 0) - Number(a.totalScore || 0);
}

function parsePrice(value) {
  const price = Number(String(value).replace(/[^\d.]/g, ""));
  return Number.isFinite(price) && price > 0 ? price : Number.MAX_SAFE_INTEGER;
}

function resetFilters() {
  sortOption.value = "score";
  hideApprovalRequired.value = false;
  registeredOnly.value = false;
}

function openDetail(item) {
  selectedRecommendation.value = item;
}

function closeDetail() {
  selectedRecommendation.value = null;
}

function openInquiry(item) {
  selectedInquirySupplier.value = item;
  inquiryStatus.value = "";
  inquiryForm.quantity = request.value?.requiredQuantity || "";
  selectedRecommendation.value = null;
}

function closeInquiry() {
  selectedInquirySupplier.value = null;
  inquiryStatus.value = "";
}

async function submitInquiry() {
  const inquiry = await createSupplierInquiry({
    requestId: route.query.requestId,
    requestMaterial: request.value,
    supplier: selectedInquirySupplier.value,
    requesterName: inquiryForm.requesterName,
    contact: inquiryForm.contact,
    quantity: inquiryForm.quantity,
    desiredDate: inquiryForm.desiredDate,
    message: inquiryForm.message,
  });

  inquiryStatus.value = `${inquiry.id} 문의가 임시 저장되었습니다. 실제 전송 API가 연결되면 이 흐름을 그대로 사용할 수 있습니다.`;
  inquiryForm.message = "";
}
</script>
