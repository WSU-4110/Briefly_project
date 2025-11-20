/***** CONFIG *****/
const BASE_URL =
  "https://universityprojectbucket.s3.us-east-1.amazonaws.com/FinalArticles";
const DAYS_TO_LOAD = 7;
const SAVED_STORAGE_KEY = "unipro_saved_articles_v1";
const USER_STORAGE_KEY = "unipro_user_data_v1";

/***** GLOBAL STATE *****/
let categories = {
  all: [],
  technology: [],
  crypto: [],
  economy: [],
  finance: [],
  markets: [],
  sustainability: []
};

let currentCategory = "all";
let itemsLoaded = 0;
const itemsPerPage = 5;

let savedSet = new Set();
let articlesByKey = new Map();
let allArticlesList = [];
let currentReadingCard = null;
let currentUtterance = null;
let currentTtsButton = null;
let isSpeaking = false;
let currentUser = null;

/***** DOM REFERENCES *****/
const newsContainer = document.getElementById("newsContainer");
const categoryList = document.getElementById("categoryList");
const searchBox = document.getElementById("searchBox");
const clearSearchBtn = document.getElementById("clearSearch");
const modeToggle = document.getElementById("modeToggle");
const loadMoreBtn = document.getElementById("loadMoreBtn");
const resultsCount = document.getElementById("resultsCount");
const sortDropdown = document.getElementById("sortDropdown");

// Auth elements
const authArea = document.getElementById("authArea");
const signInBtn = document.getElementById("signInBtn");
const authModal = document.getElementById("authModal");
const closeAuth = document.getElementById("closeAuth");
const authForm = document.getElementById("authForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const rememberMe = document.getElementById("rememberMe");
const authError = document.getElementById("authError");
const togglePwd = document.getElementById("togglePwd");

// Preferences modal
const prefsModal = document.getElementById("prefsModal");
const savePrefsBtn = document.getElementById("savePrefsBtn");
const prefsError = document.getElementById("prefsError");

/***** USER DATA HELPERS *****/
function loadUserFromStorage() {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw);
    return data;
  } catch (e) {
    console.warn("Failed to parse user data", e);
    return null;
  }
}

function saveUserToStorage(user) {
  try {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  } catch (e) {
    console.warn("Failed to save user data", e);
  }
}

function clearUserFromStorage() {
  try {
    localStorage.removeItem(USER_STORAGE_KEY);
  } catch (e) {
    console.warn("Failed to clear user data", e);
  }
}

/***** SAVED (READ LATER) HELPERS *****/
function loadSavedFromStorage() {
  try {
    const raw = localStorage.getItem(SAVED_STORAGE_KEY);
    if (!raw) return new Set();
    const arr = JSON.parse(raw);
    if (!Array.isArray(arr)) return new Set();
    return new Set(arr);
  } catch (e) {
    console.warn("Failed to parse saved articles from storage", e);
    return new Set();
  }
}

function saveSavedToStorage() {
  try {
    localStorage.setItem(SAVED_STORAGE_KEY, JSON.stringify(Array.from(savedSet)));
  } catch (e) {
    console.warn("Failed to save saved articles", e);
  }
}

/***** S3 JSON LOADING (LAST N DAYS) *****/
function formatStampForFilename(date) {
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  const yyyy = date.getFullYear();
  return `${mm}${dd}${yyyy}`;
}

async function loadLastNDaysContent(n) {
  const today = new Date();
  const allArticles = [];

  for (let offset = 0; offset < n; offset++) {
    const d = new Date(today);
    d.setDate(d.getDate() - offset);

    const stamp = formatStampForFilename(d);
    const url = `${BASE_URL}/DAILY_CONTENT_${stamp}.json`;

    try {
      const res = await fetch(url + "?t=" + Date.now());
      if (!res.ok) {
        continue;
      }
      const data = await res.json();
      const articles = data.articles || [];

      for (const a of articles) {
        allArticles.push(a);
      }
    } catch (err) {
      console.warn("Failed to load", url, err);
    }
  }

  return allArticles;
}

