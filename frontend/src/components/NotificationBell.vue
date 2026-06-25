<template>
  <div ref="notificationWrapRef" class="notification-wrap">
    <button
      type="button"
      class="notification-trigger"
      aria-label="알림"
      :aria-expanded="isOpen"
      @click.stop="toggleNotifications"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" />
      </svg>
      <span v-if="unreadCount" class="notification-badge">{{ badgeLabel }}</span>
    </button>

    <Transition name="notification-dropdown">
      <section v-if="isOpen" class="notification-dropdown" aria-label="알림 목록">
        <header>
          <div>
            <strong>알림</strong>
            <span v-if="unreadCount">읽지 않음 {{ unreadCount }}개</span>
          </div>
          <div class="notification-header-actions">
            <button v-if="unreadCount" type="button" @click="readAll">모두 읽음</button>
            <button v-if="readCount" type="button" class="btn-delete-read" @click="deleteRead">읽은 알림 삭제</button>
          </div>
        </header>

        <div v-if="recentNotifications.length" class="notification-list">
          <article
            v-for="notification in recentNotifications"
            :key="notification.id"
            :class="['notification-item', { unread: !notification.is_read }]"
            role="button"
            tabindex="0"
            @click="openNotification(notification)"
            @keydown.enter="openNotification(notification)"
            @keydown.space.prevent="openNotification(notification)"
          >
            <span class="notification-dot" aria-hidden="true"></span>
            <span class="notification-copy">
              <strong>{{ notification.title }}</strong>
              <span>{{ notification.message }}</span>
              <time>{{ formatNotificationTime(notification.created_at) }}</time>
            </span>
            <button
              type="button"
              class="notification-delete"
              :aria-label="`${notification.title} 알림 삭제`"
              title="알림 삭제"
              @click.stop="removeNotification(notification.id)"
              @keydown.stop
            >×</button>
          </article>
        </div>
        <p v-else class="notification-empty">새 알림이 없습니다.</p>
      </section>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import {
  deleteNotification,
  deleteReadNotifications,
  getNotificationsForUser,
  getUnreadNotificationCount,
  markAllNotificationsRead,
  markNotificationRead,
  subscribeToNotificationChanges,
} from "../api/notificationApi";

const props = defineProps({
  user: { type: Object, required: true },
});

const router = useRouter();
const notificationWrapRef = ref(null);
const notifications = ref([]);
const isOpen = ref(false);
const isLoading = ref(false);
let unsubscribeNotifications = null;

const recentNotifications = computed(() => notifications.value.slice(0, 5));
const unreadCount = computed(() => notifications.value.filter((item) => !item.is_read).length);
const readCount = computed(() => notifications.value.filter((item) => item.is_read).length);
const badgeLabel = computed(() => (unreadCount.value > 99 ? "99+" : unreadCount.value));

async function refreshNotifications() {
  if (!props.user?.id) {
    notifications.value = [];
    return;
  }

  try {
    isLoading.value = true;
    const [list, count] = await Promise.all([
      getNotificationsForUser(props.user),
      getUnreadNotificationCount().catch(() => null),
    ]);
    notifications.value = Array.isArray(list) ? list : [];
    if (import.meta.env.DEV) {
      console.debug("[notifications] bell:refreshed", {
        listCount: notifications.value.length,
        unreadCount: count ?? unreadCount.value,
        hasUser: Boolean(props.user?.id),
      });
    }
  } catch (error) {
    notifications.value = [];
    if (import.meta.env.DEV) {
      console.debug("[notifications] bell:failed", {
        status: error?.response?.status,
        hasAuthorization: Boolean(error?.config?.headers?.Authorization),
      });
    }
  } finally {
    isLoading.value = false;
  }
}

function toggleNotifications() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) refreshNotifications();
}

async function readAll() {
  await markAllNotificationsRead(props.user);
  await refreshNotifications();
}

async function deleteRead() {
  await deleteReadNotifications(props.user);
  await refreshNotifications();
}

async function removeNotification(notificationId) {
  await deleteNotification(notificationId, props.user);
  await refreshNotifications();
}

async function openNotification(notification) {
  await markNotificationRead(notification.id, props.user);
  await refreshNotifications();
  isOpen.value = false;
  await router.push(notification.target_path || "/inquiries");
}

function handleOutsideClick(event) {
  if (notificationWrapRef.value && !notificationWrapRef.value.contains(event.target)) {
    isOpen.value = false;
  }
}

