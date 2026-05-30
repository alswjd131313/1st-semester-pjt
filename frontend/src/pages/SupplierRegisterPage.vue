<template>
  <section class="page-wrap">
    <div class="page-heading">
      <p class="eyebrow">Supplier</p>
      <h1>공급사 등록</h1>
      <p>회사 정보와 취급 자재를 등록하면 추천 결과의 공급사 후보로 노출됩니다.</p>
    </div>

    <section v-if="isRegistrationComplete" class="completion-card">
      <span class="completion-mark">완료</span>
      <h2>공급사 자재 등록이 완료되었습니다.</h2>
      <p>
        등록한 자재는 추천 결과 후보에 반영됩니다. 실제 노출 여부와 문의 가능 여부는
        백엔드 API 연결 이후 더 정확하게 관리할 수 있습니다.
      </p>
      <div class="completion-summary">
        <strong>{{ completedMaterial?.materialName }}</strong>
        <span>{{ completedMaterial?.supplierName }} · {{ completedMaterial?.serviceArea }}</span>
      </div>
      <div class="form-actions">
        <button type="button" class="secondary-button" @click="startNewRegistration">
          추가 등록하기
        </button>
        <RouterLink class="primary-button" to="/recommendations">추천 결과 확인하기</RouterLink>
      </div>
    </section>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="isLoading" class="loading-message">등록된 자재를 불러오는 중입니다.</p>

    <form v-if="!isRegistrationComplete" class="request-form" @submit.prevent="submitSupplier">
      <label>
        공급사명
        <input v-model="form.supplierName" type="text" placeholder="성수철강" required />
      </label>

      <label>
        연락처
        <input v-model="form.contact" type="tel" placeholder="02-1234-5678" required />
      </label>

      <label class="full-field">
        주소
        <input v-model="form.address" type="text" placeholder="서울 성동구 아차산로 123" required />
      </label>

      <label>
        주요 취급 자재
        <input v-model="form.mainMaterials" type="text" placeholder="철근, H빔, 강관" required />
      </label>

      <label>
        자재명
        <input v-model="form.materialName" type="text" placeholder="철근 SD400 D10" required />
      </label>

      <label>
        KS 규격
        <input v-model="form.standard" type="text" placeholder="KS D 3504" required />
      </label>

      <label>
        강도 등급
        <input v-model="form.strengthGrade" type="text" placeholder="SD400 / D10" required />
      </label>

      <label>
        최근 단가
        <input v-model.number="form.recentPrice" type="number" min="0" placeholder="785000" required />
      </label>

      <label>
        납품 가능 지역
        <input v-model="form.serviceArea" type="text" placeholder="서울, 경기 동부" required />
      </label>

      <label>
        현장 기준 거리(km)
        <input v-model.number="form.distanceKm" type="number" min="0" step="0.1" placeholder="3.2" />
      </label>

      <label>
        과거 납품 횟수
        <input v-model.number="form.deliveryCount" type="number" min="0" placeholder="42" required />
      </label>

      <label class="full-field">
        비고
        <textarea
          v-model="form.note"
          rows="4"
          placeholder="납품 가능 시간, 최소 발주 수량, 특이 조건을 적어주세요."
        />
      </label>

      <div class="form-actions">
        <RouterLink class="secondary-button" to="/">메인으로</RouterLink>
        <button type="submit" class="primary-button" :disabled="isSubmitting">
          {{ isSubmitting ? "등록 중" : "공급사 정보 등록하기" }}
        </button>
      </div>
    </form>

    <section v-if="registeredMaterials.length" class="registered-section">
      <div class="section-title-row">
        <h2>등록된 취급 자재</h2>
        <span>{{ registeredMaterials.length }}개</span>
      </div>

      <div class="registered-grid">
        <article v-for="item in registeredMaterials" :key="item.id" class="registered-card">
          <strong>{{ item.materialName }}</strong>
          <p>{{ item.standard }} · {{ item.strengthGrade }}</p>
          <span>{{ item.supplierName }} · {{ item.serviceArea }}</span>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { authState } from "../api/authApi";
import { getSupplierMaterials, registerSupplierMaterial } from "../api/materialApi";

const registeredMaterials = ref([]);
const isRegistrationComplete = ref(false);
const completedMaterial = ref(null);
const isLoading = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref("");

const form = reactive({
  supplierName: authState.user?.companyName || "",
  contact: "",
  address: "",
  mainMaterials: "",
  materialName: "",
  standard: "",
  strengthGrade: "",
  recentPrice: "",
  serviceArea: "",
  distanceKm: "",
  deliveryCount: "",
  note: "",
});

onMounted(loadSupplierMaterials);

async function submitSupplier() {
  try {
    isSubmitting.value = true;
    errorMessage.value = "";
    const saved = await registerSupplierMaterial({ ...form });
    completedMaterial.value = saved;
    isRegistrationComplete.value = true;
    await loadSupplierMaterials();
    resetForm();
  } catch {
    errorMessage.value = "공급사 자재 정보를 등록하지 못했습니다. 입력값을 확인한 뒤 다시 시도해주세요.";
  } finally {
    isSubmitting.value = false;
  }
}

async function loadSupplierMaterials() {
  try {
    isLoading.value = true;
    errorMessage.value = "";
    registeredMaterials.value = await getSupplierMaterials();
  } catch {
    errorMessage.value = "등록된 자재 목록을 불러오지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

function startNewRegistration() {
  isRegistrationComplete.value = false;
  completedMaterial.value = null;
  resetForm();
  form.supplierName = authState.user?.companyName || "";
}

function resetForm() {
  form.supplierName = "";
  form.contact = "";
  form.address = "";
  form.mainMaterials = "";
  form.materialName = "";
  form.standard = "";
  form.strengthGrade = "";
  form.recentPrice = "";
  form.serviceArea = "";
  form.distanceKm = "";
  form.deliveryCount = "";
  form.note = "";
}
</script>
