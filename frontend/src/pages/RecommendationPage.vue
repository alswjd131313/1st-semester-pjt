<template>
  <section class="page-wrap">
    <div class="page-heading rec-page-heading">
      <div class="rec-header-row">
        <div>
          <h1>추천 결과</h1>
          <p>입력하신 자재와 현장 정보를 기반으로 최적의 공급사를 추천했습니다.<br />랭킹은 KS 적합도, 납품 신뢰도, 거리, 가격을 종합적으로 반영합니다.</p>
        </div>
        <button type="button" class="btn-summary-toggle" @click="showRequestSummary = !showRequestSummary">
          요청 정보 요약 보기 {{ showRequestSummary ? '▲' : '▾' }}
        </button>
      </div>
      <div v-if="showRequestSummary && request" class="request-summary-panel">
        <span>{{ request.materialName }} · {{ request.standard }} · {{ request.siteAddress }}</span>
      </div>
    </div>

    <div class="criteria-card">
      <span class="criteria-card-title">추천 기준<br /><small>(가중치)</small></span>
      <div class="criteria-items">
        <div class="criteria-item">
          <div class="criteria-icon criteria-icon-blue">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>
          </div>
          <span class="criteria-name">KS 적합성</span>
          <div class="criteria-stars"><span class="cstar cstar-on">★</span><span class="cstar cstar-on">★</span><span class="cstar cstar-on">★</span><span class="cstar cstar-off">★</span><span class="cstar cstar-off">★</span></div>
          <div class="criteria-bar-wrap"><div class="criteria-bar-fill" style="width:45%"></div></div>
          <span class="criteria-pct">45%</span>
        </div>
        <div class="criteria-item">
          <div class="criteria-icon criteria-icon-orange">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/></svg>
          </div>
          <span class="criteria-name">납품 신뢰도</span>
          <div class="criteria-stars"><span class="cstar cstar-on">★</span><span class="cstar cstar-on">★</span><span class="cstar cstar-on">★</span><span class="cstar cstar-off">★</span><span class="cstar cstar-off">★</span></div>
          <div class="criteria-bar-wrap"><div class="criteria-bar-fill" style="width:30%"></div></div>
          <span class="criteria-pct">30%</span>
        </div>
        <div class="criteria-item">
          <div class="criteria-icon criteria-icon-green">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          </div>
          <span class="criteria-name">현장 거리</span>
          <div class="criteria-stars"><span class="cstar cstar-on">★</span><span class="cstar cstar-on">★</span><span class="cstar cstar-off">★</span><span class="cstar cstar-off">★</span><span class="cstar cstar-off">★</span></div>
          <div class="criteria-bar-wrap"><div class="criteria-bar-fill" style="width:15%"></div></div>
          <span class="criteria-pct">15%</span>
        </div>
        <div class="criteria-item">
          <div class="criteria-icon criteria-icon-purple">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>
          </div>
          <span class="criteria-name">가격 경쟁력</span>
          <div class="criteria-stars"><span class="cstar cstar-on">★</span><span class="cstar cstar-on">★</span><span class="cstar cstar-off">★</span><span class="cstar cstar-off">★</span><span class="cstar cstar-off">★</span></div>
          <div class="criteria-bar-wrap"><div class="criteria-bar-fill" style="width:10%"></div></div>
          <span class="criteria-pct">10%</span>
        </div>
      </div>
    </div>

    <p v-if="isLoading" class="loading-message">추천 결과를 계산하는 중입니다.</p>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <section v-if="!isLoading" class="top5-section">
      <div class="top5-header">
        <h2>TOP 5 추천 공급사</h2>
        <label class="sort-label">
          랭킹 보기
          <select v-model="sortOption">
            <option value="score">종합 추천순</option>
            <option value="spec">규격 신뢰도순</option>
            <option value="distance">긴급 납품순</option>
            <option value="price">단가 우선순</option>
            <option value="delivery">납품 신뢰도순</option>
          </select>
        </label>
        <div class="filter-toggles">
          <label><input v-model="hideApprovalRequired" type="checkbox" /> 국제 규격/감리 승인 필요 제외</label>
          <label><input v-model="registeredOnly" type="checkbox" /> 등록 공급사만 보기</label>
        </div>
        <button type="button" class="secondary-button reset-btn" @click="resetFilters">초기화</button>
      </div>

      <div class="recommendation-list">
        <article
          v-for="item in displayedRecommendations"
          :key="`${item.supplierName}-${item.materialName}-${item.standard}`"
          class="rec-row"
        >
          <div class="rec-rank">
            <span :class="['rank-num', { 'rank-first': item.displayRank === 1 }]">{{ item.displayRank }}</span>
          </div>

          <div class="rec-main">
            <h2>{{ item.supplierName }}</h2>
            <p class="rec-material">{{ item.materialName }} · {{ item.standard }}</p>
            <div class="rec-tags">
              <span class="rec-tag rec-tag-blue">{{ getRankingLabel(item) }}</span>
              <span class="rec-tag rec-tag-gray">{{ getMaterialTypeLabel(item) }}</span>
              <span :class="['rec-tag', getMatchSignalClass(item) === 'high' ? 'rec-tag-green' : 'rec-tag-gray']">{{ getMatchConfidenceLabel(item) }}</span>
            </div>
            <div class="rec-metrics-row">
              <span class="metric-pill">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>
                단가 {{ item.price }}
              </span>
              <span class="metric-pill">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                {{ getDistanceSignal(item) }}
              </span>
              <span class="metric-pill">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M20 6h-2.18c.07-.44.18-.88.18-1.25C18 2.68 16.32 1 14.25 1c-1.19 0-2.14.56-2.86 1.38L10 4.5 8.61 2.38C7.89 1.56 6.94 1 5.75 1 3.68 1 2 2.68 2 4.75c0 .37.11.81.18 1.25H0v14h24V6h-4zm-7.27-2.12c.38-.49.9-.76 1.52-.76 1.04 0 1.75.71 1.75 1.75 0 .37-.12.81-.32 1.13H13.5l-.77-2.12zM5.75 2.98c.62 0 1.14.27 1.52.76L6.5 5.75H4.07c-.2-.32-.32-.76-.32-1.13 0-1.04.71-1.64 2-1.64zM22 18H2V8h20v10z"/></svg>
                납품 {{ item.deliveryCount }}회
              </span>
            </div>
          </div>

          <div class="rec-score-col">
            <span class="rec-score-label">종합 점수</span>
            <strong class="rec-score-num">{{ item.totalScore }}점</strong>
            <div class="rec-stars">
              <span v-for="n in getScoreStarsFull(item.totalScore)" :key="`f${n}`" class="star-full">★</span>
              <span v-if="getScoreStarsHalf(item.totalScore)" class="star-half">★</span>
              <span v-for="n in getScoreStarsEmpty(item.totalScore)" :key="`e${n}`" class="star-empty">★</span>
            </div>
            <button type="button" class="btn-score-detail" @click.stop="toggleScoreExpand(getItemKey(item))">
              점수 상세 보기 {{ isScoreExpanded(getItemKey(item)) ? '▲' : '▾' }}
            </button>
            <div v-if="isScoreExpanded(getItemKey(item))" class="score-detail-panel">
              <div class="sub-score-item"><span>적합성</span><strong>{{ Math.round(getMaterialFitScore(item) * 0.45) }}</strong></div>
              <div class="sub-score-item"><span>신뢰도</span><strong>{{ Math.round(Number(item.reliabilityScore || 0) * 0.3) }}</strong></div>
              <div class="sub-score-item"><span>거리</span><strong>{{ hasRouteInformation(item) ? Math.round(Number(item.distanceScore || 0) * 0.15) : '-' }}</strong></div>
              <div class="sub-score-item"><span>가격</span><strong>{{ Math.round(Number(item.priceScore || 0) * 0.1) }}</strong></div>
            </div>
          </div>

          <div class="rec-reasons-col">
            <span class="rec-reasons-label">추천 이유</span>
            <ul class="rec-reason-list">
              <li v-for="reason in getReasonItems(item).slice(0, 3)" :key="reason">
                <span class="reason-check">✓</span>{{ reason }}
              </li>
            </ul>
          </div>

          <div class="rec-actions">
            <button type="button" class="btn-detail" @click.stop="openDetail(item)">상세 보기</button>
            <button type="button" class="btn-inquiry" @click.stop="openInquiry(item)">공급사 문의</button>
          </div>
        </article>

        <div v-if="!displayedRecommendations.length" class="empty-state">
          <strong>추천 결과가 없습니다.</strong>
          <p>필터를 초기화하거나 다른 조건으로 검색해보세요.</p>
          <button type="button" class="primary-button" @click="resetFilters">필터 초기화</button>
        </div>
      </div>

      <div class="show-all-wrap">
        <button type="button" class="btn-show-all" @click="showAllList = !showAllList">
          전체 랭킹 리스트 보기 (TOP 20) ›
        </button>
      </div>
    </section>

    <section v-if="!isLoading && showAllList" class="ranking-table-section">
      <h2>전체 랭킹 리스트 (TOP 20)</h2>
      <div class="ranking-table-wrap">
        <table class="ranking-table">
          <thead>
            <tr>
              <th>순위</th>
              <th>공급사</th>
              <th>주요 자재/규격</th>
              <th>종합 점수</th>
              <th>세부 점수</th>
              <th>단가(예상)</th>
              <th>현장 거리</th>
              <th>납품 이력</th>
              <th>문의</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in allRankingList" :key="`tbl-${item.supplierName}-${item.materialName}`">
              <td>
                <span :class="['rank-badge', { 'rank-badge-first': item.displayRank === 1 }]">{{ item.displayRank }}</span>
              </td>
              <td>
                <div class="tbl-supplier-name">{{ item.supplierName }}</div>
                <div class="tbl-supplier-type">{{ getMaterialTypeLabel(item) }}</div>
              </td>
              <td class="tbl-material">{{ item.materialName }}<br /><small>{{ item.standard }}</small></td>
              <td class="tbl-score-cell">{{ item.totalScore }}<small>점</small></td>
              <td class="tbl-sub-scores">
                <div class="sub-score-bar-row">
                  <span class="sub-label">적합</span>
                  <div class="bar-wrap"><div class="bar-fill bar-blue" :style="{ width: getMaterialFitScore(item) + '%' }"></div></div>
                  <span class="sub-val">{{ Math.round(getMaterialFitScore(item) * 0.45) }}</span>
                </div>
                <div class="sub-score-bar-row">
                  <span class="sub-label">신뢰</span>
                  <div class="bar-wrap"><div class="bar-fill bar-orange" :style="{ width: Number(item.reliabilityScore || 0) + '%' }"></div></div>
                  <span class="sub-val">{{ Math.round(Number(item.reliabilityScore || 0) * 0.3) }}</span>
                </div>
                <div class="sub-score-bar-row">
                  <span class="sub-label">거리</span>
                  <div class="bar-wrap"><div class="bar-fill bar-green" :style="{ width: Number(item.distanceScore || 0) + '%' }"></div></div>
                  <span class="sub-val">{{ hasRouteInformation(item) ? Math.round(Number(item.distanceScore || 0) * 0.15) : '-' }}</span>
                </div>
                <div class="sub-score-bar-row">
                  <span class="sub-label">가격</span>
                  <div class="bar-wrap"><div class="bar-fill bar-purple" :style="{ width: Number(item.priceScore || 0) + '%' }"></div></div>
                  <span class="sub-val">{{ Math.round(Number(item.priceScore || 0) * 0.1) }}</span>
                </div>
              </td>
              <td>{{ item.price }}</td>
              <td>{{ getShortDistance(item) }}</td>
              <td>{{ item.deliveryCount }}회</td>
              <td class="tbl-action-cell">
                <button type="button" class="btn-inquiry-sm" @click="openInquiry(item)">문의</button>
                <button type="button" class="btn-detail-sm" @click="openDetail(item)">상세</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="!isLoading" class="map-section">
      <div class="map-section-header">
        <h2>지도로 보는 공급사 위치</h2>
        <ul class="map-legend">
          <li><span class="legend-dot legend-site"></span> 현장 위치</li>
          <li><span class="legend-dot legend-top"></span> 추천 공급사 (TOP 5)</li>
          <li><span class="legend-dot legend-other"></span> 기타 공급사</li>
        </ul>
      </div>
      <KakaoMap
        :site="rankingMapSite"
        :suppliers="mapRecommendations"
        :selected-supplier="selectedMapSupplier"
        @select-supplier="selectSupplierForRoute"
      />
    </section>

    <p v-if="!isLoading" class="rec-disclaimer">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="flex-shrink:0;margin-top:1px"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>
      본 추천 결과는 입력하신 정보와 당사의 데이터 기반으로 산출되었으며, 실제 거래 조건은 공급사와의 협의가 필요합니다.
    </p>

    <Teleport to="body">
      <div
        v-if="selectedRecommendation"
        class="modal-backdrop"
        role="presentation"
        @click.self="closeDetail"
      >
        <section
          class="detail-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="recommendation-detail-title"
        >
          <div class="modal-header">
            <div>
              <p class="eyebrow">Ranking Detail</p>
              <h2 id="recommendation-detail-title">
                TOP {{ selectedRecommendation.displayRank || selectedRecommendation.rank }} · {{ selectedRecommendation.supplierName }}
              </h2>
              <span>
                {{ getMaterialTypeLabel(selectedRecommendation) }} ·
                {{ selectedRecommendation.materialName }} ·
                {{ selectedRecommendation.standard }}
              </span>
            </div>
            <button type="button" class="icon-button" aria-label="상세 닫기" @click="closeDetail">
              ×
            </button>
          </div>

          <div class="detail-score-panel">
            <div>
              <span>랭킹 점수</span>
              <strong>{{ selectedRecommendation.totalScore }}점</strong>
            </div>
            <p>
              {{ getRankingSummary(selectedRecommendation) }} 가격, 거리, 납품 이력, KS 물성 적합도를 함께 반영했습니다.
            </p>
          </div>

          <div class="detail-grid">
            <article>
              <h3>공급 조건</h3>
              <dl class="detail-list">
                <div>
                  <dt>자재 분류</dt>
                  <dd>{{ getMaterialTypeLabel(selectedRecommendation) }}</dd>
                </div>
                <div>
                  <dt>최근 단가</dt>
                  <dd>{{ selectedRecommendation.price }}</dd>
                </div>
                <div>
                  <dt>현장 거리</dt>
                  <dd>{{ getDistanceLabel(selectedRecommendation) }}</dd>
                </div>
                <div v-if="selectedRecommendation.locationBasis && selectedRecommendation.locationBasis !== 'supplier_address'">
                  <dt>위치 기준</dt>
                  <dd>{{ getLocationBasisLabel(selectedRecommendation) }}</dd>
                </div>
                <div>
                  <dt>납품 이력</dt>
                  <dd>{{ selectedRecommendation.deliveryCount }}회</dd>
                </div>
                <div v-if="selectedRecommendation.contact">
                  <dt>연락처</dt>
                  <dd>{{ selectedRecommendation.contact }}</dd>
                </div>
                <div v-if="selectedRecommendation.serviceArea">
                  <dt>납품 가능 지역</dt>
                  <dd>{{ selectedRecommendation.serviceArea }}</dd>
                </div>
              </dl>
            </article>

            <article>
              <h3>랭킹 산정 근거</h3>
              <div class="match-basis-box">
                <span>규격 판단</span>
                <strong>{{ getMatchSignalLabel(selectedRecommendation) }}</strong>
                <p>{{ getMatchSignalDescription(selectedRecommendation) }}</p>
              </div>
              <div class="score-breakdown">
                <div>
                  <span>물성 적합도</span>
                  <strong>{{ getMaterialFitScore(selectedRecommendation) }}</strong>
                  <meter min="0" max="100" :value="getMaterialFitScore(selectedRecommendation)" />
                </div>
                <div>
                  <span>신뢰도 점수</span>
                  <strong>{{ selectedRecommendation.reliabilityScore }}</strong>
                  <meter min="0" max="100" :value="selectedRecommendation.reliabilityScore" />
                </div>
                <div>
                  <span>거리 점수</span>
                  <strong>{{ getDistanceScoreLabel(selectedRecommendation) }}</strong>
                  <meter
                    v-if="hasRouteInformation(selectedRecommendation)"
                    min="0"
                    max="100"
                    :value="selectedRecommendation.distanceScore"
                  />
                </div>
                <div>
                  <span>가격 점수</span>
                  <strong>{{ selectedRecommendation.priceScore }}</strong>
                  <meter min="0" max="100" :value="selectedRecommendation.priceScore" />
                </div>
              </div>
            </article>
          </div>

          <div class="detail-note">
            <h3>단가 트렌드</h3>
            <div class="price-trend-panel">
              <div class="trend-summary">
                <span>최근 단가</span>
                <strong>{{ selectedRecommendation.price }}</strong>
                <p>{{ getPriceTrendSummary(selectedRecommendation) }}</p>
              </div>
              <div v-if="getPriceTrendBars(selectedRecommendation).length" class="trend-chart" aria-label="최근 단가 추이">
                <div
                  v-for="point in getPriceTrendBars(selectedRecommendation)"
                  :key="point.label"
                  class="trend-bar-item"
                >
                  <span>{{ point.display }}</span>
                  <i :style="{ height: `${point.height}%` }" />
                  <small>{{ point.label }}</small>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-note">
            <h3>추천 이유</h3>
            <ul class="reason-list">
              <li
                v-for="reason in getReasonItems(selectedRecommendation)"
                :key="reason"
              >
                {{ reason }}
              </li>
            </ul>
          </div>

          <div class="detail-note">
            <h3>핵심 검토 근거</h3>
            <div class="hard-filter-grid">
              <article
                v-for="evidence in getHardFilterEvidence(selectedRecommendation)"
                :key="evidence.label"
                :class="{ warn: isHardFilterWarning(evidence) }"
              >
                <span>{{ evidence.label }}</span>
                <strong>{{ evidence.status }}</strong>
                <p>{{ evidence.description }}</p>
              </article>
            </div>
          </div>

          <div class="detail-note">
            <h3>KS·규격 근거</h3>
            <div class="standard-detail-grid">
              <article>
                <span>적용 기준</span>
                <strong>{{ getStandardEvidence(selectedRecommendation).standard }}</strong>
                <p>{{ getStandardEvidence(selectedRecommendation).title }} · {{ getEvidenceVerificationLabel(selectedRecommendation) }}</p>
              </article>
              <article>
                <span>규격 근거</span>
                <strong>{{ getMaterialTypeLabel(selectedRecommendation) }}</strong>
                <p>{{ getStandardEvidence(selectedRecommendation).specificationBasis }}</p>
              </article>
              <article>
                <span>승인 리스크</span>
                <strong>{{ isApprovalReviewRequired(selectedRecommendation) ? "검토 필요" : "낮음" }}</strong>
                <p>{{ getStandardEvidence(selectedRecommendation).approvalRisk }}</p>
              </article>
            </div>
          </div>

          <div class="detail-note">
            <h3>물성 비교</h3>
            <div class="property-summary">
              <strong>{{ getPropertySummary(selectedRecommendation).label }}</strong>
              <span>{{ getPropertySummary(selectedRecommendation).message }}</span>
            </div>
            <div class="property-table" role="table" aria-label="물성 비교표">
              <div class="property-row property-head" role="row">
                <span>항목</span>
                <span>기준 자재</span>
                <span>추천 자재</span>
                <span>기준</span>
              </div>
              <div
                v-for="row in getPropertyComparison(selectedRecommendation)"
                :key="row.label"
                class="property-row"
                role="row"
              >
                <span>{{ row.label }}</span>
                <span>{{ row.original }}</span>
                <span>
                  {{ row.candidate }}
                  <b :class="['property-result', { fail: row.passed === false }]">
                    {{ getPropertyResultLabel(row) }}
                  </b>
                </span>
                <span>{{ row.standard }}</span>
              </div>
            </div>
          </div>

          <div class="detail-note">
            <h3>랭킹 점수 근거</h3>
            <div class="evidence-grid">
              <article>
                <strong>물성 {{ getMaterialFitScore(selectedRecommendation) }}점</strong>
                <p>{{ getScoreEvidence(selectedRecommendation).materialFit }}</p>
              </article>
              <article>
                <strong>신뢰도 {{ selectedRecommendation.reliabilityScore }}점</strong>
                <p>{{ getScoreEvidence(selectedRecommendation).reliability }}</p>
              </article>
              <article>
                <strong>거리 {{ getDistanceScoreLabel(selectedRecommendation) }}</strong>
                <p>{{ getScoreEvidence(selectedRecommendation).distance }}</p>
              </article>
              <article>
                <strong>가격 {{ selectedRecommendation.priceScore }}점</strong>
                <p>{{ getScoreEvidence(selectedRecommendation).price }}</p>
              </article>
            </div>
          </div>

          <div :class="['approval-note', { warn: isApprovalReviewRequired(selectedRecommendation) }]">
            <strong>
              {{ getApprovalRiskLabel(selectedRecommendation) }}
            </strong>
            <p>{{ getApprovalRiskNote(selectedRecommendation) }}</p>
            <ul class="approval-checklist">
              <li
                v-for="risk in getApprovalChecklist(selectedRecommendation)"
                :key="risk.label"
              >
                <span>{{ risk.label }}</span>
                <strong>{{ risk.status }}</strong>
                <small>{{ risk.description }}</small>
              </li>
            </ul>
          </div>

          <div class="modal-actions">
            <button type="button" class="secondary-button" @click="closeDetail">닫기</button>
            <button type="button" class="primary-button" @click="openInquiry(selectedRecommendation)">
              공급사 문의
            </button>
          </div>
        </section>
      </div>
    </Teleport>

    <Teleport to="body">
      <div
        v-if="selectedInquirySupplier"
        class="modal-backdrop"
        role="presentation"
        @click.self="closeInquiry"
      >
        <section
          class="detail-modal inquiry-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="supplier-inquiry-title"
        >
          <div class="modal-header">
            <div>
              <p class="eyebrow">Supplier Inquiry</p>
              <h2 id="supplier-inquiry-title">공급사 문의</h2>
              <span>
                {{ selectedInquirySupplier.supplierName }} ·
                {{ selectedInquirySupplier.materialName }}
                {{ selectedInquirySupplier.standard }}
              </span>
            </div>
            <button type="button" class="icon-button" aria-label="문의 닫기" @click="closeInquiry">
              ×
            </button>
          </div>

          <div class="inquiry-summary">
            <strong>문의 전 확인</strong>
            <p>PaceFlow는 문의 우선순위를 추천합니다. 실제 재고, 견적, 납품 가능 여부는 공급사 확인 후 확정됩니다.</p>
          </div>

          <form class="inquiry-form" @submit.prevent="submitInquiry">
            <label>
              담당자명
              <input v-model.trim="inquiryForm.requesterName" type="text" placeholder="예: 김현장" required />
            </label>
            <label>
              연락처
              <input v-model.trim="inquiryForm.contact" type="tel" placeholder="예: 010-1234-5678" required />
            </label>
            <label>
              문의 수량
              <input v-model.trim="inquiryForm.quantity" type="text" placeholder="예: 50톤" required />
            </label>
            <label>
              희망 납기
              <input v-model="inquiryForm.desiredDate" type="date" />
            </label>
            <label class="full-field">
              문의 메모
              <textarea
                v-model.trim="inquiryForm.message"
                rows="4"
                placeholder="희망 납기, 긴급 여부, 현장 조건 등을 남겨주세요."
              />
            </label>

            <p v-if="inquiryStatus" class="success-message full-field">{{ inquiryStatus }}</p>
            <p v-if="inquiryErrorMessage" class="error-message full-field">{{ inquiryErrorMessage }}</p>

            <div class="modal-actions full-field">
              <button type="button" class="secondary-button" @click="closeInquiry">취소</button>
              <button
                type="submit"
                class="primary-button"
                :disabled="isInquirySubmitting"
              >
                {{ submitButtonLabel }}
              </button>
            </div>
          </form>
        </section>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  createSupplierInquiry,
  getDrivingRoute,
  getLatestMaterialRequest,
  getRecommendations,
} from "../api/materialApi";
import KakaoMap from "../components/KakaoMap.vue";
import {
  getMatchedStandardEvidenceForMaterial,
  getPrimaryStandardEvidenceForMaterial,
} from "../data/standardEvidenceData";
import {
  getMaterialSubtype,
  getMaterialTaxonomyByEvidenceId,
  materialTaxonomy,
} from "../data/materialTaxonomyData";

