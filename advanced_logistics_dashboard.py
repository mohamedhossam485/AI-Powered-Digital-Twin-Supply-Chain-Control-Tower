"""
Enterprise Logistics & Fleet Performance Dashboard
Generates 5,000-row fleet_deliveries.csv, then builds a premium dark-themed
Power BI-style HTML dashboard with CSS Grid (1920x1080).
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
from pathlib import Path

RANDOM_SEED = 42
NUM_RECORDS = 5000
OUTPUT_CSV = "fleet_deliveries.csv"
OUTPUT_HTML = "Advanced_Logistics_Dashboard.html"

ROUTES = [
    "Warsaw to Berlin",
    "Berlin to Prague",
    "Prague to Vienna",
    "Vienna to Budapest",
    "Budapest to Bucharest",
    "Warsaw to Krakow",
    "Krakow to Bratislava",
    "Berlin to Hamburg",
    "Hamburg to Amsterdam",
    "Amsterdam to Brussels",
    "Brussels to Paris",
    "Paris to Lyon",
    "Lyon to Milan",
    "Milan to Zurich",
    "Zurich to Munich",
]

NEON_PURPLE = "#8A2BE2"
NEON_CYAN = "#00FFFF"
NEON_GREEN = "#39FF14"
NEON_ORANGE = "#FF6600"

random.seed(RANDOM_SEED)
ROUTE_DISTANCES = {r: random.randint(350, 1200) for r in ROUTES}

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Segoe UI, Roboto, sans-serif", color="#FFFFFF", size=11),
    margin=dict(t=32, b=32, l=48, r=24),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#FFFFFF")),
    autosize=True,
)


def generate_mock_data():
    """Generate 5,000 delivery records. Columns: Date, Route, Truck_ID, Distance, Fuel_Cost, Status, Driver_Rating."""
    random.seed(RANDOM_SEED)
    start = datetime(2025, 1, 1)
    end = datetime(2026, 2, 28)
    date_range = (end - start).days
    records = []
    truck_ids = [f"TRK_{i:04d}" for i in range(1, 51)]
    for _ in range(NUM_RECORDS):
        days_offset = random.randint(0, date_range)
        date = start + timedelta(days=days_offset)
        truck_id = random.choice(truck_ids)
        route = random.choice(ROUTES)
        base_km = ROUTE_DISTANCES.get(route, 600)
        distance = round(base_km * random.uniform(0.95, 1.05), 1)
        base_hours = distance / random.uniform(50, 65)
        is_delayed = random.random() < 0.18
        if is_delayed:
            delivery_time = round(base_hours * random.uniform(1.15, 1.55), 2)
        else:
            delivery_time = round(base_hours * random.uniform(0.92, 1.08), 2)
        fuel_per_100 = random.uniform(28, 35)
        fuel_cost = round((distance / 100) * fuel_per_100 * random.uniform(1.4, 1.7), 2)
        status = "Delayed" if is_delayed else "On-Time"
        driver_rating = round(random.uniform(2.5, 5.0), 1)
        records.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Route": route,
            "Truck_ID": truck_id,
            "Distance": distance,
            "Fuel_Cost": fuel_cost,
            "Status": status,
            "Driver_Rating": driver_rating,
        })
    return pd.DataFrame(records)


def build_chart_html(fig, div_id):
    """Return (div_html, script_content) for injecting into template."""
    raw = fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id, config=dict(responsive=True))
    idx = raw.find("<script>")
    if idx == -1:
        return raw.strip(), ""
    div_part = raw[:idx].strip()
    start = raw.find(">", idx) + 1
    end = raw.find("</script>", start)
    script_part = raw[start:end] if end != -1 else ""
    return div_part, script_part


def fig_gradient_area(monthly_costs):
    """Chart 1: Smooth Gradient Area (Monthly Costs)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_costs["YearMonth"].tolist(),
        y=monthly_costs["Fuel_Cost"].tolist(),
        fill="tozeroy",
        mode="lines",
        line=dict(color=NEON_CYAN, width=2),
        fillgradient=dict(type="vertical", colorscale=[[0, "rgba(0,255,255,0.5)"], [1, "rgba(0,255,255,0.02)"]]),
        name="Monthly Cost (€)",
    ))
    fig.update_layout(**LAYOUT_BASE, title=dict(text="Monthly Fuel Costs (€)", font=dict(size=13, color="#FFFFFF")))
    return fig


