import { reactive } from "vue";

const STORAGE_KEY = "paceflow_mock_user";

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY));
  } catch {
    return null;
  }
}

export const authState = reactive({
  user: readStoredUser(),
});

export async function loginUser({ email, password, companyName, role = "requester" }) {
  if (!email || !password) {
    throw new Error("이메일과 비밀번호를 입력해주세요.");
  }

  const user = {
    email,
    companyName: companyName || (role === "supplier" ? "공급사 계정" : "현장 담당자"),
    role,
    loggedInAt: new Date().toISOString(),
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  authState.user = user;
  return user;
}

export async function loginSupplier(payload) {
  return loginUser({ ...payload, role: "supplier" });
}

export function logout() {
  localStorage.removeItem(STORAGE_KEY);
  authState.user = null;
}

export function isLoggedIn() {
  return Boolean(authState.user);
}
