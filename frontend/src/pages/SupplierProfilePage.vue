<template>
  <main class="supplier-profile-page">
    <header class="page-header">
      <div>
        <h1>자재 관리</h1>
        <p class="page-sub">회사 위치와 취급 자재 정보를 관리합니다. 등록한 자재는 추천 결과의 공급사 후보, 거리 계산, 납품 가능성 판단에 활용됩니다.</p>
      </div>
    </header>

    <section class="profile-card">
      <div class="card-header">
        <div>
          <h2 class="card-title">기본 정보</h2>
          <p>추천 후보에 표시할 회사 정보와 위치를 관리합니다.</p>
        </div>
        <span :class="['save-state', { saved: profileSaved }]">{{ profileSaved ? "저장 완료" : "저장 필요" }}</span>
      </div>

      <div class="form-grid">
        <label class="form-group">회사명<input v-model.trim="form.name" type="text" placeholder="회사명을 입력하세요" @input="markDirty" /></label>
        <label class="form-group">사업자 번호<input v-model.trim="form.businessNumber" type="text" placeholder="000-00-00000" @input="markDirty" /></label>
        <div class="form-group span-2">
          <AddressSearchField
            v-model="form.address"
            :zip-no="form.zipNo"
            label="주소"
            placeholder="도로명과 건물번호를 입력하세요"
            @selected="handleAddressSelected"
          />
        </div>
        <label class="form-group span-2">상세주소<input v-model.trim="form.detailAddress" type="text" placeholder="동·호수 또는 상세 위치" @input="markDirty" /></label>
        <label class="form-group">연락처<input v-model.trim="form.phone" type="text" placeholder="02-0000-0000" @input="markDirty" /></label>
        <label class="form-group">이메일<input v-model.trim="form.email" type="email" placeholder="contact@company.com" @input="markDirty" /></label>
      </div>

      <div v-if="form.latitude && form.longitude" class="coordinate-note">
        위치 좌표 저장됨 · {{ form.latitude }}, {{ form.longitude }}
      </div>
      <div class="form-actions">
        <span v-if="saveMessage" class="save-message">{{ saveMessage }}</span>
        <button class="btn-primary" type="button" :disabled="isSaving" @click="saveProfile">
          {{ isSaving ? "저장 중" : "기본 정보 저장" }}
        </button>
      </div>
    </section>

    <section class="profile-card materials-card">
      <div class="card-header">
        <div>
          <h2 class="card-title">취급 자재</h2>
          <p>등록한 자재는 추천 결과의 공급사 후보로 활용됩니다.</p>
        </div>
        <button class="btn-add" type="button" @click="openMaterialModal">+ 자재 추가</button>
      </div>

      <p v-if="materialError" class="error-message">{{ materialError }}</p>
      <div v-if="materials.length === 0" class="empty-state">
        아직 등록된 자재가 없습니다. 취급 가능한 자재를 추가하면 추천 결과의 공급사 후보로 노출됩니다.
      </div>
      <div v-else class="material-grid">
        <article v-for="material in materials" :key="material.id" class="material-card">
          <div class="material-topline">
            <span>{{ materialGroupOf(material) }}</span>
            <span :class="['stock-badge', { unavailable: !stockOf(material) }]">{{ stockOf(material) ? "재고 있음" : "재고 없음" }}</span>
          </div>
          <h3>{{ material.materialName || material.material_name || "자재명 확인 필요" }}</h3>
          <dl>
            <div><dt>규격</dt><dd>{{ specificationOf(material) }}</dd></div>
            <div><dt>KS 기준/등급</dt><dd>{{ ksStandardOf(material) }}</dd></div>
            <div><dt>단가</dt><dd>{{ priceOf(material) }}</dd></div>
            <div><dt>제조사</dt><dd>{{ material.manufacturer || "미등록" }}</dd></div>
          </dl>
          <p v-if="material.note" class="material-note">{{ material.note }}</p>
          <button class="btn-remove" type="button" @click="removeMaterial(material.id)">삭제</button>
        </article>
      </div>
    </section>

    <div v-if="showAddMaterial" class="modal-backdrop" @click.self="closeMaterialModal">
      <section class="material-modal" role="dialog" aria-modal="true" aria-labelledby="material-modal-title">
        <div class="modal-header">
          <div><p class="eyebrow">Supplier Material</p><h2 id="material-modal-title">취급 자재 추가</h2></div>
          <button class="modal-close" type="button" aria-label="닫기" @click="closeMaterialModal">×</button>
        </div>
        <div class="modal-grid">
          <label class="form-group">자재군
            <select v-model="newMaterial.materialGroup" required>
              <option value="" disabled>선택하세요</option>
              <option v-for="group in materialGroups" :key="group" :value="group">{{ group }}</option>
            </select>
          </label>
          <label class="form-group">자재명<input v-model.trim="newMaterial.materialName" placeholder="예: H형강" /></label>
          <label class="form-group">규격<input v-model.trim="newMaterial.specification" :placeholder="materialPlaceholder.specification" /></label>
          <label class="form-group">KS 기준/등급<input v-model.trim="newMaterial.ksStandard" :placeholder="materialPlaceholder.ksStandard" /></label>
          <label class="form-group">단가<input v-model="newMaterial.recentPrice" type="number" min="0" placeholder="예: 800000" /></label>
          <label class="form-group">단위<input v-model.trim="newMaterial.unit" :placeholder="materialPlaceholder.unit" /></label>
          <label class="form-group">제조사<input v-model.trim="newMaterial.manufacturer" placeholder="예: 현대제철" /></label>
          <label class="form-group stock-field">재고 여부
            <select v-model="newMaterial.stockAvailable"><option :value="true">재고 있음</option><option :value="false">재고 없음</option></select>
          </label>
          <label class="form-group span-2">비고<textarea v-model.trim="newMaterial.note" rows="3" placeholder="납품 조건이나 취급 특이사항을 입력하세요." /></label>
        </div>
        <p v-if="modalError" class="error-message">{{ modalError }}</p>
        <div class="modal-actions">
          <button class="btn-ghost" type="button" @click="closeMaterialModal">취소</button>
          <button class="btn-primary" type="button" :disabled="isAddingMaterial" @click="addMaterial">{{ isAddingMaterial ? "추가 중" : "추가" }}</button>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { authState, updateProfile } from "../api/authApi";
