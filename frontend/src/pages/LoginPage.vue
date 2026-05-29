<template>
  <section class="auth-page">
    <div class="auth-panel">
      <div class="auth-copy">
        <p class="eyebrow dark">{{ isSupplier ? "Supplier Access" : "Requester Access" }}</p>
        <h1>{{ isSupplier ? "공급사 로그인" : "자재 요청자 로그인" }}</h1>
        <p>
          MVP에서는 실제 인증 없이 주요 흐름을 확인할 수 있는 mock 로그인을 제공합니다.
          {{ isSupplier ? "로그인 후 회사 정보와 취급 자재를 등록할 수 있습니다." : "로그인 후 자재 요청을 등록하고 추천 결과를 확인할 수 있습니다." }}
        </p>
      </div>

      <form class="auth-card" @submit.prevent="submit">
        <label>
          <span>{{ isSupplier ? "회사명" : "현장/회사명" }}</span>
          <input v-model="form.companyName" :placeholder="isSupplier ? '예: C철강(주)' : '예: 성수동 현장'" />
        </label>
        <label>
          <span>이메일</span>
          <input v-model="form.email" type="email" placeholder="supplier@paceflow.kr" required />
        </label>
        <label>
          <span>비밀번호</span>
          <input v-model="form.password" type="password" placeholder="데모용 비밀번호" required />
        </label>
        <p v-if="error" class="error-message">{{ error }}</p>
        <button class="btn primary" type="submit">{{ isSupplier ? "로그인하고 등록하기" : "로그인하고 요청하기" }}</button>
        <p class="auth-help">데모 환경에서는 입력한 정보가 브라우저 localStorage에만 저장됩니다.</p>
      </form>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { loginUser } from "../api/authApi";

const route = useRoute();
const router = useRouter();
const error = ref("");
const form = reactive({
  companyName: "",
  email: "",
  password: "demo1234",
});
const isSupplier = computed(() => route.query.role === "supplier");

watchEffect(() => {
  form.companyName = isSupplier.value ? "C철강(주)" : "성수동 현장";
  form.email = isSupplier.value ? "supplier@paceflow.kr" : "site@paceflow.kr";
});

async function submit() {
  error.value = "";
  try {
    await loginUser({ ...form, role: isSupplier.value ? "supplier" : "requester" });
    router.push(isSupplier.value ? "/supplier-register" : "/request");
  } catch (err) {
    error.value = err.message;
  }
}
</script>
