<template>
  <div class="success-page">
    <div class="success-card">
      <div class="check-icon" aria-hidden="true">✓</div>
      <h1>가입이 완료되었습니다</h1>
      <p class="success-desc">
        <strong>{{ roleName }}</strong>으로 PaceFlow에 가입하셨습니다.<br />
        지금 바로 서비스를 이용해보세요.
      </p>

      <div class="success-actions">
        <RouterLink class="btn-primary" :to="primaryPath">
          {{ primaryLabel }}
        </RouterLink>
        <RouterLink class="btn-ghost" to="/">홈으로 이동</RouterLink>
      </div>

      <div class="success-tip">
        <p>PaceFlow는 대체 자재 추천부터 공급사 문의까지 한 곳에서 처리할 수 있는 의사결정 지원 플랫폼입니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const role = route.query.role ?? "requester";

const roleName = computed(() => (role === "supplier" ? "공급사" : "자재 요청자"));
const primaryPath = computed(() =>
  role === "supplier" ? "/supplier/dashboard" : "/materials/request"
);
const primaryLabel = computed(() =>
  role === "supplier" ? "공급사 대시보드 시작" : "자재 요청하기"
);
</script>

<style scoped>
.success-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
}

.success-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 24px;
  padding: 56px 48px;
  max-width: 480px;
  width: 100%;
  text-align: center;
}

.check-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #10b981;
  color: #fff;
  font-size: 36px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 28px;
}

h1 {
  font-size: 26px;
  font-weight: 700;
  color: #102a56;
  margin: 0 0 14px;
}

.success-desc {
  font-size: 16px;
  color: #71809a;
  line-height: 1.7;
  margin: 0 0 36px;
}

.success-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 32px;
}

.btn-primary {
  display: block;
  background: #1559e8;
  color: #fff;
  border-radius: 12px;
  padding: 14px 0;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
}

.btn-ghost {
  display: block;
  background: none;
  border: 1px solid #dde7f7;
  border-radius: 12px;
  padding: 13px 0;
  font-size: 15px;
  color: #71809a;
  text-decoration: none;
}

.success-tip {
  background: #f6f8fc;
  border-radius: 12px;
  padding: 16px 20px;
}

.success-tip p {
  font-size: 13px;
  color: #aab4c4;
  margin: 0;
  line-height: 1.6;
}
</style>
