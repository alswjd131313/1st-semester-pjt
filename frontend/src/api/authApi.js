import { reactive } from "vue";
import { apiClient, AUTH_TOKEN_KEY, buildApiUrl } from "./apiClient";

const STORAGE_KEY = "paceflow_v2_user";

function loadStoredUser() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

function saveSession({ token, user }) {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  authState.user = user;
  return user;
}

function clearSession() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(STORAGE_KEY);
  authState.user = null;
}

function normalizeEmail(email = "") {
  return email.trim().toLowerCase();
}

function extractErrorMessage(error, fallbackMessage) {
  const data = error?.response?.data;
  if (!data) return fallbackMessage;
  if (typeof data === "string") return data;
  if (data.error) return data.error;
  if (data.message) return data.message;

  const firstField = Object.keys(data)[0];
  const firstError = firstField ? data[firstField] : null;
  if (Array.isArray(firstError)) return firstError[0];
  if (typeof firstError === "string") return firstError;

  return fallbackMessage;
}

export const authState = reactive({
  user: loadStoredUser(),
});

export async function registerUser(payload) {
  try {
    const { data } = await apiClient.post(buildApiUrl("/api/v1/auth/register/"), {
      role: payload.role,
      name: payload.name?.trim(),
      email: normalizeEmail(payload.email),
      password: payload.password,
      password_confirm: payload.passwordConfirm,
      company_name: payload.companyName?.trim(),
    });

    return saveSession(data);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "회원가입 정보를 확인해 주세요."));
  }
}

export async function loginUser(payload) {
  try {
    const { data } = await apiClient.post(buildApiUrl("/api/v1/auth/login/"), {
      role: payload.role,
      email: normalizeEmail(payload.email),
      password: payload.password,
    });

    return saveSession(data);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "로그인 정보를 확인해 주세요."));
  }
}

export async function logoutUser() {
  try {
    if (localStorage.getItem(AUTH_TOKEN_KEY)) {
      await apiClient.post(buildApiUrl("/api/v1/auth/logout/"));
    }
  } catch {
    // 로컬 세션은 항상 정리해서 사용자가 로그아웃 상태로 돌아가게 둡니다.
  } finally {
    clearSession();
  }
}

export function isLoggedIn() {
  return Boolean(authState.user && localStorage.getItem(AUTH_TOKEN_KEY));
}

export function hasRole(role) {
  return authState.user?.role === role;
}

export async function updateProfile(payload) {
  try {
    const body = {};
    if (payload.name?.trim()) body.name = payload.name.trim();
    if (payload.companyName?.trim()) body.company_name = payload.companyName.trim();
    if (payload.newPassword?.trim()) {
      body.current_password = payload.currentPassword || "";
      body.new_password = payload.newPassword.trim();
    }
    const { data } = await apiClient.patch(buildApiUrl("/api/v1/auth/profile/"), body);
    const updated = data.user || data;
    if (data.token) {
      localStorage.setItem(AUTH_TOKEN_KEY, data.token);
      apiClient.defaults.headers.common["Authorization"] = `Token ${data.token}`;
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    authState.user = updated;
    return updated;
  } catch (error) {
    throw new Error(extractErrorMessage(error, "프로필 수정에 실패했습니다."));
  }
}
