import { reactive } from "vue";

const STORAGE_KEY = "paceflow_v2_user";

function loadStoredUser() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

export const authState = reactive({
  user: loadStoredUser(),
});

export function loginUser(payload) {
  const user = {
    id: `USER-${Date.now()}`,
    name: payload.name || "PaceFlow 사용자",
    email: payload.email,
    role: payload.role,
    companyName: payload.companyName || "",
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  authState.user = user;
  return user;
}

export function logoutUser() {
  localStorage.removeItem(STORAGE_KEY);
  authState.user = null;
}

export function isLoggedIn() {
  return Boolean(authState.user);
}

export function hasRole(role) {
  return authState.user?.role === role;
}
