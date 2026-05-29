<template>
  <section class="request-summary">
    <div>
      <span>요청 자재</span>
      <strong>{{ request.materialName }} {{ request.strengthGrade }}</strong>
    </div>
    <div>
      <span>현장 위치</span>
      <strong>{{ request.siteAddress }}</strong>
    </div>
    <div>
      <span>필요 수량</span>
      <strong>{{ request.quantity }}</strong>
    </div>
    <div>
      <span>긴급 여부</span>
      <strong :class="{ danger: request.urgent }">{{ request.urgent ? "긴급" : "일반" }}</strong>
    </div>
  </section>
</template>

<script setup>
defineProps({
  request: {
    type: Object,
    required: true,
  },
});
</script>
