<template>
  <section class="page-wrap">
    <!-- 페이지 헤더 -->
    <div class="page-heading">
      <h1>자재 조달 요청</h1>
      <p>필요한 자재와 현장 정보를 입력하시면<br>대체 가능한 자재와 최적의 공급사를 추천해드립니다.</p>
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
    <p v-if="successMessage" class="success-message">{{ successMessage }}</p>

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
              KS 규격
              <select v-model="form.standard">
                <option value="">선택 안함</option>
                <option v-for="s in currentMaterialOptions.ksStandards" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </label>
          </div>

          <div class="mrf-row-3">
            <label class="mrf-label">
              강도 등급
              <select v-model="form.strengthGrade">
                <option value="">선택 안함</option>
                <option v-for="g in currentMaterialOptions.strengthGrades" :key="g" :value="g">{{ g }}</option>
              </select>
            </label>
            <label class="mrf-label">
              직경 / 사이즈
              <input
                v-model.trim="form.size"
                type="text"
                :list="sizeDatalistId"
                :placeholder="currentMaterialOptions.sizePlaceholder"
              />
              <datalist :id="sizeDatalistId">
                <option v-for="size in currentMaterialOptions.sizes" :key="size" :value="size" />
              </datalist>
            </label>
            <label class="mrf-label">
              형태
              <select v-model="form.shape">
                <option value="">선택 안함</option>
                <option v-for="shape in currentMaterialOptions.shapes" :key="shape" :value="shape">{{ shape }}</option>
              </select>
            </label>
          </div>
          <p class="material-option-help">
            규격을 모르는 경우 선택 안함으로 두면 더 넓은 후보군을 추천받을 수 있습니다. 정확한 규격을 입력할수록 추천 정확도가 높아집니다.
          </p>

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
              <label class="extra-field">
                <span>재질 / 등급 변경 요청</span>
                <input
                  class="extra-note-input"
                  type="text"
                  v-model="form.extraGradeNote"
                  placeholder="예: SS275 → SS355 상향 가능"
                />
              </label>
              <label class="extra-field">
                <span>제조사 선호 조건</span>
                <input
                  class="extra-note-input"
                  type="text"
                  v-model="form.manufacturer"
                  placeholder="예: 현대제철, POSCO 우선"
                />
              </label>
              <label class="extra-field extra-field-wide">
                <span>기타 요구사항</span>
                <input
                  class="extra-note-input"
                  type="text"
                  v-model="form.extraNote"
                  placeholder="도급 여부, 포장 조건 등 추가 요청사항"
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 현장 정보 -->
      <div class="mrf-section" ref="siteSectionRef">
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
        <button type="button" class="btn-save-draft" :disabled="isDraftSaving" @click="saveDraft">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          {{ isDraftSaving ? '저장 중…' : '임시 저장' }}
        </button>
        <div class="form-actions-right">
          <RouterLink class="btn-cancel" to="/">취소</RouterLink>
          <button type="submit" class="btn-submit" :disabled="isSubmitting">
            {{ isSubmitting ? '추천 준비 중…' : '공급사 추천 받기 →' }}
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authState } from '../api/authApi'
import { createMaterialRequest, getMaterialRequestDraft, saveMaterialRequestDraft } from '../api/materialApi'
import { categories } from '../data/dummyData'
import AddressSearchField from '../components/AddressSearchField.vue'