function formatNotificationTime(value) {
  const timestamp = new Date(value).getTime();
  if (!Number.isFinite(timestamp)) return "방금 전";
  const minutes = Math.max(0, Math.floor((Date.now() - timestamp) / 60000));
  if (minutes < 1) return "방금 전";
  if (minutes < 60) return `${minutes}분 전`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  const days = Math.floor(hours / 24);
  return `${days}일 전`;
}

watch(() => props.user, () => {
  refreshNotifications();
}, { deep: true });

onMounted(() => {
  refreshNotifications();
  unsubscribeNotifications = subscribeToNotificationChanges(refreshNotifications);
  document.addEventListener("click", handleOutsideClick);
});

onBeforeUnmount(() => {
  unsubscribeNotifications?.();
  document.removeEventListener("click", handleOutsideClick);
});
</script>

<style scoped>
.notification-wrap{position:relative}.notification-trigger{position:relative;display:grid;width:42px;height:42px;place-items:center;border:1px solid #d8e4f3;border-radius:50%;color:#40516b;background:rgba(255,255,255,.92);cursor:pointer;transition:transform .18s,border-color .18s,background .18s}.notification-trigger:hover{transform:translateY(-1px);border-color:#9db9e6;background:#f7faff}.notification-trigger svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.notification-badge{position:absolute;top:-5px;right:-5px;display:grid;min-width:19px;height:19px;box-sizing:border-box;place-items:center;border:2px solid #fff;border-radius:999px;padding:0 4px;color:#fff;background:#ef4444;font-size:10px;font-weight:900}.notification-dropdown{position:absolute;top:calc(100% + 10px);right:0;z-index:300;overflow:hidden;width:min(380px,calc(100vw - 28px));border:1px solid #dce6f4;border-radius:18px;background:#fff;box-shadow:0 22px 60px rgba(24,50,90,.2)}.notification-dropdown>header{display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:1px solid #edf2f8;padding:16px 18px}.notification-dropdown>header div{display:grid;gap:2px}.notification-dropdown>header strong{color:#102a56;font-size:16px}.notification-dropdown>header span{color:#8492a8;font-size:11px}.notification-dropdown>header button{border:0;color:#1559e8;background:transparent;cursor:pointer;font-size:12px;font-weight:900}.notification-list{display:grid}.notification-item{display:grid;grid-template-columns:8px minmax(0,1fr) 28px;gap:10px;width:100%;box-sizing:border-box;border:0;border-bottom:1px solid #eef3f9;padding:14px 12px 14px 17px;color:inherit;background:#fff;cursor:pointer;text-align:left}.notification-item:last-child{border-bottom:0}.notification-item:hover{background:#f7faff}.notification-item.unread{background:#f1f6ff}.notification-dot{width:7px;height:7px;margin-top:6px;border-radius:50%;background:transparent}.notification-item.unread .notification-dot{background:#1559e8}.notification-copy{display:grid;gap:4px;min-width:0}.notification-copy strong{overflow:hidden;color:#18345e;font-size:13px;text-overflow:ellipsis;white-space:nowrap}.notification-copy>span{display:-webkit-box;overflow:hidden;color:#607087;font-size:12px;line-height:1.45;-webkit-box-orient:vertical;-webkit-line-clamp:2}.notification-copy time{color:#9aa7b8;font-size:10px}.notification-delete{display:grid;width:28px;height:28px;place-items:center;align-self:start;border:0;border-radius:8px;color:#9aa7b8;background:transparent;cursor:pointer;font-size:20px;line-height:1;transition:color .15s,background .15s}.notification-delete:hover,.notification-delete:focus-visible{color:#dc2626;background:#fee2e2;outline:0}.notification-empty{margin:0;padding:38px 20px;color:#7b8ba2;text-align:center}.notification-header-actions{display:flex;gap:8px;align-items:center}.btn-delete-read{border:0;color:#e53e3e;background:transparent;cursor:pointer;font-size:12px;font-weight:900}.btn-delete-read:hover{text-decoration:underline}
.notification-dropdown-enter-active,.notification-dropdown-leave-active{transition:opacity .16s,transform .16s}.notification-dropdown-enter-from,.notification-dropdown-leave-to{opacity:0;transform:translateY(-6px)}:global(.app-shell:has(.home-page)) .notification-trigger{border-color:rgba(216,226,240,.95);color:#40516b;background:rgba(255,255,255,.96);box-shadow:0 10px 28px rgba(8,24,54,.16)}:global(.app-shell:has(.home-page)) .notification-trigger:hover{border-color:#bcd0ee;background:#fff}@media(max-width:640px){.notification-dropdown{position:fixed;top:74px;right:14px;left:14px;width:auto}.notification-trigger{width:39px;height:39px}}
</style>
