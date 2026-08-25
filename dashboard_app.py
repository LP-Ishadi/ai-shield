from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from shield.database import get_all_blocks

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def dashboard():
    blocks = get_all_blocks()

    rows_html = ""
    for block in blocks:
        id_, ip, path, reason, timestamp = block
        rows_html += f"""
        <tr>
            <td>{id_}</td>
            <td>{ip}</td>
            <td>{path}</td>
            <td>{reason}</td>
            <td>{timestamp}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>AI Shield Dashboard</title>
        <style>
            body {{ background-color: #0d1117; color: #e6edf3; font-family: sans-serif; padding: 40px; }}
            h1 {{ color: #58a6ff; }}
            .stat {{ font-size: 24px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 10px; border-bottom: 1px solid #30363d; text-align: left; }}
            th {{ background-color: #161b22; color: #58a6ff; }}
            tr:hover {{ background-color: #161b22; }}
        </style>
    </head>
    <body>
        <h1>🛡️ AI Shield Dashboard</h1>
        <div class="stat">Total attacks blocked: <strong>{len(blocks)}</strong></div>
        <table>
            <tr>
                <th>ID</th><th>IP</th><th>Path</th><th>Reason</th><th>Timestamp</th>
            </tr>
            {rows_html}
        </table>
    </body>
    </html>
    """
    return html