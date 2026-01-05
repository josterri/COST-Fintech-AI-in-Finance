# Financial Summary

Complete financial overview of COST Action CA19130.

## Key Metrics

<div class="stats-banner" markdown>

<div class="stat-card" markdown>
<span class="stat-value">EUR 964K</span>
<span class="stat-label">Total Budget</span>
</div>

<div class="stat-card" markdown>
<span class="stat-value">EUR 775K</span>
<span class="stat-label">Total Spent</span>
</div>

<div class="stat-card" markdown>
<span class="stat-value">80.4%</span>
<span class="stat-label">Execution Rate</span>
</div>

</div>

## Spending by Category

<div class="chart-row" markdown>
<div class="chart-container" style="max-width: 500px; margin: auto;">
<canvas id="categoryChart"></canvas>
</div>
</div>

| Category | Amount | Percentage |
|----------|--------|------------|
| Meetings | EUR 423,694.69 | 54.7% |
| Training Schools | EUR 108,816.05 | 14.0% |
| Fsac | EUR 101,042.91 | 13.0% |
| Virtual Mobility | EUR 72,500.00 | 9.4% |
| Stsm | EUR 60,082.00 | 7.8% |
| Dissemination | EUR 6,637.12 | 0.9% |
| Oersa | EUR 5,709.75 | 0.7% |
| Itc Grants | EUR 375.00 | 0.0% |

## Budget vs Actual by Grant Period

<div class="chart-container" style="max-width: 700px; margin: auto;">
<canvas id="gpChart"></canvas>
</div>

| Grant Period | Budget | Actual | Execution |
|--------------|--------|--------|-----------|
| GP1 | EUR 62,985.50 | EUR 47,459.83 | 75.4% |
| GP2 | EUR 202,607.00 | EUR 33,770.46 | 16.7% |
| GP3 | EUR 169,820.50 | EUR 166,262.38 | 97.9% |
| GP4 | EUR 257,925.91 | EUR 256,854.39 | 99.6% |
| GP5 | EUR 270,315.26 | EUR 270,315.26 | 100.0% |

<script>
document.addEventListener("DOMContentLoaded", function() {
  // Category Doughnut Chart
  var ctx1 = document.getElementById("categoryChart");
  if (ctx1) {
    new Chart(ctx1, {
      type: "doughnut",
      data: {
        labels: ['Meetings', 'Training Schools', 'Fsac', 'Virtual Mobility', 'Stsm', 'Dissemination', 'Oersa', 'Itc Grants'],
        datasets: [{{
          data: [423694.69, 108816.05, 101042.91, 72500.0, 60082.0, 6637.12, 5709.75, 375.0],
          backgroundColor: ["#7B1FA2", "#FF9800", "#4CAF50", "#2196F3", "#9E9E9E"]
        }}]
      },
      options: {
        plugins: {
          legend: {{ position: "bottom" }},
          title: {{ display: true, text: "Spending by Category" }}
        }
      }
    });
  }

  // GP Budget vs Actual Bar Chart
  var ctx2 = document.getElementById("gpChart");
  if (ctx2) {
    new Chart(ctx2, {
      type: "bar",
      data: {
        labels: ['GP1', 'GP2', 'GP3', 'GP4', 'GP5'],
        datasets: [
          {{
            label: "Budget",
            data: [62985.5, 202607.0, 169820.5, 257925.91, 270315.26],
            backgroundColor: "#7B1FA2"
          }},
          {{
            label: "Actual",
            data: [47459.83, 33770.46, 166262.38, 256854.39, 270315.26],
            backgroundColor: "#FF9800"
          }}
        ]
      },
      options: {
        plugins: {{
          title: {{ display: true, text: "Budget vs Actual by Grant Period" }}
        }},
        scales: {{
          y: {{
            beginAtZero: true,
            ticks: {{
              callback: function(value) {{ return "EUR " + (value/1000).toFixed(0) + "K"; }}
            }}
          }}
        }}
      }
    });
  }
});
</script>