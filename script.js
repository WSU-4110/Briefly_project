// script.js - Fetch headlines from TheNewsAPI
document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("news-container");

  try {
    const response = await fetch("https://api.thenewsapi.com/v1/news/top?api_token=YOUR_KEY_HERE&locale=us");
    const data = await response.json();

    data.data.slice(0, 5).forEach(article => {
      const div = document.createElement("div");
      div.className = "article";
      div.innerHTML = `
        <h2>${article.title}</h2>
        <p>${article.description || ""}</p>
        <a href="${article.url}" target="_blank">Read more</a>
      `;
      container.appendChild(div);
    });
  } catch (err) {
    container.innerHTML = `<p>Error fetching news: ${err.message}</p>`;
  }
});
