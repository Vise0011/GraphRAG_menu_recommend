document.getElementById("recommendForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());

  const res = await fetch("/api/v1/condition-weight", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const json = await res.json();

  const resultList = document.getElementById("selectedList");
  resultList.innerHTML = json.top5
    .map(m => `<li>${m.replace(/\n/g, "<br>")}</li>`)
    .join("");

  document.getElementById("recommendForm").classList.add("hidden");
  document.getElementById("resultSection").classList.remove("hidden");
});
