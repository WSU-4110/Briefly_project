// userSession.js
// Pattern Applied: Singleton Pattern
// Purpose: Manage login, dark/light mode, and persistent user preferences


class UserSession {
  static #instance = null;

  username = null;
  email = null;
  theme = "light";
  fontSize = 16;

  constructor() {
    if (UserSession.#instance) return UserSession.#instance;
    this.#loadFromStorage();
    UserSession.#instance = this;
  }

  static getInstance() {
    if (!UserSession.#instance) {
      UserSession.#instance = new UserSession();
    }
    return UserSession.#instance;
  }

  login(email) {
    this.email = email;
    this.username = email.split("@")[0];
    this.#saveToStorage();
  }

  logout() {
    this.username = null;
    this.email = null;
    localStorage.removeItem("briefly_user");
  }

  toggleTheme() {
    this.theme = this.theme === "dark" ? "light" : "dark";
    document.body.classList.toggle("dark-mode");
    this.#saveToStorage();
  }

  #saveToStorage() {
    localStorage.setItem(
      "briefly_user",
      JSON.stringify({
        username: this.username,
        email: this.email,
        theme: this.theme,
      })
    );
  }

  #loadFromStorage() {
    const raw = localStorage.getItem("briefly_user");
    if (!raw) return;
    try {
      const data = JSON.parse(raw);
      this.username = data.username;
      this.email = data.email;
      this.theme = data.theme;
      if (this.theme === "dark") document.body.classList.add("dark-mode");
    } catch {
      console.warn("Session data corrupted");
    }
  }
}

export default UserSession;