const route = useRoute();
const router = useRouter();
const request = ref(null);
const recommendations = ref([]);
const selectedRouteSupplier = ref(null);
const selectedRoute = ref(null);
const routeResultCache = new Map();
const selectedRecommendation = ref(null);
const selectedInquirySupplier = ref(null);
const inquiryStatus = ref("");
const inquiryErrorMessage = ref("");
const isLoading = ref(false);
const isInquirySubmitting = ref(false);
const errorMessage = ref("");
const sortOption = ref("score");
const activeRankingTab = ref("all");
const hideApprovalRequired = ref(false);
const registeredOnly = ref(false);
const inquiryForm = reactive({
  requesterName: "",
  contact: "",
  quantity: "",
  desiredDate: "",
  message: "",
});

onMounted(() => {
  syncRankingTabFromKeyword();
  loadRecommendations();
});

watch(hideApprovalRequired, () => {
  loadRecommendations();
});

watch(
  () => route.query.keyword,
  () => {
    syncRankingTabFromKeyword();
  },
);

const rankingTabs = [
  { id: "all", label: "전체 TOP", description: "자재 구분 없이 종합 점수순" },
  ...materialTaxonomy,
];

const rankedRecommendations = computed(() =>
  recommendations.value.map((item) => ({
    ...item,
    materialFitScore: getMaterialFitScore(item),
    totalScore: calculateRankingScore(item),
  })),
);

