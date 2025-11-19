/***** Demo data (unchanged) *****/
const newsData = {
  finance: [
    { headline: "Global markets rebound", summary: "Stocks climb as investors shake off recession fears.", source: "Bloomberg", date: "2025-09-25", link: "https://www.bloomberg.com" },
    { headline: "Oil prices hit record high", summary: "Crude oil surges past $100 per barrel.", source: "Reuters", date: "2025-09-20", link: "https://www.reuters.com" },
    { headline: "Central banks adjust policies", summary: "Interest rates revised to stabilize markets.", source: "Financial Times", date: "2025-09-18", link: "https://www.ft.com" }
  ],
  banking: [
    { headline: "Banks tighten credit rules", summary: "Lenders become cautious amid rising defaults.", source: "WSJ", date: "2025-09-22", link: "https://www.wsj.com" },
    { headline: "Digital banks on the rise", summary: "Online-only banks attract younger customers.", source: "CNBC", date: "2025-09-19", link: "https://www.cnbc.com" },
    { headline: "Bank mergers accelerate", summary: "Major banks merge to cut costs.", source: "Reuters", date: "2025-09-15", link: "https://www.reuters.com" }
  ],
  retail: [
    { headline: "Holiday shopping boom", summary: "Consumers spend more during Black Friday.", source: "NY Times", date: "2025-09-21", link: "https://www.nytimes.com" },
    { headline: "E-commerce continues growth", summary: "Online shopping grows 15% year-over-year.", source: "TechCrunch", date: "2025-09-18", link: "https://www.techcrunch.com" },
    { headline: "Retailers cut prices", summary: "Stores slash prices to attract customers.", source: "Bloomberg", date: "2025-09-12", link: "https://www.bloomberg.com" }
  ],
  tech: [
    { headline: "AI breakthrough in healthcare", summary: "AI helps detect diseases faster.", source: "BBC", date: "2025-09-15", link: "https://www.bbc.com" },
    { headline: "Tech giants face regulation", summary: "Governments push stricter laws for big tech.", source: "CNN", date: "2025-09-10", link: "https://www.cnn.com" },
    { headline: "Quantum computing advances", summary: "New qubit record achieved by researchers.", source: "MIT Tech Review", date: "2025-09-05", link: "https://www.technologyreview.com" }
  ],
  manufacturing: [
    { headline: "Factories embrace robotics", summary: "Automation increases production efficiency.", source: "Forbes", date: "2025-09-17", link: "https://www.forbes.com" },
    { headline: "Supply chain challenges", summary: "Companies struggle with material shortages.", source: "Bloomberg", date: "2025-09-14", link: "https://www.bloomberg.com" },
    { headline: "Green manufacturing grows", summary: "Eco-friendly production gains traction.", source: "Reuters", date: "2025-09-09", link: "https://www.reuters.com" }
  ],
  consumer: [
    { headline: "Smartphones in high demand", summary: "New models see record sales.", source: "Engadget", date: "2025-09-16", link: "https://www.engadget.com" },
    { headline: "Consumer confidence rises", summary: "Shoppers optimistic about economy.", source: "MarketWatch", date: "2025-09-11", link: "https://www.marketwatch.com" },
    { headline: "Luxury goods sales up", summary: "High-end brands report strong profits.", source: "WSJ", date: "2025-09-07", link: "https://www.wsj.com" }
  ],
  stock: [
    { headline: "Dow Jones hits 35,000", summary: "Markets celebrate positive economic outlook.", source: "Yahoo Finance", date: "2025-09-05", link: "https://finance.yahoo.com" },
    { headline: "Nasdaq rallies", summary: "Tech stocks fuel Nasdaq surge.", source: "CNBC", date: "2025-09-01", link: "https://www.cnbc.com" },
    { headline: "S&P 500 climbs", summary: "Broad market index reaches record highs.", source: "Reuters", date: "2025-08-30", link: "https://www.reuters.com" }
  ]
};

/***** DOM refs *****/
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

let currentCategory = "finance";
let itemsLoaded = 0;
const itemsPerPage = 2;

/***** Utilities *****/
const debounce = (fn, ms = 250) => {
  let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
};
const escapeReg = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const highlight = (text, term) => {
  if (!term) return text;
  const re = new RegExp(`(${escapeReg(term)})`, "ig");
  return text.replace(re, "<mark>$1</mark>");
};
const formatCountText = (n, scopeLabel) =>
  n === 0 ? `No results ${scopeLabel}` :
  n === 1 ? `1 result ${scopeLabel}` : `${n} results ${scopeLabel}`;

/***** Rendering *****/
function renderCard(article, query = "") {
  const card = document.createElement("div");
  card.classList.add("card");
  card.innerHTML = `
    <h2><a href="${article.link}" target="_blank" rel="noopener">${highlight(article.headline, query)}</a></h2>
    <p class="summary">${highlight(article.summary, query)}</p>
    <span class="source">Source: ${highlight(article.source, query)}</span>
    <span class="date">Date: ${highlight(article.date, query)}</span>
  `;
  return card;
}

