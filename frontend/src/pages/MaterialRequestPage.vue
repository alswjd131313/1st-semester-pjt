<template>
  <section class="page-card">
    <p class="eyebrow">Step 1</p>
    <h1>자재 요청 등록</h1>
    <p class="notice">현재 로그인 역할: {{ authState.user?.name }} · 자재 요청자</p>
    <p>다음 단계에서 이 화면에 요청 폼을 붙이면 됩니다.</p>
    <p v-if="keyword" class="notice">검색어: {{ keyword }}</p>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { authState } from "../api/authApi";

const route = useRoute();
const keyword = computed(() => route.query.keyword || "");
</script>