import { deleteSupplierMaterial, getSupplierMaterials, registerSupplierMaterial } from "../api/materialApi";
import AddressSearchField from "../components/AddressSearchField.vue";

const router = useRouter();
const materials = ref([]);
const isSaving = ref(false);
const isAddingMaterial = ref(false);
const profileSaved = ref(false);
const saveMessage = ref("");
const materialError = ref("");
const modalError = ref("");
const showAddMaterial = ref(false);
const profileStorageKey = computed(() => `paceflow_v2_supplier_profile:${authState.user?.id || authState.user?.email || "current"}`);
const materialGroups = ["철근", "형강/강재", "시멘트", "단열재", "전기 배관재"];

const form = reactive({
  name: "", businessNumber: "", address: "", detailAddress: "", zipNo: "",
  latitude: null, longitude: null, phone: "", email: "",
});
const newMaterial = reactive({
  materialGroup: "", materialName: "", specification: "", ksStandard: "",
  recentPrice: "", unit: "", manufacturer: "", stockAvailable: true, note: "",
});
const placeholderByGroup = {
  철근: { specification: "D10 / D13 / D16", ksStandard: "SD400 / SD500", unit: "원/톤" },
  "형강/강재": { specification: "H-250×250", ksStandard: "KS D 3503 / SS235", unit: "원/톤" },
  "전기 배관재": { specification: "16A / 22A / 28A", ksStandard: "KS C IEC 61386-1", unit: "원/본 또는 원/m" },
  시멘트: { specification: "1종 / 2종", ksStandard: "KS L 5210", unit: "원/포 또는 원/톤" },
  단열재: { specification: "24K / 32K", ksStandard: "KS L 9102", unit: "원/㎡" },
};
const materialPlaceholder = computed(() => placeholderByGroup[newMaterial.materialGroup] || {
  specification: "규격을 입력하세요", ksStandard: "KS 기준 또는 등급", unit: "예: 원/톤",
});

onMounted(async () => {
  restoreProfile();
  try {
    materials.value = await getSupplierMaterials();
  } catch {
    materialError.value = "등록 자재를 불러오지 못했습니다.";
  }
});

function restoreProfile() {
  try {
    const saved = JSON.parse(localStorage.getItem(profileStorageKey.value) || "null");
    if (saved) {
      Object.assign(form, saved);
      form.name = authState.user?.companyName || saved.name || "";
      form.email = authState.user?.email || saved.email || "";
      profileSaved.value = true;
    } else {
      form.name = authState.user?.companyName || "";
      form.email = authState.user?.email || "";
    }
  } catch {
    form.name = authState.user?.companyName || "";
    form.email = authState.user?.email || "";
  }
}