const filteredRecommendations = computed(() => {
  const activeTab = rankingTabs.find((tab) => tab.id === activeRankingTab.value);
  return rankedRecommendations.value
    .filter((item) =>
      activeRankingTab.value === "all" || activeTab?.evidenceIds?.includes(getStandardEvidence(item).id),
    )
    .filter((item) => !hideApprovalRequired.value || !item.approvalRequired)
    .filter((item) => !registeredOnly.value || item.isRegisteredSupplier)
    .slice()
    .sort((a, b) => compareRecommendations(a, b));
});

const displayedRecommendations = computed(() =>
  filteredRecommendations.value.slice(0, 5).map((item, index) => ({
    ...item,
    displayRank: index + 1,
  })),
);

const mapRecommendations = computed(() =>
  filteredRecommendations.value
    .filter((item) => hasKoreaCoordinate(item.latitude, item.longitude))
    .slice(0, 30),
);

const activeFilterLabel = computed(() => {
  const filters = [];

  if (hideApprovalRequired.value) {
    filters.push("승인 리스크 제외");
  }

  if (registeredOnly.value) {
    filters.push("등록 공급사");
  }

  return filters.length ? filters.join(" · ") : "종합 추천 랭킹을 표시 중입니다.";
});

const activeRankingLabel = computed(() =>
  rankingTabs.find((tab) => tab.id === activeRankingTab.value)?.label || "전체 TOP",
);

