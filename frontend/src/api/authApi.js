import { reactive } from "vue";
import { apiClient, AUTH_TOKEN_KEY, AUTH_UNAUTHORIZED_EVENT, AUTH_USER_KEY, buildApiUrl } from "./apiClient";

const STORAGE_KEY = AUTH_USER_KEY;

function normalizeProfileImageUrl(value) {
  if (!value || typeof value !== "string") return "";
  if (value.startsWith("data:") || /^https?:\/\//i.test(value)) return value;

  const base = apiClient.defaults.baseURL || import.meta.env.VITE_API_BASE_URL || "";
  if (!base) return value;

  return `${String(base).replace(/\/$/, "")}/${value.replace(/^\//, "")}`;
}

function normalizeAuthUser(user) {
  if (!user) return user;
  const profileImage = normalizeProfileImageUrl(
    user.profile_image || user.profileImage || user.avatar || user.profile?.image || "",
  );
  const defaultSiteLatitude = toNullableNumber(user.defaultSiteLatitude ?? user.default_site_latitude);
  const defaultSiteLongitude = toNullableNumber(user.defaultSiteLongitude ?? user.default_site_longitude);

  return {
    ...user,
    companyName: user.companyName ?? user.company_name ?? "",
    company_name: user.companyName ?? user.company_name ?? "",
    profile_image: profileImage,
    profileImage: profileImage,
    defaultSiteAddress: user.defaultSiteAddress ?? user.default_site_address ?? "",
    defaultSiteDetailAddress: user.defaultSiteDetailAddress ?? user.default_site_detail_address ?? "",
    defaultSiteZipNo: user.defaultSiteZipNo ?? user.default_site_zip_no ?? "",
    defaultSiteLatitude,
    defaultSiteLongitude,
    default_site_address: user.defaultSiteAddress ?? user.default_site_address ?? "",
    default_site_detail_address: user.defaultSiteDetailAddress ?? user.default_site_detail_address ?? "",
    default_site_zip_no: user.defaultSiteZipNo ?? user.default_site_zip_no ?? "",
    default_site_latitude: defaultSiteLatitude,
    default_site_longitude: defaultSiteLongitude,
  };
}

function toNullableNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function loadStoredUser() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? normalizeAuthUser(JSON.parse(saved)) : null;
  } catch {
    return null;
  }
}

function saveSession({ token, user }) {
  const normalizedUser = normalizeAuthUser(user);
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(normalizedUser));
  authState.user = normalizedUser;
  return normalizedUser;
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

if (typeof window !== "undefined") {
  window.addEventListener(AUTH_UNAUTHORIZED_EVENT, () => {
    authState.user = null;
  });
}

export async function registerUser(payload) {
  try {
    const { data } = await apiClient.post(buildApiUrl("/api/v1/auth/register/"), {
      role: payload.role,
      name: payload.name?.trim(),
      email: normalizeEmail(payload.email),
      password: payload.password,
      password_confirm: payload.passwordConfirm,
      company_name: payload.companyName?.trim(),
      default_site_address: payload.role === "requester" ? payload.defaultSiteAddress?.trim() || "" : "",
      default_site_detail_address: payload.role === "requester" ? payload.defaultSiteDetailAddress?.trim() || "" : "",
      default_site_zip_no: payload.role === "requester" ? payload.defaultSiteZipNo || "" : "",
      default_site_latitude: payload.role === "requester" ? toNullableNumber(payload.defaultSiteLatitude) : null,
      default_site_longitude: payload.role === "requester" ? toNullableNumber(payload.defaultSiteLongitude) : null,
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

export function getProfileImageUrl(user) {
  return normalizeProfileImageUrl(
    user?.profile_image || user?.profileImage || user?.avatar || user?.profile?.image || "",
  );
}

function isUploadFile(value) {
  return typeof File !== "undefined" && value instanceof File
    || typeof Blob !== "undefined" && value instanceof Blob;
}

export async function updateProfile(payload) {
  try {
    const profileFile = payload.profileImage || payload.profile_image;
    const hasFile = isUploadFile(profileFile);
    const body = hasFile ? new FormData() : {};
    const setField = (key, value) => {
      if (hasFile) {
        body.append(key, value);
      } else {
        body[key] = value;
      }
    };

    if (payload.name?.trim()) setField("name", payload.name.trim());
    if (payload.companyName?.trim()) setField("company_name", payload.companyName.trim());
    if (hasFile) setField("profile_image", profileFile);
    if (Object.prototype.hasOwnProperty.call(payload, "defaultSiteAddress")) {
      setField("default_site_address", payload.defaultSiteAddress?.trim() || "");
    }
    if (Object.prototype.hasOwnProperty.call(payload, "defaultSiteDetailAddress")) {
      setField("default_site_detail_address", payload.defaultSiteDetailAddress?.trim() || "");
    }
    if (Object.prototype.hasOwnProperty.call(payload, "defaultSiteZipNo")) {
      setField("default_site_zip_no", payload.defaultSiteZipNo || "");
    }
    if (Object.prototype.hasOwnProperty.call(payload, "defaultSiteLatitude")) {
      setField("default_site_latitude", toNullableNumber(payload.defaultSiteLatitude));
    }
    if (Object.prototype.hasOwnProperty.call(payload, "defaultSiteLongitude")) {
      setField("default_site_longitude", toNullableNumber(payload.defaultSiteLongitude));
    }
    if (payload.newPassword?.trim()) {
      setField("current_password", payload.currentPassword || "");
      setField("new_password", payload.newPassword.trim());
    }
    const config = hasFile ? { headers: { "Content-Type": "multipart/form-data" } } : undefined;
    const { data } = await apiClient.patch(buildApiUrl("/api/v1/auth/profile/"), body, config);
    const updated = normalizeAuthUser(data.user || data);
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