/***** NORMALIZATION & CATEGORIES *****/
function resetState() {
  categories = {
    all: [],
    technology: [],
    crypto: [],
    economy: [],
    finance: [],
    markets: [],
    sustainability: []
  };
  articlesByKey = new Map();
  allArticlesList = [];
}

function getArticleKey(art) {
  if (art.id !== undefined && art.id !== null) {
    return String(art.id);
  }
  const sector = art.sector || "";
  const title = art.title || "";
  const date = art.date || "";
  return `${sector}|${title}|${date}`;
}

function buildCategoriesFromArticles(rawArticles) {
  resetState();

  for (const art of rawArticles) {
    const sectorRaw = art.sector || "";
    const sector = sectorRaw.toLowerCase();
    const key = getArticleKey(art);

    let article = articlesByKey.get(key);
    if (!article) {
      article = {
        key,
        headline: art.title,
        summary: art.description,
        sectorLabel: sectorRaw || "Unknown",
        date: art.date,
        link: "#",
        saved: false
      };

      if (savedSet.has(key)) {
        article.saved = true;
      }

      articlesByKey.set(key, article);
      allArticlesList.push(article);
    } else {
      article.headline = art.title;
      article.summary = art.description;
      article.sectorLabel = sectorRaw || "Unknown";
      article.date = art.date;
    }

    pushIfMissing(categories.all, article);

    if (sector === "technology") pushIfMissing(categories.technology, article);
    if (sector === "crypto") pushIfMissing(categories.crypto, article);
    if (sector === "economy") pushIfMissing(categories.economy, article);
    if (sector === "finance") pushIfMissing(categories.finance, article);
    if (sector === "markets") pushIfMissing(categories.markets, article);
    if (sector === "sustainability") pushIfMissing(categories.sustainability, article);
  }
}

function pushIfMissing(arr, item) {
  if (!arr.includes(item)) {
    arr.push(item);
  }
}

/***** RENDERING *****/
function renderCard(article, query = "") {
  const card = document.createElement("div");
  card.classList.add("card");
  card.dataset.key = article.key;

  card.innerHTML = `
    <h2>
      <a href="${article.link}" target="_blank" rel="noopener">
        ${highlight(article.headline, query)}
      </a>
      <div class="card-actions">
        <button class="resize-btn" title="Enlarge text" aria-label="Enlarge text">🔍</button>
        <button class="tts-btn" title="Read aloud" aria-label="Read aloud">🔊</button>
      </div>
    </h2>
    <p class="summary">${highlight(article.summary, query)}</p>
    <div class="meta-row">
      <span class="meta-pill sector-pill">Sector: ${highlight(article.sectorLabel, query)}</span>
      <span class="meta-pill date-pill">${highlight(article.date, query)}</span>
      <button class="save-btn" type="button" aria-label="Save for later">
        <span class="save-icon">${article.saved ? "♥" : "♡"}</span>
      </button>
    </div>
  `;

  const resizeBtn = card.querySelector(".resize-btn");
  resizeBtn.addEventListener("click", () => {
    toggleCardSize(card, resizeBtn);
  });

  const ttsBtn = card.querySelector(".tts-btn");
  ttsBtn.addEventListener("click", () => {
    speakArticle(article, card, ttsBtn);
  });

  const saveBtn = card.querySelector(".save-btn");
  saveBtn.classList.toggle("saved", article.saved);
  saveBtn.addEventListener("click", () => {
    toggleSaved(article, saveBtn);
  });

  return card;
}

function highlight(text, query) {
  if (!query) return text;
  const pattern = new RegExp(`(${escapeRegExp(query)})`, "gi");
  return text.replace(pattern, "<mark>$1</mark>");
}

function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/***** FONT RESIZING FOR CARDS *****/
function toggleCardSize(cardEl, btnEl) {
  const isEnlarged = cardEl.classList.toggle("enlarged");
  btnEl.textContent = isEnlarged ? "🔎" : "🔍";
  btnEl.title = isEnlarged ? "Normal text" : "Enlarge text";
}

