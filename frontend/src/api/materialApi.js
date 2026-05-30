import { rankingMaterials, recommendationResults } from "../data/dummyData";

export async function getRankingMaterials() {
  return rankingMaterials;
}

export async function createMaterialRequest(payload) {
  return {
    id: "REQ-MOCK-001",
    ...payload,
  };
}

export async function getRecommendations() {
  return recommendationResults;
}

export async function registerSupplierMaterial(payload) {
  return {
    id: "SUP-MOCK-001",
    ...payload,
  };
}
