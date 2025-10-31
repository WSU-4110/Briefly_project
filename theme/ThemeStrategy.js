export class ThemeStrategy {
  applyTheme() {
    throw new Error("applyTheme() must be implemented by a concrete theme strategy.");
  }

  getName() {
    throw new Error("getName() must be implemented by a concrete theme strategy.");
  }
}