def fig_radar(route_metrics):
    """Chart 2: Radar/Spider - Route Efficiency Metrics."""
    categories = list(route_metrics.keys())
    values = list(route_metrics.values())
    if len(categories) < 3:
        categories = ["On-Time %", "Avg Rating", "Volume"][: len(categories)]
        values = values + [0] * (3 - len(values))
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(138,43,226,0.3)",
        line=dict(color=NEON_PURPLE, width=2),
        name="Efficiency",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.12)", range=[0, 100]),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.12)", tickfont=dict(color="#FFFFFF")),
        ),
        title=dict(text="Route Efficiency (Radar)", font=dict(size=13, color="#FFFFFF")),
        showlegend=False,
    )
    return fig


def fig_donut(status_counts):
    """Chart 3: Donut with neon hollow center (On-Time vs Delayed)."""
    labels = list(status_counts.index)
    values = list(status_counts.values)
    colors = [NEON_GREEN if "On-Time" in str(l) else "#DC143C" for l in labels]
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        marker=dict(colors=colors, line=dict(color="#1A1A1A", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#FFFFFF", size=11),
        hoverinfo="label+value+percent",
    )])
    layout = {**LAYOUT_BASE, "title": dict(text="Fleet Status", font=dict(size=13, color="#FFFFFF")), "showlegend": True}
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    fig.update_layout(
        **layout,
        annotations=[dict(text="Status", x=0.5, y=0.5, font=dict(size=14, color=NEON_CYAN), showarrow=False)],
    )
    return fig


def fig_top5_routes(top5):
    """Chart 4: Horizontal Bar, Top 5 Routes, with data labels."""
    routes = top5["Route"].tolist()
    vals = top5["Volume"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=routes,
        x=vals,
        orientation="h",
        marker=dict(color=NEON_ORANGE, line=dict(color="rgba(255,255,255,0.2)", width=1)),
        text=vals,
        textposition="outside",
        textfont=dict(color="#FFFFFF", size=11),
    ))
    layout = {**LAYOUT_BASE, "title": dict(text="Top 5 Routes by Volume", font=dict(size=13, color="#FFFFFF"))}
    layout["xaxis"] = dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False, title_text="Deliveries")
    layout["yaxis"] = dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False, autorange="reversed")
    fig.update_layout(**layout)
    return fig


