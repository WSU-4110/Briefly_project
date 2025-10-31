import { ThemeStrategy } from "./ThemeStrategy.js";

export class DarkThemeStrategy extends ThemeStrategy {
  applyTheme() {
    // Body
    document.body.classList.remove("light-mode");
    document.body.classList.add("dark-mode");

    // Header bar colors
    const header = document.querySelector("header");
    if (header) {
        header.classList.remove("header-light");
        header.classList.add("header-dark");
    }

    // Article cards
    document.querySelectorAll(".card").forEach(card => {
      card.classList.remove("card-light");
      card.classList.add("card-dark");
    });

    // Toggle button icon
    const btn = document.getElementById("modeToggle");
    if (btn) btn.textContent = "☀️";
  }

  getName() {
    return "dark";
  }
}
