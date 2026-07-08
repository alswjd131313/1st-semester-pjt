<template>
  <div class="supplier-dashboard">
    <div class="page-header">
      <div>
        <h1>공급사 대시보드</h1>
        <p class="page-sub">접수된 문의와 등록 자재를 관리합니다.</p>
      </div>
      <RouterLink class="btn-primary" to="/supplier/profile">프로필 설정</RouterLink>
    </div>

    <!-- 통계 카드 -->
    <div class="stat-row">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <span class="stat-label">{{ s.label }}</span>
        <strong class="stat-value">{{ s.value }}</strong>
        <span class="stat-unit">{{ s.unit }}</span>
      </div>
    </div>

    <!-- 문의 목록 -->
    <section class="dashboard-section">
      <div class="section-header">
        <h2>접수 문의</h2>
        <div class="tab-group">
          <button
            v-for="tab in inquiryTabs"
            :key="tab.key"
            :class="['tab-btn', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>
      </div>

      <div v-if="isLoading" class="empty-state">불러오는 중...</div>
      <div v-else-if="filteredInquiries.length === 0" class="empty-state">해당 문의가 없습니다.</div>
      <div v-else class="inquiry-list">
        <div
          v-for="inq in filteredInquiries"
          :key="inq.id"
          class="inquiry-item"
          @click="router.push(`/inquiries/${inq.id}`)"
        >
          <div class="inquiry-main">
            <span class="inq-material">{{ inq.material_name ?? '자재 정보 없음' }}</span>
            <span :class="['inq-status', statusClass(inq.status)]">{{ statusLabel(inq.status) }}</span>
          </div>
          <p class="inq-desc">{{ inq.message ?? '-' }}</p>
          <span class="inq-date">{{ formatDate(inq.created_at) }}</span>
        </div>
      </div>
    </section>

    <!-- 등록 자재 -->
    <section class="dashboard-section">
      <div class="section-header">
        <h2>등록 자재</h2>
        <RouterLink class="btn-secondary-sm" to="/supplier/profile">자재 추가</RouterLink>
      </div>
      <div v-if="materials.length === 0" class="empty-state">등록된 자재가 없습니다.</div>
      <div v-else class="material-grid">
        <div v-for="mat in materials" :key="mat.id" class="material-item">
          <div class="material-header">
            <strong>{{ mat.ks_grade }} {{ mat.diameter }}</strong>
            <span class="mat-price">{{ mat.unit_price ? Number(mat.unit_price).toLocaleString() + ' 원/톤' : '-' }}</span>
          </div>
          <p class="mat-desc">{{ mat.manufacturer ?? '' }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { getSupplierInquiries, getSupplierMaterials } from "../api/materialApi";

const router = useRouter();
const inquiries = ref([]);
const materials = ref([]);
const isLoading = ref(false);
const activeTab = ref("all");

const inquiryTabs = [
  { key: "all", label: "전체" },
  { key: "pending", label: "검토 중" },
  { key: "accepted", label: "수락" },
  { key: "rejected", label: "거절" },
];

const filteredInquiries = computed(() => {
  if (activeTab.value === "all") return inquiries.value;
  return inquiries.value.filter((i) => i.status === activeTab.value);
});

const stats = computed(() => [
  { label: "전체 문의", value: inquiries.value.length, unit: "건" },
  { label: "검토 중", value: inquiries.value.filter((i) => i.status === "pending").length, unit: "건" },
  { label: "등록 자재", value: materials.value.length, unit: "종" },
]);

onMounted(async () => {
  isLoading.value = true;
  try {
    [inquiries.value, materials.value] = await Promise.all([
      getSupplierInquiries(),
      getSupplierMaterials(),
    ]);
  } catch {
    // pass
  } finally {
    isLoading.value = false;
  }
});

function statusLabel(s) {
  return { pending: "검토 중", accepted: "수락", rejected: "거절" }[s] ?? s;
}
function statusClass(s) {
  return { pending: "status-pending", accepted: "status-accepted", rejected: "status-rejected" }[s] ?? "";
}
function formatDate(d) {
  if (!d) return "";
  return new Date(d).toLocaleDateString("ko-KR", { year: "numeric", month: "short", day: "numeric" });
}
</script>

<style scoped>
.supplier-dashboard {
  max-width: 1080px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.page-header h1 { font-size: 28px; font-weight: 700; color: #102a56; margin: 0 0 6px; }
.page-sub { color: #71809a; font-size: 15px; margin: 0; }

.btn-primary {
  background: #1559e8;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 10px 24px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 40px;
}

.stat-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 14px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stat-label { font-size: 13px; color: #71809a; }
.stat-value { font-size: 36px; font-weight: 800; color: #102a56; }
.stat-unit { font-size: 14px; color: #aab4c4; }

.dashboard-section {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.section-header h2 { font-size: 18px; font-weight: 700; color: #102a56; margin: 0; }

.tab-group { display: flex; gap: 8px; }
.tab-btn {
  background: none;
  border: 1px solid #dde7f7;
  border-radius: 8px;
  padding: 6px 16px;
  font-size: 14px;
  color: #4b6380;
  cursor: pointer;
}
.tab-btn.active { background: #1559e8; color: #fff; border-color: #1559e8; }

.empty-state { text-align: center; color: #aab4c4; padding: 40px 0; font-size: 15px; }

.inquiry-list { display: flex; flex-direction: column; gap: 12px; }
.inquiry-item {
  border: 1px solid #f0f4fa;
  border-radius: 10px;
  padding: 16px 20px;
  cursor: pointer;
  transition: border-color 0.15s;
}
.inquiry-item:hover { border-color: #1559e8; }

.inquiry-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.inq-material { font-weight: 600; color: #102a56; font-size: 15px; }
.inq-status { font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 999px; }
.status-pending { background: #fef9ec; color: #b45309; }
.status-accepted { background: #ecfdf5; color: #059669; }
.status-rejected { background: #fef2f2; color: #dc2626; }

.inq-desc { font-size: 14px; color: #71809a; margin: 0 0 8px; }
.inq-date { font-size: 13px; color: #aab4c4; }

.btn-secondary-sm {
  border: 1px solid #1559e8;
  color: #1559e8;
  background: none;
  border-radius: 8px;
  padding: 6px 16px;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
}

.material-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.material-item {
  border: 1px solid #f0f4fa;
  border-radius: 10px;
  padding: 16px 20px;
}
.material-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.material-header strong { font-size: 15px; color: #102a56; }
.mat-price { font-size: 13px; color: #1559e8; font-weight: 600; }
.mat-desc { font-size: 13px; color: #aab4c4; margin: 0; }
</style>