const MATERIAL_OPTION_MAP = {
  rebar: {
    labels: ['철근', '이형철근', '원형철근'],
    category: '철근',
    ksStandards: [
      { value: 'KS D 3504', label: 'KS D 3504 — 철근 콘크리트용 봉강' },
    ],
    strengthGrades: ['SD300', 'SD400', 'SD500', 'SD600'],
    shapes: ['이형철근', '원형철근'],
    sizes: ['D10', 'D13', 'D16', 'D19', 'D22', 'D25'],
    sizePlaceholder: '선택 안함 또는 예: D13',
  },
  hbeam: {
    labels: ['H빔', 'H형강', '형강', '강재', '철강빔'],
    category: '형강·강재',
    ksStandards: [
      { value: 'KS D 3503', label: 'KS D 3503 — 일반구조용 압연강재' },
      { value: 'KS D 3502', label: 'KS D 3502 — 열간 압연 형강' },
    ],
    strengthGrades: ['SS275', 'SS355', 'SM275', 'SM355', 'SM420'],
    shapes: ['H형강', '형강', '강재'],
    sizes: ['H-100x100', 'H-150x150', 'H-200x200', 'H-300x300'],
    sizePlaceholder: '선택 안함 또는 예: H-200x200',
  },
  cement: {
    labels: ['시멘트', '포틀랜드 시멘트', '고로슬래그 시멘트', '벌크시멘트'],
    category: '시멘트',
    ksStandards: [
      { value: 'KS L 5201', label: 'KS L 5201 — 포틀랜드 시멘트' },
      { value: 'KS L 5210', label: 'KS L 5210 — 고로슬래그 시멘트' },
    ],
    strengthGrades: [],
    shapes: ['포틀랜드 시멘트', '벌크시멘트', '1종 시멘트', '고로슬래그 시멘트'],
    sizes: ['40kg 포대', '벌크'],
    sizePlaceholder: '선택 안함 또는 예: 40kg 포대',
  },
  insulation: {
    labels: ['단열재', '글라스울', 'EPS', 'XPS', '보온판', '발포폴리스티렌'],
    category: '단열재',
    ksStandards: [
      { value: 'KS M 3880', label: 'KS M 3880 — 단열재 관련 규격' },
      { value: 'KS M 3871', label: 'KS M 3871 — 발포 플라스틱 보온재' },
      { value: 'KS M ISO 4898', label: 'KS M ISO 4898 — 발포 플라스틱 단열재' },
    ],
    strengthGrades: [],
    shapes: ['EPS', 'XPS', '글라스울', '발포폴리스티렌단열재', '압출법보온판', '비드법보온판'],
    sizes: ['50T', '75T', '100T'],
    sizePlaceholder: '선택 안함 또는 예: 100T',
  },
  conduit: {
    labels: ['전선관', '가요 전선관', '합성수지제 전선관', 'CD관', 'PF관'],
    category: '전기 배관재',
    ksStandards: [
      { value: 'KS C 8401', label: 'KS C 8401 — 강제 전선관' },
      { value: 'KS C 8431', label: 'KS C 8431 — 경질 폴리염화비닐 전선관' },
      { value: 'KS C 8454', label: 'KS C 8454 — 합성수지제 가요 전선관' },
    ],
    strengthGrades: [],
    shapes: ['전선관', '가요 전선관', '합성수지제 전선관', 'CD관', 'PF관'],
    sizes: ['16F', '22F', '28F', '36F'],
    sizePlaceholder: '선택 안함 또는 예: 22F',
  },
  generic: {
    labels: [],
    category: '',
    ksStandards: [],
    strengthGrades: [],
    shapes: [],
    sizes: [],
    sizePlaceholder: '선택 안함 또는 직접 입력',
  },
}
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
const isDraftSaving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const expandedInfo = ref(false)
const siteSectionRef = ref(null)
const sizeDatalistId = 'material-size-options'

