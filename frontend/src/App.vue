<template>
  <div class="app-shell">
    <HeaderNav />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { nextTick, watch } from "vue";
import { useRoute } from "vue-router";
import HeaderNav from "./components/HeaderNav.vue";

const route = useRoute();

watch(
  () => route.fullPath,
  async () => {
    await nextTick();
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  },
);
</script>