const activeRankingEvidenceText = computed(() => {
  if (activeRankingTab.value === "all") {
    return "";
  }

  return activeRankingLabel.value;
});

const selectedMapSupplier = computed(() =>
  selectedRouteSupplier.value
    ? { ...selectedRouteSupplier.value, ...(selectedRoute.value || {}) }
    : null,
);

const rankingMapSite = computed(() => ({
  latitude: hasKoreaCoordinate(request.value?.siteLat, request.value?.siteLng)
    ? Number(request.value.siteLat)
    : null,
  longitude: hasKoreaCoordinate(request.value?.siteLat, request.value?.siteLng)
    ? Number(request.value.siteLng)
    : null,
  address: request.value?.siteAddress || "현장 주소 확인 필요",
}));

function getRankingLabel(item) {
  if (item.displayRank === 1 || item.rank === 1) {
    return item.approvalRequired ? "검토형 1위" : "종합 1위 추천";
  }

  if (item.approvalRequired) {
    return "승인 검토 후보";
  }

  if (hasRouteInformation(item) && Number(item.distanceScore || 0) >= 90) {
    return "긴급 납품 후보";
  }

  if (Number(item.priceScore || 0) >= 92) {
    return "단가 우위 후보";
  }

  if (Number(item.reliabilityScore || 0) >= 88) {
    return "납품 신뢰 후보";
  }

  return "비교 문의 후보";
}

function getRankingSummary(item) {
  if (item.approvalRequired) {
    return "물성 조건은 맞지만 승인 리스크를 함께 확인해야 하는 비교 후보입니다.";
  }

  if (hasRouteInformation(item) && Number(item.distanceScore || 0) >= 90) {
    return "현장 접근성이 좋아 긴급 문의 우선순위가 높은 후보입니다.";
  }

  if (Number(item.priceScore || 0) >= 92) {
    return "후보군 대비 단가 경쟁력이 높은 비교 견적 후보입니다.";
  }

  if (Number(item.reliabilityScore || 0) >= 88) {
    return "납품 이력이 안정적이라 반복 공급 가능성을 우선 확인할 후보입니다.";
  }

  return hasRouteInformation(item)
    ? "가격, 차량 거리, 납품 이력을 종합해 비교 대상으로 표시한 후보입니다."
    : "가격, 납품 이력, KS 적합도를 기준으로 비교하고 차량 거리는 확인이 필요한 후보입니다.";
}

function getCardSummary(item) {
  const hasUnverifiedDistanceClaim = !hasRouteInformation(item)
    && /거리|접근성|가까/.test(item.reason || "");
  if (item.reason && item.dataSource !== "narajangteo" && !hasUnverifiedDistanceClaim) {
    return item.reason;
  }

  return getRankingSummary(item);
}

function getMaterialTypeLabel(item) {
  const evidence = getStandardEvidence(item);
  const group = getMaterialTaxonomyByEvidenceId(evidence.id);
  if (!group) return evidence.category;

  const subtype = getMaterialSubtype(
    [item?.materialName, item?.standard, item?.strengthGrade].filter(Boolean).join(" "),
    group.id,
  );
  return subtype ? `${group.label} · ${subtype}` : group.label;
}

function getCompactEvidenceText(item) {
  const evidence = getStandardEvidence(item);
  return `핵심 검토: ${evidence.metrics.slice(0, 3).join(" · ")}`;
}

function getEvidenceVerificationLabel(item) {
  const evidence = getStandardEvidence(item);
  return evidence.verificationLabel || (evidence.verificationStatus === "verified" ? "핵심 기준 구조화" : "검토 필요");
}

function getMaterialFitScore(item) {
  const evidence = getStandardEvidence(item);
  const suppliedScore = Number(item.materialFitScore);
  const hasSuppliedScore = Number.isFinite(suppliedScore);

  if (evidence.verificationStatus === "needs_source") {
    return hasSuppliedScore ? Math.min(suppliedScore, 55) : 55;
  }

  if (item.approvalRequired) {
    return hasSuppliedScore ? Math.min(suppliedScore, 78) : 78;
  }

  const rows = item.propertyComparison?.length ? item.propertyComparison : evidence.propertyChecks;
  const evaluated = rows.filter((row) => typeof row.passed === "boolean");
  if (!evaluated.length) {
    const evidenceCap = evidence.verificationStatus === "verified" ? 84 : 80;
    return hasSuppliedScore ? Math.min(suppliedScore, evidenceCap) : evidenceCap;
  }

  if (hasSuppliedScore && item.propertyComparison?.length) {
    return suppliedScore;
  }

  const passed = evaluated.filter((row) => row.passed).length;
  return Math.round(70 + (passed / evaluated.length) * 28);
}

