<template>
  <div class="profile-page">
    <div class="page-header">
      <button class="back-btn" @click="router.back()">← 뒤로</button>
      <div>
        <h1>공급사 프로필</h1>
        <p class="page-sub">취급 자재와 공급사 기본 정보를 관리합니다.</p>
      </div>
    </div>

    <!-- 기본 정보 -->
    <section class="profile-card">
      <h2 class="card-title">기본 정보</h2>
      <div class="form-grid">
        <div class="form-group">
          <label>회사명</label>
          <input v-model="form.name" type="text" placeholder="회사명을 입력하세요" />
        </div>
        <div class="form-group">
          <label>사업자 번호</label>
          <input v-model="form.business_number" type="text" placeholder="000-00-00000" />
        </div>
        <div class="form-group span-2">
          <label>주소</label>
          <input v-model="form.address" type="text" placeholder="주소를 입력하세요" />
        </div>
        <div class="form-group">
          <label>연락처</label>
          <input v-model="form.phone" type="text" placeholder="02-0000-0000" />
        </div>
        <div class="form-group">
          <label>이메일</label>
          <input v-model="form.email" type="email" placeholder="contact@company.com" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn-primary" @click="saveProfile" :disabled="isSaving">
          {{ isSaving ? '저장 중...' : '저장' }}
        </button>
        <span v-if="saveMsg" class="save-msg">{{ saveMsg }}</span>
      </div>
    </section>

    <!-- 취급 자재 -->
    <section class="profile-card">
      <div class="card-header">
        <h2 class="card-title">취급 자재</h2>
        <button class="btn-add" @click="showAddMaterial = true">+ 추가</button>
      </div>

      <div v-if="materials.length === 0" class="empty-state">등록된 자재가 없습니다.</div>
      <div v-else class="material-list">
        <div v-for="mat in materials" :key="mat.id" class="material-row">
          <div class="mat-info">
            <strong>{{ mat.ks_grade }} {{ mat.diameter }}</strong>
            <span class="mat-price">{{ mat.unit_price ? Number(mat.unit_price).toLocaleString() + ' 원/톤' : '단가 미등록' }}</span>
          </div>
          <div class="mat-meta">
            <span>{{ mat.manufacturer ?? '-' }}</span>
            <span>재고: {{ mat.stock_available ? '있음' : '없음' }}</span>
          </div>
          <button class="btn-remove" @click="removeMaterial(mat.id)">삭제</button>
        </div>
      </div>
    </section>

    <!-- 자재 추가 모달 -->
    <div v-if="showAddMaterial" class="modal-backdrop" @click.self="showAddMaterial = false">
      <div class="modal">
        <h3>자재 추가</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>KS 등급</label>
            <select v-model="newMat.ks_grade">
              <option value="">선택</option>
              <option v-for="g in ksGrades" :key="g">{{ g }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>직경</label>
            <select v-model="newMat.diameter">
              <option value="">선택</option>
              <option v-for="d in diameters" :key="d">{{ d }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>단가 (원/톤)</label>
            <input v-model="newMat.unit_price" type="number" placeholder="800000" />
          </div>
          <div class="form-group">
            <label>제조사</label>
            <input v-model="newMat.manufacturer" type="text" placeholder="현대제철 등" />
          </div>
        </div>
        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="newMat.stock_available" />
            재고 있음
          </label>
        </div>
        <div class="modal-actions">
          <button class="btn-primary" @click="addMaterial">추가</button>
          <button class="btn-ghost" @click="showAddMaterial = false">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { getSupplierMaterials } from "../api/materialApi";

const router = useRouter();
const materials = ref([]);
const isSaving = ref(false);
const saveMsg = ref("");
const showAddMaterial = ref(false);

const form = reactive({
  name: "",
  business_number: "",
  address: "",
  phone: "",
  email: "",
});

const newMat = reactive({
  ks_grade: "",
  diameter: "",
  unit_price: "",
  manufacturer: "",
  stock_available: true,
});

const ksGrades = ["SD300", "SD400", "SD500", "SD600"];
const diameters = ["D10", "D13", "D16", "D19", "D22", "D25", "D29", "D32"];

onMounted(async () => {
  try {
    materials.value = await getSupplierMaterials();
  } catch {
    // pass
  }
});

async function saveProfile() {
  isSaving.value = true;
  saveMsg.value = "";
  try {
    await new Promise((r) => setTimeout(r, 600));
    saveMsg.value = "저장되었습니다.";
  } finally {
    isSaving.value = false;
  }
}

function addMaterial() {
  if (!newMat.ks_grade || !newMat.diameter) return;
  materials.value.push({
    id: Date.now(),
    ks_grade: newMat.ks_grade,
    diameter: newMat.diameter,
    unit_price: newMat.unit_price || null,
    manufacturer: newMat.manufacturer || null,
    stock_available: newMat.stock_available,
  });
  Object.assign(newMat, { ks_grade: "", diameter: "", unit_price: "", manufacturer: "", stock_available: true });
  showAddMaterial.value = false;
}

function removeMaterial(id) {
  materials.value = materials.value.filter((m) => m.id !== id);
}
</script>

<style scoped>
.profile-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 40px;
}

.back-btn {
  background: none;
  border: 1px solid #dde7f7;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  color: #4b6380;
  cursor: pointer;
  white-space: nowrap;
}

.page-header h1 { font-size: 28px; font-weight: 700; color: #102a56; margin: 0 0 4px; }
.page-sub { color: #71809a; font-size: 15px; margin: 0; }

.profile-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}

.card-title { font-size: 18px; font-weight: 700; color: #102a56; margin: 0 0 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.card-header .card-title { margin: 0; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
}
.span-2 { grid-column: span 2; }

.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; font-weight: 600; color: #4b6380; }
.form-group input,
.form-group select {
  border: 1px solid #dde7f7;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 15px;
  color: #102a56;
  outline: none;
}
.form-group input:focus,
.form-group select:focus { border-color: #1559e8; }

.checkbox-label { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #4b6380; cursor: pointer; }

.form-actions { display: flex; align-items: center; gap: 16px; margin-top: 24px; }

.btn-primary {
  background: #1559e8;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 10px 28px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.save-msg { font-size: 14px; color: #10b981; }

.btn-add {
  background: none;
  border: 1px dashed #1559e8;
  color: #1559e8;
  border-radius: 8px;
  padding: 6px 16px;
  font-size: 14px;
  cursor: pointer;
}

.empty-state { text-align: center; color: #aab4c4; padding: 32px; font-size: 15px; }

.material-list { display: flex; flex-direction: column; gap: 12px; }
.material-row {
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #f0f4fa;
  border-radius: 10px;
  padding: 14px 18px;
}
.mat-info { flex: 1; display: flex; align-items: center; gap: 12px; }
.mat-info strong { font-size: 15px; color: #102a56; }
.mat-price { font-size: 13px; color: #1559e8; font-weight: 600; }
.mat-meta { display: flex; gap: 16px; font-size: 13px; color: #71809a; }
.btn-remove {
  background: none;
  border: 1px solid #fca5a5;
  color: #dc2626;
  border-radius: 8px;
  padding: 5px 12px;
  font-size: 13px;
  cursor: pointer;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 20, 50, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal {
  background: #fff;
  border-radius: 20px;
  padding: 36px;
  width: 480px;
  max-width: 90vw;
}
.modal h3 { font-size: 20px; font-weight: 700; color: #102a56; margin: 0 0 24px; }
.modal-actions { display: flex; gap: 12px; margin-top: 24px; }
.btn-ghost {
  background: none;
  border: 1px solid #dde7f7;
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 15px;
  color: #71809a;
  cursor: pointer;
}
</style>
