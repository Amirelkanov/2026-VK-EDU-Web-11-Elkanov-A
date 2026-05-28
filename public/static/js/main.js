import { onVoteClick } from "./vote.js";
import { onCorrectClick } from "./correct.js";

document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll("[data-vote-box] button[data-vote-value]")
    .forEach((btn) => btn.addEventListener("click", onVoteClick));

  document
    .querySelectorAll('[data-correct-wrapper] input[type="checkbox"]')
    .forEach((cb) => cb.addEventListener("change", onCorrectClick));
});
