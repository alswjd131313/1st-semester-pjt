<template>
  <div class="app-shell">
    <HeaderNav />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import HeaderNav from "./components/HeaderNav.vue";
</script>
