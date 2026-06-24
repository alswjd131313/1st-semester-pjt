<template>
  <section class="page-wrap">
    <!-- 페이지 헤더 -->
    <div class="page-heading">
      <h1>자재 조달 요청</h1>
      <p>필요한 자재와 현장 정보를 입력하시면<br>대체 가능한 자재와 최적의 공급사를 추천해드립니다.</p>
      <span class="time-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <path d="M12 7v5l3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        평균 1분 소요
      </span>
    </div>

    <!-- 스텝 인디케이터 -->
    <div class="step-indicator">
      <template v-for="(s, i) in steps" :key="i">
        <div :class="['step-item', stepStatus(i)]">
          <div :class="['step-circle', stepStatus(i)]">
            <svg v-if="stepStatus(i) === 'done'" width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span v-else>{{ i + 1 }}</span>
          </div>
          <div class="step-labels">
            <strong>{{ s.label }}</strong>
            <span>{{ s.sub }}</span>
          </div>
        </div>
        <div v-if="i < steps.length - 1" :class="['step-connector', { filled: stepStatus(i) === 'done' }]"></div>
      </template>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <form class="mrf" @submit.prevent="submitRequest">

      <!-- 1. 자재 정보 -->
      <div class="mrf-section">
        <div class="mrf-section-header">
          <span class="step-num">1</span>
          <strong>자재 정보</strong>
          <span class="section-hint">정확한 자재 정보를 입력할수록 더 정확한 추천을 받을 수 있습니다.</span>
        </div>

        <div class="mrf-body">
          <div class="mrf-row-2">
            <label class="mrf-label">
              자재명 <span class="req">*</span>
              <input v-model="form.materialName" type="text" placeholder="예: 철근" required />
            </label>
            <label class="mrf-label">
              KS 규격 <span class="req">*</span>
              <select v-model="form.standard" required>
                <option value="" disabled>선택하세요</option>
                <option v-for="s in KS_STANDARDS" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </label>
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

          <!-- 추가 조건 -->
          <div class="mrf-extra">
            <button type="button" class="mrf-extra-toggle" @click="expandedInfo = !expandedInfo">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path :d="expandedInfo ? 'M18 15l-6-6-6 6' : 'M6 9l6 6 6-6'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              추가 조건 입력 (선택)
              <svg class="extra-toggle-end" width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path :d="expandedInfo ? 'M18 15l-6-6-6 6' : 'M6 9l6 6 6-6'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>

            <div v-if="expandedInfo" class="mrf-extra-body">
              <label class="mrf-check">
                <input type="checkbox" v-model="form.allowGradeChange" />
                <span>재질/등급 변경 가능</span>
              </label>
              <label class="mrf-check">
                <input type="checkbox" v-model="form.subcontract" />
                <span>도급 여부</span>
              </label>
              <label class="mrf-check">
                <input type="checkbox" v-model="form.specifyManufacturer" />
                <span>제조사 지정</span>
              </label>
              <label class="mrf-check">
                <input type="checkbox" v-model="form.hasOtherReq" />
                <span>기타 요구사항</span>
              </label>
              <input
                class="extra-note-input"
                type="text"
                v-model="form.extraNote"
                placeholder="요청사항을 입력하세요"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 현장 정보 -->
      <div class="mrf-section">
        <div class="mrf-section-header">
          <span class="step-num">2</span>
          <strong>현장 정보</strong>
          <span class="section-hint">정확한 납품을 위해 현장 주소를 입력해주세요.</span>
        </div>

        <div class="mrf-body">
          <AddressSearchField
            v-model="form.siteAddress"
            label="현장 주소"
            :zip-no="form.siteZipNo"
            placeholder="예: 서울 성동구 아차산로 123"
            @selected="applySiteAddress"
          />
        </div>
      </div>

      <!-- 3. 납기 및 수량 -->
      <div class="mrf-section">
        <div class="mrf-section-header">
          <span class="step-num">3</span>
          <strong>납기 및 수량</strong>
          <span class="section-hint">납기 일정과 필요한 수량을 입력해주세요.</span>
        </div>

        <div class="mrf-body">
          <div class="mrf-row-delivery">
            <label class="mrf-label">
              필요 날짜 <span class="req">*</span>
              <div class="date-input-wrap">
                <input v-model="form.requiredDate" type="date" required />
              </div>
            </label>

            <label class="mrf-label">
              필요 수량 <span class="req">*</span>
              <div class="mrf-qty-row">
                <input v-model="form.quantity" type="number" min="1" placeholder="10,000" required />
                <select v-model="form.unit">
                  <option v-for="u in UNITS" :key="u" :value="u">{{ u }}</option>
                </select>
              </div>
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
          </div>
        </div>
      </div>

      <!-- 4. 요청 메모 -->
      <div class="mrf-section">
        <div class="mrf-section-header">
          <span class="step-num">4</span>
          <strong>요청 메모</strong>
          <span class="section-hint">공급사에게 전달할 추가 요청사항이 있다면 입력해주세요.</span>
        </div>

        <div class="mrf-body">
          <label class="mrf-label">
            요청 내용
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
      </div>

      <!-- 액션 바 -->
      <div class="form-actions">
        <button type="button" class="btn-save-draft">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          임시 저장
        </button>
        <div class="form-actions-right">
          <RouterLink class="btn-cancel" to="/">취소</RouterLink>
          <button type="submit" class="btn-submit" :disabled="isSubmitting">
            {{ isSubmitting ? '저장 중…' : '공급사 추천 받기 →' }}
          </button>
        </div>
      </div>

      <p class="form-disclaimer">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
          <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        입력하신 정보는 안전하게 저장되며, 추천 이외의 용도로 사용되지 않습니다.
      </p>
    </form>
  </section>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
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

