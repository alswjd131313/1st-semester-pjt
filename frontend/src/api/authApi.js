import { reactive } from "vue";

const STORAGE_KEY = "paceflow_v2_user";
const REGISTERED_USERS_KEY = "paceflow_v2_registered_users";

export const demoAccounts = [
  {
    role: "requester",
    roleLabel: "자재 요청자",
    name: "김현장",
    email: "requester@paceflow.kr",
    password: "paceflow123",
    companyName: "성수건설",
  },
  {
    role: "supplier",
    roleLabel: "공급사",
    name: "박공급",
    email: "supplier@paceflow.kr",
    password: "paceflow123",
    companyName: "성수철강",
  },
];

function normalizeEmail(email = "") {
  return email.trim().toLowerCase();
}

function loadRegisteredUsers() {
  try {
    const saved = localStorage.getItem(REGISTERED_USERS_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function saveRegisteredUsers(users) {
  localStorage.setItem(REGISTERED_USERS_KEY, JSON.stringify(users));
}

function getAllAccounts() {
  return [...demoAccounts, ...loadRegisteredUsers()];
}

function toSessionUser(account) {
  return {
    id: account.id || `USER-${Date.now()}`,
    name: account.name,
    email: account.email,
    role: account.role,
    companyName: account.companyName,
  };
}

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

export function registerUser(payload) {
  const email = normalizeEmail(payload.email);
  const password = payload.password || "";
  const passwordConfirm = payload.passwordConfirm || "";

  if (!payload.role || !payload.name?.trim() || !email || !payload.companyName?.trim()) {
    throw new Error("필수 정보를 모두 입력해 주세요.");
  }

  if (password.length < 6) {
    throw new Error("비밀번호는 6자 이상 입력해 주세요.");
  }

  if (password !== passwordConfirm) {
    throw new Error("비밀번호 확인이 일치하지 않습니다.");
  }

  const registeredUsers = loadRegisteredUsers();
  const duplicated = getAllAccounts().some((account) => normalizeEmail(account.email) === email);

  if (duplicated) {
    throw new Error("이미 가입된 이메일입니다.");
  }

  const user = {
    id: `USER-${Date.now()}`,
    role: payload.role,
    roleLabel: payload.role === "supplier" ? "공급사" : "자재 요청자",
    name: payload.name.trim(),
    email,
    password,
    companyName: payload.companyName.trim(),
  };

  saveRegisteredUsers([...registeredUsers, user]);
  return toSessionUser(user);
}

export function loginUser(payload) {
  const account = getAllAccounts().find(
    (item) =>
      item.role === payload.role &&
      item.email === normalizeEmail(payload.email) &&
      item.password === payload.password,
  );

  if (!account) {
    throw new Error("가입된 계정 정보와 일치하지 않습니다.");
  }

  const user = toSessionUser(account);

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
