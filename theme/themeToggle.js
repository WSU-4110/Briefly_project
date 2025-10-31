import { ThemeContext } from "./theme/ThemeContext.js";
import { LightThemeStrategy } from "./theme/LightThemeStrategy.js";
import { DarkThemeStrategy } from "./theme/DarkThemeStrategy.js";

// Get your existing toggle button from the header
const modeToggleBtn = document.getElementById("modeToggle");

// Create the two strategies
const lightStrategy = new LightThemeStrategy();
const darkStrategy = new DarkThemeStrategy();

// Create context with the default strategy = light
const themeContext = new ThemeContext(lightStrategy);

// Apply initial theme on page load
themeContext.applyTheme();

// When user clicks 🌙 / ☀️, switch strategies
modeToggleBtn.addEventListener("click", () => {
  if (themeContext.getCurrentThemeName() === "light") {
    themeContext.setStrategy(darkStrategy);
  } else {
    themeContext.setStrategy(lightStrategy);
  }

  themeContext.applyTheme();
});
