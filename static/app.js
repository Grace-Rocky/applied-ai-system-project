const byId = (id) => document.getElementById(id);
const state = {
  charts: {},
  catalogInsights: null,
};

const sliderIds = ["energy", "valence", "danceability"];
sliderIds.forEach((id) => {
  const input = byId(id);
  const out = byId(`${id}-value`);
  input.addEventListener("input", () => {
    out.textContent = Number(input.value).toFixed(2);
  });
});

function profilePayload() {
  return {
    genre: byId("genre").value,
    mood: byId("mood").value,
    energy: Number(byId("energy").value),
    valence: Number(byId("valence").value),
    danceability: Number(byId("danceability").value),
    likes_acoustic: byId("likes-acoustic").checked,
  };
}

function status(id, text) {
  byId(id).textContent = text;
}

function destroyChart(name) {
  if (state.charts[name]) {
    state.charts[name].destroy();
  }
}

function gradient(ctx, start, end) {
  const g = ctx.createLinearGradient(0, 0, 0, 240);
  g.addColorStop(0, start);
  g.addColorStop(1, end);
  return g;
}

function animateReveal(root) {
  root.querySelectorAll(".card, .featured-card, .workflow-step").forEach((el, index) => {
    el.style.animationDelay = `${index * 45}ms`;
    el.classList.add("reveal");
  });
}

function renderFeaturedTracks(items) {
  const root = byId("featured-tracks");
  root.innerHTML = "";
  items.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "featured-card reveal";
    card.innerHTML = `
      <div class="track">${index + 1}. ${item.title}</div>
      <div class="meta-line">${item.artist} · ${item.genre} · ${item.mood}</div>
      <div class="meta-line">Energy ${Number(item.energy).toFixed(2)} · Danceability ${Number(item.danceability).toFixed(2)}</div>
      <div class="featured-meter"><span style="width:${Math.round((Number(item.energy) * 0.55 + Number(item.danceability) * 0.45) * 100)}%"></span></div>
    `;
    root.appendChild(card);
  });
}

function renderCatalogCharts(data) {
  if (!window.Chart) return;

  const catalogCanvas = byId("catalogChart");
  if (catalogCanvas) {
    destroyChart("catalogChart");
    const ctx = catalogCanvas.getContext("2d");
    state.charts.catalogChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: (data.genres || []).map((item) => item.label),
        datasets: [{
          label: "Songs by genre",
          data: (data.genres || []).map((item) => item.value),
          borderWidth: 0,
          borderRadius: 12,
          backgroundColor: gradient(ctx, "rgba(75,216,255,0.95)", "rgba(255,175,82,0.75)"),
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "rgba(6,8,15,0.95)",
            titleColor: "#e8edf7",
            bodyColor: "#e8edf7",
          },
        },
        scales: {
          x: { ticks: { color: "#9cadcb" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { ticks: { color: "#9cadcb" }, grid: { color: "rgba(255,255,255,0.06)" } },
        },
      },
    });
  }

  const ragCanvas = byId("ragChart");
  if (ragCanvas) {
    destroyChart("ragChart");
    const ctx = ragCanvas.getContext("2d");
    const energy = data.energy_buckets || { Low: 0, Balanced: 0, High: 0 };
    state.charts.ragChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: Object.keys(energy),
        datasets: [{
          data: Object.values(energy),
          backgroundColor: ["#4bd8ff", "#ffaf52", "#59ffa2"],
          borderColor: "rgba(12,16,26,0.95)",
          borderWidth: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#e8edf7" } },
        },
        cutout: "62%",
      },
    });
  }
}

