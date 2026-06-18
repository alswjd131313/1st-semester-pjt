import { apiClient, buildApiUrl } from "./apiClient";

export async function searchAddresses(keyword) {
  const { data } = await apiClient.get(buildApiUrl("/api/v1/addresses/search/"), {
    params: { keyword },
  });
  return data.addresses || [];
}

export async function geocodeAddress(address) {
  const { data } = await apiClient.get(buildApiUrl("/api/v1/addresses/geocode/"), {
    params: { address },
  });
  return data;
}
