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
          placeholder="예: 철근 SD400 D10, H빔 300x300, 시멘트 1종"
        />
        <button type="submit">대체 자재 찾기</button>
      </form>

      <div class="hero-actions">
        <RouterLink to="/login?role=requester">자재 요청자 로그인</RouterLink>
        <RouterLink to="/login?role=supplier">공급사 로그인</RouterLink>
      </div>
    </div>

    <aside class="hero-panel">
      <span>이번 단계</span>
      <strong>역할별 흐름 분리</strong>
      <p>자재 요청자는 요청 등록으로, 공급사는 취급 자재 등록으로 이동합니다.</p>
    </aside>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const keyword = ref("");

function goToRequest() {
  router.push({
    path: "/request",
    query: keyword.value ? { keyword: keyword.value } : {},
  });
}
</script>
