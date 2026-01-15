const API_BASE = "https://file-audit-backend.onrender.com";

let barChart = null;
let pieChart = null;

const fill = document.getElementById("progressFill");
const statusText = document.getElementById("scanStatus");

// ✅ CRASH-PROOF references
const reportRow =
  document.getElementById("reportRow") || { classList: { add() {}, remove() {} } };

const stages = {
  "Sequential scan": document.getElementById("stage2"),
  "Parallel scan": document.getElementById("stage3"),
  "Generating report": document.getElementById("stage4"),
};

document.getElementById("startScanBtn").addEventListener("click", handleScan);

async function handleScan() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) {
    alert("Select a file first");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  if (document.getElementById("scanSensitive").checked)
    formData.append("scan_sensitive", "1");
  if (document.getElementById("scanForbidden").checked)
    formData.append("scan_forbidden", "1");
  if (document.getElementById("scanPolicy").checked)
    formData.append("scan_policy", "1");

  // 🔁 Reset UI
  fill.style.width = "0%";
  statusText.textContent = "Starting...";
  Object.values(stages).forEach((s) => s && s.classList.remove("active"));

  reportRow.classList.add("hidden");

  await fetch(`${API_BASE}/start_scan`, { method: "POST", body: formData });

  const timer = setInterval(async () => {
    const res = await fetch(`${API_BASE}/scan_progress`);
    const data = await res.json();

    fill.style.width = data.progress + "%";
    statusText.textContent = data.status + " (" + data.stage + ")";

    Object.entries(stages).forEach(([name, el]) => {
      if (!el) return;
      if (data.stage.includes(name.split(" ")[0])) {
        el.classList.add("active");
      } else {
        el.classList.remove("active");
      }
    });

    if (data.status === "Completed") {
      clearInterval(timer);
      applyResults(data.result);

      // ✅ SHOW download & hint
      reportRow.classList.remove("hidden");
    }

    if (data.status === "Error") {
      clearInterval(timer);
      alert(data.result.error);

      reportRow.classList.add("hidden");
    }
  }, 300);
}

function downloadCSV() {
  window.open(`${API_BASE}/download_csv`, "_blank");
}

function applyResults(data) {
  document.getElementById("totalIssues").textContent = data.total_issues;
  document.getElementById("sensitiveCount").textContent = data.by_category.sensitive;
  document.getElementById("forbiddenCount").textContent = data.by_category.forbidden;
  document.getElementById("policyCount").textContent = data.by_category.policy;
  document.getElementById("sequentialTime").textContent =
    data.time_taken_sequential.toFixed(4);
  document.getElementById("parallelTime").textContent =
    data.time_taken_parallel.toFixed(4);

  renderCharts(data.by_category);
}

function renderCharts(byCategory) {
  const labels = ["Sensitive", "Forbidden", "Policy"];
  const dataVals = [
    byCategory.sensitive,
    byCategory.forbidden,
    byCategory.policy,
  ];

  if (barChart) barChart.destroy();
  if (pieChart) pieChart.destroy();

  // 🔥 Dynamic Y-axis scaling
  const maxValue = Math.max(...dataVals);

  function getNiceMax(val) {
    if (val <= 100) return 100;
    if (val <= 1000) return Math.ceil(val / 100) * 100;
    if (val <= 10000) return Math.ceil(val / 1000) * 1000;
    if (val <= 100000) return Math.ceil(val / 10000) * 10000;
    return Math.ceil(val / 100000) * 100000;
  }

  const yMax = getNiceMax(maxValue);
  const step =
    yMax <= 1000 ? 100 :
    yMax <= 10000 ? 1000 :
    yMax <= 100000 ? 10000 :
    100000;

  barChart = new Chart(document.getElementById("barChart"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{ label: "Issues", data: dataVals }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: yMax,
          ticks: {
            stepSize: step
          }
        }
      }
    }
  });

  pieChart = new Chart(document.getElementById("pieChart"), {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{ data: dataVals }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
}
