<template>
  <section class="page-wrap">
    <div class="page-heading">
      <p class="eyebrow">Step 1</p>
      <h1>자재 요청 등록</h1>
      <p>기존 자재 정보와 현장 조건을 입력하면 문의 우선순위가 높은 공급사 후보를 보여줍니다.</p>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <form class="request-form" @submit.prevent="submitRequest">
      <label>
        자재명
        <input v-model="form.materialName" type="text" placeholder="철근" required />
      </label>

      <label>
        자재 카테고리
        <select v-model="form.category" required>
          <option value="" disabled>카테고리 선택</option>
          <option v-for="category in categories" :key="category.name" :value="category.name">
            {{ category.name }}
          </option>
        </select>
      </label>

      <label>
        KS 규격 또는 규격명
        <input v-model="form.standard" type="text" placeholder="KS D 3504" required />
      </label>

      <label>
        강도 등급
        <input v-model="form.strengthGrade" type="text" placeholder="SD400 / D10" required />
      </label>

      <label>
        필요 수량
        <input v-model="form.requiredQuantity" type="text" placeholder="50톤" required />
      </label>

      <label>
        현장 주소
        <input v-model="form.siteAddress" type="text" placeholder="서울 성수동" required />
      </label>

      <label>
        필요 날짜
        <input v-model="form.requiredDate" type="date" required />
      </label>

      <label class="checkbox-field">
        <input v-model="form.isUrgent" type="checkbox" />
        긴급 요청입니다
      </label>

      <label class="full-field">
        요청 메모
        <textarea
          v-model="form.memo"
          rows="4"
          placeholder="대체 가능 조건, 납품 희망 시간, 현장 특이사항을 적어주세요."
        />
      </label>

      <div class="form-actions">
        <RouterLink class="secondary-button" to="/">취소</RouterLink>
        <button type="submit" class="primary-button" :disabled="isSubmitting">
          {{ isSubmitting ? "요청 저장 중" : "추천 결과 보기" }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createMaterialRequest } from "../api/materialApi";
import { categories } from "../data/dummyData";

const route = useRoute();
const router = useRouter();
const keyword = String(route.query.keyword || "");
const isSubmitting = ref(false);
const errorMessage = ref("");

const form = reactive({
  materialName: parseMaterialName(keyword),
  category: parseCategory(keyword),
  standard: keyword.includes("SD") ? "KS D 3504" : "",
  strengthGrade: keyword.replace(parseMaterialName(keyword), "").trim(),
  requiredQuantity: "",
  siteAddress: "",
  requiredDate: "",
  isUrgent: false,
  memo: "",
});

async function submitRequest() {
  try {
    isSubmitting.value = true;
    errorMessage.value = "";
    const request = await createMaterialRequest({ ...form });
    router.push({
      path: "/recommendations",
      query: { requestId: request.id },
    });
  } catch {
    errorMessage.value = "자재 요청을 저장하지 못했습니다. 잠시 후 다시 시도해주세요.";
  } finally {
    isSubmitting.value = false;
  }
}

function parseMaterialName(value) {
  if (!value) return "";
  return value.split(" ")[0] || "";
}

function parseCategory(value) {
  return categories.find((category) => value.includes(category.name))?.name || "";
}
</script>