function calculateRankingScore(item) {
  const materialFitScore = getMaterialFitScore(item);
  const reliabilityScore = Number(item.reliabilityScore || 0);
  const distanceScore = Number(item.distanceScore || 0);
  const priceScore = Number(item.priceScore || 0);
  let weightedScore =
    materialFitScore * 0.45 +
    reliabilityScore * 0.3 +
    priceScore * 0.1;
  let knownWeight = 0.85;

  if (hasRouteInformation(item)) {
    weightedScore += distanceScore * 0.15;
    knownWeight += 0.15;
  }

  return Math.round(weightedScore / knownWeight);
}

function syncRankingTabFromKeyword() {
  const keywordEvidence = getMatchedStandardEvidenceForMaterial(route.query.keyword || "");
  activeRankingTab.value = getMaterialTaxonomyByEvidenceId(keywordEvidence?.id)?.id || "all";
}

const submitButtonLabel = computed(() => {
  return isInquirySubmitting.value ? "문의 요청 보내는 중" : "문의 요청 보내기";
});

const requestEvidenceText = computed(() =>
  [
    request.value?.materialName,
    request.value?.standard,
    request.value?.strengthGrade,
    request.value?.category,
  ]
    .filter(Boolean)
    .join(" "),
);

function compareRecommendations(a, b) {
  if (sortOption.value === "distance") {
    return compareNumber(getDistanceConfidenceScore(b), getDistanceConfidenceScore(a), "asc") ||
      compareNumber(getSortableDistance(a), getSortableDistance(b), "asc") ||
      compareNumber(b.totalScore, a.totalScore, "asc");
  }

  if (sortOption.value === "price") {
    return compareNumber(parsePrice(a.price), parsePrice(b.price), "asc") || compareNumber(b.totalScore, a.totalScore, "asc");
  }

  if (sortOption.value === "delivery") {
    return compareNumber(b.deliveryCount, a.deliveryCount, "asc") || compareNumber(b.totalScore, a.totalScore, "asc");
  }

  if (sortOption.value === "spec") {
    return compareNumber(getMatchConfidenceScore(b), getMatchConfidenceScore(a), "asc") ||
      compareNumber(getMaterialFitScore(b), getMaterialFitScore(a), "asc") ||
      compareNumber(b.totalScore, a.totalScore, "asc");
  }

  return compareNumber(b.totalScore, a.totalScore, "asc") || compareNumber(getSortableDistance(a), getSortableDistance(b), "asc");
}

function getSortableDistance(item) {
  const distance = Number(item.routeDistanceM);
  return hasRouteInformation(item) && Number.isFinite(distance)
    ? distance
    : Number.MAX_SAFE_INTEGER;
}

function hasActualSupplierDistance(item) {
  return hasRouteInformation(item);
}

function hasRouteInformation(item) {
  return item.routeStatus === "success"
    && Number.isFinite(Number(item.routeDistanceM))
    && Number.isFinite(Number(item.routeDurationSec));
}

function getDistanceConfidenceScore(item) {
  if (hasActualSupplierDistance(item)) {
    return 2;
  }

  if (item.locationBasis === "contract_agency_estimated") {
    return 1;
  }

  return 0;
}

function getDistanceLabel(item) {
  const routeItem = getRouteDisplayItem(item);
  if (hasRouteInformation(routeItem)) {
    const minutes = Math.max(1, Math.round(Number(routeItem.routeDurationSec) / 60));
    const distanceKm = (Number(routeItem.routeDistanceM) / 1000).toFixed(1);
    return `차량 기준 약 ${minutes}분 · ${distanceKm}km`;
  }

  return routeItem.routeNote || "거리 정보 확인 필요";
}

function getDistanceSignal(item) {
  const routeItem = getRouteDisplayItem(item);
  if (hasRouteInformation(routeItem)) {
    const minutes = Math.max(1, Math.round(Number(routeItem.routeDurationSec) / 60));
    const distanceKm = (Number(routeItem.routeDistanceM) / 1000).toFixed(1);
    return `차량 ${minutes}분 · ${distanceKm}km`;
  }

  return routeItem.routeNote || "거리 정보 확인 필요";
}

function getRouteDisplayItem(item) {
  return selectedRouteSupplier.value
    && getRouteCandidateKey(selectedRouteSupplier.value) === getRouteCandidateKey(item)
    && selectedRoute.value
    ? { ...item, ...selectedRoute.value }
    : item;
}

function getRouteCandidateKey(item) {
  return [
    item?.dataSource || "",
    item?.id || item?.candidateId || "",
    item?.supplierName || "",
    item?.materialName || "",
    item?.standard || "",
  ].join("|");
}

function getRouteCacheKey(item) {
  return [
    Number(request.value?.siteLat).toFixed(6),
    Number(request.value?.siteLng).toFixed(6),
    Number(item?.latitude).toFixed(6),
    Number(item?.longitude).toFixed(6),
    getRouteCandidateKey(item),
  ].join("|");
}

function hasKoreaCoordinate(latitude, longitude) {
  if (latitude === null || latitude === undefined || longitude === null || longitude === undefined) {
    return false;
  }
  const lat = Number(latitude);
  const lng = Number(longitude);
  return Number.isFinite(lat) && Number.isFinite(lng) && lat >= 32 && lat <= 39 && lng >= 124 && lng <= 132;
}

let routeRequestSequence = 0;
async function selectSupplierForRoute(item) {
  const currentRequest = ++routeRequestSequence;
  selectedRouteSupplier.value = item;

  if (!hasKoreaCoordinate(item?.latitude, item?.longitude)) {
    selectedRoute.value = {
      routeDistanceM: null,
      routeDurationSec: null,
      routeStatus: "unavailable",
      routeNote: "위치 정보 확인 필요",
      routePath: [],
    };
    return;
  }
  if (!hasKoreaCoordinate(request.value?.siteLat, request.value?.siteLng)) {
    selectedRoute.value = {
      routeDistanceM: null,
      routeDurationSec: null,
      routeStatus: "unavailable",
      routeNote: "자재 요청에서 현장 주소를 먼저 선택해 주세요.",
      routePath: [],
    };
    return;
  }

  const cacheKey = getRouteCacheKey(item);
  const cachedRoute = routeResultCache.get(cacheKey);
  if (cachedRoute) {
    selectedRoute.value = cachedRoute;
    return;
  }

  selectedRoute.value = {
    routeDistanceM: null,
    routeDurationSec: null,
    routeStatus: "not_requested",
    routeNote: "차량 경로 확인 중",
    routePath: [],
  };
  try {
    const result = await getDrivingRoute({
      originLat: request.value.siteLat,
      originLng: request.value.siteLng,
      destinationLat: item.latitude,
      destinationLng: item.longitude,
    });
    if (currentRequest === routeRequestSequence) {
      selectedRoute.value = result;
      if (result.routeStatus === "success") {
        routeResultCache.set(cacheKey, result);
      }
    }
  } catch {
    if (currentRequest === routeRequestSequence) {
      selectedRoute.value = {
        routeDistanceM: null,
        routeDurationSec: null,
        routeStatus: "failed",
        routeNote: "거리 정보 확인 필요",
        routePath: [],
      };
    }
  }
}

function getDistanceScoreLabel(item) {
  return hasRouteInformation(item)
    ? `${Math.round(Number(item.distanceScore || 0))}점`
    : "미확인";
}

function getMatchSignalLabel(item) {
  if (item.specSourceLabel) {
    return item.specSourceLabel;
  }

  if (item.dataSource === "narajangteo") {
    return "계약 이력 기반";
  }

  return "KS 수동 DB";
}

function getMatchSignalClass(item) {
  const label = getMatchSignalLabel(item);
  if (label.includes("품명") || label.includes("규격 매칭")) {
    return "high";
  }
  if (label.includes("대표")) {
    return "medium";
  }
  if (label.includes("계약 이력")) {
    return "review";
  }
  return "standard";
}

function getMatchConfidenceScore(item) {
  const label = getMatchSignalLabel(item);
  if (label.includes("품명") || label.includes("규격 매칭")) {
    return 3;
  }
  if (label.includes("대표")) {
    return 2;
  }
  if (label.includes("계약 이력")) {
    return 1;
  }
  return 2;
}

