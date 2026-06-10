<template>
  <section class="auth-page">
    <div class="auth-card signup-card">
      <p class="eyebrow">Create Account</p>
      <h1>{{ selectedRoleLabel }} 회원가입</h1>
      <p class="auth-description">
        PaceFlow MVP에서는 가입한 계정으로만 로그인할 수 있습니다. 역할에 따라 자재 요청과
        공급사 등록 화면 접근 권한이 나뉩니다.
      </p>

      <div class="role-switch" aria-label="회원가입 역할 선택">
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

      <form class="auth-form" @submit.prevent="handleSignup">
        <label>
          이름
          <input v-model="form.name" type="text" placeholder="담당자 이름" required />
        </label>

        <label>
          회사명
          <input v-model="form.companyName" type="text" placeholder="회사 또는 현장명" required />
        </label>

        <label>
          이메일
          <input v-model="form.email" type="email" placeholder="user@paceflow.kr" required />
        </label>

        <label>
          비밀번호
          <input v-model="form.password" type="password" placeholder="6자 이상" required />
        </label>

        <label>
          비밀번호 확인
          <input v-model="form.passwordConfirm" type="password" placeholder="비밀번호 재입력" required />
        </label>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <button type="submit">{{ selectedRoleLabel }} 계정 만들기</button>
      </form>

      <div class="auth-secondary-action">
        <span>이미 계정이 있나요?</span>
        <RouterLink :to="{ path: '/login', query: { role: form.role } }">로그인하기</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { registerUser } from "../api/authApi";

const route = useRoute();
const router = useRouter();

const form = reactive({
  role: route.query.role === "supplier" ? "supplier" : "requester",
  name: "",
  companyName: "",
  email: "",
  password: "",
  passwordConfirm: "",
});
const errorMessage = ref("");

const selectedRoleLabel = computed(() =>
  form.role === "supplier" ? "공급사" : "자재 요청자",
);

watch(
  () => route.query.role,
  (role) => {
    form.role = role === "supplier" ? "supplier" : "requester";
    errorMessage.value = "";
  },
);

function handleSignup() {
  try {
    errorMessage.value = "";
    registerUser(form);
    router.push({ path: "/login", query: { role: form.role, registered: "true" } });
  } catch (error) {
    errorMessage.value = error.message || "회원가입 정보를 확인해 주세요.";
  }
}
</script>
