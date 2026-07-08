<template>
  <section class="page-wrap inquiry-edit-page">
    <div class="page-heading">
      <p class="eyebrow">Inquiry Management</p>
      <h1>문의 수정</h1>
      <p>공급사와 자재 정보는 유지하고, 문의에 필요한 연락·요청 정보를 수정합니다.</p>
    </div>

    <p v-if="loading" class="loading-message">문의 정보를 불러오는 중입니다.</p>
    <div v-else-if="notFound" class="empty-state">
      <strong>수정할 문의를 찾을 수 없습니다.</strong>
      <p>문의 내역에서 저장된 문의를 다시 선택해주세요.</p>
      <RouterLink class="primary-button" to="/inquiries">문의 내역으로</RouterLink>
    </div>

    <form v-else class="inquiry-edit-form" @submit.prevent="saveInquiry">
      <div class="edit-summary">
        <span>문의 ID {{ inquiryId }}</span>
        <strong>{{ supplierSummary }}</strong>
      </div>
      <div class="form-grid">
        <label>담당자<input v-model.trim="form.requesterName" required /></label>
        <label>연락처<input v-model.trim="form.contact" type="tel" required /></label>
        <label>문의 수량<input v-model.trim="form.quantity" required /></label>
        <label>희망 납기<input v-model="form.desiredDate" type="date" /></label>
        <label>
          문의 상태
          <select v-model="form.status">
            <option v-if="form.status === 'need_more_info'" value="need_more_info">추가 확인 필요 (기존 상태)</option>
            <option v-for="status in statuses" :key="status.value" :value="status.value">{{ status.label }}</option>
          </select>
        </label>
        <label class="full-field">메모/문의 내용<textarea v-model.trim="form.message" rows="6" /></label>
      </div>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <div class="form-actions">
        <RouterLink class="secondary-button" :to="`/inquiries/${inquiryId}`">취소</RouterLink>
        <button class="primary-button" type="submit" :disabled="saving">{{ saving ? "저장 중" : "수정 저장" }}</button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getSupplierInquiry, updateSupplierInquiry } from "../api/materialApi";

const route = useRoute();
const router = useRouter();
const inquiryId = computed(() => String(route.params.id || ""));
const loading = ref(true);
const saving = ref(false);
const notFound = ref(false);
const errorMessage = ref("");
const originalInquiry = ref(null);
const form = reactive({ requesterName: "", contact: "", quantity: "", desiredDate: "", status: "pending", message: "" });
const statuses = [
  { value: "pending", label: "협의 필요" },
  { value: "accepted", label: "납품 가능" },
  { value: "rejected", label: "거절" },
];
const normalizedStatus = (status) => {
  if (["received", "pending", "reviewing"].includes(status)) return "pending";
  if (["quoted", "accepted"].includes(status)) return "accepted";
  if (["rejected", "unavailable"].includes(status)) return "rejected";
  if (status === "need_more_info") return "need_more_info";
  return "pending";
};
const supplierSummary = computed(() => {
  const supplier = originalInquiry.value?.supplier;
  return `${supplier?.supplierName || "공급사 미지정"} · ${supplier?.materialName || "자재 미지정"}${supplier?.standard ? ` · ${supplier.standard}` : ""}`;
});

onMounted(async () => {
  try {
    const inquiry = await getSupplierInquiry(inquiryId.value);
    if (!inquiry) {
      notFound.value = true;
      return;
    }
    originalInquiry.value = inquiry;
    Object.assign(form, {
      requesterName: inquiry.requesterName || "",
      contact: inquiry.contact || "",
      quantity: inquiry.quantity || "",
      desiredDate: inquiry.desiredDate || "",
      status: normalizedStatus(inquiry.status),
      message: inquiry.message || "",
    });
  } finally {
    loading.value = false;
  }
});

async function saveInquiry() {
  try {
    saving.value = true;
    errorMessage.value = "";
    const updated = await updateSupplierInquiry(inquiryId.value, { ...form });
    if (!updated) {
      notFound.value = true;
      return;
    }
    router.push(`/inquiries/${updated.id}`);
  } catch {
    errorMessage.value = "문의 수정 내용을 저장하지 못했습니다.";
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.inquiry-edit-page{max-width:900px}.inquiry-edit-form{border:1px solid #dbe6f8;border-radius:28px;padding:clamp(22px,4vw,36px);background:#fff;box-shadow:0 22px 70px rgba(31,61,115,.1)}.edit-summary{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-bottom:24px;border-radius:16px;padding:16px 18px;background:#f4f8ff}.edit-summary span{color:#1559e8;font-size:12px;font-weight:900}.edit-summary strong{color:#18365f}.form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.form-grid label{display:grid;gap:8px;color:#40506a;font-weight:800}.form-grid input,.form-grid select,.form-grid textarea{width:100%;box-sizing:border-box;border:1px solid #cddbf0;border-radius:13px;padding:13px;background:#fff;font:inherit}.full-field{grid-column:1/-1}.form-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:22px}@media(max-width:650px){.edit-summary{align-items:flex-start;flex-direction:column}.form-grid{grid-template-columns:1fr}.full-field{grid-column:auto}}
</style>