function loadNews(category) {
  const all = sortArticles(newsData[category].slice());
  const page = all.slice(itemsLoaded, itemsLoaded + itemsPerPage);
  page.forEach(a => newsContainer.appendChild(renderCard(a)));
  itemsLoaded += itemsPerPage;

  resultsCount.textContent = `Showing ${Math.min(itemsLoaded, all.length)} of ${all.length} in ${category.toUpperCase()}`;
  loadMoreBtn.style.display = itemsLoaded >= all.length ? "none" : "block";
}

function sortArticles(arr) {
  const mode = sortDropdown.value;
  if (mode === "latest") {
    return arr.sort((a, b) => new Date(b.date) - new Date(a.date));
  }
  // demo: “popular/trending” fallback to latest
  return arr.sort((a, b) => new Date(b.date) - new Date(a.date));
}

/***** Init *****/
loadNews(currentCategory);

/***** Category click *****/
categoryList.addEventListener("click", (e) => {
  const li = e.target.closest("li[data-category]");
  if (!li) return;
  [...categoryList.querySelectorAll("li")].forEach(n => n.classList.remove("active"));
  li.classList.add("active");

  currentCategory = li.dataset.category;
  itemsLoaded = 0;
  newsContainer.innerHTML = "";
  loadNews(currentCategory);
  searchBox.value = "";
  clearSearchBtn.style.display = "none";
  resultsCount.textContent = `Showing latest in ${currentCategory.toUpperCase()}`;
});

/***** Sort *****/
sortDropdown.addEventListener("change", () => {
  itemsLoaded = 0;
  newsContainer.innerHTML = "";
  loadNews(currentCategory);
});

/***** Search (debounced, cross-category, highlight) *****/
const doSearch = () => {
  const query = searchBox.value.trim().toLowerCase();
  clearSearchBtn.style.display = query ? "inline-block" : "none";

  if (!query) {
    // restore category page
    newsContainer.innerHTML = "";
    itemsLoaded = 0;
    loadNews(currentCategory);
    return;
  }

  const allArticles = Object.entries(newsData).flatMap(([cat, arr]) =>
    arr.map(a => ({ ...a, _cat: cat }))
  );

  const filtered = allArticles.filter(a =>
    a.headline.toLowerCase().includes(query) ||
    a.summary.toLowerCase().includes(query) ||
    a.source.toLowerCase().includes(query) ||
    a.date.toLowerCase().includes(query)
  );

  newsContainer.innerHTML = "";
  sortArticles(filtered).forEach(a => newsContainer.appendChild(renderCard(a, query)));
  resultsCount.textContent = formatCountText(filtered.length, "across all categories");
  loadMoreBtn.style.display = "none";
};
searchBox.addEventListener("input", debounce(doSearch, 250));
clearSearchBtn.addEventListener("click", () => {
  searchBox.value = "";
  doSearch();
  searchBox.focus();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && searchBox === document.activeElement) {
    clearSearchBtn.click();
  }
});

/***** Dark Mode *****/
modeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  modeToggle.textContent = document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
});

/***** Auth (modal + localStorage “session”) *****/
function openAuth() {
  authModal.classList.add("show");
  authModal.setAttribute("aria-hidden", "false");
  authError.textContent = "";
  setTimeout(() => emailInput.focus(), 0);
}
function closeAuthModal() {
  authModal.classList.remove("show");
  authModal.setAttribute("aria-hidden", "true");
}
function renderSignedIn(email) {
  authArea.innerHTML = `
    <span class="user-chip" title="${email}">
      <span>Hi, ${email.split("@")[0]}</span>
      <button id="logoutBtn" type="button">Logout</button>
    </span>
  `;
  document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("news_demo_user");
    location.reload();
  });
}
function restoreSession() {
  const saved = localStorage.getItem("news_demo_user");
  if (saved) {
    try {
      const { email } = JSON.parse(saved);
      if (email) renderSignedIn(email);
    } catch {}
  }
}
restoreSession();

if (signInBtn) {
  signInBtn.addEventListener("click", openAuth);
}
closeAuth.addEventListener("click", closeAuthModal);
authModal.addEventListener("click", (e) => {
  if (e.target === authModal) closeAuthModal(); // click backdrop closes
});
togglePwd.addEventListener("click", () => {
  const isPwd = passwordInput.type === "password";
  passwordInput.type = isPwd ? "text" : "password";
  togglePwd.textContent = isPwd ? "🙈" : "👁️";
});

authForm.addEventListener("submit", (e) => {
  e.preventDefault();
  authError.textContent = "";

  const email = emailInput.value.trim();
  const pwd = passwordInput.value;

  // Simple client validation
  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const pwdOk = pwd.length >= 6;

  if (!emailOk) {
    authError.textContent = "Please enter a valid email address.";
    emailInput.focus();
    return;
  }
  if (!pwdOk) {
    authError.textContent = "Password must be at least 6 characters.";
    passwordInput.focus();
    return;
  }

  // Fake sign-in (no server). Save to localStorage if "remember me" checked.
  const user = { email, signedAt: new Date().toISOString() };
  if (rememberMe.checked) {
    localStorage.setItem("news_demo_user", JSON.stringify(user));
  }

  // Replace Sign In button with chip
  renderSignedIn(email);
  closeAuthModal();
});
