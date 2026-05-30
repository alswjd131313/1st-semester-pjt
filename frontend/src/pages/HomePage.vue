<template>
  <section class="hero-section">
    <div class="hero-copy">
      <p class="eyebrow">PaceFlow MVP</p>
      <h1>공사 지연은 막고,<br />대체 자재는 빠르게 찾으세요</h1>
      <p class="hero-description">
        규격, 물성 정보, 가격, 거리, 과거 납품 이력을 비교해 먼저 문의할 만한
        공급사 후보를 추천합니다.
      </p>

      <form class="search-box" @submit.prevent="goToRequest">
        <input
          v-model="keyword"
          type="search"
          :disabled="isSupplier"
          placeholder="예: 철근 SD400 D10, H빔 300x300, 시멘트 1종"
        />
        <button type="submit" :disabled="isSupplier">
          {{ isSupplier ? "요청자 전용" : "대체 자재 찾기" }}
        </button>
      </form>

      <div class="hero-actions">
        <template v-if="authState.user">
          <span class="disabled-action">요청자 로그인</span>
          <span class="disabled-action">공급사 로그인</span>
          <RouterLink to="/dashboard">{{ roleLabel }} 대시보드</RouterLink>
        </template>
        <template v-else>
          <RouterLink to="/login?role=requester">요청자 로그인</RouterLink>
          <RouterLink to="/login?role=supplier">공급사 로그인</RouterLink>
        </template>
        <RouterLink to="/recommendations">추천 결과 보기</RouterLink>
      </div>
    </div>

    <aside class="hero-panel">
      <span>누적 구현 상태</span>
      <strong>요청부터 상세 확인까지</strong>
      <p>로그인, 자재 요청, 공급사 등록, 추천 결과, 상세 보기 흐름을 한 번에 확인할 수 있습니다.</p>
      <div class="flow-list">
        <span v-if="isSupplier" class="disabled-flow">자재 요청 등록</span>
        <RouterLink v-else to="/request">자재 요청 등록</RouterLink>
        <span v-if="isRequester" class="disabled-flow">공급사 자재 등록</span>
        <RouterLink v-else to="/supplier-register">공급사 자재 등록</RouterLink>
        <RouterLink to="/recommendations">추천 상세 보기</RouterLink>
        <RouterLink to="/dashboard">문의 내역 확인</RouterLink>
      </div>
    </aside>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { authState } from "../api/authApi";

const router = useRouter();
const keyword = ref("");
const isSupplier = computed(() => authState.user?.role === "supplier");
const isRequester = computed(() => authState.user?.role === "requester");
const roleLabel = computed(() => (isSupplier.value ? "공급사" : "요청자"));

function goToRequest() {
  if (isSupplier.value) {
    return;
  }

  router.push({
    path: "/request",
    query: keyword.value ? { keyword: keyword.value } : {},
  });
}
</script>