/***** CATEGORY + NEWS LOADING *****/
function setActiveCategory(cat) {
  currentCategory = cat;
  itemsLoaded = 0;
  newsContainer.innerHTML = "";
  loadMoreBtn.style.display = "block";
  clearSearchInternal();
  loadNews(cat);
}

function getArticlesForCategory(cat) {
  if (cat === "saved") {
    const savedArticles = allArticlesList.filter((a) => a.saved);
    return sortArticles(savedArticles.slice());
  }
  
  // If user is logged in and viewing "all" (which becomes HOME), show personalized feed
  if (cat === "all" && currentUser && currentUser.preferences && currentUser.preferences.length === 3) {
    const personalizedArticles = allArticlesList.filter(art => {
      const sector = art.sectorLabel.toLowerCase();
      return currentUser.preferences.includes(sector);
    });
    return sortArticles(personalizedArticles.slice());
  }
  
  const arr = categories[cat] || [];
  return sortArticles(arr.slice());
}

function loadNews(category) {
  const all = getArticlesForCategory(category);
  const page = all.slice(itemsLoaded, itemsLoaded + itemsPerPage);

  page.forEach((a) => newsContainer.appendChild(renderCard(a)));
  itemsLoaded += itemsPerPage;

  const total = all.length;
  const categoryLabel = (category === "all" && currentUser && currentUser.preferences && currentUser.preferences.length === 3) 
    ? "HOME" 
    : category.toUpperCase();
  
  resultsCount.textContent =
    total === 0
      ? `No articles in ${categoryLabel}`
      : `Showing ${Math.min(itemsLoaded, total)} of ${total} in ${categoryLabel}`;
  loadMoreBtn.style.display = itemsLoaded >= total ? "none" : "block";
}

function sortArticles(arr) {
  const mode = sortDropdown.value;
  if (mode === "latest") {
    return arr.sort((a, b) => new Date(b.date) - new Date(a.date));
  }
  if (mode === "trending") {
    return arr.sort((a, b) => new Date(a.date) - new Date(b.date));
  }
  return arr;
}

/***** UPDATE CATEGORY LABELS BASED ON LOGIN STATE *****/
function updateCategoryLabels() {
  const allLi = document.querySelector('#categoryList li[data-category="all"]');
  if (allLi) {
    if (currentUser && currentUser.preferences && currentUser.preferences.length === 3) {
      allLi.textContent = "HOME";
    } else {
      allLi.textContent = "ALL";
    }
  }
}

/***** INIT *****/
(async function init() {
  savedSet = loadSavedFromStorage();
  currentUser = loadUserFromStorage();
  
  if (currentUser) {
    renderSignedIn(currentUser.email);
    updateCategoryLabels();
  }
  
  newsContainer.innerHTML = "<p>Loading articles...</p>";

  try {
    const backendArticles = await loadLastNDaysContent(DAYS_TO_LOAD);
    if (!backendArticles.length) {
      newsContainer.innerHTML = "<p>No articles available yet.</p>";
      loadMoreBtn.style.display = "none";
      return;
    }

    buildCategoriesFromArticles(backendArticles);

    document
      .querySelectorAll("#categoryList li")
      .forEach((li) =>
        li.classList.toggle("active", li.dataset.category === currentCategory)
      );

    newsContainer.innerHTML = "";
    loadNews(currentCategory);
  } catch (err) {
    console.error("Failed to load content:", err);
    newsContainer.innerHTML = "<p>Failed to load articles.</p>";
  }
})();

/***** CATEGORY CLICK HANDLER *****/
categoryList.addEventListener("click", (e) => {
  const li = e.target.closest("li");
  if (!li) return;
  const cat = li.dataset.category;
  if (!cat) return;

  document
    .querySelectorAll("#categoryList li")
    .forEach((item) => item.classList.toggle("active", item === li));

  setActiveCategory(cat);
});

/***** LOAD MORE *****/
loadMoreBtn.addEventListener("click", () => {
  loadNews(currentCategory);
});

