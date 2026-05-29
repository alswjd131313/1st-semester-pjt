<template>
  <article class="value-card">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
  </article>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
});
</script>
