<template>
  <section class="auth-page">
    <div class="auth-card">
      <p class="eyebrow">Login</p>
      <h1>{{ selectedRoleLabel }} 로그인</h1>
      <p class="auth-description">
        지금은 실제 인증 전 단계입니다. 역할을 선택하면 해당 역할 기준으로 화면 접근이
        분리됩니다.
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
          이름
          <input v-model="form.name" type="text" placeholder="홍길동" required />
        </label>

        <label>
          이메일
          <input v-model="form.email" type="email" placeholder="user@paceflow.kr" required />
        </label>

        <label>
          회사명
          <input v-model="form.companyName" type="text" placeholder="성수건설" />
        </label>

        <button type="submit">{{ selectedRoleLabel }}로 시작하기</button>
      </form>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { loginUser } from "../api/authApi";

const route = useRoute();
const router = useRouter();

const form = reactive({
  role: route.query.role === "supplier" ? "supplier" : "requester",
  name: "",
  email: "",
  companyName: "",
});

const selectedRoleLabel = computed(() =>
  form.role === "supplier" ? "공급사" : "자재 요청자",
);

watch(
  () => route.query.role,
  (role) => {
    form.role = role === "supplier" ? "supplier" : "requester";
  },
);

function handleLogin() {
  loginUser(form);
  router.push(route.query.redirect || (form.role === "supplier" ? "/supplier-register" : "/request"));
}
</script>