function renderEvaluationChart(data) {
  if (!window.Chart) return;
  const canvas = byId("evaluationChart");
  if (!canvas) return;
  destroyChart("evaluationChart");
  const ctx = canvas.getContext("2d");

  state.charts.evaluationChart = new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Consistency", "Coverage", "Diversity", "Confidence", "Fact Check", "Baseline"],
      datasets: [{
        label: "Average reliability",
        data: [
          Number(data.summary.average_consistency || 0),
          Number(data.summary.average_coverage || 0),
          Number(data.summary.average_diversity || 0),
          Number(data.summary.average_confidence || 0),
          Number(data.summary.average_fact_check || 0),
          Number(data.summary.average_baseline_overlap || 0),
        ],
        fill: true,
        backgroundColor: "rgba(75,216,255,0.18)",
        borderColor: "#4bd8ff",
        pointBackgroundColor: "#ffaf52",
        pointBorderColor: "#fff",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#e8edf7" } },
      },
      scales: {
        r: {
          angleLines: { color: "rgba(255,255,255,0.08)" },
          grid: { color: "rgba(255,255,255,0.08)" },
          pointLabels: { color: "#e8edf7" },
          ticks: { color: "#9cadcb", backdropColor: "transparent", beginAtZero: true, max: 1 },
        },
      },
    },
  });
}

function renderRecommendations(rows) {
  const root = byId("recommend-results");
  root.innerHTML = "";
  rows.forEach((row, index) => {
    const card = document.createElement("article");
    card.className = "card";

    const tags = (row.rag?.tags || []).slice(0, 5).map((tag) => `<span class=\"badge\">${tag}</span>`).join(" ");
    const explanation = row.explanation.slice(0, 4).map((r) => `<li>${r}</li>`).join("");

    card.innerHTML = `
      <div class="title">#${index + 1} ${row.song.title}</div>
      <div class="meta">${row.song.artist} | ${row.song.genre} | ${row.song.mood}</div>
      <div class="score">Score ${row.score.toFixed(2)} | Confidence ${(row.confidence * 100).toFixed(1)}%</div>
      <ul>${explanation}</ul>
      ${row.rag ? `<p>${row.rag.description || ""}</p>` : ""}
      <div>${tags}</div>
    `;
    root.appendChild(card);
  });
  animateReveal(root);
}

function renderWorkflow(workflow) {
  const root = byId("workflow-results");
  root.innerHTML = "";
  workflow.forEach((step, idx) => {
    const el = document.createElement("div");
    el.className = "workflow-step";
    el.innerHTML = `
      <strong>${idx + 1}. ${step.step}</strong>
      <div>Confidence ${(step.confidence * 100).toFixed(1)}%</div>
      <div>${step.reasoning}</div>
    `;
    root.appendChild(el);
  });
  animateReveal(root);
}

function metricCard(label, value) {
  const div = document.createElement("div");
  div.className = "card";
  div.innerHTML = `<div class=\"meta\">${label}</div><div class=\"title\">${value}</div>`;
  return div;
}

function renderEvaluation(data) {
  const summary = data.summary;
  const summaryRoot = byId("evaluation-summary");
  summaryRoot.innerHTML = "";

  const summaryPairs = [
    ["Overall", Number(summary.average_overall_score || 0).toFixed(3)],
    ["Consistency", Number(summary.average_consistency || 0).toFixed(3)],
    ["Coverage", Number(summary.average_coverage || 0).toFixed(3)],
    ["Diversity", Number(summary.average_diversity || 0).toFixed(3)],
    ["Fact Check", Number(summary.average_fact_check || 0).toFixed(3)],
    ["Baseline Overlap", Number(summary.average_baseline_overlap || 0).toFixed(3)],
  ];

  summaryPairs.forEach(([k, v]) => summaryRoot.appendChild(metricCard(k, v)));
  animateReveal(summaryRoot);
  renderEvaluationChart(data);

  const scenarioRoot = byId("scenario-results");
  scenarioRoot.innerHTML = "";
  Object.entries(data.scenarios).forEach(([name, row]) => {
    const card = document.createElement("article");
    card.className = "card";

    const checks = (row.verification_details || [])
      .slice(0, 2)
      .map((item) => {
        const inner = (item.checks || [])
          .slice(0, 3)
          .map((c) => `<li>${c.claim}: ${c.passed ? "pass" : "fail"} (${c.evidence || "n/a"})</li>`)
          .join("");
        return `<p><strong>${item.song}</strong></p><ul>${inner}</ul>`;
      })
      .join("");

    card.innerHTML = `
      <div class="title">${name.replaceAll("_", " ")}</div>
      <div class="meta">Overall ${row.overall.toFixed(3)} | Fact check ${row.fact_check.toFixed(3)}</div>
      <div class="meta">Consistency ${row.consistency.toFixed(3)} | Baseline overlap ${row.baseline_overlap.toFixed(3)}</div>
      ${checks}
    `;
    scenarioRoot.appendChild(card);
  });
  animateReveal(scenarioRoot);
}

