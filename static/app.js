document.querySelectorAll(".delete-form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    const company = form.dataset.company || "this application";
    if (!window.confirm(`Delete the application for ${company}? This cannot be undone.`)) {
      event.preventDefault();
    }
  });
});
window.setTimeout(() => {
  document.querySelectorAll(".flash").forEach((message) => {
    message.style.opacity = "0";
    window.setTimeout(() => message.remove(), 300);
  });
}, 4000);