function getMatchConfidenceLabel(item) {
  const score = getMatchConfidenceScore(item);
  if (score >= 3) {
    return "규격 신뢰도 높음";
  }
  if (score === 2) {
    return "규격 신뢰도 보통";
  }
  return "규격 확인 필요";
}

function getMatchSignalDescription(item) {
  const evidence = getScoreEvidence(item).materialFit;
  if (evidence) {
    return evidence;
  }

  return `${getStandardEvidence(item).standard} 기준의 물성·규격 적합도를 랭킹에 반영했습니다.`;
}

function getLocationBasisLabel(item) {
  if (item.locationBasis === "supplier_address") {
    return "공급사 등록 주소 기준";
  }

  if (item.locationBasis === "contract_agency_estimated") {
    return `${item.locationLabel || "계약기관"} 기준 추정`;
  }

  return "좌표 확인 필요";
}

function compareNumber(left, right, direction = "asc") {
  const leftValue = Number(left);
  const rightValue = Number(right);
  const normalizedLeft = Number.isFinite(leftValue) ? leftValue : Number.MAX_SAFE_INTEGER;
  const normalizedRight = Number.isFinite(rightValue) ? rightValue : Number.MAX_SAFE_INTEGER;
  const result = normalizedLeft - normalizedRight;
  return direction === "desc" ? -result : result;
}

function parsePrice(value) {
  const price = Number(String(value).replace(/[^\d.]/g, ""));
  return Number.isFinite(price) && price > 0 ? price : Number.MAX_SAFE_INTEGER;
}

function resetFilters() {
  sortOption.value = "score";
  hideApprovalRequired.value = false;
  registeredOnly.value = false;
}

function getReasonItems(item) {
  return item.reasonItems?.length ? item.reasonItems : [item.reason];
}

function getPropertyComparison(item) {
  if (item.propertyComparison?.length) {
    return item.propertyComparison;
  }

  return getStandardEvidence(item).propertyChecks;
}

function getPropertySummary(item) {
  const rows = getPropertyComparison(item);
  const passed = rows.filter((row) => row.passed === true).length;
  const pending = rows.filter((row) => row.passed == null).length;
  const hasCarbon = rows.some((row) => row.label.includes("탄소"));

  return {
    passed,
    label: pending ? `${pending}개 항목 검토` : `${passed}개 기준 통과`,
    message: pending
      ? `${pending}개 항목은 후보의 시험성적 또는 상세 규격 확인이 필요합니다.`
      : hasCarbon
      ? "항복강도·인장강도·연신율은 기준 이상, 탄소당량은 기준 이하 조건으로 확인합니다."
      : `${getStandardEvidence(item).category} 기준 자재와 추천 자재의 주요 물성치를 비교합니다.`,
  };
}

function getPropertyResultLabel(row) {
  if (row.passed === true) return "통과";
  if (row.passed === false) return "미충족";
  return "검토";
}

function getPriceTrendBars(item) {
  const values = getPriceTrendValues(item);
  if (!values.length) {
    return [];
  }

  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = Math.max(1, max - min);
  const labels = item.trendLabels?.length === values.length
    ? item.trendLabels
    : values.map((_, index) => `${index + 1}월`);

  return values.map((value, index) => ({
    label: labels[index],
    value,
    display: formatShortPrice(value),
    height: 34 + ((value - min) / range) * 66,
  }));
}

function getPriceTrendValues(item) {
  if (item.priceTrend?.length) {
    return item.priceTrend.map(Number).filter((value) => Number.isFinite(value) && value > 0);
  }

  const price = parsePrice(item.price);
  if (!Number.isFinite(price) || price === Number.MAX_SAFE_INTEGER) {
    return [];
  }

  return [1.07, 1.045, 1.025, 1.015, 0.995, 1].map((ratio) => Math.round(price * ratio));
}

function getPriceTrendSummary(item) {
  const values = getPriceTrendValues(item);
  if (values.length < 2) {
    return "단가 이력 데이터가 충분하지 않아 현재 등록 단가 기준으로 표시합니다.";
  }

  const first = values[0];
  const latest = values[values.length - 1];
  const diffRate = ((latest - first) / first) * 100;
  const direction = diffRate <= 0 ? "하락" : "상승";
  return `최근 기준 ${Math.abs(diffRate).toFixed(1)}% ${direction} 흐름입니다. 실제 견적은 공급사 문의로 확정해야 합니다.`;
}

function formatShortPrice(value) {
  const price = Number(value);
  if (!Number.isFinite(price)) {
    return "-";
  }

  if (price >= 10000) {
    return `${(price / 10000).toFixed(price % 10000 === 0 ? 0 : 1)}만`;
  }

  return price.toLocaleString();
}

function getHardFilterEvidence(item) {
  if (item.hardFilterEvidence?.length) {
    return item.hardFilterEvidence;
  }

  const evidence = getStandardEvidence(item);
  const needsSource = evidence.verificationStatus === "needs_source";
  return [
    ...evidence.filters.slice(0, 3).map((description, index) => ({
      label: evidence.metrics[index] || "검증 항목",
      status: needsSource ? "기준 보강" : "확인",
      description,
    })),
    {
      label: "승인 리스크",
      status: isApprovalReviewRequired(item) ? "검토 필요" : "낮음",
      description: evidence.approvalRisk,
    },
  ];
}

function isApprovalReviewRequired(item) {
  return Boolean(item?.approvalRequired) || getStandardEvidence(item).verificationStatus === "needs_source";
}

function getApprovalRiskLabel(item) {
  if (item?.approvalRequired) {
    return "감리 승인 확인 필요";
  }

  return getStandardEvidence(item).verificationStatus === "needs_source"
    ? "적용 기준 검토 필요"
    : "승인 리스크 낮음";
}

function isHardFilterWarning(evidence) {
  return ["승인", "문의", "확인 필요", "보강"].some((keyword) => evidence.status?.includes(keyword));
}

function getScoreEvidence(item) {
  const evidence = getStandardEvidence(item);
  return {
    materialFit:
      item.scoreEvidence?.materialFit ||
      (evidence.verificationStatus === "needs_source"
        ? "적용 KS 기준이 확보되지 않아 물성 점수를 보수적으로 반영했습니다."
        : `${evidence.standard} 기준의 물성·규격 적합도를 가장 높은 비중으로 반영했습니다.`),
    price: item.scoreEvidence?.price || `${item.price} 기준으로 가격 점수 ${item.priceScore}점을 부여했습니다.`,
    distance:
      item.scoreEvidence?.distance ||
      (hasRouteInformation(item)
        ? `카카오 차량 경로 ${getDistanceLabel(item)}를 거리 점수에 반영했습니다.`
        : item.routeNote || "차량 경로가 확인되지 않아 거리 가중치를 제외했습니다."),
    reliability:
      item.scoreEvidence?.reliability ||
      `과거 납품 이력 ${item.deliveryCount}회를 기준으로 신뢰도 점수 ${item.reliabilityScore}점을 부여했습니다.`,
  };
}

function getApprovalRiskNote(item) {
  if (item.approvalRiskNote) {
    return item.approvalRiskNote;
  }

  const evidence = getStandardEvidence(item);
  return isApprovalReviewRequired(item)
    ? evidence.approvalRisk
    : `${evidence.standard} 기준으로 우선 검토 가능한 후보입니다. 최종 납품 가능 여부는 공급사 문의가 필요합니다.`;
}