function markDirty() {
  profileSaved.value = false;
  saveMessage.value = "";
}

function handleAddressSelected(address) {
  form.address = address.fullRoadAddress || address.roadAddress || address.address || "";
  form.zipNo = address.zipNo || "";
  form.latitude = address.latitude ?? null;
  form.longitude = address.longitude ?? null;
  markDirty();
}

async function saveProfile() {
  try {
    isSaving.value = true;
    saveMessage.value = "";
    if (form.name.trim()) {
      await updateProfile({ companyName: form.name.trim() });
    }
    localStorage.setItem(profileStorageKey.value, JSON.stringify({ ...form }));
    materials.value = materials.value.map((material) => ({
      ...material,
      supplierName: form.name.trim() || material.supplierName,
      supplier_name: form.name.trim() || material.supplier_name,
    }));
    profileSaved.value = true;
    saveMessage.value = "공급사 정보가 저장되었습니다.";
  } catch {
    saveMessage.value = "공급사 정보를 저장하지 못했습니다.";
  } finally {
    isSaving.value = false;
  }
}

function openMaterialModal() {
  modalError.value = "";
  showAddMaterial.value = true;
}

function closeMaterialModal() {
  showAddMaterial.value = false;
  modalError.value = "";
}

function fullAddress() {
  return [form.address, form.detailAddress].filter(Boolean).join(" ");
}

async function addMaterial() {
  if (!newMaterial.materialGroup || !newMaterial.materialName || !newMaterial.specification) {
    modalError.value = "자재군, 자재명, 규격을 입력해주세요.";
    return;
  }
  try {
    isAddingMaterial.value = true;
    modalError.value = "";
    const material = await registerSupplierMaterial({
      supplierName: form.name || authState.user?.companyName || "공급사명 확인 필요",
      contact: form.phone,
      address: fullAddress(),
      zipNo: form.zipNo,
      latitude: form.latitude,
      longitude: form.longitude,
      mainMaterials: newMaterial.materialGroup,
      ...newMaterial,
    });
    materials.value = [material, ...materials.value];
    Object.assign(newMaterial, {
      materialGroup: "", materialName: "", specification: "", ksStandard: "",
      recentPrice: "", unit: "", manufacturer: "", stockAvailable: true, note: "",
    });
    closeMaterialModal();
  } catch (error) {
    modalError.value = error.response?.data?.error || "자재를 등록하지 못했습니다. 입력 정보와 로그인 상태를 확인해주세요.";
  } finally {
    isAddingMaterial.value = false;
  }
}

async function removeMaterial(id) {
  if (!window.confirm("이 자재를 삭제하시겠습니까?")) return;
  try {
    await deleteSupplierMaterial(id);
    materials.value = materials.value.filter((material) => String(material.id) !== String(id));
  } catch {
    materialError.value = "자재를 삭제하지 못했습니다.";
  }
}

function materialGroupOf(material) { return material.materialGroup || material.mainMaterials || material.main_materials || "자재군 미등록"; }
function specificationOf(material) { return material.specification || material.standard || material.diameter || "미등록"; }
function ksStandardOf(material) { return material.ksStandard || material.strengthGrade || material.ks_grade || "미등록"; }
function stockOf(material) { return material.stockAvailable ?? material.stock_available ?? true; }
function priceOf(material) {
  const price = material.recentPrice ?? material.unit_price;
  if (price === null || price === undefined || price === "") return "단가 미등록";
  return `${Number(price).toLocaleString()} ${material.unit || "원/톤"}`;
}
</script>

