import { apiClient, buildApiUrl } from "./apiClient";

export async function getCommunityPosts(type = "") {
  const { data } = await apiClient.get(buildApiUrl("/api/v1/community/posts/"), {
    params: type ? { type } : {},
  });
  return Array.isArray(data) ? data : data.results || [];
}

export async function getCommunityPost(postId) {
  const { data } = await apiClient.get(buildApiUrl(`/api/v1/community/posts/${postId}/`));
  return data;
}

export async function getCommunityProfile(profileId) {
  const { data } = await apiClient.get(buildApiUrl(`/api/v1/community/profiles/${profileId}/`));
  return data;
}

export async function createCommunityPost(payload) {
  const { data } = await apiClient.post(buildApiUrl("/api/v1/community/posts/"), payload);
  return data;
}

export async function updateCommunityPost(postId, payload) {
  const { data } = await apiClient.patch(
    buildApiUrl(`/api/v1/community/posts/${postId}/`),
    payload,
  );
  return data;
}

export async function deleteCommunityPost(postId) {
  await apiClient.delete(buildApiUrl(`/api/v1/community/posts/${postId}/`));
}

export async function createCommunityComment(postId, content, displayMode = "profile") {
  const { data } = await apiClient.post(
    buildApiUrl(`/api/v1/community/posts/${postId}/comments/`),
    { content, display_mode: displayMode },
  );
  return data;
}

export async function createCommunityContactRequest(postId, message) {
  const { data } = await apiClient.post(buildApiUrl("/api/v1/community/contact-requests/"), {
    post: Number(postId),
    message,
  });
  return data;
}

export async function getCommunityContactRequests() {
  const { data } = await apiClient.get(buildApiUrl("/api/v1/community/contact-requests/"));
  return Array.isArray(data) ? data : data.results || [];
}

export async function updateCommunityContactRequest(requestId, status) {
  const { data } = await apiClient.patch(
    buildApiUrl(`/api/v1/community/contact-requests/${requestId}/`),
    { status },
  );
  return data;
}
