<template>
  <section class="auth-page">
    <div class="auth-card">
      <p class="eyebrow">Login</p>
      <h1>{{ selectedRoleLabel }} 로그인</h1>
      <p class="auth-description">
        가입한 계정으로 로그인하면 역할에 따라 자재 요청과 공급사 등록 화면 접근 권한이
        달라집니다. 데모 확인이 필요하면 아래 계정을 선택해 빠르게 둘러볼 수 있습니다.
      </p>

      <p v-if="route.query.registered" class="success-message">
        회원가입이 완료되었습니다. 가입한 이메일과 비밀번호로 로그인해 주세요.
      </p>

      <div class="role-switch" aria-label="로그인 역할 선택">
        <button
          type="button"
          :class="{ active: form.role === 'requester' }"
          @click="form.role = 'requester'"
        >
          자재 요청자
        </button>
        <button
          type="button"
          :class="{ active: form.role === 'supplier' }"
          @click="form.role = 'supplier'"
        >
          공급사
        </button>
      </div>

      <form class="auth-form" @submit.prevent="handleLogin">
        <label>
          이메일
          <input v-model="form.email" type="email" placeholder="user@paceflow.kr" required />
        </label>

        <label>
          비밀번호
          <input v-model="form.password" type="password" placeholder="데모 비밀번호" required />
        </label>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <button type="submit">{{ selectedRoleLabel }}로 로그인</button>
      </form>

      <section class="demo-account-box">
        <div class="section-title-row">
          <h2>데모 계정</h2>
          <span>실제 회원가입 전 임시 인증</span>
        </div>
        <button
          v-for="account in filteredDemoAccounts"
          :key="account.email"
          type="button"
          class="demo-account-card"
          @click="fillDemoAccount(account)"
        >
          <strong>{{ account.roleLabel }}</strong>
          <span>{{ account.email }}</span>
          <small>{{ account.companyName }} · 비밀번호 paceflow123</small>
        </button>
      </section>

      <div class="auth-secondary-action">
        <span>아직 계정이 없나요?</span>
        <RouterLink :to="{ path: '/signup', query: { role: form.role } }">회원가입하기</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { demoAccounts, loginUser } from "../api/authApi";

const route = useRoute();
const router = useRouter();

const form = reactive({
  role: route.query.role === "supplier" ? "supplier" : "requester",
  email: "",
  password: "",
});
const errorMessage = ref("");

const selectedRoleLabel = computed(() =>
  form.role === "supplier" ? "공급사" : "자재 요청자",
);
const filteredDemoAccounts = computed(() =>
  demoAccounts.filter((account) => account.role === form.role),
);

watch(
  () => route.query.role,
  (role) => {
    form.role = role === "supplier" ? "supplier" : "requester";
    errorMessage.value = "";
  },
);

function handleLogin() {
  try {
    errorMessage.value = "";
    loginUser(form);
    router.push(route.query.redirect || "/");
  } catch (error) {
    errorMessage.value = error.message || "로그인 정보를 확인해 주세요.";
  }
}

function fillDemoAccount(account) {
  form.role = account.role;
  form.email = account.email;
  form.password = account.password;
  errorMessage.value = "";
}
</script>
