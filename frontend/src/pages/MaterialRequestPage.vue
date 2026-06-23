<template>
  <section class="page-wrap">
    <div class="page-heading">
      <h1>자재 조달 요청</h1>
      <p>현장에 필요한 자재 정보를 등록하고 조달 가능 공급사를 찾습니다.</p>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <form class="mrf" @submit.prevent="submitRequest">

      <!-- 1. 자재 정보 -->
      <div class="mrf-section">
        <div class="mrf-section-header">
          <span class="mrf-sec-icon mrf-blue">🔩</span>
          <strong>1. 자재 정보</strong>
        </div>

        <div class="mrf-row-2">
          <label class="mrf-label">
            자재명 <span class="req">*</span>
            <input v-model="form.materialName" type="text" placeholder="예: 철근" required />
          </label>
          <div class="mrf-label">
            KS 규격 <span class="req">*</span>
            <div class="mrf-row-std">
              <select v-model="form.standard" required>
                <option value="" disabled>선택하세요</option>
                <option v-for="s in KS_STANDARDS" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="mrf-row-3">
          <label class="mrf-label">
            강도 등급 <span class="req">*</span>
            <select v-model="form.strengthGrade" required>
              <option value="" disabled>선택하세요</option>
              <option v-for="g in STRENGTH_GRADES" :key="g" :value="g">{{ g }}</option>
            </select>
          </label>
          <label class="mrf-label">
            직경 / 사이즈 <span class="req">*</span>
            <input v-model="form.size" type="text" placeholder="예: D10" required />
          </label>
          <label class="mrf-label">
            형태
            <input v-model="form.shape" type="text" placeholder="예: H형강, 앵글 등 (선택)" />
          </label>
        </div>

        <div class="mrf-expand" :class="{ open: expandedInfo }">
          <button type="button" class="mrf-expand-header" @click="expandedInfo = !expandedInfo">
            <span class="mrf-expand-star">✦</span>
            <div class="mrf-expand-text">
              <strong>자재 정보를 더 정확하게 입력해보세요!</strong>
              <span>상세한 정보를 입력할수록 더 정확한 대체 자재와 공급사를 추천받을 수 있습니다.</span>
            </div>
            <span class="mrf-expand-arrow">{{ expandedInfo ? '▲' : '▼' }}</span>
          </button>

          <div v-if="!expandedInfo" class="mrf-expand-tags">
            <button type="button" v-for="tag in EXTRA_TAGS" :key="tag" class="mrf-tag" @click="expandedInfo = true">
              {{ tag }}
            </button>
          </div>

          <div v-if="expandedInfo" class="mrf-expand-body">
            <label class="mrf-label">
              재질 / 등급 변경 요청
              <input v-model="form.extraGradeNote" type="text" placeholder="예: SS275 → SS355 상향 가능" />
            </label>
            <label class="mrf-label">
              제조사 선호 조건
              <input v-model="form.manufacturer" type="text" placeholder="예: 현대제철, POSCO 우선" />
            </label>
            <label class="mrf-label mrf-full">
              기타 요구사항
              <input v-model="form.extraNote" type="text" placeholder="도급 여부, 포장 조건 등 추가 요청사항" />
            </label>
          </div>
        </div>
      </div>

      <!-- 2. 현장 정보 -->
      <div class="mrf-section">
        <div class="mrf-section-header">
          <span class="mrf-sec-icon mrf-purple">📍</span>
          <strong>2. 현장 정보</strong>
        </div>

        <AddressSearchField
          v-model="form.siteAddress"
          label="현장 주소"
          :zip-no="form.siteZipNo"
          placeholder="예: 서울 성동구 아차산로 123"
          @selected="applySiteAddress"
        />
      </div>

      <!-- 3. 납기 및 수량 -->
      <div class="mrf-section">
        <div class="mrf-section-header">
          <span class="mrf-sec-icon mrf-teal">📅</span>
          <strong>3. 납기 및 수량</strong>
        </div>

        <div class="mrf-row-delivery">
          <label class="mrf-label">
            필요 날짜 <span class="req">*</span>
            <input v-model="form.requiredDate" type="date" required />
          </label>

          <fieldset class="mrf-label mrf-fieldset">
            <legend>긴급 여부</legend>
            <div class="mrf-radio-group">
              <label class="mrf-radio">
                <input v-model="form.isUrgent" type="radio" :value="false" />
                <span>일반</span>
              </label>
              <label class="mrf-radio">
                <input v-model="form.isUrgent" type="radio" :value="true" />
                <span>긴급</span>
              </label>
            </div>
          </fieldset>

          <label class="mrf-label">
            필요 수량 <span class="req">*</span>
            <div class="mrf-qty-row">
              <input v-model="form.quantity" type="number" min="1" placeholder="10,000" required />
              <select v-model="form.unit">
                <option v-for="u in UNITS" :key="u" :value="u">{{ u }}</option>
              </select>
            </div>
          </label>
        </div>
      </div>

      <!-- 4. 요청 메모 -->
      <div class="mrf-section">
        <div class="mrf-section-header">
          <span class="mrf-sec-icon mrf-green">✏️</span>
          <strong>4. 요청 메모</strong>
        </div>

        <label class="mrf-label">
          공급사에게 전달할 메모 (선택)
          <div class="mrf-textarea-wrap">
            <textarea
              v-model="form.memo"
              rows="4"
              maxlength="500"
              placeholder="추가로 전달하고 싶은 내용이 있다면 입력해주세요."
            />
            <span class="mrf-char-count">{{ form.memo.length }} / 500</span>
          </div>
        </label>
      </div>

      <div class="form-actions">
        <RouterLink class="secondary-button" to="/">취소</RouterLink>
        <button type="submit" class="primary-button" :disabled="isSubmitting">
          {{ isSubmitting ? '요청 저장 중' : '요청 등록하기' }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createMaterialRequest } from '../api/materialApi'
