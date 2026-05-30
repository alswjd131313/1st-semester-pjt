<template>
  <section class="page-card">
    <p class="eyebrow">Supplier</p>
    <h1>공급사 등록</h1>
    <p class="notice">현재 로그인 역할: {{ authState.user?.name }} · 공급사</p>
    <p>공급사 정보 등록은 추천 흐름이 안정된 뒤 별도 기능으로 구현합니다.</p>
  </section>
</template>

<script setup>
import { authState } from "../api/authApi";
</script>