/***** SORT DROPDOWN *****/
sortDropdown.addEventListener("change", () => {
  itemsLoaded = 0;
  newsContainer.innerHTML = "";
  loadNews(currentCategory);
});

/***** SEARCH *****/
function clearSearchInternal() {
  searchBox.value = "";
  clearSearchBtn.style.display = "none";
}

function formatCountText(count, context) {
  if (count === 0) return `No ${context}.`;
  if (count === 1) return `Found 1 ${context}.`;
  return `Found ${count} ${context}.`;
}

const doSearch = () => {
  const query = searchBox.value.trim().toLowerCase();
  clearSearchBtn.style.display = query ? "inline-block" : "none";

  if (!query) {
    newsContainer.innerHTML = "";
    itemsLoaded = 0;
    loadNews(currentCategory);
    return;
  }

  const filtered = allArticlesList.filter(
    (a) =>
      a.headline.toLowerCase().includes(query) ||
      a.summary.toLowerCase().includes(query) ||
      a.sectorLabel.toLowerCase().includes(query) ||
      a.date.toLowerCase().includes(query)
  );

  newsContainer.innerHTML = "";
  sortArticles(filtered).forEach((a) =>
    newsContainer.appendChild(renderCard(a, query))
  );
  resultsCount.textContent = formatCountText(
    filtered.length,
    "articles matching your search"
  );
  loadMoreBtn.style.display = "none";
};

searchBox.addEventListener("input", debounce(doSearch, 250));
clearSearchBtn.addEventListener("click", () => {
  clearSearchInternal();
  doSearch();
  searchBox.focus();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && document.activeElement === searchBox) {
    clearSearchBtn.click();
  }
});

/***** DARK MODE *****/
modeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  modeToggle.textContent = document.body.classList.contains("dark-mode")
    ? "☀️"
    : "🌙";
});

/***** AUTH MODAL *****/
signInBtn.addEventListener("click", () => {
  openAuthModal();
});

closeAuth.addEventListener("click", () => {
  closeAuthModal();
});

authModal.addEventListener("click", (e) => {
  if (e.target === authModal) {
    closeAuthModal();
  }
});

function openAuthModal() {
  authModal.style.display = "flex";
  authModal.setAttribute("aria-hidden", "false");
}

function closeAuthModal() {
  authModal.style.display = "none";
  authModal.setAttribute("aria-hidden", "true");
  authError.textContent = "";
}

/***** PREFERENCES MODAL *****/
function openPrefsModal() {
  prefsModal.style.display = "flex";
  prefsModal.setAttribute("aria-hidden", "false");
  
  // Pre-select saved preferences if they exist
  const checkboxes = document.querySelectorAll('input[name="pref-cat"]');
  checkboxes.forEach(cb => {
    cb.checked = currentUser && currentUser.preferences && currentUser.preferences.includes(cb.value);
  });
}

function closePrefsModal() {
  prefsModal.style.display = "none";
  prefsModal.setAttribute("aria-hidden", "true");
  prefsError.textContent = "";
}

savePrefsBtn.addEventListener("click", () => {
  const checkboxes = document.querySelectorAll('input[name="pref-cat"]:checked');
  
  if (checkboxes.length !== 3) {
    prefsError.textContent = "Please select exactly 3 categories.";
    return;
  }
  
  const preferences = Array.from(checkboxes).map(cb => cb.value);
  
  if (currentUser) {
    currentUser.preferences = preferences;
    saveUserToStorage(currentUser);
    updateCategoryLabels();
    closePrefsModal();
    
    // Refresh the view if on home page
    if (currentCategory === "all") {
      itemsLoaded = 0;
      newsContainer.innerHTML = "";
      loadNews(currentCategory);
    }
  }
});