def fig_dual_axis(volume_series, delay_series):
    """Chart 5: Dual-Axis Line + Bar (Volume vs Avg Delay Time)."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    x = volume_series.index.tolist()
    fig.add_trace(go.Bar(x=x, y=volume_series.tolist(), name="Volume", marker_color=NEON_CYAN), secondary_y=False)
    fig.add_trace(go.Scatter(x=x, y=delay_series.tolist(), name="Avg Delay (h)", line=dict(color=NEON_ORANGE, width=2)), secondary_y=True)
    fig.update_layout(**LAYOUT_BASE, title=dict(text="Volume vs Average Delay Time", font=dict(size=13, color="#FFFFFF")))
    fig.update_xaxes(title_text="Month", gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(title_text="Deliveries", secondary_y=False, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(title_text="Avg Delay (h)", secondary_y=True, gridcolor="rgba(255,255,255,0.08)")
    return fig


def main():
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / OUTPUT_CSV
    html_path = base_dir / OUTPUT_HTML

    print("Generating mock dataset (5,000 rows)...")
    df = generate_mock_data()
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(df)} records to {csv_path}")

    df["Date"] = pd.to_datetime(df["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

    total_deliveries = len(df)
    total_fuel = df["Fuel_Cost"].sum()
    on_time_pct = 100 * (df["Status"] == "On-Time").sum() / total_deliveries
    delivery_times_approx = df["Distance"] / 55
    avg_delivery_time = round(delivery_times_approx.mean(), 1)

    monthly_costs = df.groupby("YearMonth", as_index=False)["Fuel_Cost"].sum()
    status_counts = df["Status"].value_counts()
    top5 = df.groupby("Route", as_index=False).size().rename(columns={"size": "Volume"}).nlargest(5, "Volume")

    route_on_time = df.groupby("Route")["Status"].apply(lambda x: 100 * (x == "On-Time").sum() / len(x))
    route_rating = df.groupby("Route")["Driver_Rating"].mean()
    route_vol = df.groupby("Route").size()
    route_vol_norm = (route_vol - route_vol.min()) / (route_vol.max() - route_vol.min() + 1e-9) * 100
    route_metrics = {
        "On-Time %": round(route_on_time.mean(), 1),
        "Avg Rating": round(route_rating.mean() * 20, 1),
        "Volume (norm)": round(route_vol_norm.mean(), 1),
    }

    monthly_vol = df.groupby("YearMonth").size()
    monthly_delay = df[df["Status"] == "Delayed"].groupby("YearMonth")["Distance"].apply(lambda x: (x / 55).mean())
    monthly_delay = monthly_delay.reindex(monthly_vol.index, fill_value=0).fillna(0)

    f_area = fig_gradient_area(monthly_costs)
    f_radar = fig_radar(route_metrics)
    f_donut = fig_donut(status_counts)
    f_top5 = fig_top5_routes(top5)
    f_dual = fig_dual_axis(monthly_vol, monthly_delay)

    div_area, script_area = build_chart_html(f_area, "chart-area")
    div_radar, script_radar = build_chart_html(f_radar, "chart-radar")
    div_donut, script_donut = build_chart_html(f_donut, "chart-donut")
    div_top5, script_top5 = build_chart_html(f_top5, "chart-top5")
    div_dual, script_dual = build_chart_html(f_dual, "chart-dual")

    sidebar_html = f"""
        <aside class="sidebar">
            <div class="slicer-header">Filters</div>
            <div class="slicer-item"><span class="slicer-label">Date Range</span><span class="slicer-value">Jan 2025 – Feb 2026</span></div>
            <div class="slicer-item"><span class="slicer-label">Route</span><span class="slicer-value">All</span></div>
            <div class="slicer-item"><span class="slicer-label">Status</span><span class="slicer-value">All</span></div>
            <div class="slicer-header">Views</div>
            <div class="slicer-item"><span class="slicer-value">Fleet Overview</span></div>
        </aside>
    """

    kpi_html = f"""
        <div class="kpi-card"><div class="kpi-label">Total Deliveries</div><div class="kpi-value kpi-cyan">{total_deliveries:,}</div></div>
        <div class="kpi-card"><div class="kpi-label">Total Revenue / Fuel</div><div class="kpi-value kpi-orange">€{total_fuel:,.0f}</div></div>
        <div class="kpi-card"><div class="kpi-label">On-Time %</div><div class="kpi-value kpi-green">{on_time_pct:.1f}%</div></div>
        <div class="kpi-card"><div class="kpi-label">Avg Delivery Time</div><div class="kpi-value kpi-purple">{avg_delivery_time:.1f} h</div></div>
    """

    css = """
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; background: #090909; color: #fff; font-family: 'Segoe UI', Roboto, sans-serif; }
    .dashboard { display: grid; grid-template-columns: 200px 1fr; grid-template-rows: auto 1fr; width: 1920px; height: 1080px; }
    .sidebar { grid-column: 1; grid-row: 1 / -1; background: #1A1A1A; border-right: 1px solid #333; border-radius: 0 8px 8px 0; padding: 16px; }
    .slicer-header { color: #8A2BE2; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin: 12px 0 6px; }
    .slicer-item { padding: 6px 0; border-bottom: 1px solid #333; font-size: 11px; }
    .slicer-label { color: rgba(255,255,255,0.6); }
    .slicer-value { color: #fff; margin-left: 4px; }
    .main { grid-column: 2; grid-row: 1 / -1; display: flex; flex-direction: column; padding: 16px; gap: 12px; min-height: 0; }
    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; flex-shrink: 0; }
    .kpi-card { background: #1A1A1A; border: 1px solid #333; border-radius: 8px; padding: 16px; }
    .kpi-label { font-size: 10px; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .kpi-value { font-size: 28px; font-weight: 800; }
    .kpi-cyan { color: #00FFFF; }
    .kpi-orange { color: #FF6600; }
    .kpi-green { color: #39FF14; }
    .kpi-purple { color: #8A2BE2; }
    .charts { flex: 1; min-height: 0; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; gap: 12px; }
    .panel { background: #1A1A1A; border: 1px solid #333; border-radius: 8px; padding: 10px; min-height: 0; overflow: hidden; display: flex; flex-direction: column; }
    .panel > div { flex: 1; min-height: 0; }
    .panel [id^="chart-"] { width: 100% !important; height: 100% !important; min-height: 0 !important; }
    .panel .plotly { width: 100% !important; height: 100% !important; }
    .span-2 { grid-column: span 2; }
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1920, height=1080"/>
<title>Advanced Logistics Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>{css}</style>
</head>
<body>
<div class="dashboard">
{sidebar_html}
<div class="main">
<div class="kpi-row">{kpi_html}</div>
<div class="charts">
<div class="panel">{div_area}</div>
<div class="panel">{div_radar}</div>
<div class="panel">{div_donut}</div>
<div class="panel">{div_top5}</div>
<div class="panel span-2">{div_dual}</div>
</div>
</div>
</div>
<script>{script_area}</script>
<script>{script_radar}</script>
<script>{script_donut}</script>
<script>{script_top5}</script>
<script>{script_dual}</script>
</body>
</html>
"""

    html_path.write_text(html, encoding="utf-8")
    print(f"Dashboard saved to {html_path}")


if __name__ == "__main__":
    main()