function getApprovalChecklist(item) {
  if (item.approvalChecklist?.length) {
    return item.approvalChecklist;
  }

  const evidence = getStandardEvidence(item);
  if (evidence.verificationStatus === "needs_source") {
    return [
      { label: "적용 표준", status: "기준 보강", description: "재료군에 맞는 KS 기준 자료를 확인해야 합니다." },
      { label: "물성 기준", status: "검토 필요", description: "시험성적과 상세 규격 확인 전에는 적합 판정을 확정하지 않습니다." },
      { label: "현장 확인", status: "필요", description: "최종 납품 서류와 재고 여부는 공급사에 확인하세요." },
    ];
  }

  return item.approvalRequired
    ? [
        { label: "국제 규격", status: "승인 확인", description: "ASTM/JIS 등 동등 규격 자료 확인이 필요합니다." },
        { label: "구조 검토", status: "검토 필요", description: "강도 상향 또는 규격 변경 시 구조 영향 여부를 확인하세요." },
        { label: "감리 승인", status: "필요", description: "현장 적용 전 승인 절차를 확인해야 합니다." },
      ]
    : [
        { label: "규격 일치", status: "낮음", description: "동일 계열 규격 후보로 우선 문의가 가능합니다." },
        { label: "물성 기준", status: "통과", description: "Hard Filter 기준을 통과한 후보입니다." },
        { label: "현장 확인", status: "필요", description: "최종 납품 서류와 재고 여부는 공급사에 확인하세요." },
      ];
}

function getStandardEvidence(item) {
  const itemText = [
    item?.materialName,
    item?.standard,
    item?.strengthGrade,
  ]
    .filter(Boolean)
    .join(" ");
  const itemEvidence = getMatchedStandardEvidenceForMaterial(itemText);

  if (itemEvidence) {
    return itemEvidence;
  }

  const fallbackText = [
    itemText,
    request.value?.materialName,
    request.value?.standard,
    request.value?.strengthGrade,
    request.value?.category,
  ]
    .filter(Boolean)
    .join(" ");

  return getPrimaryStandardEvidenceForMaterial(fallbackText);
}

function openDetail(item) {
  selectedRecommendation.value = item;
}

function closeDetail() {
  selectedRecommendation.value = null;
}

function openInquiry(item) {
  selectedInquirySupplier.value = item;
  inquiryStatus.value = "";
  inquiryErrorMessage.value = "";
  inquiryForm.quantity = request.value?.requiredQuantity || "";
  inquiryForm.desiredDate = request.value?.requiredDate || "";
  inquiryForm.message = "";
  selectedRecommendation.value = null;
}

function closeInquiry() {
  selectedInquirySupplier.value = null;
  inquiryStatus.value = "";
}

async function submitInquiry() {
  if (isInquirySubmitting.value) return;
  try {
    isInquirySubmitting.value = true;
    inquiryStatus.value = "";
    inquiryErrorMessage.value = "";
    const inquiry = await createSupplierInquiry({
      requestId: route.query.requestId,
      requestMaterial: request.value,
      supplier: selectedInquirySupplier.value,
      requestType: "general",
      priority: "normal",
      requesterName: inquiryForm.requesterName,
      contact: inquiryForm.contact,
      quantity: inquiryForm.quantity,
      desiredDate: inquiryForm.desiredDate,
      message: inquiryForm.message,
    });

    inquiryStatus.value = "공급사 문의 요청이 접수되었습니다. 마이페이지 > 문의 내역에서 상태를 확인할 수 있습니다.";
    inquiryForm.message = "";
    await new Promise((resolve) => window.setTimeout(resolve, 650));
    closeInquiry();
    await router.push("/inquiries");
  } catch {
    inquiryErrorMessage.value = "공급사 문의를 저장하지 못했습니다. 잠시 후 다시 시도해주세요.";
  } finally {
    isInquirySubmitting.value = false;
  }
}

async function loadRecommendations() {
  try {
    isLoading.value = true;
    errorMessage.value = "";
    selectedRouteSupplier.value = null;
    selectedRoute.value = null;
    request.value = await getLatestMaterialRequest();
    recommendations.value = await getRecommendations(route.query.requestId, {
      includeInternational: !hideApprovalRequired.value,
      keyword: route.query.keyword || "",
      request: request.value,
    });
  } catch {
    errorMessage.value = "추천 결과를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.";
  } finally {
    isLoading.value = false;
  }
}

const showAllList = ref(false);
const showRequestSummary = ref(false);
const expandedScores = ref({});

const allRankingList = computed(() =>
  filteredRecommendations.value.slice(0, 20).map((item, index) => ({
    ...item,
    displayRank: index + 1,
  })),
);

function getItemKey(item) {
  return `${item.supplierName}|${item.materialName}|${item.standard}`;
}

function toggleScoreExpand(key) {
  expandedScores.value = { ...expandedScores.value, [key]: !expandedScores.value[key] };
}

function isScoreExpanded(key) {
  return !!expandedScores.value[key];
}

function getScoreStarsFull(score) {
  const s = Math.min(100, Math.max(0, Number(score) || 0));
  return Math.floor(s / 20);
}

function getScoreStarsHalf(score) {
  const s = Math.min(100, Math.max(0, Number(score) || 0));
  return (s % 20) >= 10 ? 1 : 0;
}

function getScoreStarsEmpty(score) {
  return 5 - getScoreStarsFull(score) - getScoreStarsHalf(score);
}

function getShortDistance(item) {
  const routeItem = getRouteDisplayItem(item);
  if (hasRouteInformation(routeItem)) {
    const distanceKm = (Number(routeItem.routeDistanceM) / 1000).toFixed(1);
    return `${distanceKm}km`;
  }
  return routeItem.routeNote || "-";
}
</script>

