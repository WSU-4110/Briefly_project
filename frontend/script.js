/******************************
 * DEMO NEWS DATA
 ******************************/
const newsData = {
  finance: [
    { headline: "Global markets rebound", summary: "Stocks climb.", source: "Bloomberg", date: "2025-09-25", link: "#" },
    { headline: "Oil prices hit record high", summary: "Crude surges.", source: "Reuters", date: "2025-09-20", link: "#" },
    { headline: "Central banks adjust policies", summary: "Rates revised.", source: "FT", date: "2025-09-18", link: "#" }
  ],
  banking: [
    { headline: "Banks tighten credit rules", summary: "Defaults rising.", source: "WSJ", date: "2025-09-22", link: "#" },
    { headline: "Digital banks grow", summary: "YOY growth.", source: "CNBC", date: "2025-09-19", link: "#" },
    { headline: "Bank mergers accelerate", summary: "Cost cuts.", source: "Reuters", date: "2025-09-15", link: "#" }
  ],
  retail: [
    { headline: "Holiday shopping boom", summary: "Record Black Friday.", source: "NYT", date: "2025-09-21", link: "#" },
    { headline: "E-commerce up 15%", summary: "Online strong.", source: "TechCrunch", date: "2025-09-18", link: "#" },
    { headline: "Retailers cut prices", summary: "Discounts rise.", source: "Bloomberg", date: "2025-09-12", link: "#" }
  ],
  tech: [
    { headline: "AI breakthrough", summary: "Disease detection.", source: "BBC", date: "2025-09-15", link: "#" },
    { headline: "Tech regulation", summary: "New laws.", source: "CNN", date: "2025-09-10", link: "#" },
    { headline: "Quantum progress", summary: "New qubit record.", source: "MIT Review", date: "2025-09-05", link: "#" }
  ],
  manufacturing: [
    { headline: "Robotics in factories", summary: "Efficiency up.", source: "Forbes", date: "2025-09-17", link: "#" },
    { headline: "Supply chain issues", summary: "Material shortages.", source: "Bloomberg", date: "2025-09-14", link: "#" },
    { headline: "Green manufacturing", summary: "Eco-friendly.", source: "Reuters", date: "2025-09-09", link: "#" }
  ],
  consumer: [
    { headline: "Smartphone demand up", summary: "Record sales.", source: "Engadget", date: "2025-09-16", link: "#" },
    { headline: "Consumer confidence rises", summary: "Optimistic.", source: "MarketWatch", date: "2025-09-11", link: "#" },
    { headline: "Luxury sales up", summary: "High profits.", source: "WSJ", date: "2025-09-07", link: "#" }
  ],
  stock: [
    { headline: "Dow hits 35,000", summary: "Markets up.", source: "Yahoo Finance", date: "2025-09-05", link: "#" },
    { headline: "Nasdaq rallies", summary: "Tech leads.", source: "CNBC", date: "2025-09-01", link: "#" },
    { headline: "S&P climbs", summary: "Record highs.", source: "Reuters", date: "2025-08-30", link: "#" }
  ]
};

/******************************
 * REMOVE ARTICLES OLDER THAN 120 DAYS
 ******************************/
function filterOld(data) {
  const now = new Date();
  const maxAge = 120 * 24 * 60 * 60 * 1000;

  for (const cat in data) {
    data[cat] = data[cat].filter(a => now - new Date(a.date) <= maxAge);
  }
}
filterOld(newsData);

/******************************
 * DOM
 ******************************/
const newsContainer = document.getElementById("newsContainer");
const categoryList = document.getElementById("categoryList");
const searchBox = document.getElementById("searchBox");
const clearSearchBtn = document.getElementById("clearSearch");
const resultsCount = document.getElementById("resultsCount");

let currentCategory = "finance";
let itemsLoaded = 0;
const itemsPerPage = 2;

/******************************
 * HELPERS
 ******************************/
function sortArticles(arr) {
  return arr.sort((a, b) => new Date(b.date) - new Date(a.date));
}

function renderCard(a) {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <h2><a href="${a.link}" target="_blank">${a.headline}</a></h2>
    <p class="summary">${a.summary}</p>
    <span class="source">Source: ${a.source}</span>
    <span class="date">Date: ${a.date}</span>
  `;
  return card;
}

/******************************
 * LOAD FIRST PAGE
 ******************************/
function loadNews(category) {
  const all = sortArticles(newsData[category].slice());
  itemsLoaded = 0;
  newsContainer.innerHTML = "";

  const first = all.slice(0, itemsPerPage);
  first.forEach(a => newsContainer.appendChild(renderCard(a)));
  itemsLoaded = first.length;

  resultsCount.textContent =
    `Showing ${itemsLoaded} of ${all.length} in ${category.toUpperCase()}`;

  setTimeout(() => loadMoreIfNeeded(), 80);
}

/******************************
 * INFINITE SCROLL
 ******************************/
let isLoading = false;

window.addEventListener("scroll", () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200) {
    loadMoreIfNeeded();
  }
});

function loadMoreIfNeeded() {
  if (isLoading) return;

  const all = sortArticles(newsData[currentCategory].slice());

  if (itemsLoaded >= all.length) return;

  isLoading = true;

  const next = all.slice(itemsLoaded, itemsLoaded + itemsPerPage);
  next.forEach(a => newsContainer.appendChild(renderCard(a)));
  itemsLoaded += next.length;

  resultsCount.textContent =
    `Showing ${itemsLoaded} of ${all.length} in ${currentCategory.toUpperCase()}`;

  isLoading = false;

  // auto-load more if no scrollbar
  if (document.body.scrollHeight <= window.innerHeight) {
    setTimeout(() => loadMoreIfNeeded(), 80);
  }
}

/******************************
 * CATEGORY CHANGE
 ******************************/
categoryList.addEventListener("click", (e) => {
  const li = e.target.closest("li[data-category]");
  if (!li) return;

  [...categoryList.querySelectorAll("li")].forEach(n => n.classList.remove("active"));
  li.classList.add("active");

  currentCategory = li.dataset.category;
  searchBox.value = "";
  clearSearchBtn.style.display = "none";

  loadNews(currentCategory);
});

/******************************
 * INITIAL LOAD
 ******************************/
loadNews(currentCategory);
