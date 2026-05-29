<template>
  <form class="search-bar" @submit.prevent="$emit('submit', keyword)">
    <span class="search-icon">⌕</span>
    <input v-model="keyword" :placeholder="placeholder" />
    <button class="btn primary" type="submit">대체 자재 찾기</button>
  </form>
</template>

<script setup>
import { ref } from "vue";

defineProps({
  placeholder: {
    type: String,
    default: "예: 철근 SD400 D10, H빔 300x300, 시멘트 1종",
  },
});

defineEmits(["submit"]);

const keyword = ref("");
</script>