import { categories } from '../data/dummyData'
import AddressSearchField from '../components/AddressSearchField.vue'

const KS_STANDARDS = [
  { value: 'KS D 3504', label: 'KS D 3504 — 철근 콘크리트용 봉강' },
  { value: 'KS D 3503', label: 'KS D 3503 — 일반구조용 압연강재' },
  { value: 'KS D 3502', label: 'KS D 3502 — 열간 압연 형강' },
  { value: 'KS D 3566', label: 'KS D 3566 — 일반구조용 탄소강관' },
  { value: 'KS D 3568', label: 'KS D 3568 — 일반구조용 각형강관' },
  { value: 'KS F 2563', label: 'KS F 2563 — 포틀랜드 시멘트' },
  { value: 'KS F 2561', label: 'KS F 2561 — 고로슬래그 시멘트' },
]

const STRENGTH_GRADES = ['SD300', 'SD400', 'SD500', 'SD600', 'SM275', 'SM355', 'SM420', 'SS275', 'SS355']

const UNITS = ['kg', 'ton', '개', 'm', 'm²', 'm³', 'bag']

const EXTRA_TAGS = ['재질/등급 변경', '도급 여부', '제조사', '기타 요구사항']

const route = useRoute()
const router = useRouter()
const keyword = String(route.query.keyword || '')
const isSubmitting = ref(false)
const errorMessage = ref('')
const expandedInfo = ref(false)

const form = reactive({
  materialName: parseMaterialName(keyword),
  category: parseCategory(keyword),
  standard: keyword.includes('SD') ? 'KS D 3504' : '',
  strengthGrade: keyword.includes('SD') ? extractGrade(keyword) : '',
  size: extractSize(keyword),
  shape: '',
  quantity: '',
  unit: 'ton',
  siteAddress: '',
  siteZipNo: '',
  siteLat: null,
  siteLng: null,
  requiredDate: '',
  isUrgent: false,
  memo: '',
  extraGradeNote: '',
  manufacturer: '',
  extraNote: '',
})

async function submitRequest() {
  if (!Number.isFinite(form.siteLat) || !Number.isFinite(form.siteLng)) {
    errorMessage.value = '주소 검색 결과에서 현장 주소를 선택해 주세요.'
    return
  }

  const extraParts = [
    form.extraGradeNote && `재질/등급: ${form.extraGradeNote}`,
    form.manufacturer && `제조사: ${form.manufacturer}`,
    form.extraNote && form.extraNote,
    form.memo,
  ].filter(Boolean)

  const payload = {
    materialName: form.materialName,
    category: form.category,
    standard: form.standard,
    strengthGrade: [form.strengthGrade, form.size].filter(Boolean).join(' / '),
    requiredQuantity: `${form.quantity}${form.unit}`,
    siteAddress: form.siteAddress,
    siteZipNo: form.siteZipNo,
    siteLat: form.siteLat,
    siteLng: form.siteLng,
    requiredDate: form.requiredDate,
    isUrgent: form.isUrgent,
    memo: extraParts.join('\n'),
  }

  try {
    isSubmitting.value = true
    errorMessage.value = ''
    await createMaterialRequest(payload)
    router.push('/inquiries')
  } catch (error) {
    errorMessage.value =
      getApiErrorMessage(error) ||
      '자재 요청을 저장하지 못했습니다. 잠시 후 다시 시도해주세요.'
  } finally {
    isSubmitting.value = false
  }
}

function applySiteAddress(address) {
  form.siteAddress = address.roadAddress
  form.siteZipNo = address.zipNo
  form.siteLat = roundCoordinate(address.latitude)
  form.siteLng = roundCoordinate(address.longitude)
}

function roundCoordinate(value) {
  return Number(Number(value).toFixed(6))
}

