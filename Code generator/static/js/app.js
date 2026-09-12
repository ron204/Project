(() => {
  const copyButton = document.getElementById("copy-button");
  const codeDisplay = document.getElementById("generated-code");
  if (copyButton && codeDisplay) copyButton.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(codeDisplay.textContent.trim()); copyButton.textContent = "Copied"; setTimeout(() => { copyButton.textContent = "Copy Code"; }, 1800); } catch { copyButton.textContent = "Copy unavailable"; }
  });
  const card = document.querySelector("[data-verification-id]");
  if (!card) return;
  const countdown = document.getElementById("countdown"), form = document.getElementById("verify-form"), submit = document.getElementById("verify-button"), input = document.getElementById("submitted-code"), status = document.getElementById("code-status"), attempts = document.getElementById("attempts-remaining"), message = document.getElementById("verification-message"), expiresAt = new Date(card.dataset.expiresAt);
  const showMessage = (text, kind) => { message.textContent = text; message.className = `notice ${kind}`; };
  const disableVerification = (label, text, kind = "warning") => { input.disabled = true; submit.disabled = true; status.textContent = label; status.className = "status-chip inactive"; showMessage(text, kind); };
  const updateTimer = () => { const seconds = Math.max(0, Math.ceil((expiresAt - new Date()) / 1000)); countdown.textContent = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`; if (seconds === 0) { clearInterval(timer); disableVerification("Expired", "This code has expired. Generate a new code."); } };
  let timer;
  updateTimer();
  timer = setInterval(updateTimer, 1000);
  form.addEventListener("submit", async (event) => { event.preventDefault(); if (!input.value.trim()) { showMessage("Enter the verification code before submitting.", "error"); input.focus(); return; } submit.disabled = true; const response = await fetch(form.action, { method: "POST", headers: { "X-Requested-With": "XMLHttpRequest" }, body: new FormData(form) }); const result = await response.json(); showMessage(result.message, result.success ? "success" : "error"); if (result.status === "active") { attempts.textContent = `${result.attempts_remaining} attempts remaining`; submit.disabled = false; input.value = ""; input.focus(); return; } clearInterval(timer); disableVerification(result.status === "verified" ? "Verified" : result.status === "locked" ? "Locked" : "Unavailable", result.message, result.success ? "success" : "error"); });
})();
