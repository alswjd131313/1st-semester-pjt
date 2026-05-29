<template>
  <section class="page">
    <div class="page-title">
      <p>Supplier</p>
      <h1>공급사 정보 등록</h1>
      <span>로그인한 공급사가 회사 정보와 취급 자재를 등록하는 MVP 화면입니다.</span>
    </div>

    <section v-if="!authState.user" class="login-required-card">
      <div>
        <h2>공급사 로그인이 필요합니다</h2>
        <p>회사 정보와 취급 자재를 등록하려면 먼저 공급사 계정으로 로그인해주세요.</p>
      </div>
      <RouterLink class="btn primary no-wrap" to="/login?role=supplier">공급사 로그인/등록</RouterLink>
    </section>

    <form v-else class="form-card" @submit.prevent="submit">
      <div class="account-banner full">
        <span>로그인 계정</span>
        <strong>{{ authState.user.companyName }}</strong>
        <small>{{ authState.user.email }}</small>
      </div>
      <label><span>공급사명</span><input v-model="form.supplierName" required /></label>
      <label><span>연락처</span><input v-model="form.phone" required /></label>
      <label class="full"><span>주소</span><input v-model="form.address" required /></label>
      <label class="full"><span>주요 취급 자재</span><input v-model="form.mainMaterials" required /></label>
      <label><span>자재명</span><input v-model="form.materialName" required /></label>
      <label><span>KS 규격</span><input v-model="form.standard" required /></label>
      <label><span>강도 등급</span><input v-model="form.strengthGrade" required /></label>
      <label><span>최근 단가</span><input v-model="form.price" required /></label>
      <label><span>납품 가능 지역</span><input v-model="form.availableRegion" required /></label>
      <label><span>과거 납품 횟수</span><input v-model="form.deliveryCount" type="number" required /></label>
      <label class="full"><span>비고</span><textarea v-model="form.memo" rows="4" /></label>

      <button class="btn primary" type="submit">공급사 정보 등록하기</button>
      <p v-if="submitted" class="success-message">등록 요청이 저장되었습니다. 실제 연동 시 API 응답으로 교체됩니다.</p>
    </form>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { registerSupplierMaterial } from "../api/materialApi";
import { authState } from "../api/authApi";

const submitted = ref(false);
const form = reactive({
  supplierName: "",
  phone: "",
  address: "",
  mainMaterials: "",
  materialName: "",
  standard: "",
  strengthGrade: "",
  price: "",
  availableRegion: "",
  deliveryCount: 0,
  memo: "",
});

async function submit() {
  await registerSupplierMaterial({ ...form });
  submitted.value = true;
}

onMounted(() => {
  if (authState.user?.companyName && !form.supplierName) {
    form.supplierName = authState.user.companyName;
  }
});
</script>
