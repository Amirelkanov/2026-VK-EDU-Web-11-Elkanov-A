import {
  isAuthenticated,
  handleAuthRedirect,
  postJSON,
  showError,
} from "./api.js";

export async function onCorrectClick(event) {
  const input = event.currentTarget;
  const wrapper = input.closest("[data-correct-wrapper]");
  if (!wrapper) return;

  if (!isAuthenticated()) {
    handleAuthRedirect();
    return;
  }

  const url = wrapper.dataset.markCorrectUrl;
  const questionId = wrapper.dataset.questionId;
  const answerId = wrapper.dataset.answerId;
  const newValue = input.checked;

  if (!url || !questionId || !answerId) {
    showError("Invalid configuration");
    return;
  }

  // Disable input during request
  input.disabled = true;
  const payload = { question_id: questionId, answer_id: answerId };
  if (newValue) payload.is_correct = "on";

  try {
    const res = await postJSON(url, payload);

    if (res.status === 401 || res.status === 403) {
      showError(res.body?.error || "Permission denied");
      input.checked = !newValue;
      return;
    }

    if (!res.body?.ok) {
      showError(res.body?.error || "Failed to update");
      input.checked = !newValue;
      return;
    }

    input.checked = !!res.body.is_correct;
  } catch (err) {
    showError("Network error");
    input.checked = !newValue;
  } finally {
    input.disabled = false;
  }
}