const steps = [
  { label: '자재 정보', sub: '필요 자재의 상세 정보' },
  { label: '현장 정보', sub: '납품 현장 주소 및 정보' },
  { label: '납기 및 수량', sub: '납기 일정 및 수량 설정' },
  { label: '요청 메모', sub: '추가 요청사항 입력' },
]

const route = useRoute()
const router = useRouter()
const keyword = String(route.query.keyword || '')
const isSubmitting = ref(false)
const errorMessage = ref('')
const expandedInfo = ref(false)

const stepDone = computed(() => [
  !!(form.materialName && form.standard && form.strengthGrade && form.size),
  !!(form.siteAddress && Number.isFinite(form.siteLat) && Number.isFinite(form.siteLng)),
  !!(form.requiredDate && form.quantity),
  !!form.memo,
])

function stepStatus(i) {
  if (stepDone.value[i]) return 'done'
  const firstIncomplete = stepDone.value.findIndex(v => !v)
  if (i === firstIncomplete) return 'active'
  return 'inactive'
}

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
  allowGradeChange: false,
  subcontract: false,
  specifyManufacturer: false,
  hasOtherReq: false,
  extraNote: '',
})

async function submitRequest() {
  if (!Number.isFinite(form.siteLat) || !Number.isFinite(form.siteLng)) {
    errorMessage.value = '주소 검색 결과에서 현장 주소를 선택해 주세요.'
    return
  }

  const extraParts = [
    form.allowGradeChange && '재질/등급 변경 가능',
    form.subcontract && '도급 여부 있음',
    form.specifyManufacturer && '제조사 지정',
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
/* ── 페이지 헤더 ── */
.page-heading {
  margin-bottom: 28px;
}

.page-heading h1 {
  font-size: 32px;
  font-weight: 900;
  color: #102a56;
  margin: 0 0 10px;
  letter-spacing: -0.03em;
}

.page-heading p {
  font-size: 16px;
  color: #65748d;
  line-height: 1.7;
  margin: 0 0 14px;
}

.time-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #dde7f7;
  border-radius: 999px;
  padding: 5px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #4b6380;
  background: #fff;
}

/* ── 스텝 인디케이터 ── */
.step-indicator {
  display: flex;
  align-items: flex-start;
  background: #fff;
  border: 1px solid #e2eaf5;
  border-radius: 16px;
  padding: 22px 32px;
  margin-bottom: 20px;
  gap: 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
  position: relative;
}

.step-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e9eef8;
  color: #8fa3be;
  font-size: 15px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.25s, color 0.25s;
}

.step-circle.active {
  background: #1559e8;
  color: #fff;
}

.step-circle.done {
  background: #1559e8;
  color: #fff;
}

.step-labels {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.step-labels strong {
  font-size: 13px;
  font-weight: 700;
  color: #8fa3be;
  white-space: nowrap;
  transition: color 0.25s;
}

.step-item.active .step-labels strong,
.step-item.done .step-labels strong {
  color: #102a56;
}

.step-labels span {
  font-size: 11px;
  color: #aab4c4;
  white-space: nowrap;
}

.step-connector {
  flex: 1;
  height: 2px;
  border: none;
  background: repeating-linear-gradient(
    90deg,
    #d4e0f4 0px,
    #d4e0f4 6px,
    transparent 6px,
    transparent 12px
  );
  margin: 0 10px;
  align-self: center;
  margin-top: -14px;
  transition: background 0.3s;
}

.step-connector.filled {
  background: #1559e8;
  border-radius: 2px;
}

/* ── 폼 ── */
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
  padding: 18px 24px;
  border-bottom: 1px solid #f0f4fa;
}