function renderRag(data) {
  const root = byId("rag-results");
  root.innerHTML = "";

  const semantic = data.semantic_matches || [];
  const mood = data.mood_matches || [];

  semantic.forEach((row) => {
    const card = document.createElement("article");
    card.className = "card";
    const tags = (row.metadata.tags || []).slice(0, 6).map((t) => `<span class=\"badge\">${t}</span>`).join(" ");
    card.innerHTML = `
      <div class="title">Semantic: ${row.metadata.title}</div>
      <div class="meta">Score ${row.score.toFixed(4)}</div>
      <p>${row.metadata.description || ""}</p>
      <div>${tags}</div>
    `;
    root.appendChild(card);
  });
  animateReveal(root);

  mood.forEach((row) => {
    const card = document.createElement("article");
    card.className = "card";
    card.innerHTML = `
      <div class="title">Mood Match: ${row.metadata.title}</div>
      <div class="meta">${(row.metadata.tags || []).join(", ")}</div>
      <p>${row.metadata.description || ""}</p>
    `;
    root.appendChild(card);
  });
  animateReveal(root);
}

async function loadCatalogInsights() {
  try {
    const response = await fetch("/api/catalog/insights");
    state.catalogInsights = await response.json();
    renderFeaturedTracks(state.catalogInsights.featured || []);
    renderCatalogCharts(state.catalogInsights);
  } catch (error) {
    console.error("Failed to load catalog insights", error);
  }
}

byId("run-recommend").addEventListener("click", async () => {
  status("recommend-status", "Generating recommendation graph...");
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        profile: profilePayload(),
        k: Number(byId("topk").value || 8),
        use_rag: byId("use-rag").checked,
        use_agent: byId("use-agent").checked,
      }),
    });
    const data = await response.json();
    renderRecommendations(data.recommendations || []);
    renderWorkflow(data.workflow || []);
    status("recommend-status", `Generated ${data.recommendations.length} recommendations from ${data.catalog_size} songs.`);
    renderCatalogCharts(state.catalogInsights || {});
  } catch (error) {
    status("recommend-status", `Recommendation failed: ${error}`);
  }
});

byId("run-evaluation").addEventListener("click", async () => {
  status("evaluation-status", "Running reliability and fact-check suite...");
  try {
    const response = await fetch("/api/evaluate", { method: "POST" });
    const data = await response.json();
    renderEvaluation(data);
    status("evaluation-status", "Evaluation complete with cross-verification details.");
  } catch (error) {
    status("evaluation-status", `Evaluation failed: ${error}`);
  }
});

byId("run-rag").addEventListener("click", async () => {
  status("rag-status", "Searching RAG memory...");
  try {
    const response = await fetch("/api/rag/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: byId("rag-query").value,
        mood: byId("rag-mood").value,
      }),
    });
    const data = await response.json();
    renderRag(data);
    status("rag-status", "RAG retrieval complete.");
  } catch (error) {
    status("rag-status", `RAG search failed: ${error}`);
  }
});

byId("run-recommend").click();
loadCatalogInsights();
