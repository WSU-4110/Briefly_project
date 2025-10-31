export class ThemeContext {
  constructor(strategy) {
    this.strategy = strategy; // current theme strategy
  }

  setStrategy(newStrategy) {
    this.strategy = newStrategy;
  }

  applyTheme() {
    this.strategy.applyTheme();
  }

  getCurrentThemeName() {
    return this.strategy.getName();
  }
}
