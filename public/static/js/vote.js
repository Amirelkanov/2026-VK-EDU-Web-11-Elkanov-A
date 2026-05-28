import {
  isAuthenticated,
  handleAuthRedirect,
  postJSON,
  showError,
} from "./api.js";

function updateVoteUI(box, rating, userVote) {
  const ratingEl = box.querySelector(".vote-count");
  if (ratingEl) ratingEl.textContent = rating;

  const up = box.querySelector('[data-vote-value="1"]');
  const down = box.querySelector('[data-vote-value="-1"]');
  if (up) up.classList.toggle("active", userVote === 1);
  if (down) down.classList.toggle("active", userVote === -1);

  box.dataset.userVote = String(userVote);
}

export async function onVoteClick(event) {
  const btn = event.currentTarget;
  const box = btn.closest("[data-vote-box]");
  if (!box) return;

  if (!isAuthenticated()) {
    handleAuthRedirect();
    return;
  }

  const url = box.dataset.voteUrl;
  const targetId = box.dataset.targetId;
  const value = btn.dataset.voteValue;
  if (!url || !targetId || !value) {
    showError("Invalid vote configuration");
    return;
  }

  // Disable buttons during request
  const buttons = box.querySelectorAll("button[data-vote-value]");
  buttons.forEach((b) => (b.disabled = true));

  try {
    const res = await postJSON(url, { target_id: targetId, value: value });

    if (res.status === 401 || res.status === 403) {
      if (res.body?.error) {
        showError(res.body.error);
      } else {
        handleAuthRedirect();
      }
      return;
    }

    if (!res.body?.ok) {
      showError(res.body?.error || "Vote failed");
      return;
    }

    updateVoteUI(box, res.body.rating, res.body.user_vote);
  } catch (err) {
    showError("Network error");
  } finally {
    buttons.forEach((b) => (b.disabled = false));
  }
}
