import { ThemeStrategy } from "./ThemeStrategy.js";

export class LightThemeStrategy extends ThemeStrategy {
  applyTheme() {
    // Body (page background + text color)
    document.body.classList.remove("dark-mode");
    document.body.classList.add("light-mode");

    // Header bar colors
    const header = document.querySelector("header");
    if (header) {
        header.classList.remove("header-dark");
        header.classList.add("header-light");
    }

    // Article cards
    document.querySelectorAll(".card").forEach(card => {
      card.classList.remove("card-dark");
      card.classList.add("card-light");
    });

    // Toggle button icon
    const btn = document.getElementById("modeToggle");
    if (btn) btn.textContent = "🌙";
  }

  getName() {
    return "light";
  }
}
