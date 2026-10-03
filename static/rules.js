(() => {
  const dialog = document.querySelector("#rules-dialog");
  const openButton = document.querySelector("[data-rules-open]");

  if (!dialog || !openButton) return;

  openButton.addEventListener("click", () => {
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
  });

  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
})();