function getApiErrorMessage(error) {
  const data = error.response?.data
  if (!data) return ''
  if (typeof data.error === 'string') return data.error
  return Object.values(data).flat().filter(Boolean).join(' ')
}

function parseMaterialName(value) {
  return value ? value.split(' ')[0] || '' : ''
}

function extractGrade(value) {
  const match = value.match(/SD\d+/)
  return match ? match[0] : ''
}

function extractSize(value) {
  const match = value.match(/D\d+|[0-9]+x[0-9]+|[0-9]+A/)
  return match ? match[0] : ''
}

function parseCategory(value) {
  return categories.find((c) => value.includes(c.name))?.name || ''
}
</script>

<style scoped>
.mrf {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mrf-section {
  border: 1px solid #e2eaf5;
  border-radius: 20px;
  background: #fff;
  overflow: hidden;
}

.mrf-section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f4fa;
  font-size: 17px;
  font-weight: 800;
  color: #102a56;
}

.mrf-sec-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  font-size: 18px;
}

.mrf-blue { background: #eef5ff; }
.mrf-purple { background: #f5f3ff; }
.mrf-teal { background: #e0f9ff; }
.mrf-green { background: #ecfdf5; }

.mrf-row-2,
.mrf-row-3,
.mrf-row-delivery {
  display: grid;
  gap: 16px;
  padding: 20px 24px;
}

.mrf-row-2 { grid-template-columns: 1fr 1fr; }
.mrf-row-3 { grid-template-columns: 1fr 1fr 1fr; padding-top: 0; }
.mrf-row-delivery { grid-template-columns: 1fr auto 1fr; align-items: start; }

.mrf-section :deep(.address-search-field) {
  padding: 20px 24px;
}

.mrf-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.mrf-full {
  grid-column: 1 / -1;
}

.req {
  color: #1559e8;
}

.mrf-label input,
.mrf-label select {
  width: 100%;
  min-height: 48px;
  border: 1px solid #dde7f7;
  border-radius: 12px;
  padding: 0 14px;
  color: #102a56;
  background: #fff;
  font-size: 15px;
  font: inherit;
  outline: 0;
  transition: border-color 0.15s;
}

.mrf-label input:focus,
.mrf-label select:focus {
  border-color: #1559e8;
}

.mrf-row-std {
  display: flex;
  gap: 10px;
}

.mrf-row-std select { flex: 1; }

.mrf-fieldset {
  border: 0;
  padding: 0;
  margin: 0;
}

.mrf-fieldset legend {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 8px;
}

.mrf-radio-group {
  display: flex;
  gap: 20px;
  align-items: center;
  min-height: 48px;
}

.mrf-radio {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 700;
  color: #334155;
}

.mrf-radio input[type="radio"] {
  width: 18px;
  min-height: 18px;
  accent-color: #1559e8;
}

.mrf-qty-row {
  display: flex;
  gap: 8px;
}

.mrf-qty-row input { flex: 1; }
.mrf-qty-row select { width: 80px; flex-shrink: 0; }

.mrf-textarea-wrap {
  position: relative;
}

.mrf-label textarea {
  width: 100%;
  min-height: 120px;
  border: 1px solid #dde7f7;
  border-radius: 12px;
  padding: 14px 16px;
  color: #102a56;
  background: #fff;
  font: inherit;
  font-size: 15px;
  resize: vertical;
  outline: 0;
  transition: border-color 0.15s;
  display: block;
}

.mrf-label textarea:focus { border-color: #1559e8; }

.mrf-char-count {
  position: absolute;
  right: 14px;
  bottom: 12px;
  font-size: 12px;
  color: #8fa3be;
  font-weight: 700;
}

.mrf-expand {
  border-top: 1px solid #f0f4fa;
}

.mrf-expand-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  padding: 16px 24px;
  border: 0;
  background: #fafbff;
  cursor: pointer;
  text-align: left;
}

.mrf-expand.open .mrf-expand-header {
  background: #f5f8ff;
}

.mrf-expand-star {
  color: #1559e8;
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.mrf-expand-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mrf-expand-text strong {
  font-size: 14px;
  color: #1559e8;
}

.mrf-expand-text span {
  font-size: 13px;
  color: #65748d;
  line-height: 1.5;
}

.mrf-expand-arrow {
  font-size: 13px;
  color: #8fa3be;
  margin-top: 2px;
  flex-shrink: 0;
}

.mrf-expand-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 24px 16px;
  background: #fafbff;
}

.mrf-tag {
  border: 1px solid #dde7f7;
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}

.mrf-tag:hover {
  border-color: #1559e8;
  color: #1559e8;
}

.mrf-expand-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px 24px 20px;
}

@media (max-width: 700px) {
  .mrf-row-2,
  .mrf-row-3,
  .mrf-row-delivery,
  .mrf-expand-body {
    grid-template-columns: 1fr;
  }
}
</style>