<style scoped>
/* ─── Page Header ─── */
.rec-page-heading { margin-bottom: 28px; }
.rec-eyebrow-wrap { display: flex; align-items: center; gap: 6px; margin-bottom: 10px; }
.rec-eyebrow-wrap .eyebrow { font-size: 13px; font-weight: 600; color: var(--color-primary, #2563eb); letter-spacing: .04em; }
.eyebrow-icon { color: var(--color-primary, #2563eb); }
.rec-header-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.rec-header-row h1 { font-size: 32px; font-weight: 900; margin: 0 0 8px; }
.rec-header-row p { color: #475569; font-size: 15px; line-height: 1.6; margin: 0; }
.btn-summary-toggle { flex-shrink: 0; padding: 8px 18px; border: 1.5px solid #cbd5e1; border-radius: 8px; background: #fff; font-size: 13px; font-weight: 600; color: #334155; cursor: pointer; white-space: nowrap; }
.btn-summary-toggle:hover { background: #f8fafc; }
.request-summary-panel { margin-top: 12px; background: #f1f5f9; border-radius: 8px; padding: 12px 16px; font-size: 14px; color: #475569; }

/* ─── Criteria Card ─── */
.criteria-card { display: flex; align-items: center; gap: 24px; background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px 28px; margin-bottom: 32px; flex-wrap: wrap; }
.criteria-card-title { font-size: 13px; font-weight: 700; color: #64748b; text-align: center; min-width: 60px; line-height: 1.4; }
.criteria-card-title small { font-size: 11px; color: #94a3b8; }
.criteria-items { display: flex; gap: 20px; flex: 1; flex-wrap: wrap; }
.criteria-item { display: flex; align-items: center; gap: 8px; min-width: 180px; flex: 1; }
.criteria-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.criteria-icon-blue { background: #dbeafe; color: #2563eb; }
.criteria-icon-orange { background: #ffedd5; color: #ea580c; }
.criteria-icon-green { background: #dcfce7; color: #16a34a; }
.criteria-icon-purple { background: #ede9fe; color: #7c3aed; }
.criteria-name { font-size: 13px; font-weight: 600; color: #334155; min-width: 60px; }
.criteria-stars { display: flex; gap: 1px; }
.cstar { font-size: 14px; }
.cstar-on { color: #f59e0b; }
.cstar-off { color: #e2e8f0; }
.criteria-bar-wrap { flex: 1; height: 6px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
.criteria-bar-fill { height: 100%; background: var(--color-primary, #2563eb); border-radius: 99px; }
.criteria-pct { font-size: 13px; font-weight: 700; color: #334155; min-width: 32px; text-align: right; }

/* ─── TOP 5 Section ─── */
.top5-section { margin-bottom: 40px; }
.top5-header { display: flex; align-items: center; gap: 14px; margin-bottom: 18px; flex-wrap: wrap; padding: 14px 20px; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; }
.top5-header h2 { font-size: 18px; font-weight: 800; color: #1e293b; margin: 0; white-space: nowrap; }
.sort-label { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: #64748b; }
.sort-label select { border: 1.5px solid #cbd5e1; border-radius: 7px; padding: 5px 10px; font-size: 13px; color: #334155; background: #fff; }
.top5-header .filter-toggles { display: flex; gap: 12px; flex-wrap: wrap; }
.top5-header .filter-toggles label { display: flex; align-items: center; gap: 5px; font-size: 13px; color: #475569; cursor: pointer; }
.reset-btn { margin-left: auto; padding: 7px 16px; font-size: 13px; }

/* ─── Supplier Card (rec-row) ─── */
.recommendation-list { display: flex; flex-direction: column; gap: 16px; }
.rec-row { display: grid; grid-template-columns: 52px 1fr 140px 180px 120px; gap: 20px; align-items: start; background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px 24px; transition: box-shadow .15s; }
.rec-row:hover { box-shadow: 0 4px 18px rgba(0,0,0,.07); }

.rec-rank { display: flex; justify-content: center; padding-top: 4px; }
.rank-num { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 800; background: #e2e8f0; color: #64748b; }
.rank-num.rank-first { background: #f59e0b; color: #fff; }

.rec-main h2 { font-size: 17px; font-weight: 800; color: #1e293b; margin: 0 0 3px; }
.rec-material { font-size: 13px; color: #64748b; margin: 0 0 8px; }
.rec-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.rec-tag { font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 99px; }
.rec-tag-blue { background: #dbeafe; color: #1d4ed8; }
.rec-tag-green { background: #dcfce7; color: #15803d; }
.rec-tag-gray { background: #f1f5f9; color: #475569; }
.rec-metrics-row { display: flex; flex-wrap: wrap; gap: 10px; }
.metric-pill { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 3px 8px; }

.rec-score-col { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 4px; }
.rec-score-label { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: .04em; }
.rec-score-num { font-size: 28px; font-weight: 800; color: #1e293b; line-height: 1.1; }
.rec-stars { display: flex; gap: 2px; margin: 2px 0; }
.star-full { color: #f59e0b; font-size: 16px; }
.star-half { color: #f59e0b; font-size: 16px; opacity: .55; }
.star-empty { color: #e2e8f0; font-size: 16px; }
.btn-score-detail { font-size: 11px; color: #2563eb; background: none; border: none; cursor: pointer; padding: 2px 0; white-space: nowrap; }
.btn-score-detail:hover { text-decoration: underline; }
.score-detail-panel { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 6px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; width: 100%; }
.sub-score-item { display: flex; justify-content: space-between; font-size: 11px; color: #64748b; }
.sub-score-item strong { color: #1e293b; font-weight: 700; }

.rec-reasons-col { }
.rec-reasons-label { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: .04em; display: block; margin-bottom: 6px; }
.rec-reason-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 5px; }
.rec-reason-list li { font-size: 12.5px; color: #334155; display: flex; gap: 5px; align-items: flex-start; line-height: 1.4; }
.reason-check { color: #16a34a; font-weight: 700; flex-shrink: 0; }

.rec-actions { display: flex; flex-direction: column; gap: 8px; padding-top: 2px; }
.btn-detail { padding: 8px 16px; border: 1.5px solid #cbd5e1; border-radius: 8px; background: #fff; font-size: 13px; font-weight: 600; color: #334155; cursor: pointer; white-space: nowrap; }
.btn-detail:hover { background: #f8fafc; }
.btn-inquiry { padding: 8px 16px; border-radius: 8px; background: var(--color-primary, #2563eb); border: none; font-size: 13px; font-weight: 600; color: #fff; cursor: pointer; white-space: nowrap; }
.btn-inquiry:hover { opacity: .88; }

/* ─── Show All Button ─── */
.show-all-wrap { display: flex; justify-content: center; margin-top: 20px; }
.btn-show-all { padding: 11px 32px; border: 1.5px solid #cbd5e1; border-radius: 99px; background: #fff; font-size: 14px; font-weight: 700; color: #334155; cursor: pointer; }
.btn-show-all:hover { background: #f8fafc; }

/* ─── Full Ranking Table ─── */
.ranking-table-section { margin-bottom: 40px; }
.ranking-table-section h2 { font-size: 18px; font-weight: 800; color: #1e293b; margin-bottom: 16px; }
.ranking-table-wrap { overflow-x: auto; border-radius: 14px; border: 1px solid #e2e8f0; }
.ranking-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.ranking-table thead th { background: #f8fafc; padding: 12px 14px; text-align: left; font-size: 12px; font-weight: 700; color: #64748b; white-space: nowrap; border-bottom: 1px solid #e2e8f0; }
.ranking-table tbody tr:hover { background: #f8fafc; }
.ranking-table tbody td { padding: 13px 14px; vertical-align: middle; border-bottom: 1px solid #f1f5f9; color: #334155; }
.ranking-table tbody tr:last-child td { border-bottom: none; }
.rank-badge { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: #e2e8f0; color: #64748b; font-size: 13px; font-weight: 700; }
.rank-badge.rank-badge-first { background: #f59e0b; color: #fff; }
.tbl-supplier-name { font-weight: 700; color: #1e293b; margin-bottom: 2px; }
.tbl-supplier-type { font-size: 11px; color: #94a3b8; }
.tbl-material { color: #475569; }
.tbl-material small { color: #94a3b8; font-size: 11px; }
.tbl-score-cell { font-size: 18px; font-weight: 800; color: #1e293b; white-space: nowrap; }
.tbl-score-cell small { font-size: 11px; color: #94a3b8; font-weight: 500; }
.tbl-sub-scores { min-width: 160px; }
.sub-score-bar-row { display: flex; align-items: center; gap: 5px; margin-bottom: 3px; }
.sub-label { font-size: 10px; color: #94a3b8; min-width: 22px; }
.bar-wrap { flex: 1; height: 5px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 99px; }
.bar-blue { background: #3b82f6; }
.bar-orange { background: #f97316; }
.bar-green { background: #22c55e; }
.bar-purple { background: #a855f7; }
.sub-val { font-size: 10px; font-weight: 700; color: #334155; min-width: 16px; text-align: right; }
.tbl-action-cell { display: flex; flex-direction: column; gap: 5px; }
.btn-inquiry-sm { padding: 5px 12px; border-radius: 6px; background: var(--color-primary, #2563eb); border: none; font-size: 12px; font-weight: 600; color: #fff; cursor: pointer; }
.btn-inquiry-sm:hover { opacity: .88; }
.btn-detail-sm { padding: 5px 12px; border-radius: 6px; background: #fff; border: 1.5px solid #cbd5e1; font-size: 12px; font-weight: 600; color: #334155; cursor: pointer; }
.btn-detail-sm:hover { background: #f8fafc; }

/* ─── Map Section ─── */
.map-section { margin-bottom: 32px; }
.map-section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 12px; }
.map-section-header h2 { font-size: 18px; font-weight: 800; color: #1e293b; margin: 0; }
.map-legend { display: flex; gap: 16px; list-style: none; padding: 0; margin: 0; flex-wrap: wrap; }
.map-legend li { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #64748b; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-site { background: #ef4444; }
.legend-top { background: #f59e0b; }
.legend-other { background: #94a3b8; border: 2px solid #cbd5e1; }

/* ─── Disclaimer ─── */
.rec-disclaimer { display: flex; align-items: flex-start; gap: 7px; font-size: 12px; color: #94a3b8; line-height: 1.5; padding: 14px 18px; background: #f8fafc; border-radius: 10px; margin-top: 8px; }

/* ─── Responsive ─── */
@media (max-width: 900px) {
  .rec-row { grid-template-columns: 44px 1fr; }
  .rec-score-col, .rec-reasons-col { grid-column: 1 / -1; border-top: 1px solid #f1f5f9; padding-top: 12px; }
  .rec-actions { flex-direction: row; grid-column: 1 / -1; }
  .criteria-items { gap: 12px; }
  .criteria-item { min-width: 140px; }
}
@media (max-width: 600px) {
  .rec-row { grid-template-columns: 1fr; }
  .rec-rank { justify-content: flex-start; }
  .top5-header { gap: 10px; }
  .sort-label { width: 100%; }
  .criteria-card { flex-direction: column; align-items: flex-start; }
}
</style>
