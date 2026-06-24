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

export function getNotificationsForUser(user) {
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

export function markNotificationRead(notificationId, user) {
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

export function markAllNotificationsRead(user) {
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

export function deleteReadNotifications(user) {
  const recipientKeys = getUserRecipientKeys(user);
  const notifications = readNotifications().filter((item) => !(
    item.recipient_role === user.role
    && recipientKeys.has(item.recipient_key)
    && item.is_read
  ));
  writeNotifications(notifications);
}

export function deleteNotification(notificationId, user) {
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
