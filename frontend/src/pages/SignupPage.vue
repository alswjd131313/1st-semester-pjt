<template>
  <section class="auth-page">
    <div class="auth-card signup-card">
      <p class="eyebrow">Create Account</p>
      <h1>{{ selectedRoleLabel }} 회원가입</h1>
      <p class="auth-description">
        PaceFlow 계정을 만들면 역할에 따라 자재 요청과 공급사 등록 화면 접근 권한이
        나뉩니다.
      </p>

      <div class="role-switch" aria-label="회원가입 역할 선택">
        <button
          type="button"
          :class="{ active: form.role === 'requester' }"
          @click="form.role = 'requester'"
        >
          자재 요청자
        </button>
        <button
          type="button"
          :class="{ active: form.role === 'supplier' }"
          @click="form.role = 'supplier'"
        >
          공급사
        </button>
      </div>

      <form class="auth-form" @submit.prevent="handleSignup">
        <label>
          이름
          <input v-model="form.name" type="text" placeholder="담당자 이름" required />
        </label>

        <label>
          회사명
          <input v-model="form.companyName" type="text" placeholder="회사 또는 현장명" required />
        </label>

        <div v-if="form.role === 'requester'" class="signup-address-section">
          <AddressSearchField
            v-model="form.defaultSiteAddress"
            label="기본 현장 주소"
            :zip-no="form.defaultSiteZipNo"
            placeholder="추천 거리 계산에 사용할 기본 현장 주소를 검색하세요"
            @selected="handleDefaultAddressSelected"
          />
          <label>
            상세 주소
            <input v-model.trim="form.defaultSiteDetailAddress" type="text" placeholder="동·호수, 현장 출입구 등 상세 위치" />
          </label>
          <p v-if="hasDefaultCoordinate" class="address-coordinate-note">
            좌표 저장됨 · {{ form.defaultSiteLatitude }}, {{ form.defaultSiteLongitude }}
          </p>
          <p v-else class="address-helper-note">
            주소를 선택하면 자재 요청 시 현장 주소가 자동 입력됩니다.
          </p>
        </div>

        <label>
          이메일
          <input v-model="form.email" type="email" placeholder="user@paceflow.kr" required />
        </label>

        <label>
          비밀번호
          <input v-model="form.password" type="password" placeholder="6자 이상" required />
        </label>

        <label>
          비밀번호 확인
          <input v-model="form.passwordConfirm" type="password" placeholder="비밀번호 재입력" required />
        </label>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <button type="submit">{{ selectedRoleLabel }} 계정 만들기</button>
      </form>

      <div class="auth-secondary-action">
        <span>이미 계정이 있나요?</span>
        <RouterLink :to="{ path: '/login', query: { role: form.role } }">로그인하기</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { registerUser } from "../api/authApi";
import AddressSearchField from "../components/AddressSearchField.vue";

const route = useRoute();
const router = useRouter();

const form = reactive({
  role: route.query.role === "supplier" ? "supplier" : "requester",
  name: "",
  companyName: "",
  email: "",
  password: "",
  passwordConfirm: "",
  defaultSiteAddress: "",
  defaultSiteDetailAddress: "",
  defaultSiteZipNo: "",
  defaultSiteLatitude: null,
  defaultSiteLongitude: null,
});
const errorMessage = ref("");

const selectedRoleLabel = computed(() =>
  form.role === "supplier" ? "공급사" : "자재 요청자",
);
const hasDefaultCoordinate = computed(() =>
  hasKoreaCoordinate(form.defaultSiteLatitude, form.defaultSiteLongitude),
);

watch(
  () => route.query.role,
  (role) => {
    form.role = role === "supplier" ? "supplier" : "requester";
    errorMessage.value = "";
  },
);

watch(
  () => form.role,
  (role) => {
    errorMessage.value = "";
    if (role === "supplier") {
      clearDefaultAddress();
    }
  },
);

async function handleSignup() {
  try {
    errorMessage.value = "";
    if (form.role === "requester" && form.defaultSiteAddress && !hasDefaultCoordinate.value) {
      errorMessage.value = "기본 현장 주소는 주소 검색 결과에서 선택해야 좌표가 함께 저장됩니다.";
      return;
    }
    await registerUser(form);
    router.push({ path: "/signup-success", query: { role: form.role } });
  } catch (error) {
    errorMessage.value = error.message || "회원가입 정보를 확인해 주세요.";
  }
}

function handleDefaultAddressSelected(address) {
  form.defaultSiteAddress = address.roadAddress || address.fullRoadAddress || address.address || "";
  form.defaultSiteZipNo = address.zipNo || "";
  form.defaultSiteLatitude = roundCoordinate(address.latitude);
  form.defaultSiteLongitude = roundCoordinate(address.longitude);
  if (!hasKoreaCoordinate(form.defaultSiteLatitude, form.defaultSiteLongitude)) {
    form.defaultSiteLatitude = null;
    form.defaultSiteLongitude = null;
    errorMessage.value = "선택한 주소의 좌표를 확인할 수 없습니다. 다른 주소를 선택해 주세요.";
  }
}

function clearDefaultAddress() {
  form.defaultSiteAddress = "";
  form.defaultSiteDetailAddress = "";
  form.defaultSiteZipNo = "";
  form.defaultSiteLatitude = null;
  form.defaultSiteLongitude = null;
}

function roundCoordinate(value) {
  const number = Number(value);
  return Number.isFinite(number) ? Number(number.toFixed(6)) : null;
}

function hasKoreaCoordinate(latitude, longitude) {
  const lat = Number(latitude);
  const lng = Number(longitude);
  return Number.isFinite(lat) && Number.isFinite(lng) && lat >= 33 && lat <= 39 && lng >= 124 && lng <= 132;
}
</script>

<style scoped>
.signup-address-section {
  display: grid;
  gap: 12px;
  border: 1px solid #dbe6f8;
  border-radius: 18px;
  padding: 16px;
  background: #f8fbff;
}

.address-coordinate-note,
.address-helper-note {
  margin: 0;
  color: #4b6380;
  font-size: 13px;
  font-weight: 700;
}

.address-coordinate-note {
  color: #047857;
}
</style>
