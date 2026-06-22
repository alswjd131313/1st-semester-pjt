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
    id: 'structural-steel',
    category: '형강·강재',
    standard: 'KS D 3503:2018',
    title: '일반 구조용 압연 강재',
    keywords: ['강재', 'ss235', 'ss275', 'ss315', 'ss410', 'ss450', 'ss550'],
    metrics: ['항복강도', '인장강도', '연신율', '강재 두께', '강종 기호'],
    propertyChecks: [
      { label: '강종 기호', original: '요청 강종', candidate: '동일 또는 동등 강종', standard: 'KS D 3503', passed: true },
      { label: '항복강도', original: '두께별 하한 충족', candidate: '기준 하한 이상', standard: 'KS D 3503', passed: true },
      { label: '인장강도', original: '강종별 범위', candidate: '기준 범위 확인', standard: 'KS D 3503', passed: true },
      { label: '연신율', original: '두께별 최소값', candidate: '기준 하한 이상', standard: 'KS D 3503', passed: true },
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
    keywords: ['h빔', 'h형강', '형강', '형강·강재', '300x300', '300×300', 'i형강', 'ㄱ형강', 'ㄷ형강', '각형강관'],
    metrics: ['표준 단면치수', '단위무게', '단면적', '단면 2차 모멘트', '치수 허용차'],
    propertyChecks: [
      { label: '단면 치수', original: '호칭 치수 일치', candidate: '동일 호칭 또는 구조 검토 치수', standard: 'KS D 3502', passed: true },
      { label: '단위무게', original: '표준 단위무게', candidate: '표준값 허용 범위', standard: 'KS D 3502', passed: true },
      { label: '단면 성능', original: '단면적·2차 모멘트 기준', candidate: '기준 이상 확인', standard: 'KS D 3502', passed: true },
      { label: '치수 허용차', original: '형상별 허용차', candidate: '허용차 범위 확인', standard: 'KS D 3502', passed: true },
    ],
    filters: ['단면 형상과 호칭 치수 일치 확인', '단위무게와 단면 성능 비교', '치수 허용차 범위 확인'],
    specificationBasis: '형강은 형상과 강종뿐 아니라 단면 치수, 단위무게, 단면 성능을 함께 비교합니다.',
    approvalRisk: '단면 성능이 바뀌면 구조 검토 필요',
    risk: '형강은 단면 성능이 구조 계산에 연결되므로 명칭만으로 대체 판단하면 안 됩니다.',
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
    id: 'insulation',
    category: '단열재',
    standard: 'KS M 3880 / KS M 3871-1 / KS M ISO 4898',
    title: '건축용 단열재 주요 기준',
    keywords: ['단열재', 'insulation', '셀룰로오스', '우레탄', '폴리우레탄', 'eps', 'xps', 'pur', 'pf', '50t'],
    metrics: ['열전도율', '밀도', '압축강도', '치수 안정성', '연소성'],
    propertyChecks: [
      { label: '열전도율', original: '요구 열성능 이하', candidate: '동등 이하 확인', standard: 'KS M 계열', passed: true },
      { label: '밀도', original: '재료군별 기준', candidate: '기준 범위 확인', standard: 'KS M 계열', passed: true },
      { label: '압축강도', original: '사용 부위별 하중 조건', candidate: '기준 이상 확인', standard: 'KS M 계열', passed: true },
      { label: '연소성', original: '현장 요구 등급', candidate: '등급 확인 필요', standard: 'KS M 계열', passed: true },
    ],
    filters: ['사용 부위와 재료군 일치 확인', '열전도율 또는 장기 열저항 비교', '압축·치수 안정성 기준 확인'],
    specificationBasis: '재료군과 사용 부위가 맞는지 확인한 뒤 열전도율, 압축강도, 치수 안정성을 비교합니다.',
    approvalRisk: '난연 등급, 유해물질, 시공 방식 차이는 검토 필요',
    risk: '난연성, 유해물질, 현장 시공 방식 차이는 별도 확인이 필요합니다.',
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
