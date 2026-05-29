<template>
  <div class="category-tabs">
    <button v-for="category in categories" :key="category.name" type="button" @click="$emit('select', category)">
      <span>{{ category.icon }}</span>
      {{ category.name }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  categories: {
    type: Array,
    required: true,
  },
});

defineEmits(["select"]);
</script>
