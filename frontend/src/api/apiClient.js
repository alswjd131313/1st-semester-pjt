import axios from "axios";

export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK !== "false";
export const AUTH_TOKEN_KEY = "paceflow_v2_auth_token";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export function buildApiUrl(path) {
  return path.startsWith("/") ? path : `/${path}`;
}