<style scoped>
.supplier-profile-page{width:min(1040px,calc(100% - 40px));margin:0 auto;padding:48px 0 80px}.page-header{display:flex;align-items:flex-start;gap:20px;margin-bottom:30px}.back-btn{flex:0 0 auto;border:1px solid #d8e4f5;border-radius:999px;padding:9px 15px;color:#4b6380;background:#fff;cursor:pointer}.eyebrow{margin:0 0 8px;color:#1559e8;font-size:13px;font-weight:900}.page-header h1{margin:0;color:#102a56;font-size:32px;line-height:1.1}.page-sub{max-width:760px;margin:10px 0 0;color:#65748d;line-height:1.7}.profile-card{margin-bottom:22px;border:1px solid #dbe6f8;border-radius:24px;padding:clamp(22px,4vw,32px);background:#fff;box-shadow:0 18px 55px rgba(31,61,115,.08)}.card-header{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:24px}.card-title{margin:0;color:#102a56;font-size:21px; font-weight: 800;}.card-header p{margin:7px 0 0;color:#71809a;font-size:14px}.save-state{border-radius:999px;padding:7px 11px;color:#9a5b00;background:#fff2cc;font-size:12px;font-weight:900;white-space:nowrap}.save-state.saved{color:#047857;background:#dcf8ed}.form-grid,.modal-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:17px 20px}.span-2{grid-column:1/-1}.form-group{display:grid;min-width:0;gap:7px;color:#4b6380;font-size:13px;font-weight:800}.form-group input,.form-group select,.form-group textarea{min-width:0;width:100%;box-sizing:border-box;border:1px solid #d5e1f2;border-radius:11px;padding:12px 13px;color:#102a56;background:#fff;font:inherit;font-weight:500;outline:none}.form-group input:focus,.form-group select:focus,.form-group textarea:focus{border-color:#1559e8;box-shadow:0 0 0 3px rgba(21,89,232,.08)}.coordinate-note{margin-top:14px;border-radius:10px;padding:10px 12px;color:#47705d;background:#effaf3;font-size:12px}.form-actions,.modal-actions{display:flex;align-items:center;justify-content:flex-end;gap:12px;margin-top:24px}.save-message{margin-right:auto;color:#047857;font-size:14px;font-weight:800}.btn-primary,.btn-add,.btn-ghost{border-radius:11px;padding:11px 19px;cursor:pointer;font-weight:900}.btn-primary{border:0;color:#fff;background:linear-gradient(135deg,#1559e8,#1f8df2)}.btn-primary:disabled{opacity:.55;cursor:not-allowed}.btn-add{border:1px solid #1559e8;color:#1559e8;background:#f5f8ff}.btn-ghost{border:1px solid #d5e1f2;color:#65748d;background:#fff}.empty-state{border:1px dashed #cbd9ee;border-radius:17px;padding:34px;color:#71809a;background:#f8faff;text-align:center;line-height:1.7}.material-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.material-card{position:relative;border:1px solid #dfe8f6;border-radius:18px;padding:18px;background:#fbfdff}.material-topline{display:flex;align-items:center;justify-content:space-between;gap:12px}.material-topline>span:first-child{color:#1559e8;font-size:12px;font-weight:900}.stock-badge{border-radius:999px;padding:5px 8px;color:#047857;background:#dcf8ed;font-size:11px;font-weight:900}.stock-badge.unavailable{color:#b42318;background:#fee7e7}.material-card h3{margin:13px 0;color:#102a56;font-size:19px}.material-card dl{display:grid;gap:8px;margin:0}.material-card dl div{display:grid;grid-template-columns:88px minmax(0,1fr);gap:8px;font-size:13px}.material-card dt{color:#8492a8}.material-card dd{margin:0;color:#40506a;font-weight:800}.material-note{margin:13px 0 0;border-radius:10px;padding:10px;color:#65748d;background:#f3f6fb;font-size:13px;line-height:1.5}.btn-remove{margin-top:14px;border:1px solid #fecaca;border-radius:9px;padding:7px 11px;color:#b42318;background:#fff;cursor:pointer}.modal-backdrop{position:fixed;inset:0;z-index:900;display:grid;place-items:center;padding:24px;background:rgba(8,24,54,.52)}.material-modal{overflow:auto;width:min(760px,100%);max-height:calc(100vh - 48px);box-sizing:border-box;border-radius:24px;padding:clamp(22px,4vw,34px);background:#fff;box-shadow:0 30px 90px rgba(0,0,0,.24)}.modal-header{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:24px}.modal-header h2{margin:0;color:#102a56}.modal-close{border:0;color:#65748d;background:transparent;cursor:pointer;font-size:28px}.error-message{color:#b42318}.address-search-field :deep(.address-search-row input){min-width:0}.address-search-field :deep(.address-search-row){display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px}@media(max-width:720px){.page-header{flex-direction:column}.form-grid,.modal-grid,.material-grid{grid-template-columns:1fr}.span-2{grid-column:auto}.card-header{align-items:flex-start;flex-direction:column}.btn-add{align-self:stretch}.material-modal{max-height:calc(100vh - 24px)}.modal-backdrop{padding:12px}}
</style>
