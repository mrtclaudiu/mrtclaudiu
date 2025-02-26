from flask import Flask, render_template_string
from database.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)
app = Flask(__name__)
db = DatabaseManager()

dashboard_html = """
<!DOCTYPE html>
<html>
<head><title>Trading Bot Dashboard</title></head>
<body>
    <h1>Trading Bot Dashboard</h1>
    <h2>Performance</h2>
    <table border="1">
        <tr><th>Pair</th><th>Total Profit</th><th>Win Rate</th><th>Trade Count</th></tr>
        {% for row in performance %}
        <tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def dashboard():
    with db.conn:
        cursor = db.conn.execute("SELECT pair, total_profit, win_rate, trade_count FROM performance")
        performance = cursor.fetchall()
    return render_template_string(dashboard_html, performance=performance)

def run_dashboard(host, port):
    logger.info(f"Starting dashboard at http://{host}:{port}")
    app.run(host=host, port=port)
