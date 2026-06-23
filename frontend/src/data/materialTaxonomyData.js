export const materialTaxonomy = [
  {
    id: 'rebar',
    label: '철근',
    description: '형상과 강도 등급 기준 철근 차트',
    evidenceIds: ['rebar'],
    subtypes: [
      { label: '이형철근', keywords: ['이형철근', 'sd300', 'sd400', 'sd500', 'sd600'] },
      { label: '원형철근', keywords: ['원형철근', 'sr235', 'sr295'] },
    ],
  },
  {
    id: 'shape-steel',
    label: '형강·강재',
    description: 'H형강·앵글·채널·강판 차트',
    evidenceIds: ['shape-steel', 'structural-steel', 'square-tube'],
    subtypes: [
      { label: 'H형강', keywords: ['h형강', 'h빔', '에이치빔'] },
      { label: 'ㄱ형강', keywords: ['ㄱ형강', '앵글', 'angle'] },
      { label: 'ㄷ형강', keywords: ['ㄷ형강', '채널', 'channel'] },
      { label: '각형강관', keywords: ['각형강관', '각관'] },
      { label: '강판', keywords: ['강판', 'steel plate'] },
    ],
  },
  {
    id: 'cement',
    label: '시멘트',
    description: '종류·압축강도 기준 시멘트 차트',
    evidenceIds: ['cement', 'blast-furnace-slag-cement'],
    subtypes: [
      { label: '고로슬래그 시멘트', keywords: ['고로슬래그', '슬래그 시멘트'] },
      { label: '조강 포틀랜드 시멘트', keywords: ['조강', '3종'] },
      { label: '보통 포틀랜드 시멘트', keywords: ['보통 포틀랜드', '1종'] },
    ],
  },
  {
    id: 'insulation',
    label: '단열재',
    description: '재료군·열성능 기준 단열재 차트',
    evidenceIds: ['glass-wool-insulation', 'insulation-source-pending'],
    subtypes: [
      { label: 'EPS', keywords: ['eps', '비드법'] },
      { label: 'XPS', keywords: ['xps', '압출법'] },
      { label: '글라스울', keywords: ['글라스울', '유리면'] },
      { label: '경질 우레탄폼', keywords: ['경질 우레탄', '우레탄폼', 'pur'] },
      { label: 'PF 단열재', keywords: ['단열재 pf', 'pf보드', '페놀폼', 'phenolic foam'] },
    ],
  },
  {
    id: 'conduit',
    label: '전기 배관재',
    description: '전선관 타입·시공 조건 기준 차트',
    evidenceIds: ['conduit'],
    subtypes: [
      { label: '경질 전선관', keywords: ['경질 전선관', '경질 합성수지', 'pvc전선관'] },
      { label: '가요 전선관', keywords: ['가요 전선관', '플렉시블'] },
      { label: 'CD관', keywords: ['cd관'] },
      { label: 'PF관', keywords: ['pf관'] },
    ],
  },
]

export function getMaterialTaxonomyByEvidenceId(evidenceId) {
  return materialTaxonomy.find((group) => group.evidenceIds.includes(evidenceId)) || null
}

export function getMaterialSubtype(text = '', groupId = '') {
  const normalized = String(text).toLowerCase().replace(/\s+/g, '')
  const group = materialTaxonomy.find((item) => item.id === groupId)
  if (!group) return ''

  return group.subtypes.find((subtype) =>
    subtype.keywords.some((keyword) => normalized.includes(keyword.toLowerCase().replace(/\s+/g, ''))),
  )?.label || ''
}
