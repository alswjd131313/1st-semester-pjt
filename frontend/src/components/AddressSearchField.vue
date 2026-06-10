<template>
  <div class="address-search-field">
    <span class="field-label">{{ label }}</span>
    <div class="address-search-row">
      <input
        v-model.trim="keyword"
        type="search"
        :placeholder="placeholder"
        autocomplete="off"
        @keydown.enter.prevent="runSearch"
      />
      <button type="button" class="secondary-button" :disabled="isSearching" @click="runSearch">
        {{ isSearching ? "검색 중" : "주소 검색" }}
      </button>
    </div>

    <p v-if="modelValue" class="selected-address">
      <strong>선택된 주소</strong>
      <span>{{ modelValue }}</span>
      <small v-if="zipNo">우편번호 {{ zipNo }}</small>
    </p>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <div v-if="results.length" class="address-results">
      <button
        v-for="item in results"
        :key="`${item.roadAddress}-${item.zipNo}`"
        type="button"
        @click="selectAddress(item)"
      >
        <strong>{{ item.roadAddress }}</strong>
        <span>{{ item.jibunAddress }}</span>
        <small>{{ item.zipNo }}</small>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { geocodeAddress, searchAddresses } from "../api/addressApi";

const props = defineProps({
  label: { type: String, default: "주소" },
  modelValue: { type: String, default: "" },
  zipNo: { type: String, default: "" },
  placeholder: { type: String, default: "예: 서울 성동구 아차산로 123" },
});

const emit = defineEmits(["update:modelValue", "selected"]);
const keyword = ref(props.modelValue);
const results = ref([]);
const isSearching = ref(false);
const errorMessage = ref("");

async function runSearch() {
  if (keyword.value.length < 2) {
    errorMessage.value = "주소 검색어를 두 글자 이상 입력해 주세요.";
    return;
  }

  try {
    isSearching.value = true;
    errorMessage.value = "";
    results.value = await searchAddresses(keyword.value);
    if (!results.value.length) {
      errorMessage.value = "검색 결과가 없습니다. 도로명과 건물번호를 함께 입력해 보세요.";
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.error || "주소 검색에 실패했습니다.";
  } finally {
    isSearching.value = false;
  }
}

async function selectAddress(item) {
  try {
    isSearching.value = true;
    errorMessage.value = "";
    const coordinates = await geocodeAddress(item.roadAddress);
    keyword.value = item.roadAddress;
    results.value = [];
    emit("update:modelValue", item.roadAddress);
    emit("selected", { ...item, ...coordinates });
  } catch (error) {
    errorMessage.value = error.response?.data?.error || "선택한 주소의 좌표를 찾지 못했습니다.";
  } finally {
    isSearching.value = false;
  }
}
</script>
