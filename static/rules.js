(() => {
  const dialog = document.querySelector("#rules-dialog");
  const openButtons = document.querySelectorAll("[data-rules-open]");

  if (!dialog || !openButtons.length) return;

  openButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (typeof dialog.showModal === "function") {
        if (!dialog.open) dialog.showModal();
      } else {
        dialog.setAttribute("open", "");
      }
    });
  });

  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
})();
