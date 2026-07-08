export const standardEvidenceItems = [
  {
    id: 'rebar',
    category: '철근',
    standard: 'KS D 3504:2025',
    title: '철근 콘크리트용 봉강',
    keywords: ['철근', 'rebar', 'sd400', 'sd500', 'sd600', 'd10', 'd13', 'd16', 'astm a615', 'grade 60'],
    metrics: ['항복강도', '인장강도', '연신율', '탄소당량', '용접·내진 구분'],
    propertyChecks: [
      { label: '항복강도', original: '요청 강도 등급 이상', candidate: '동일 또는 상향 등급', standard: 'KS D 3504', passed: true },
      { label: '인장강도', original: '등급별 하한 충족', candidate: '기준 하한 이상', standard: 'KS D 3504', passed: true },
      { label: '연신율', original: '등급별 최소 연신율', candidate: '기준 하한 이상', standard: 'KS D 3504', passed: true },
      { label: '탄소당량', original: '용접·내진 조건 기준 이하', candidate: '기준 이하 확인', standard: 'KS D 3504', passed: true },
    ],
    filters: ['요청 강도 등급 이상인지 확인', '탄소당량은 기준 이하인지 확인', '용접용·내진용 표기 일치 여부 확인'],
    specificationBasis: '강도 등급, 호칭 지름, 용접·내진 표기가 요청 자재와 맞는지 우선 확인합니다.',
    approvalRisk: '동일 KS 등급은 낮음, 강도 상향 또는 국제 규격 대체는 검토 필요',
    risk: '강도 상향 제품 또는 국제 규격 대체재는 구조 검토와 감리 승인 안내가 필요합니다.',
  },
  {
    id: 'square-tube',
    category: '형강·강재',
    standard: 'KS D 3568:2025',
    title: '일반 구조용 각형 강관',
    verificationStatus: 'partial',
    verificationLabel: '핵심 기준 구조화',
    keywords: ['각형강관', '각형 강관', '정사각형 강관', '직사각형 강관', 'srt275', 'srt355', 'srt410', 'srt450', 'srt550'],
    metrics: ['SRT 강종', '단면 치수', '항복·인장강도', '연신율', '치수 허용차'],
    requirements: [
      { property: '항복강도', rule: '등급별 하한', condition: 'SRT275~SRT550', source: '표 3' },
      { property: '치수·단위무게', rule: '공칭 규격 일치', condition: '정사각형·직사각형', source: '부표 1' },
      { property: '치수 허용차', rule: '제조 방법·두께별 범위', condition: '용접관·이음매 없는 관', source: '표 4' },
    ],
    propertyChecks: [
      { label: 'SRT 강종', original: '요청 강종', candidate: '동일 강종 확인', standard: 'KS D 3568', passed: null },
      { label: '단면 치수', original: '변 길이·두께', candidate: '공칭 치수 대조', standard: 'KS D 3568', passed: null },
      { label: '기계적 성질', original: '항복·인장·연신율', candidate: '등급별 하한 대조', standard: 'KS D 3568', passed: null },
    ],
    filters: ['SRT 강종과 두께 확인', '단면 치수·단위무게 대조', '항복·인장강도와 연신율 확인'],
    specificationBasis: '각형강관은 SRT 강종과 단면 치수, 두께별 허용차를 함께 확인합니다.',
    approvalRisk: '용접 시공 또는 내화 성능 요구 시 추가 검토 필요',
    risk: '일반 구조용 각형강관은 용접 구조용 적용이 제한되므로 시공 조건을 확인해야 합니다.',
  },
  {
    id: 'structural-steel',
    category: '형강·강재',
    standard: 'KS D 3503:2018',
    title: '일반 구조용 압연 강재',
    verificationStatus: 'verified',
    verificationLabel: '조건부 물성 구조화',
    keywords: ['강재', 'ss235', 'ss275', 'ss315', 'ss410', 'ss450', 'ss550'],
    metrics: ['항복강도', '인장강도', '연신율', '강재 두께', '강종 기호'],
    requirements: [
      { property: '항복강도', rule: '두께별 하한', condition: '16 / 40 / 100 mm 구간', source: '표 3' },
      { property: '인장강도', rule: '강종별 범위', condition: 'SS235~SS550', source: '표 3' },
      { property: '연신율', rule: '두께·시험편별 하한', condition: '제품 형상 포함', source: '표 3' },
    ],
    propertyChecks: [
      { label: '강종 기호', original: '요청 강종', candidate: '동일 또는 동등 강종', standard: 'KS D 3503', passed: null },
      { label: '항복강도', original: '두께별 하한 충족', candidate: '기준 하한 이상', standard: 'KS D 3503', passed: null },
      { label: '인장강도', original: '강종별 범위', candidate: '기준 범위 확인', standard: 'KS D 3503', passed: null },
      { label: '연신율', original: '두께별 최소값', candidate: '기준 하한 이상', standard: 'KS D 3503', passed: null },
    ],
    filters: ['강종과 적용 두께 범위 일치 확인', '항복·인장강도 기준 이상 확인', '연신율 하한 충족 여부 확인'],
    specificationBasis: 'SS 계열 강종 표기와 적용 두께 범위를 함께 확인합니다.',
    approvalRisk: '구기호·신기호 대응이나 국제 규격 대체 시 검토 필요',
    risk: '구기호와 신기호가 항상 동일하지 않으므로 표기 기준과 강종 대응을 함께 확인해야 합니다.',
  },
  {
    id: 'shape-steel',
    category: '형강·강재',
    standard: 'KS D 3502:2022',
    title: '열간 압연 형강의 모양·치수·무게 및 허용차',
    verificationStatus: 'partial',
    verificationLabel: '주요 단면 구조화',
    keywords: ['h빔', 'h형강', '형강', '형강·강재', '300x300', '300×300', 'i형강', 'ㄱ형강', 'ㄷ형강', '각형강관'],
    metrics: ['표준 단면치수', '단위무게', '단면적', '단면 2차 모멘트', '치수 허용차'],
    requirements: [
      { property: '단면 치수', rule: '공칭 규격 일치', condition: 'H·ㄱ·ㄷ형강', source: '부표 1·5·9' },
      { property: '단위무게', rule: '표준 단위무게 대조', condition: '호칭 치수별', source: '부표 1·5·9' },
      { property: '치수 허용차', rule: '형상·치수 구간별', condition: '변·높이·두께·길이', source: '표 3·4' },
    ],
    propertyChecks: [
      { label: '단면 치수', original: '호칭 치수 일치', candidate: '동일 호칭 또는 구조 검토 치수', standard: 'KS D 3502', passed: null },
      { label: '단위무게', original: '표준 단위무게', candidate: '표준값 허용 범위', standard: 'KS D 3502', passed: null },
      { label: '단면 성능', original: '단면적·2차 모멘트 기준', candidate: '기준 이상 확인', standard: 'KS D 3502', passed: null },
      { label: '치수 허용차', original: '형상별 허용차', candidate: '허용차 범위 확인', standard: 'KS D 3502', passed: null },
    ],
    filters: ['단면 형상과 호칭 치수 일치 확인', '단위무게와 단면 성능 비교', '치수 허용차 범위 확인'],
    specificationBasis: '형강은 형상과 강종뿐 아니라 단면 치수, 단위무게, 단면 성능을 함께 비교합니다.',
    approvalRisk: '단면 성능이 바뀌면 구조 검토 필요',
    risk: '형강은 단면 성능이 구조 계산에 연결되므로 명칭만으로 대체 판단하면 안 됩니다.',
  },
  {
    id: 'blast-furnace-slag-cement',
    category: '시멘트',
    standard: 'KS L 5210:2017',
    title: '고로 슬래그 시멘트',
    verificationStatus: 'verified',
    verificationLabel: '핵심 물성 구조화',
    keywords: ['고로슬래그', '고로 슬래그', '슬래그 시멘트', 'blast furnace', 'ks l 5210'],
    metrics: ['슬래그 함유율', '재령별 압축강도', '분말도', '응결시간', '안정도'],
    requirements: [
      { property: '슬래그 함유율', rule: '1종 5~30 / 2종 30~60 / 3종 60~70%', condition: '하한 초과·상한 이하', source: '표 1' },
      { property: '압축강도', rule: '3·7·28일 하한', condition: '시멘트 종류별', source: '표 3' },
      { property: '응결시간', rule: '초결 하한·종결 상한', condition: '시멘트 종류별', source: '표 3' },
    ],
    propertyChecks: [
      { label: '시멘트 종류', original: '1·2·3종', candidate: '동일 종류 확인', standard: 'KS L 5210', passed: null },
      { label: '슬래그 함유율', original: '종류별 범위', candidate: '시험성적 대조', standard: 'KS L 5210', passed: null },
      { label: '재령별 강도', original: '3·7·28일 하한', candidate: '시험성적 대조', standard: 'KS L 5210', passed: null },
    ],
    filters: ['고로 슬래그 함유율로 종류 확인', '3·7·28일 압축강도 확인', '분말도·응결시간 확인'],
    specificationBasis: '고로 슬래그 함유율과 종류별 재령 압축강도를 우선 비교합니다.',
    approvalRisk: '시멘트 종류 변경 시 배합과 양생 조건 검토 필요',
    risk: '종류별 조기 강도와 응결 조건이 다르므로 동일 종류를 우선합니다.',
  },
  {
    id: 'cement',
    category: '시멘트',
    standard: 'KS L 5201:2021',
    title: '포틀랜드 시멘트',
    keywords: ['시멘트', 'cement', '포틀랜드', '1종', '2종', '3종', '4종', '5종'],
    metrics: ['압축강도', '응결시간', '분말도', '안정도', '화학성분'],
    propertyChecks: [
      { label: '시멘트 종류', original: '1종~5종 용도 일치', candidate: '동일 종류 우선', standard: 'KS L 5201', passed: true },
      { label: '압축강도', original: '재령별 하한 충족', candidate: '기준 하한 이상', standard: 'KS L 5201', passed: true },
      { label: '응결시간', original: '초결·종결 범위', candidate: '기준 범위 확인', standard: 'KS L 5201', passed: true },
      { label: '안정도', original: '팽창 안정성 기준', candidate: '기준 충족 확인', standard: 'KS L 5201', passed: true },
    ],
    filters: ['시멘트 종류 일치 확인', '재령별 압축강도 기준 확인', '응결·안정도 기준 확인'],
    specificationBasis: '포틀랜드 시멘트 종류와 재령별 압축강도, 응결·안정도 조건을 비교합니다.',
    approvalRisk: '종류 변경 또는 특수 용도 적용 시 배합·양생 조건 검토 필요',
    risk: '조강·저열·내황산염 등 용도 차이가 있어 양생 계획과 배합 검토가 필요합니다.',
  },
  {
    id: 'glass-wool-insulation',
    category: '단열재',
    standard: 'KS L 9102:2026',
    title: '인조 광물섬유 단열재',
    verificationStatus: 'partial',
    verificationLabel: '글라스울 기준 구조화',
    keywords: ['글라스울', '그라스울', 'glass wool', 'mineral wool', '광물섬유', '24k', '32k', '40k', '48k', '64k', '80k', '96k', '120k'],
    metrics: ['열전도도', '밀도', '열간 수축 온도', '치수 허용차', '수분 성능'],
    requirements: [
      { property: '열전도도', rule: '20°C·70°C 상한', condition: '제품 종류·밀도별', source: '표 2-2' },
      { property: '밀도', rule: '호칭 밀도별 허용차', condition: '24K~120K', source: '표 2-2' },
      { property: '수분 성능', rule: '단기 1.0 / 장기 3.0 kg/m² 이하', condition: '수분 노출 제품', source: '7.11' },
    ],
    propertyChecks: [
      { label: '열전도도', original: '사용 온도별 상한', candidate: '성적값 대조', standard: 'KS L 9102', passed: null },
      { label: '밀도', original: '제품 종류별 범위', candidate: '호칭 밀도 확인', standard: 'KS L 9102', passed: null },
      { label: '열간 수축', original: '종류별 온도 하한', candidate: '성적값 대조', standard: 'KS L 9102', passed: null },
    ],
    filters: ['글라스울 제품 형태·호칭 밀도 확인', '평균온도별 열전도도 상한 확인', '수분 노출 시 흡수·투습 성능 확인'],
    specificationBasis: 'KS L 9102는 글라스울·미네랄울에 적용되며 제품 형태와 밀도별 열전도도를 비교합니다.',
    approvalRisk: '수분 노출 부위는 흡수·투습 성능 검토 필요',
    risk: '외피와 표면 마감은 열성능 판정 범위가 다를 수 있어 제품 성적 확인이 필요합니다.',
  },
  {
    id: 'insulation-source-pending',
    category: '단열재',
    standard: '적용 KS 기준 보강 필요',
    title: 'EPS·XPS·경질 우레탄폼·PF 단열재',
    verificationStatus: 'needs_source',
    verificationLabel: '기준 자료 보강 필요',
    keywords: [
      'eps',
      '비드법',
      'xps',
      '압출법',
      '우레탄',
      '폴리우레탄',
      'urethane',
      'pur',
      '경질폼',
      '단열재 pf',
      'pf보드',
      '페놀폼',
      'phenolic foam',
    ],
    metrics: ['재료 종류', '열전도율', '밀도', '압축강도', '연소성'],
    requirements: [],
    propertyChecks: [
      { label: '적용 표준', original: '재료군별 KS', candidate: '기준 자료 보강 필요', standard: '검토 필요', passed: null },
      { label: '열성능', original: '사용 부위 요구값', candidate: '시험성적 확인', standard: '검토 필요', passed: null },
      { label: '시공 조건', original: '압축·연소·수분 조건', candidate: '제품별 확인', standard: '검토 필요', passed: null },
    ],
    filters: ['재료군에 맞는 적용 표준 확인', '열전도율 시험성적 확인', '압축·연소·수분 조건 확인'],
    specificationBasis: '현재 확보한 KS L 9102는 EPS·XPS·우레탄폼에 적용되지 않습니다.',
    approvalRisk: '제품별 적용 KS와 시험성적 검토 필요',
    risk: '기준 자료가 확보되기 전에는 KS 적합 판정을 확정하지 않습니다.',
  },
  {
    id: 'conduit',
    category: '전기 배관재',
    standard: 'KS C IEC 61386-1:2008',
    title: '전기 설비용 전선관 시스템 일반 요구사항',
    keywords: ['전선관', '전기 배관재', '전기배관', 'conduit', '25a', '16a', '32a', '경질', '가요', '플렉시블', 'cd관', 'pf관'],
    metrics: ['압축 복원력', '충격 시험값', '인장력', '온도 범위', '내연성'],
    propertyChecks: [
      { label: '압축 성능', original: '시공 환경별 등급', candidate: '동일 등급 이상', standard: 'KS C IEC 61386-1', passed: true },
      { label: '충격 성능', original: '노출 조건별 등급', candidate: '동일 등급 이상', standard: 'KS C IEC 61386-1', passed: true },
      { label: '온도 범위', original: '최저·최고 사용 온도', candidate: '현장 조건 포함', standard: 'KS C IEC 61386-1', passed: true },
      { label: '재질 구분', original: '금속·비금속·복합재', candidate: '요청 타입 일치 확인', standard: 'KS C IEC 61386-1', passed: true },
    ],
    filters: ['내충격·압축 등급 일치 확인', '최저·최고 사용 온도 범위 확인', '금속·비금속·복합재 구분 확인'],
    specificationBasis: 'MVP에서는 KS C IEC 61386-1 일반 요구사항 기준으로 압축, 충격, 온도, 재질 구분을 확인합니다.',
    approvalRisk: '노출 환경이나 전선관 타입 세분화가 필요하면 추가 규격 검토 필요',
    risk: '전선관은 전기 안전과 노출 환경 영향이 커서 시공 환경 기준을 함께 확인해야 합니다.',
  },
]

export function getStandardEvidenceForMaterial(text = '', limit = 3) {
  const normalized = String(text).toLowerCase()
  const ranked = getRankedStandardEvidence(normalized)

  const matched = ranked.filter(({ score }) => score > 0).map(({ item }) => item)
  return (matched.length ? matched : standardEvidenceItems).slice(0, limit)
}

export function getPrimaryStandardEvidenceForMaterial(text = '') {
  return getStandardEvidenceForMaterial(text, 1)[0] || standardEvidenceItems[0]
}

export function getMatchedStandardEvidenceForMaterial(text = '') {
  const normalized = String(text).toLowerCase()
  const match = getRankedStandardEvidence(normalized).find(({ score }) => score > 0)
  return match?.item || null
}

function getRankedStandardEvidence(normalizedText) {
  return standardEvidenceItems
    .map((item) => ({
      item,
      score: item.keywords.reduce((sum, keyword) => sum + (normalizedText.includes(keyword.toLowerCase()) ? 1 : 0), 0),
    }))
    .sort((a, b) => b.score - a.score)
}
