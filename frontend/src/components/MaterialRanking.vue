<template>
  <section class="card">
    <div class="section-head">
      <h2>자주 찾는 대체 자재 랭킹</h2>
      <p>현장에서 자주 검색되는 자재를 빠르게 찾아보세요.</p>
    </div>
    <ol class="ranking-list">
      <li v-for="item in materials" :key="item.rank">
        <strong>{{ item.rank }}위</strong>
        <span>{{ item.name }}</span>
        <button type="button" @click="$emit('select', item)">바로 찾기</button>
      </li>
    </ol>
  </section>
</template>

<script setup>
defineProps({
  materials: {
    type: Array,
    required: true,
  },
});

defineEmits(["select"]);
</script>
