import { apiClient, buildApiUrl, USE_MOCK_API } from "./apiClient";

const NOTIFICATION_STORAGE_KEY = "paceflow_v2_notifications";
export const NOTIFICATION_CHANGE_EVENT = "paceflow:notifications-changed";

function normalizeIdentity(value = "") {
  return String(value).trim().toLocaleLowerCase("ko-KR");
}

function readNotifications() {
  try {
    const saved = localStorage.getItem(NOTIFICATION_STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function writeNotifications(notifications) {
  localStorage.setItem(NOTIFICATION_STORAGE_KEY, JSON.stringify(notifications));
  window.dispatchEvent(new CustomEvent(NOTIFICATION_CHANGE_EVENT));
}

export function buildUserRecipientKey(user = {}) {
  if (user.id !== null && user.id !== undefined && user.id !== "") {
    return `user:${user.id}`;
  }
  if (user.email) {
    return `email:${normalizeIdentity(user.email)}`;
  }
  if (user.role === "supplier" && user.companyName) {
    return `supplier:${normalizeIdentity(user.companyName)}`;
  }
  return "";
}

export function buildSupplierRecipientKey(supplier = {}) {
  const ownerId = supplier.ownerUserId ?? supplier.owner_user_id;
  if (ownerId !== null && ownerId !== undefined && ownerId !== "") {
    return `user:${ownerId}`;
  }
  const ownerEmail = supplier.ownerEmail || supplier.owner_email;
  if (ownerEmail) {
    return `email:${normalizeIdentity(ownerEmail)}`;
  }
  const supplierName = supplier.supplierName || supplier.supplier_name || supplier.companyName;
  return supplierName ? `supplier:${normalizeIdentity(supplierName)}` : "";
}

export function getUserRecipientKeys(user = {}) {
  const keys = new Set();
  if (user.id !== null && user.id !== undefined && user.id !== "") {
    keys.add(`user:${user.id}`);
  }
  if (user.email) {
    keys.add(`email:${normalizeIdentity(user.email)}`);
  }
  if (user.role === "supplier" && user.companyName) {
    keys.add(`supplier:${normalizeIdentity(user.companyName)}`);
  }
  return keys;
}

function debugNotificationLog(message, payload = {}) {
  if (!import.meta.env.DEV) return;
  console.debug(`[notifications] ${message}`, payload);
}

function normalizeBackendNotification(item = {}) {
  return {
    id: item.id,
    recipient_user_id: item.recipient_id ?? null,
    actor_user_id: item.actor_id ?? null,
    type: item.type,
    title: item.title || "알림",
    message: item.message || "",
    related_inquiry_id: item.related_inquiry_id ?? null,
    target_path: item.target_path || "/inquiries",
    is_read: Boolean(item.is_read),
    created_at: item.created_at || new Date().toISOString(),
    event_key: item.event_key || "",
  };
}

export async function getNotificationsForUser(user) {
  if (!USE_MOCK_API) {
    debugNotificationLog("fetch:start", { hasUser: Boolean(user?.id) });
    try {
      const { data } = await apiClient.get(buildApiUrl("/api/v1/notifications/"));
      const list = Array.isArray(data) ? data : data.results || [];
      const notifications = list.map(normalizeBackendNotification);
      debugNotificationLog("fetch:success", { count: notifications.length });
      return notifications;
    } catch (error) {
      debugNotificationLog("fetch:failed", {
        status: error?.response?.status,
        hasAuthorization: Boolean(error?.config?.headers?.Authorization),
      });
      throw error;
    }
  }

  const recipientKeys = getUserRecipientKeys(user);
  if (!recipientKeys.size) return [];

  return readNotifications()
    .filter((notification) => (
      notification.recipient_role === user.role
      && recipientKeys.has(notification.recipient_key)
    ))
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
}

export function createNotification(payload) {
  if (!payload.recipient_key || !payload.recipient_role) return null;

  const notifications = readNotifications();
  if (
    payload.event_key
    && notifications.some((item) => (
      item.event_key === payload.event_key && item.recipient_key === payload.recipient_key
    ))
  ) {
    return null;
  }

  const notification = {
    id: `NTF-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    recipient_user_id: payload.recipient_user_id ?? null,
    recipient_role: payload.recipient_role,
    recipient_key: payload.recipient_key,
    type: payload.type,
    title: payload.title,
    message: payload.message,
    related_inquiry_id: payload.related_inquiry_id ?? null,
    target_path: payload.target_path || "/inquiries",
    is_read: false,
    created_at: payload.created_at || new Date().toISOString(),
    event_key: payload.event_key || "",
  };

  writeNotifications([notification, ...notifications].slice(0, 200));
  return notification;
}

export async function getUnreadNotificationCount() {
  if (!USE_MOCK_API) {
    debugNotificationLog("unread-count:start");
    try {
      const { data } = await apiClient.get(buildApiUrl("/api/v1/notifications/unread-count/"));
      debugNotificationLog("unread-count:success", { count: Number(data.count || 0) });
      return Number(data.count || 0);
    } catch (error) {
      debugNotificationLog("unread-count:failed", {
        status: error?.response?.status,
        hasAuthorization: Boolean(error?.config?.headers?.Authorization),
      });
      throw error;
    }
  }
  return null;
}

export async function markNotificationRead(notificationId, user) {
  if (!USE_MOCK_API) {
    await apiClient.post(buildApiUrl(`/api/v1/notifications/${notificationId}/read/`));
    window.dispatchEvent(new CustomEvent(NOTIFICATION_CHANGE_EVENT));
    return;
  }

  const recipientKeys = getUserRecipientKeys(user);
  let changed = false;
  const notifications = readNotifications().map((item) => {
    if (
      item.id !== notificationId
      || item.recipient_role !== user.role
      || !recipientKeys.has(item.recipient_key)
      || item.is_read
    ) {
      return item;
    }
    changed = true;
    return { ...item, is_read: true };
  });
  if (changed) writeNotifications(notifications);
}

export async function markAllNotificationsRead(user) {
  if (!USE_MOCK_API) {
    await apiClient.post(buildApiUrl("/api/v1/notifications/read-all/"));
    window.dispatchEvent(new CustomEvent(NOTIFICATION_CHANGE_EVENT));
    return;
  }

  const recipientKeys = getUserRecipientKeys(user);
  let changed = false;
  const notifications = readNotifications().map((item) => {
    if (item.recipient_role !== user.role || !recipientKeys.has(item.recipient_key) || item.is_read) {
      return item;
    }
    changed = true;
    return { ...item, is_read: true };
  });
  if (changed) writeNotifications(notifications);
}

export async function deleteReadNotifications(user) {
  if (!USE_MOCK_API) {
    // 서버에는 "읽은 알림 일괄 삭제" API를 두지 않고, 프론트에서 읽은 알림을 순차 삭제합니다.
    const notifications = await getNotificationsForUser(user);
    await Promise.all(
      notifications
        .filter((item) => item.is_read)
        .map((item) => deleteNotification(item.id, user)),
    );
    window.dispatchEvent(new CustomEvent(NOTIFICATION_CHANGE_EVENT));
    return;
  }

  const recipientKeys = getUserRecipientKeys(user);
  const notifications = readNotifications().filter((item) => !(
    item.recipient_role === user.role
    && recipientKeys.has(item.recipient_key)
    && item.is_read
  ));
  writeNotifications(notifications);
}

export async function deleteNotification(notificationId, user) {
  if (!USE_MOCK_API) {
    await apiClient.delete(buildApiUrl(`/api/v1/notifications/${notificationId}/`));
    window.dispatchEvent(new CustomEvent(NOTIFICATION_CHANGE_EVENT));
    return;
  }

  const recipientKeys = getUserRecipientKeys(user);
  let changed = false;
  const notifications = readNotifications().filter((item) => {
    const shouldDelete = (
      item.id === notificationId
      && item.recipient_role === user.role
      && recipientKeys.has(item.recipient_key)
    );
    if (shouldDelete) changed = true;
    return !shouldDelete;
  });
  if (changed) writeNotifications(notifications);
}

export function subscribeToNotificationChanges(listener) {
  const handleStorage = (event) => {
    if (event.key === NOTIFICATION_STORAGE_KEY) listener();
  };
  window.addEventListener(NOTIFICATION_CHANGE_EVENT, listener);
  window.addEventListener("storage", handleStorage);
  return () => {
    window.removeEventListener(NOTIFICATION_CHANGE_EVENT, listener);
    window.removeEventListener("storage", handleStorage);
  };
}
