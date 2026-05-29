<template>
  <section class="page">
    <div class="page-title">
      <p>Material Request</p>
      <h1>대체 자재 추천 요청</h1>
      <span>기존 자재 정보와 현장 조건을 입력하면 더미 추천 결과로 이동합니다.</span>
    </div>

    <section v-if="!authState.user" class="login-required-card">
      <div>
        <h2>자재 요청자 로그인이 필요합니다</h2>
        <p>자재 요청을 등록하고 추천 결과를 확인하려면 먼저 로그인해주세요.</p>
      </div>
      <RouterLink class="btn primary no-wrap" to="/login?role=requester">요청자 로그인</RouterLink>
    </section>

    <form v-else class="form-card" @submit.prevent="submit">
      <div class="account-banner full">
        <span>로그인 계정</span>
        <strong>{{ authState.user.companyName }}</strong>
        <small>{{ authState.user.email }}</small>
      </div>
      <label><span>자재명</span><input v-model="form.materialName" required /></label>
      <label><span>자재 카테고리</span><input v-model="form.category" required /></label>
      <label><span>KS 규격 또는 규격명</span><input v-model="form.standard" required /></label>
      <label><span>강도 등급</span><input v-model="form.strengthGrade" required /></label>
      <label><span>필요 수량</span><input v-model="form.quantity" required /></label>
      <label><span>현장 주소</span><input v-model="form.siteAddress" required /></label>
      <label><span>필요 날짜</span><input v-model="form.neededDate" type="date" required /></label>
      <label class="checkbox-row"><input v-model="form.urgent" type="checkbox" /> 긴급 여부</label>
      <label class="full"><span>요청 메모</span><textarea v-model="form.memo" rows="4" /></label>

      <div class="form-actions">
        <RouterLink class="btn outline" to="/">취소</RouterLink>
        <button class="btn primary" type="submit">추천 결과 보기</button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createMaterialRequest } from "../api/materialApi";
import { authState } from "../api/authApi";

const route = useRoute();
const router = useRouter();
const keyword = String(route.query.keyword || "철근 SD400 D10");

const form = reactive({
  materialName: keyword.includes("H빔") ? "H빔" : keyword.includes("시멘트") ? "시멘트" : keyword.includes("전선관") ? "전선관" : keyword.includes("단열재") ? "단열재" : "철근",
  category: keyword.includes("H빔") ? "강재" : keyword.includes("시멘트") ? "시멘트" : keyword.includes("전선관") ? "전기자재" : keyword.includes("단열재") ? "단열재" : "철근",
  standard: keyword.includes("H빔") ? "SS275" : keyword.includes("시멘트") ? "KS L 5201" : "KS D 3504",
  strengthGrade: keyword.replace(/철근|H빔|시멘트|전선관|단열재/g, "").trim() || "SD400 D10",
  quantity: "50톤",
  siteAddress: "서울 성수동",
  neededDate: "2026-06-12",
  urgent: true,
  memo: "",
});

async function submit() {
  const created = await createMaterialRequest({ ...form });
  router.push({ path: "/recommendations", query: { requestId: created.id } });
}
</script>
