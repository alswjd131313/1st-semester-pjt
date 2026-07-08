import axios from "axios";

export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK !== "false";
export const AUTH_TOKEN_KEY = "paceflow_v2_auth_token";
export const AUTH_USER_KEY = "paceflow_v2_user";
export const AUTH_UNAUTHORIZED_EVENT = "paceflow:auth-unauthorized";

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
  if (import.meta.env.DEV && /\/notifications\//.test(config.url || "")) {
    console.debug("[api] notification request auth", { hasAuthorization: Boolean(config.headers.Authorization) });
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(AUTH_USER_KEY);
      window.dispatchEvent(new CustomEvent(AUTH_UNAUTHORIZED_EVENT));
      if (import.meta.env.DEV) {
        console.debug("[api] unauthorized: cleared local auth session");
      }
    }
    return Promise.reject(error);
  },
);

export function buildApiUrl(path) {
  return path.startsWith("/") ? path : `/${path}`;
}
