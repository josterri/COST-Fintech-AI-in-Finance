# Geographic Distribution

Member distribution and contributions across **36 countries**.

<div class="stats-banner" markdown>
<div class="stat-card" markdown>
<span class="stat-value">36</span>
<span class="stat-label">Countries</span>
</div>
<div class="stat-card" markdown>
<span class="stat-value">19</span>
<span class="stat-label">ITC Countries</span>
</div>
<div class="stat-card" markdown>
<span class="stat-value">EUR 389K</span>
<span class="stat-label">Total Contributions</span>
</div>
</div>

## Member Distribution by Country

<div class="chart-container" style="max-width: 800px; margin: auto;">
<canvas id="countryChart"></canvas>
</div>

## ITC vs Non-ITC Comparison

<div class="chart-row" markdown>
<div class="chart-container" style="max-width: 400px; margin: auto;">
<canvas id="itcChart"></canvas>
</div>
</div>

## Top Contributing Countries

| Country | Members | Total Contribution | ITC |
|---------|---------|-------------------|-----|
| Romania | 23 | EUR 71,345.43 | Yes |
| Switzerland | 19 | EUR 41,966.99 | No |
| Italy | 17 | EUR 35,880.27 | No |
| Poland | 7 | EUR 24,974.66 | Yes |
| Turkey | 13 | EUR 24,593.32 | Yes |
| Albania | 17 | EUR 22,310.65 | Yes |
| Netherlands | 10 | EUR 20,350.79 | No |
| Germany | 10 | EUR 19,516.92 | No |
| North Macedonia | 11 | EUR 18,640.18 | Yes |
| Ireland | 10 | EUR 16,961.80 | No |
| Greece | 5 | EUR 15,563.68 | Yes |
| France | 4 | EUR 11,663.89 | No |
| Czech Republic | 6 | EUR 11,296.00 | Yes |
| Kosovo | 3 | EUR 8,264.64 | No |
| Iceland | 2 | EUR 5,564.34 | No |

??? info "View All 36 Countries"

    | Country | Members | Total Contribution | ITC |
    |---------|---------|-------------------|-----|
    | Romania | 23 | EUR 71,345.43 | Yes |
    | Switzerland | 19 | EUR 41,966.99 | No |
    | Italy | 17 | EUR 35,880.27 | No |
    | Poland | 7 | EUR 24,974.66 | Yes |
    | Turkey | 13 | EUR 24,593.32 | Yes |
    | Albania | 17 | EUR 22,310.65 | Yes |
    | Netherlands | 10 | EUR 20,350.79 | No |
    | Germany | 10 | EUR 19,516.92 | No |
    | North Macedonia | 11 | EUR 18,640.18 | Yes |
    | Ireland | 10 | EUR 16,961.80 | No |
    | Greece | 5 | EUR 15,563.68 | Yes |
    | France | 4 | EUR 11,663.89 | No |
    | Czech Republic | 6 | EUR 11,296.00 | Yes |
    | Kosovo | 3 | EUR 8,264.64 | No |
    | Iceland | 2 | EUR 5,564.34 | No |
    | Slovakia | 5 | EUR 5,524.16 | Yes |
    | Lithuania | 3 | EUR 3,805.15 | Yes |
    | United Kingdom | 4 | EUR 3,237.06 | No |
    | Spain | 3 | EUR 3,163.93 | No |
    | Hungary | 3 | EUR 2,670.41 | Yes |
    | Portugal | 2 | EUR 2,467.51 | Yes |
    | Latvia | 2 | EUR 2,230.92 | Yes |
    | Austria | 1 | EUR 1,466.95 | No |
    | Ukraine | 2 | EUR 1,440.32 | Yes |
    | United States | 2 | EUR 1,324.92 | No |
    | Croatia | 3 | EUR 1,182.33 | Yes |
    | Israel | 1 | EUR 866.87 | No |
    | Norway | 2 | EUR 597.69 | No |
    | Liechtenstein | 1 | EUR 441.60 | No |
    | Cyprus | 2 | EUR 406.39 | Yes |
    | Belgium | 1 | EUR 308.00 | No |
    | Bulgaria | 1 | EUR 197.19 | Yes |
    | Finland | 1 | EUR 165.60 | No |
    | Serbia | 1 | EUR 128.64 | Yes |
    | Estonia | 1 | EUR 82.80 | Yes |
    | Bosnia and Herzegovina | 1 | EUR 13.90 | Yes |

<script>
document.addEventListener("DOMContentLoaded", function() {
  // Country Bar Chart
  var ctx1 = document.getElementById("countryChart");
  if (ctx1) {
    new Chart(ctx1, {
      type: "bar",
      data: {
        labels: ["Romania", "Switzerland", "Italy", "Poland", "Turkey", "Albania", "Netherlands", "Germany", "North Macedonia", "Ireland", "Greece", "France"],
        datasets: [{
          label: "Members",
          data: [23, 19, 17, 7, 13, 17, 10, 10, 11, 10, 5, 4],
          backgroundColor: ["#FF9800", "#7B1FA2", "#7B1FA2", "#FF9800", "#FF9800", "#FF9800", "#7B1FA2", "#7B1FA2", "#FF9800", "#7B1FA2", "#FF9800", "#7B1FA2"]
        }]
      },
      options: {
        indexAxis: "y",
        plugins: {
          legend: { display: false },
          title: { display: true, text: "Top 12 Countries by Member Count (Purple=Non-ITC, Orange=ITC)" }
        },
        scales: {
          x: { beginAtZero: true }
        }
      }
    });
  }

  // ITC Comparison Chart
  var ctx2 = document.getElementById("itcChart");
  if (ctx2) {
    new Chart(ctx2, {
      type: "doughnut",
      data: {
        labels: ["ITC Countries", "Non-ITC Countries"],
        datasets: [{
          data: [108, 91],
          backgroundColor: ["#FF9800", "#7B1FA2"]
        }]
      },
      options: {
        plugins: {
          legend: { position: "bottom" },
          title: { display: true, text: "Member Distribution" }
        }
      }
    });
  }
});
</script>