const stepDone = computed(() => [
  !!form.materialName,
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
  draftId: null,
  category: parseCategory(keyword),
  standard: '',
  strengthGrade: '',
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

const currentMaterialKey = computed(() => getMaterialOptionKey(form.materialName))
const currentMaterialOptions = computed(() => MATERIAL_OPTION_MAP[currentMaterialKey.value] || MATERIAL_OPTION_MAP.generic)

applyKeywordOptions(keyword)
applyDefaultSiteFromProfile()
onMounted(loadDraft)

watch(currentMaterialKey, (next, previous) => {
  if (next === previous) return
  resetMaterialSpecificOptions()
  form.category = currentMaterialOptions.value.category || parseCategory(form.materialName)
})

async function submitRequest() {
  const validationMessage = validateForRecommendation()
  if (validationMessage) {
    errorMessage.value = validationMessage
    successMessage.value = ''
    if (validationMessage.includes('현장')) scrollToSiteSection()
    return
  }

  try {
    isSubmitting.value = true
    errorMessage.value = ''
    successMessage.value = ''
    const saved = await createMaterialRequest(buildRequestPayload())
    router.push({
      name: 'recommendation',
      query: {
        requestId: saved.backendDemandId || saved.id,
        keyword: form.materialName,
      },
    })
  } catch (error) {
    errorMessage.value =
      getApiErrorMessage(error) ||
      error.message ||
      '자재 요청을 저장하지 못했습니다. 잠시 후 다시 시도해주세요.'
  } finally {
    isSubmitting.value = false
  }
}

async function saveDraft() {
  try {
    isDraftSaving.value = true
    errorMessage.value = ''
    successMessage.value = ''
    const draft = await saveMaterialRequestDraft(buildRequestPayload())
    form.draftId = draft.draftId || draft.id || form.draftId
    successMessage.value = '임시 저장되었습니다.'
  } catch (error) {
    errorMessage.value =
      getApiErrorMessage(error) ||
      error.message ||
      '임시 저장에 실패했습니다. 잠시 후 다시 시도해주세요.'
  } finally {
    isDraftSaving.value = false
  }
}

async function loadDraft() {
  const draft = await getMaterialRequestDraft()
  if (draft) applyDraftToForm(draft)
}

function validateForRecommendation() {
  if (!form.siteAddress?.trim()) {
    return '현장 주소를 입력해야 거리 기반 추천이 가능합니다. 주소 검색으로 현장 주소를 선택해 주세요.'
  }
  if (!Number.isFinite(form.siteLat) || !Number.isFinite(form.siteLng)) {
    return '현장 주소의 위도/경도가 없어 거리 계산을 할 수 없습니다. 주소 검색 결과에서 현장 주소를 다시 선택해 주세요.'
  }
  if (!form.materialName?.trim()) {
    return '추천받을 자재명을 입력해주세요.'
  }
  const combinationMessage = validateMaterialOptionCombination()
  if (combinationMessage) {
    return combinationMessage
  }
  if (!form.quantity || Number(form.quantity) <= 0) {
    return '추천받을 수량을 입력해주세요.'
  }
  if (!form.unit) {
    return '수량 단위를 선택해주세요.'
  }
  if (!form.requiredDate) {
    return '희망 납기일을 입력해주세요.'
  }
  return ''
}

function buildRequestPayload() {
  const extraParts = [
    form.extraGradeNote && `재질/등급: ${form.extraGradeNote}`,
    form.manufacturer && `제조사: ${form.manufacturer}`,
    form.extraNote && form.extraNote,
    form.memo,
  ].filter(Boolean)

  return {
    draftId: form.draftId,
    materialName: form.materialName,
    category: form.category,
    standard: form.standard,
    shape: form.shape,
    strengthGrade: [form.strengthGrade, form.shape, form.size].filter(Boolean).join(' / '),
    requiredQuantity: `${form.quantity}${form.unit}`,
    siteAddress: form.siteAddress,
    siteZipNo: form.siteZipNo,
    siteLat: form.siteLat,
    siteLng: form.siteLng,
    requiredDate: form.requiredDate,
    isUrgent: form.isUrgent,
    memo: extraParts.join('\n'),
    extraGradeNote: form.extraGradeNote,
    manufacturer: form.manufacturer,
    extraNote: form.extraNote,
  }
}

function applyDraftToForm(draft) {
  form.draftId = draft.draftId || draft.id || null
  form.materialName = draft.materialName || form.materialName
  form.category = draft.category || currentMaterialOptions.value.category || form.category
  form.standard = isAllowedOptionValue(draft.standard, currentMaterialOptions.value.ksStandards.map((item) => item.value))
    ? draft.standard
    : ''
  const parsedStrength = splitStrengthGrade(draft.strengthGrade || '')
  const parsedShape = draft.shape || parsedStrength.shape || ''
  form.strengthGrade = isAllowedOptionValue(parsedStrength.grade, currentMaterialOptions.value.strengthGrades)
    ? parsedStrength.grade
    : ''
  form.shape = isAllowedOptionValue(parsedShape, currentMaterialOptions.value.shapes)
    ? parsedShape
    : ''
  form.size = parsedStrength.size || form.size
  form.quantity = draft.quantity || parseQuantityValue(draft.requiredQuantity) || form.quantity
  form.unit = draft.unit || parseQuantityUnit(draft.requiredQuantity) || form.unit
  form.siteAddress = draft.siteAddress || form.siteAddress
  form.siteZipNo = draft.siteZipNo || form.siteZipNo
  form.siteLat = draft.siteLat ?? form.siteLat
  form.siteLng = draft.siteLng ?? form.siteLng
  form.requiredDate = draft.requiredDate || form.requiredDate
  form.isUrgent = Boolean(draft.isUrgent)
  form.memo = draft.memo || form.memo
  form.extraGradeNote = draft.extraGradeNote || form.extraGradeNote
  form.manufacturer = draft.manufacturer || form.manufacturer
  form.extraNote = draft.extraNote || form.extraNote
}

function applySiteAddress(address) {
  form.siteAddress = address.roadAddress || address.fullRoadAddress || address.address || ''
  form.siteZipNo = address.zipNo || ''
  form.siteLat = roundCoordinate(address.latitude)
  form.siteLng = roundCoordinate(address.longitude)
  if (!hasKoreaCoordinate(form.siteLat, form.siteLng)) {
    form.siteLat = null
    form.siteLng = null
    errorMessage.value = '선택한 주소의 좌표를 확인할 수 없습니다. 다른 주소를 선택해 주세요.'
  } else {
    errorMessage.value = ''
  }
}

function applyDefaultSiteFromProfile() {
  const user = authState.user
  if (!user || user.role !== 'requester') return
  if (!user.defaultSiteAddress || !hasKoreaCoordinate(user.defaultSiteLatitude, user.defaultSiteLongitude)) return

  form.siteAddress = [user.defaultSiteAddress, user.defaultSiteDetailAddress].filter(Boolean).join(' ')
  form.siteZipNo = user.defaultSiteZipNo || ''
  form.siteLat = roundCoordinate(user.defaultSiteLatitude)
  form.siteLng = roundCoordinate(user.defaultSiteLongitude)
}

function getMaterialOptionKey(materialName) {
  const normalized = String(materialName || '').replace(/\s+/g, '').toLowerCase()
  if (!normalized) return 'generic'
  const matched = Object.entries(MATERIAL_OPTION_MAP).find(([key, option]) =>
    key !== 'generic' && option.labels.some((label) =>
      normalized.includes(String(label).replace(/\s+/g, '').toLowerCase()),
    ),
  )
  return matched?.[0] || 'generic'
}

function resetMaterialSpecificOptions() {
  form.standard = ''
  form.strengthGrade = ''
  form.shape = ''
  form.size = ''
  errorMessage.value = ''
  successMessage.value = ''
}

function validateMaterialOptionCombination() {
  const options = currentMaterialOptions.value
  if (currentMaterialKey.value === 'generic') return ''

  if (form.standard && !isAllowedOptionValue(form.standard, options.ksStandards.map((item) => item.value))) {
    return `${form.materialName}에는 선택한 KS 규격이 맞지 않습니다. 자재명에 맞는 규격을 선택하거나 선택 안함으로 두세요.`
  }
  if (form.strengthGrade && !isAllowedOptionValue(form.strengthGrade, options.strengthGrades)) {
    return `${form.materialName}에는 선택한 강도 등급이 맞지 않습니다. 자재명에 맞는 등급을 선택하거나 선택 안함으로 두세요.`
  }
  if (form.shape && !isAllowedOptionValue(form.shape, options.shapes)) {
    return `${form.materialName}에는 선택한 형태가 맞지 않습니다. 자재명에 맞는 형태를 선택하거나 선택 안함으로 두세요.`
  }
  return ''
}

function isAllowedOptionValue(value, allowedValues = []) {
  if (!value) return true
  return allowedValues.includes(value)
}

function applyKeywordOptions(value) {
  const materialKey = getMaterialOptionKey(value)
  const options = MATERIAL_OPTION_MAP[materialKey] || MATERIAL_OPTION_MAP.generic
  form.category = options.category || parseCategory(value)
  const grade = extractGrade(value)
  if (isAllowedOptionValue(grade, options.strengthGrades)) {
    form.strengthGrade = grade
  }
  const size = extractSize(value)
  if (size) form.size = size
  if (materialKey === 'rebar' && grade) form.standard = 'KS D 3504'
}

function scrollToSiteSection() {
  siteSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function roundCoordinate(value) {
  const number = Number(value)
  return Number.isFinite(number) ? Number(number.toFixed(6)) : null
}

function hasKoreaCoordinate(latitude, longitude) {
  const lat = Number(latitude)
  const lng = Number(longitude)
  return Number.isFinite(lat) && Number.isFinite(lng) && lat >= 33 && lat <= 39 && lng >= 124 && lng <= 132
}

function getApiErrorMessage(error) {
  const data = error.response?.data
  if (!data) return ''
  if (typeof data.error === 'string') return data.error
  return Object.values(data).flat().filter(Boolean).join(' ')
}

function parseMaterialName(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  const normalized = text.replace(/\s+/g, '').toLowerCase()
  const labels = Object.values(MATERIAL_OPTION_MAP)
    .flatMap((option) => option.labels)
    .filter(Boolean)
    .sort((a, b) => b.length - a.length)
  const matched = labels.find((label) =>
    normalized.includes(String(label).replace(/\s+/g, '').toLowerCase()),
  )
  return matched || text.split(' ')[0] || ''
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

function splitStrengthGrade(value) {
  const parts = String(value || '').split('/').map((part) => part.trim()).filter(Boolean)
  const options = currentMaterialOptions.value
  const grade = parts.find((part) => options.strengthGrades.includes(part)) || ''
  const shape = parts.find((part) => options.shapes.includes(part)) || ''
  const size = parts.find((part) => part !== grade && part !== shape) || ''
  return { grade, shape, size }
}

function parseQuantityValue(value) {
  const match = String(value || '').match(/\d+(?:\.\d+)?/)
  return match ? match[0] : ''
}

function parseQuantityUnit(value) {
  const unit = String(value || '').replace(/\d+(?:\.\d+)?/g, '').trim()
  return unit || ''
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

.success-message {
  margin: 0 0 16px;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 12px 14px;
  color: #047857;
  background: #ecfdf5;
  font-size: 14px;
  font-weight: 800;
}

.material-option-help {
  margin: 10px 0 0;
  border: 1px solid #dbe8ff;
  border-radius: 12px;
  padding: 11px 13px;
  color: #4b6380;
  background: #f6f9ff;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.55;
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

.extra-field {
  display: grid;
  gap: 7px;
  flex: 1 1 220px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.extra-field-wide { flex-basis: 100%; }

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