.step-num {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #1559e8;
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mrf-section-header strong {
  font-size: 16px;
  font-weight: 800;
  color: #102a56;
}

.section-hint {
  font-size: 13px;
  color: #8fa3be;
  font-weight: 500;
}

/* ── 폼 본문 ── */
.mrf-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mrf-row-2,
.mrf-row-3,
.mrf-row-delivery {
  display: grid;
  gap: 16px;
}

.mrf-row-2 { grid-template-columns: 1fr 1fr; }
.mrf-row-3 { grid-template-columns: 1fr 1fr 1fr; align-items: end; }
.mrf-row-delivery { grid-template-columns: 1fr 1fr auto; align-items: start; }

.mrf-section :deep(.address-search-field) {
  padding: 0;
}

.mrf-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.req { color: #1559e8; }

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
  box-shadow: 0 0 0 3px rgba(21, 89, 232, 0.08);
}

/* ── 추가 조건 ── */
.mrf-extra {
  border-top: 1px solid #f0f4fa;
  margin: 0 -24px -20px;
}

.mrf-extra-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 14px 24px;
  border: 0;
  background: none;
  font-size: 14px;
  font-weight: 600;
  color: #4b6380;
  cursor: pointer;
  text-align: left;
}

.extra-toggle-end {
  margin-left: auto;
}

.mrf-extra-toggle:hover { color: #1559e8; }

.mrf-extra-body {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  padding: 12px 24px 18px;
  border-top: 1px solid #f0f4fa;
  background: #fafbff;
}

.mrf-check {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  white-space: nowrap;
}

.mrf-check input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #1559e8;
  cursor: pointer;
  flex-shrink: 0;
}

.extra-note-input {
  flex: 1;
  min-width: 160px;
  min-height: 40px;
  border: 1px solid #dde7f7;
  border-radius: 10px;
  padding: 0 12px;
  font-size: 14px;
  font: inherit;
  color: #102a56;
  background: #fff;
  outline: 0;
}
.extra-note-input:focus {
  border-color: #1559e8;
  box-shadow: 0 0 0 3px rgba(21, 89, 232, 0.08);
}

/* ── 납기 ── */
.date-input-wrap { position: relative; }

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
.mrf-qty-row select { width: 84px; flex-shrink: 0; }

/* ── 텍스트에어리어 ── */
.mrf-textarea-wrap { position: relative; }

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

.mrf-label textarea:focus {
  border-color: #1559e8;
  box-shadow: 0 0 0 3px rgba(21, 89, 232, 0.08);
}

.mrf-char-count {
  position: absolute;
  right: 14px;
  bottom: 12px;
  font-size: 12px;
  color: #8fa3be;
  font-weight: 700;
}

/* ── 액션 바 ── */
.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 4px;
}

.form-actions-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-save-draft {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid #dde7f7;
  background: #fff;
  color: #4b6380;
  border-radius: 12px;
  padding: 12px 22px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  font: inherit;
  transition: border-color 0.15s, color 0.15s;
}
.btn-save-draft:hover { border-color: #1559e8; color: #1559e8; }

.btn-cancel {
  border: 1px solid #dde7f7;
  background: #fff;
  color: #4b6380;
  border-radius: 12px;
  padding: 12px 22px;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: border-color 0.15s;
}
.btn-cancel:hover { border-color: #aab4c4; }

.btn-submit {
  background: #1559e8;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 12px 28px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  font: inherit;
  transition: background 0.15s, box-shadow 0.15s;
  white-space: nowrap;
}
.btn-submit:hover:not(:disabled) {
  background: #1047c5;
  box-shadow: 0 8px 20px rgba(21, 89, 232, 0.28);
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

.form-disclaimer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: #aab4c4;
  margin: 4px 0 0;
}

/* ── 에러 ── */
.error-message {
  background: #fff5f5;
  border: 1px solid #fca5a5;
  color: #dc2626;
  border-radius: 12px;
  padding: 14px 18px;
  font-size: 14px;
  font-weight: 600;
}

/* ── 반응형 ── */
@media (max-width: 700px) {
  .mrf-row-2,
  .mrf-row-3,
  .mrf-row-delivery {
    grid-template-columns: 1fr;
  }

  .step-indicator {
    padding: 18px 20px;
  }

  .step-labels span { display: none; }

  .form-actions { flex-wrap: wrap; }
}
</style>
