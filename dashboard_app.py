from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from shield.database import get_blocks_grouped, get_threat_levels, search_blocks
import csv
import io

app = FastAPI()

@app.get("/", response_class=HTMLResponse)


def dashboard(period: str = Query("hour"), ip: str = Query(None)):
    blocks = search_blocks(ip_filter=ip)
    grouped = get_blocks_grouped(period)
    threats = get_threat_levels(ip_filter=ip)

    chart_labels = [str(row[0]) for row in grouped]
    chart_values = [row[1] for row in grouped]

    rows_html = ""
    for block in blocks:
        id_, ip_val, path, reason, timestamp = block
        rows_html += f"""
        <tr>
            <td>{id_}</td>
            <td>{ip_val}</td>
            <td>{path}</td>
            <td>{reason}</td>
            <td>{timestamp}</td>
        </tr>
        """

    threat_colors = {"High": "#f85149", "Medium": "#d29922", "Low": "#3fb950"}
    threats_html = ""
    for threat_ip, count, level in threats:
        color = threat_colors[level]
        threats_html += f"""
        <tr>
            <td>{threat_ip}</td>
            <td>{count}</td>
            <td style="color:{color}; font-weight:bold;">{level}</td>
        </tr>
        """

    def btn(label, value):
        active = "background-color:#58a6ff; color:#0d1117;" if period == value else "background-color:#161b22; color:#e6edf3;"
        return f'<a href="/?period={value}&ip={ip or ""}" style="{active} padding:8px 16px; border-radius:6px; text-decoration:none; margin-right:8px; font-size:14px;">{label}</a>'

    html = f"""
    <html>
    <head>
        <title>AI Shield Dashboard</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
        <style>
            body {{ background-color: #0d1117; color: #e6edf3; font-family: sans-serif; padding: 40px; }}
            h1 {{ color: #58a6ff; }}
            h2 {{ color: #58a6ff; margin-top: 40px; }}
            .stat {{ font-size: 24px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 10px; border-bottom: 1px solid #30363d; text-align: left; }}
            th {{ background-color: #161b22; color: #58a6ff; }}
            tr:hover {{ background-color: #161b22; }}
            .chart-container {{ max-width: 800px; margin-top: 20px; }}
            .period-buttons {{ margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>🛡️ AI Shield Dashboard</h1>
        <div class="stat">Total attacks blocked: <strong>{len(blocks)}</strong></div>

        <form method="get" style="margin-top:20px;">
            <input type="hidden" name="period" value="{period}">
            <input type="text" name="ip" placeholder="Search by IP..." value="{ip or ''}" 
                   style="padding:8px; border-radius:6px; border:1px solid #30363d; background-color:#161b22; color:#e6edf3; width:250px;">
            <button type="submit" style="padding:8px 16px; border-radius:6px; background-color:#58a6ff; color:#0d1117; border:none; cursor:pointer;">Search</button>
        </form>

        <a href="/export?ip={ip or ''}" target="_blank" style="display:inline-block; margin-top:10px; padding:8px 16px; border-radius:6px; background-color:#3fb950; color:#0d1117; text-decoration:none; font-weight:bold;">⬇ Export to CSV</a>

        <div class="period-buttons">
            {btn("Hourly", "hour")}
            {btn("Daily", "day")}
            {btn("Weekly", "week")}
            {btn("Monthly", "month")}
        </div>

        <div class="chart-container">
            <canvas id="blocksChart"></canvas>
        </div>

        <h2>Threat Levels by IP</h2>
        <table>
            <tr><th>IP</th><th>Times Blocked</th><th>Threat Level</th></tr>
            {threats_html}
        </table>

        <h2>Blocked Events Log</h2>
        <table>
            <tr>
                <th>ID</th><th>IP</th><th>Path</th><th>Reason</th><th>Timestamp</th>
            </tr>
            {rows_html}
        </table>

        <script>
            const ctx = document.getElementById('blocksChart');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {chart_labels},
                    datasets: [{{
                        label: 'Blocked attempts',
                        data: {chart_values},
                        backgroundColor: '#58a6ff'
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                    }}
                }}
            }});
        </script>

        <script>
            const searchBox = document.querySelector('input[name="ip"]');
            let lastValue = searchBox.value;

            function reloadWithCurrentSearch() {{
                const params = new URLSearchParams(window.location.search);
                params.set('ip', searchBox.value);
                window.location.href = '/?' + params.toString();
            }}

            // Instant reload when the user clicks away from the search box,
            // but only if the value actually changed
            searchBox.addEventListener('blur', () => {{
                if (searchBox.value !== lastValue) {{
                    reloadWithCurrentSearch();
                }}
            }});

            // Regular auto-refresh, skipped while actively typing
            setInterval(() => {{
                if (document.activeElement !== searchBox) {{
                    reloadWithCurrentSearch();
                }}
            }}, 15000);
        </script>

    </body>
    </html>
    """
    return html

@app.get("/export")
def export_csv(ip: str = Query(None)):
    blocks = search_blocks(ip_filter=ip)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "IP", "Path", "Reason", "Timestamp"])
    for block in blocks:
        writer.writerow(block)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=blocked_events.csv"}
    )