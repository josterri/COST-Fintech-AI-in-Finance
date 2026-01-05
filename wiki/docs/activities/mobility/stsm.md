# Short-Term Scientific Missions (STSMs)

COST Action CA19130 funded **27 STSMs** with a total investment of **EUR 60,082.00**.

<div class="stats-banner" markdown>
<div class="stat-card" markdown>
<span class="stat-value">27</span>
<span class="stat-label">Total STSMs</span>
</div>
<div class="stat-card" markdown>
<span class="stat-value">13</span>
<span class="stat-label">Home Countries</span>
</div>
<div class="stat-card" markdown>
<span class="stat-value">12</span>
<span class="stat-label">Host Countries</span>
</div>
<div class="stat-card" markdown>
<span class="stat-value">EUR 60K</span>
<span class="stat-label">Total Funding</span>
</div>
</div>

## Mobility Flows

Visualization of STSM exchanges between countries:

<div class="chart-container" style="max-width: 800px; margin: auto;">
<canvas id="flowChart"></canvas>
</div>

## Flow Details

| From | To | Count | Total Amount |
|------|-----|-------|--------------|
| Romania | Germany | 3 | EUR 5,200.00 |
| United Kingdom | Germany | 2 | EUR 5,100.00 |
| United Kingdom | Italy | 2 | EUR 3,440.00 |
| Switzerland | Romania | 2 | EUR 5,200.00 |
| Croatia | Netherlands | 1 | EUR 1,520.00 |
| Norway | Germany | 1 | EUR 3,500.00 |
| Italy | United Kingdom | 1 | EUR 1,260.00 |
| France | Greece | 1 | EUR 2,450.00 |
| Denmark | Spain | 1 | EUR 2,540.00 |
| Germany | Romania | 1 | EUR 2,500.00 |
| Norway | France | 1 | EUR 2,030.00 |
| United Kingdom | Croatia | 1 | EUR 3,200.00 |
| Switzerland | United Kingdom | 1 | EUR 1,900.00 |
| Italy | Germany | 1 | EUR 2,000.00 |
| Switzerland | Czech Republic | 1 | EUR 4,000.00 |
| Germany | Czech Republic | 1 | EUR 3,000.00 |
| Albania | Italy | 1 | EUR 1,000.00 |
| Lithuania | Czech Republic | 1 | EUR 1,600.00 |
| Ireland | Portugal | 1 | EUR 2,500.00 |
| Turkey | Germany | 1 | EUR 1,500.00 |
| Romania | Slovakia | 1 | EUR 1,997.00 |
| Turkey | Portugal | 1 | EUR 2,645.00 |

## All STSMs

| Grantee | From | To | Duration | Amount | YRI |
|---------|------|-----|----------|--------|-----|
| Stjepan Picek | Croatia | Netherlands | 16 days | EUR 1,520.00 | Yes |
| Wei Li | Norway | Germany | 120 days | EUR 3,500.00 | No |
| Luciana Dalla Valle | Italy | United Kingdom | 6 days | EUR 1,260.00 | No |
| Danial Saef | United Kingdom | Germany | 30 days | EUR 3,500.00 | No |
| Apostolos Chalkis | France | Greece | 14 days | EUR 2,450.00 | No |
| Jasone Ramirez-Ayerbe | Denmark | Spain | 14 days | EUR 2,540.00 | No |
| Alla Petukhina | Romania | Germany | 12 days | EUR 1,500.00 | Yes |
| Ioana Coita | Germany | Romania | 10 days | EUR 2,500.00 | Yes |
| Galena Pisoni | Norway | France | 8 days | EUR 2,030.00 | No |
| Daniel Traian Pele | Romania | Germany | 10 days | EUR 1,800.00 | No |
| Cathy Yi-Hsuan Chen | United Kingdom | Croatia | 32 days | EUR 3,200.00 | No |
| Luciana Dalla Valle | United Kingdom | Italy | 9 days | EUR 1,440.00 | No |
| Jose Muniz Martinez | Switzerland | United Kingdom | 11 days | EUR 1,900.00 | Yes |
| Alla Petukhina | Italy | Germany | 10 days | EUR 2,000.00 | Yes |
| Ioana Coita | Switzerland | Romania | 11 days | EUR 2,500.00 | Yes |
| Stefana Belbe | Switzerland | Romania | 12 days | EUR 2,700.00 | Yes |
| Tomas Plihal | Switzerland | Czech Republic | 13 days | EUR 4,000.00 | Yes |
| Karel Kozmik | Germany | Czech Republic | 23 days | EUR 3,000.00 | Yes |
| Xinwen Ni | United Kingdom | Germany | 9 days | EUR 1,600.00 | Yes |
| Rezarta Shkurti Perri | Albania | Italy | 6 days | EUR 1,000.00 | No |
| Jurgita Cerneviciene | Lithuania | Czech Republic | 6 days | EUR 1,600.00 | No |
| Luciana Dalla Valle | United Kingdom | Italy | 10 days | EUR 2,000.00 | No |
| Vassilios Papavassiliou | Ireland | Portugal | 11 days | EUR 2,500.00 | No |
| Esra Kabaklarli | Turkey | Germany | 6 days | EUR 1,500.00 | No |
| Stefana Belbe | Romania | Germany | 10 days | EUR 1,900.00 | Yes |
| Ioana Coita | Romania | Slovakia | 10 days | EUR 1,997.00 | No |
| Bekir Cetintav | Turkey | Portugal | 12 days | EUR 2,645.00 | Yes |

## STSM Statistics

### By Grant Period

| Grant Period | Count | Total Amount |
|--------------|-------|--------------|
| GP1 | 9 | EUR 20,800.00 |
| GP2 | 0 | EUR 0.00 |
| GP3 | 10 | EUR 24,140.00 |
| GP4 | 6 | EUR 10,500.00 |
| GP5 | 2 | EUR 4,642.00 |

### Young Researchers & Innovators (YRI)

- **YRI Grantees**: 12
- **Non-YRI Grantees**: 15

<script>
document.addEventListener("DOMContentLoaded", function() {
  var ctx = document.getElementById("flowChart");
  if (ctx) {
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Romania -> Germany", "United Kingdom -> Germany", "United Kingdom -> Italy", "Switzerland -> Romania", "Croatia -> Netherlands", "Norway -> Germany", "Italy -> United Kingdom", "France -> Greece", "Denmark -> Spain", "Germany -> Romania"],
        datasets: [{
          label: "Number of STSMs",
          data: [3, 2, 2, 2, 1, 1, 1, 1, 1, 1],
          backgroundColor: "#7B1FA2"
        }]
      },
      options: {
        indexAxis: "y",
        plugins: {
          legend: { display: false },
          title: { display: true, text: "Top STSM Mobility Flows (Home -> Host Country)" }
        },
        scales: {
          x: { beginAtZero: true, ticks: { stepSize: 1 } }
        }
      }
    });
  }
});
</script>