<template>
  <Teleport to="body">
    <div class="community-modal-backdrop" @mousedown.self="$emit('close')">
      <section class="community-question-modal" role="dialog" aria-modal="true" aria-labelledby="question-title">
        <button class="modal-close" type="button" aria-label="닫기" @click="$emit('close')">×</button>
        <p class="modal-eyebrow">Community Conversation</p>
        <h2 id="question-title">작성자에게 질문</h2>
        <p>이 게시글 작성자에게 사례와 관련된 추가 질문을 보낼 수 있습니다.</p>
        <strong>{{ post?.author?.display_name }} · {{ post?.title }}</strong>
        <textarea
          v-model="message"
          rows="5"
          placeholder="예: 전선관 대체 검토 시 승인 과정에서 어떤 부분을 확인하셨나요?"
        ></textarea>
        <p v-if="errorMessage" class="modal-error">{{ errorMessage }}</p>
        <button class="send-button" type="button" :disabled="sending || !message.trim()" @click="send">
          {{ sending ? "전송 중" : "요청 보내기" }}
        </button>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from "vue";
import { createCommunityContactRequest } from "../api/communityApi";

const props = defineProps({ post: { type: Object, required: true } });
const emit = defineEmits(["close", "sent"]);
const message = ref("");
const sending = ref(false);
const errorMessage = ref("");

async function send() {
  try {
    sending.value = true;
    errorMessage.value = "";
    await createCommunityContactRequest(props.post.id, message.value.trim());
    emit("sent", "작성자에게 질문 요청이 전송되었습니다. 문의내역의 커뮤니티 대화 요청에서 상태를 확인할 수 있습니다.");
  } catch (error) {
    errorMessage.value = error?.response?.data?.post?.[0] || "질문 요청을 전송하지 못했습니다.";
  } finally {
    sending.value = false;
  }
}
</script>

<style scoped>
.community-modal-backdrop { position:fixed; inset:0; z-index:1000; display:grid; place-items:center; padding:20px; background:rgba(4,14,33,.62); backdrop-filter:blur(6px); }
.community-question-modal { position:relative; width:min(520px,100%); border-radius:24px; padding:28px; background:#fff; box-shadow:0 30px 100px rgba(0,0,0,.3); }
.community-question-modal h2 { margin:6px 0 8px; color:#102a56; }
.community-question-modal p { color:#65748d; line-height:1.6; }
.community-question-modal strong { display:block; margin:16px 0; color:#1f4b86; }
.community-question-modal textarea { width:100%; box-sizing:border-box; border:1px solid #cbdaf1; border-radius:15px; padding:14px; resize:vertical; font:inherit; }
.modal-eyebrow { color:#1559e8!important; font-size:12px; font-weight:900; text-transform:uppercase; }
.modal-close { position:absolute; top:16px; right:18px; border:0; background:transparent; color:#71809a; font-size:26px; cursor:pointer; }
.send-button { width:100%; margin-top:14px; border:0; border-radius:14px; padding:14px; color:#fff; background:#1559e8; font-weight:900; cursor:pointer; }
.send-button:disabled { opacity:.5; cursor:not-allowed; }
.modal-error { color:#c24141!important; font-size:13px; }
</style>
