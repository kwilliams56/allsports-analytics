"use strict";

// Keep the footer current without requiring annual template changes.
document.querySelectorAll("[data-current-year]").forEach((element) => {
    element.textContent = new Date().getFullYear();
});