/***** AUTH FORM *****/
authForm.addEventListener("submit", (e) => {
  e.preventDefault();
  authError.textContent = "";

  const email = emailInput.value.trim();
  const password = passwordInput.value.trim();

  if (!email || !password) {
    authError.textContent = "Please fill in both email and password.";
    return;
  }
  if (!email.includes("@")) {
    authError.textContent = "Please enter a valid email.";
    return;
  }
  if (password.length < 6) {
    authError.textContent = "Password must be at least 6 characters.";
    return;
  }

  const user = { 
    email, 
    signedAt: new Date().toISOString(),
    preferences: []
  };
  
  if (rememberMe.checked) {
    currentUser = user;
    saveUserToStorage(user);
  } else {
    currentUser = user;
  }

  renderSignedIn(email);
  closeAuthModal();
  
  // Prompt for category preferences
  openPrefsModal();
});

function renderSignedIn(email) {
  authArea.innerHTML = `
    <div class="user-info">
      <span class="signed-chip">${email}</span>
      <button class="sign-out-btn" id="signOutBtn">Sign Out</button>
    </div>
  `;
  
  const signOutBtn = document.getElementById("signOutBtn");
  signOutBtn.addEventListener("click", handleSignOut);
}

function handleSignOut() {
  currentUser = null;
  clearUserFromStorage();
  
  authArea.innerHTML = '<button id="signInBtn" class="primary">Sign In</button>';
  const newSignInBtn = document.getElementById("signInBtn");
  newSignInBtn.addEventListener("click", () => {
    openAuthModal();
  });
  
  updateCategoryLabels();
  
  // Refresh view if on home page
  if (currentCategory === "all") {
    itemsLoaded = 0;
    newsContainer.innerHTML = "";
    loadNews(currentCategory);
  }
}

/***** PASSWORD TOGGLE *****/
togglePwd.addEventListener("click", () => {
  const type = passwordInput.type === "password" ? "text" : "password";
  passwordInput.type = type;
  togglePwd.textContent = type === "password" ? "👁️" : "🙈";
});

/***** SAVE (READ LATER) LOGIC *****/
function toggleSaved(article, btn) {
  const key = article.key;
  if (!key) return;

  if (savedSet.has(key)) {
    savedSet.delete(key);
    article.saved = false;
  } else {
    savedSet.add(key);
    article.saved = true;
  }
  saveSavedToStorage();

  const icon = btn.querySelector(".save-icon");
  if (icon) {
    icon.textContent = article.saved ? "♥" : "♡";
  }
  btn.classList.toggle("saved", article.saved);

  if (currentCategory === "saved") {
    itemsLoaded = 0;
    newsContainer.innerHTML = "";
    loadNews(currentCategory);
  }
}

/***** DEBOUNCE *****/
function debounce(fn, delay) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

/***** TEXT-TO-SPEECH - COMPLETELY REWRITTEN TO FIX PAUSE ISSUES *****/
function stopAllSpeech() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  if (currentTtsButton) {
    currentTtsButton.textContent = "🔊";
  }
  currentReadingCard = null;
  currentTtsButton = null;
  currentUtterance = null;
  isSpeaking = false;
}

function speakArticle(article, cardEl, btnEl) {
  if (!("speechSynthesis" in window)) {
    alert("Your browser does not support speech synthesis.");
    return;
  }

  // If clicking the same card that's currently playing
  if (currentReadingCard === cardEl && isSpeaking) {
    // Pause it
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
      isSpeaking = false;
      btnEl.textContent = "▶";
      return;
    }
    // Resume it
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      isSpeaking = true;
      btnEl.textContent = "⏸";
      return;
    }
  }

  // Stop any current speech and start new one
  stopAllSpeech();
  
  // Small delay to ensure cancel completes
  setTimeout(() => {
    const text = `${article.headline}. ${article.summary}. Sector: ${article.sectorLabel}. Published on ${article.date}.`;
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => {
      currentReadingCard = cardEl;
      currentTtsButton = btnEl;
      currentUtterance = utterance;
      isSpeaking = true;
      btnEl.textContent = "⏸";
    };

    utterance.onend = () => {
      stopAllSpeech();
    };

    utterance.onerror = (event) => {
      console.error("Speech error:", event);
      stopAllSpeech();
    };

    window.speechSynthesis.speak(utterance);
  }, 100);
}