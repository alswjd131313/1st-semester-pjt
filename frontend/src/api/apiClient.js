import axios from "axios";

export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK !== "false";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  headers: {
    "Content-Type": "application/json",
  },
});

export function buildApiUrl(path) {
  return path.startsWith("/") ? path : `/${path}`;
}
