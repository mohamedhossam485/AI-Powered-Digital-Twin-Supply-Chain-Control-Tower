"""
AI-Powered Digital Twin & Supply Chain Control Tower
God-tier: Sankey, 3D Risk Matrix, AI Revenue Forecast, Glassmorphism CSS.
All charts unique keys; @st.cache_data for data generation.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import numpy as np
from pathlib import Path

import streamlit as st

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

RANDOM_SEED = 42
NUM_RECORDS = 5000
CSV_PATH = Path(__file__).resolve().parent / "fleet_deliveries.csv"

ROUTES = [
    "Warsaw to Berlin", "Berlin to Prague", "Prague to Vienna", "Vienna to Budapest",
    "Budapest to Bucharest", "Warsaw to Krakow", "Krakow to Bratislava", "Berlin to Hamburg",
    "Hamburg to Amsterdam", "Amsterdam to Brussels", "Brussels to Paris", "Paris to Lyon",
    "Lyon to Milan", "Milan to Zurich", "Zurich to Munich",
]

WEATHER = ["Clear", "Rain", "Snow", "Fog"]
WEATHER_SEVERITY = {"Clear": 1, "Rain": 4, "Snow": 7, "Fog": 5}

# Distribution hubs for Sankey (origin/dest map to nearest hub)
HUB_MAP = {
    "Warsaw": "Hub Warsaw", "Krakow": "Hub Warsaw", "Berlin": "Hub Berlin", "Hamburg": "Hub Berlin",
    "Prague": "Hub Berlin", "Vienna": "Hub Vienna", "Bratislava": "Hub Vienna", "Budapest": "Hub Vienna",
    "Bucharest": "Hub Vienna", "Amsterdam": "Hub Brussels", "Brussels": "Hub Brussels", "Paris": "Hub Paris",
    "Lyon": "Hub Paris", "Milan": "Hub Milan", "Zurich": "Hub Milan", "Munich": "Hub Milan",
}

CITY_COORDS = {
    "Warsaw": (52.2297, 21.0122), "Berlin": (52.52, 13.405), "Prague": (50.0755, 14.4378),
    "Vienna": (48.2082, 16.3738), "Budapest": (47.4979, 19.0402), "Bucharest": (44.4268, 26.1025),
    "Krakow": (50.0647, 19.945), "Bratislava": (48.1486, 17.1077), "Hamburg": (53.5511, 9.9937),
    "Amsterdam": (52.3676, 4.9041), "Brussels": (50.8503, 4.3517), "Paris": (48.8566, 2.3522),
    "Lyon": (45.764, 4.8357), "Milan": (45.4642, 9.19), "Zurich": (47.3769, 8.5417),
    "Munich": (48.1351, 11.582),
}

NEON_CYAN = "#00e5ff"
NEON_PINK = "#ff007f"
NEON_LIME = "#39ff14"
BG_DARK = "#0b0f19"

random.seed(RANDOM_SEED)
ROUTE_DISTANCES = {r: random.randint(350, 1200) for r in ROUTES}


@st.cache_data(ttl=3600)
def generate_fleet_csv():
    """Generate 5,000-row dataset; cached."""
    required_cols = {"Revenue_EUR", "Maintenance_Cost", "Weather_Condition", "Delay_Penalty", "Vehicle_Health_Score_pct"}
    if CSV_PATH.exists():
        try:
            have = set(pd.read_csv(CSV_PATH, nrows=0).columns)
            if required_cols.issubset(have):
                return
        except Exception:
            pass
    random.seed(RANDOM_SEED)
    start = datetime(2025, 1, 1)
    end = datetime(2026, 2, 28)
    days_range = (end - start).days
    records = []
    truck_ids = [f"TRK_{i:04d}" for i in range(1, 51)]
    for _ in range(NUM_RECORDS):
        date = start + timedelta(days=random.randint(0, days_range))
        truck_id = random.choice(truck_ids)
        route = random.choice(ROUTES)
        distance = round(ROUTE_DISTANCES.get(route, 600) * random.uniform(0.95, 1.05), 1)
        fuel_cost = round((distance / 100) * random.uniform(28, 35) * random.uniform(1.4, 1.7), 2)
        is_delayed = random.random() < 0.18
        status = "Delayed" if is_delayed else "On-Time"
        driver_rating = round(random.uniform(2.5, 5.0), 1)
        revenue = round(fuel_cost * random.uniform(2.2, 3.5), 2)
        maintenance_cost = round(random.uniform(15, 120), 2)
        weather = random.choice(WEATHER)
        delay_penalty = round(random.uniform(80, 250), 2) if is_delayed else 0.0
        vehicle_health = round(random.uniform(25, 98), 1)
        weather_severity = WEATHER_SEVERITY.get(weather, 3) + random.randint(-1, 1)
        records.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Route": route,
            "Truck_ID": truck_id,
            "Distance": distance,
            "Fuel_Cost": fuel_cost,
            "Status": status,
            "Driver_Rating": driver_rating,
            "Revenue_EUR": revenue,
            "Maintenance_Cost": maintenance_cost,
            "Weather_Condition": weather,
            "Delay_Penalty": delay_penalty,
            "Vehicle_Health_Score_pct": vehicle_health,
            "Weather_Severity": min(10, max(1, weather_severity)),
        })
    pd.DataFrame(records).to_csv(CSV_PATH, index=False)


def plotly_dark():
    return dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0", size=11),
        margin=dict(t=36, b=36, l=48, r=28),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        autosize=True,
    )


def inject_glassmorphism_css():
    st.markdown(
        f"""
        <style>
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ visibility: hidden; }}
        [data-testid="stHeader"] {{ visibility: hidden; }}
        [data-testid="stToolbar"] {{ visibility: hidden; }}
        [data-testid="stDeployButton"] {{ visibility: hidden; }}
        .stApp, .main {{ background: {BG_DARK}; }}
        .main .block-container {{ padding-top: 0.5rem; padding-bottom: 1rem; max-width: 100%; }}
        /* Glassmorphism: all block containers */
        .block-container > div, [data-testid="stVerticalBlock"] > div {{
            background: rgba(15, 20, 30, 0.7) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(0, 229, 255, 0.2);
            padding: 12px;
            margin-bottom: 8px;
        }}
        .element-container:has([data-testid="stPlotlyChart"]) {{
            background: rgba(15, 20, 30, 0.7) !important;
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(0, 229, 255, 0.2);
            padding: 10px;
            margin-bottom: 8px;
        }}
        [data-testid="stMetric"] {{
            background: rgba(15, 20, 30, 0.7) !important;
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 12px;
            border: 1px solid rgba(0, 229, 255, 0.2);
        }}
        .stDataFrame {{ border: 1px solid rgba(255, 0, 127, 0.3); border-radius: 12px; }}
        /* Neon scrollbars */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0b0f19; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(0, 229, 255, 0.5); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(0, 229, 255, 0.8); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Chart builders
# -----------------------------------------------------------------------------

def fig_waterfall(gross_revenue, fuel_cost, maintenance_cost, penalties, net_profit):
    layout = {**plotly_dark(), "title": "P&L Waterfall (€)"}
    fig = go.Figure(go.Waterfall(
        name="", orientation="v",
        measure=["total", "absolute", "absolute", "absolute", "total"],
        x=["Gross Revenue", "Fuel Costs", "Maintenance", "Delay Penalties", "Net Profit"],
        textposition="outside",
        text=[f"€{gross_revenue:,.0f}", f"-€{fuel_cost:,.0f}", f"-€{maintenance_cost:,.0f}", f"-€{penalties:,.0f}", f"€{net_profit:,.0f}"],
        y=[gross_revenue, -fuel_cost, -maintenance_cost, -penalties, net_profit],
        connector=dict(line=dict(color=NEON_CYAN, width=1)),
        increasing=dict(marker=dict(color=NEON_LIME)),
        decreasing=dict(marker=dict(color=NEON_PINK)),
        totals=dict(marker=dict(color=NEON_CYAN)),
    ))
    fig.update_layout(**layout)
    return fig


def fig_sunburst(costs_by_route_type):
    layout = {**plotly_dark(), "title": "Total Costs by Route & Type (Fuel vs Maintenance)"}
    fig = go.Figure(go.Sunburst(
        labels=costs_by_route_type["label"].tolist(),
        parents=costs_by_route_type["parent"].tolist(),
        values=costs_by_route_type["value"].tolist(),
        branchvalues="total",
        marker=dict(colors=[NEON_CYAN, NEON_PINK, NEON_LIME] * 20, line=dict(color=BG_DARK, width=1)),
    ))
    fig.update_layout(**layout)
    return fig


def fig_ai_forecast(hist_dates, hist_revenue, forecast_dates, forecast_revenue, lower_ci, upper_ci):
    """Historical vs AI Projected Revenue with confidence band (tonexty)."""
    layout = {**plotly_dark(), "title": "Historical vs AI Projected Revenue (€)"}
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_dates, y=hist_revenue, mode="lines", name="Historical",
        line=dict(color=NEON_LIME, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=upper_ci, mode="lines", name="Upper CI",
        line=dict(width=0), fill=None,
    ))
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=lower_ci, mode="lines", name="Lower CI",
        line=dict(width=0), fill="tonexty", fillcolor="rgba(0, 229, 255, 0.2)",
    ))
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=forecast_revenue, mode="lines", name="AI Forecast (30d)",
        line=dict(color=NEON_CYAN, width=2, dash="dot"),
    ))
    fig.update_layout(**layout)
    return fig


def fig_mapbox_europe(city_df, height=380):
    layout = {**plotly_dark(), "title": "European Hubs — Volume & Avg Delay", "height": height}
    layout["mapbox"] = dict(style="carto-darkmatter")
    fig = px.scatter_mapbox(
        city_df, lat="lat", lon="lon", size="volume", color="avg_delay",
        hover_name="city", hover_data={"volume": True, "avg_delay": ":.1f"},
        color_continuous_scale=["#00e5ff", "#ff007f"], size_max=26, zoom=3.5, center=dict(lat=50, lon=12),
    )
    fig.update_layout(**layout)
    return fig


def fig_sankey_flow(flow_df):
    """Sankey: Origin -> Hub -> Destination with neon link colors by volume."""
    # Aggregate links: origin->hub and hub->dest (sum volume for same pair)
    oh = flow_df.groupby(["origin", "hub"], as_index=False)["volume"].sum()
    hd = flow_df.groupby(["hub", "dest"], as_index=False)["volume"].sum()
    origins = sorted(flow_df["origin"].unique().tolist())
    hubs = sorted(flow_df["hub"].unique().tolist())
    dests = sorted(flow_df["dest"].unique().tolist())
    nodes = origins + hubs + dests
    node_idx = {n: i for i, n in enumerate(nodes)}
    n_orig, n_hub = len(origins), len(hubs)
    link_src, link_tgt, link_val, link_color = [], [], [], []
    v_max = max(oh["volume"].max(), hd["volume"].max()) or 1
    for _, row in oh.iterrows():
        v = row["volume"]
        t = v / v_max
        col = f"rgba({int(255*(1-t))},{int(229*t)},{255},0.85)"
        link_src.append(node_idx[row["origin"]])
        link_tgt.append(node_idx[row["hub"]])
        link_val.append(v)
        link_color.append(col)
    for _, row in hd.iterrows():
        v = row["volume"]
        t = v / v_max
        col = f"rgba({255},{int(0)},{int(127*(1-t)+255*t)},0.85)"
        link_src.append(node_idx[row["hub"]])
        link_tgt.append(node_idx[row["dest"]])
        link_val.append(v)
        link_color.append(col)
    layout = {**plotly_dark(), "title": "Supply Chain Flow: Origin → Hubs → Destinations", "height": 420}
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15, thickness=20, line=dict(color=NEON_CYAN, width=0.5),
            label=nodes,
            color=["rgba(0,229,255,0.5)"] * n_orig + ["rgba(255,0,127,0.5)"] * n_hub + ["rgba(57,255,20,0.5)"] * len(dests),
        ),
        link=dict(source=link_src, target=link_tgt, value=link_val, color=link_color),
    )])
    fig.update_layout(**layout)
    return fig


def fig_radar_multi(top3_metrics_df):
    layout = {**plotly_dark(), "title": "Top 3 Routes — 5 Metrics (Radar)", "showlegend": True}
    layout["polar"] = dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.12)", range=[0, 100]),
        angularaxis=dict(gridcolor="rgba(255,255,255,0.12)"),
    )
    fig = go.Figure()
    colors = [NEON_CYAN, NEON_PINK, NEON_LIME]
    fillcolors = ["rgba(0,229,255,0.25)", "rgba(255,0,127,0.25)", "rgba(57,255,20,0.25)"]
    theta = ["Speed", "Cost-efficiency", "Safety", "On-time", "Revenue", "Speed"]
    for i, (route, row) in enumerate(top3_metrics_df.iterrows()):
        r = [row["Speed"], row["Cost_eff"], row["Safety"], row["On_time"], row["Revenue_norm"], row["Speed"]]
        name = (route[:18] + "…") if len(route) > 18 else route
        fig.add_trace(go.Scatterpolar(
            r=r, theta=theta, fill="toself", name=name,
            line=dict(color=colors[i % 3], width=2),
            fillcolor=fillcolors[i % 3],
        ))
    fig.update_layout(**layout)
    return fig


def fig_dual_axis(daily_vol, daily_avg_time):
    layout = {**plotly_dark(), "title": "Daily Volume vs Avg Delivery Time"}
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    x = daily_vol.index.astype(str).tolist()
    fig.add_trace(go.Bar(x=x, y=daily_vol.tolist(), name="Volume", marker_color=NEON_CYAN), secondary_y=False)
    fig.add_trace(go.Scatter(x=x, y=daily_avg_time.tolist(), name="Avg Time (h)", line=dict(color=NEON_PINK, width=2)), secondary_y=True)
    fig.update_layout(**layout)
    fig.update_xaxes(title_text="Date", gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(title_text="Deliveries", secondary_y=False, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(title_text="Avg Time (h)", secondary_y=True, gridcolor="rgba(255,255,255,0.08)")
    return fig


def fig_violin_weather(delay_by_weather_df):
    layout = {**plotly_dark(), "title": "Delivery Time Distribution by Weather"}
    fig = px.violin(
        delay_by_weather_df, x="Weather_Condition", y="Delivery_Time_Hours",
        color="Weather_Condition", box=True,
        color_discrete_sequence=[NEON_CYAN, NEON_PINK, NEON_LIME, "#f59e0b"],
    )
    fig.update_layout(**layout)
    return fig


def fig_risk_3d(risk_df):
    """3D Risk Matrix: Weather Severity x Financial Impact x Probability of Delay; color by Route, glowing."""
    layout = {**plotly_dark(), "title": "3D Risk Matrix — Weather × Impact × Delay Probability", "height": 480}
    layout["scene"] = dict(
        xaxis=dict(title="Weather Severity", gridcolor="rgba(255,255,255,0.08)", backgroundcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Financial Impact (€)", gridcolor="rgba(255,255,255,0.08)", backgroundcolor="rgba(0,0,0,0)"),
        zaxis=dict(title="Probability of Delay", gridcolor="rgba(255,255,255,0.08)", backgroundcolor="rgba(0,0,0,0)"),
        bgcolor="rgba(0,0,0,0)",
    )
    fig = px.scatter_3d(
        risk_df, x="Weather_Severity", y="Financial_Impact", z="Prob_Delay",
        color="Route", hover_name="Route", hover_data=["Financial_Impact", "Prob_Delay"],
        color_discrete_sequence=[NEON_CYAN, NEON_PINK, NEON_LIME, "#00e5ff", "#ff007f", "#39ff14"],
    )
    fig.update_traces(
        marker=dict(size=10, opacity=0.9, line=dict(color="rgba(255,255,255,0.6)", width=2)),
    )
    fig.update_layout(**layout)
    return fig


# -----------------------------------------------------------------------------
# Streamlit app
# -----------------------------------------------------------------------------

st.set_page_config(page_title="AI Digital Twin & Supply Chain Control Tower", layout="wide", initial_sidebar_state="expanded")
inject_glassmorphism_css()

generate_fleet_csv()
df = pd.read_csv(CSV_PATH)
df["Date"] = pd.to_datetime(df["Date"])
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
df["Delivery_Time_Hours"] = (df["Distance"] / 55).clip(upper=24)
if "Weather_Severity" not in df.columns:
    df["Weather_Severity"] = df["Weather_Condition"].map(WEATHER_SEVERITY).fillna(3)

# Sidebar
st.sidebar.header("Filters")
date_min, date_max = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_d, end_d = date_range[0], date_range[1]
else:
    start_d = end_d = date_range if hasattr(date_range, "year") else date_min
routes_sel = st.sidebar.multiselect("Route", options=sorted(df["Route"].unique()), default=[])

mask_d = (df["Date"].dt.date >= start_d) & (df["Date"].dt.date <= end_d)
mask_r = df["Route"].isin(routes_sel) if routes_sel else pd.Series(True, index=df.index)
data = df.loc[mask_d & mask_r].copy()

# KPIs
n = len(data)
gross_revenue = data["Revenue_EUR"].sum()
fuel_cost = data["Fuel_Cost"].sum()
maintenance_cost = data["Maintenance_Cost"].sum()
penalties = data["Delay_Penalty"].sum()
net_profit = gross_revenue - fuel_cost - maintenance_cost - penalties
avg_margin_pct = 100 * (data["Revenue_EUR"] - data["Fuel_Cost"] - data["Maintenance_Cost"] - data["Delay_Penalty"]).sum() / gross_revenue if gross_revenue else 0
fleet_health = data["Vehicle_Health_Score_pct"].mean()
on_time_rate = 100 * (data["Status"] == "On-Time").sum() / n if n else 0

st.title("AI-Powered Digital Twin & Supply Chain Control Tower")
st.caption("Executive command view — Real-time KPIs, Sankey flows, 3D Risk, AI forecast")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total Deliveries", f"{n:,}", delta="5.2% MoM")
with c2:
    st.metric("Net Profit (€)", f"€{net_profit:,.0f}", delta="-1.1% MoM")
with c3:
    st.metric("Avg Margin %", f"{avg_margin_pct:.1f}%", delta="0.8% MoM")
with c4:
    st.metric("Fleet Health Score", f"{fleet_health:.1f}%", delta="2.3% MoM")
with c5:
    st.metric("On-Time Rate", f"{on_time_rate:.1f}%", delta="1.2% MoM")

tab1, tab2, tab3 = st.tabs(["Financial & Commercial Overview", "Fleet Operations & Geospatial", "AI & Predictive Analytics"])

# ---------- Tab 1: Financial ----------
with tab1:
    st.subheader("P&L, Cost Breakdown & AI Revenue Forecast")
    r1a, r1b = st.columns([1, 1])
    with r1a:
        with st.container():
            st.plotly_chart(fig_waterfall(gross_revenue, fuel_cost, maintenance_cost, penalties, net_profit), use_container_width=True, key="waterfall")
    with r1b:
        cost_rows = []
        for route in list(data["Route"].unique())[:12]:
            sub = data[data["Route"] == route]
            f, m = sub["Fuel_Cost"].sum(), sub["Maintenance_Cost"].sum()
            cost_rows.append({"label": route, "parent": "", "value": f + m})
            cost_rows.append({"label": route + " | Fuel", "parent": route, "value": f})
            cost_rows.append({"label": route + " | Maint", "parent": route, "value": m})
        cost_df = pd.DataFrame(cost_rows)
        if not cost_df.empty:
            with st.container():
                st.plotly_chart(fig_sunburst(cost_df), use_container_width=True, key="sunburst")

    # AI Time-Series Forecast (Historical vs next 30d with confidence band)
    daily_rev = data.groupby(data["Date"].dt.date)["Revenue_EUR"].sum()
    if len(daily_rev) >= 7:
        hist_dates = daily_rev.index.astype(str).tolist()
        hist_revenue = daily_rev.tolist()
        last_val = hist_revenue[-1]
        trend = (hist_revenue[-1] - hist_revenue[0]) / max(len(hist_revenue), 1)
        np.random.seed(42)
        last_d = daily_rev.index[-1]
        if hasattr(last_d, "strftime"):
            forecast_dates = [(last_d + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 31)]
        else:
            forecast_dates = [(pd.Timestamp(last_d) + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 31)]
        forecast_revenue = [last_val + trend * i + np.random.normal(0, last_val * 0.02) for i in range(30)]
        lower_ci = [x - abs(np.random.normal(last_val * 0.05, last_val * 0.02)) for x in forecast_revenue]
        upper_ci = [x + abs(np.random.normal(last_val * 0.05, last_val * 0.02)) for x in forecast_revenue]
        with st.container():
            st.plotly_chart(fig_ai_forecast(hist_dates, hist_revenue, forecast_dates, forecast_revenue, lower_ci, upper_ci), use_container_width=True, key="ai_forecast")
    else:
        with st.container():
            st.info("Need at least 7 days of data for AI forecast.")

# ---------- Tab 2: Operations (Map, Sankey, Radar, Dual-axis) ----------
with tab2:
    st.subheader("Map, Supply Chain Sankey, Radar & Daily Trends")
    origin = data["Route"].str.extract(r"^(.*?) to", expand=False)
    dest = data["Route"].str.extract(r" to (.*)$", expand=False)
    data_od = data.assign(origin=origin.values, dest=dest.values)
    data_od["hub"] = data_od["origin"].map(HUB_MAP).fillna("Hub Berlin")

    # Sankey: Origin -> Hub -> Dest
    flow = data_od.groupby(["origin", "hub", "dest"], as_index=False).size().rename(columns={"size": "volume"})
    if not flow.empty:
        with st.container():
            st.plotly_chart(fig_sankey_flow(flow), use_container_width=True, key="sankey")

    city_vol = data.assign(city=origin.values).groupby("city", as_index=False).agg(
        volume=("Route", "count"),
        avg_delay=("Delivery_Time_Hours", "mean"),
    )
    city_vol["lat"] = city_vol["city"].map(lambda c: CITY_COORDS.get(c, (50, 10))[0])
    city_vol["lon"] = city_vol["city"].map(lambda c: CITY_COORDS.get(c, (50, 10))[1])
    if city_vol.empty:
        city_vol = pd.DataFrame([{"city": "Warsaw", "lat": 52.23, "lon": 21.01, "volume": 1, "avg_delay": 12}])

    r2a, r2b = st.columns([2, 1])
    with r2a:
        with st.container():
            st.plotly_chart(fig_mapbox_europe(city_vol, height=400), use_container_width=True, key="mapbox")
    with r2b:
        daily_vol = data.groupby(data["Date"].dt.date).size()
        daily_time = data.groupby(data["Date"].dt.date)["Delivery_Time_Hours"].mean()
        daily_time = daily_time.reindex(daily_vol.index, fill_value=0)
        with st.container():
            st.plotly_chart(fig_dual_axis(daily_vol, daily_time), use_container_width=True, key="dualaxis")

    by_route = data.groupby("Route").agg(
        Volume=("Route", "count"),
        Revenue=("Revenue_EUR", "sum"),
        On_time=("Status", lambda s: 100 * (s == "On-Time").mean()),
        Safety=("Driver_Rating", "mean"),
        Fuel=("Fuel_Cost", "sum"),
        Maint=("Maintenance_Cost", "sum"),
        AvgTime=("Delivery_Time_Hours", "mean"),
    )
    by_route["Cost_eff"] = (by_route["Revenue"] / (by_route["Fuel"] + by_route["Maint"] + 1e-9) * 10).clip(0, 100)
    by_route["Speed"] = (100 - (by_route["AvgTime"] / 24 * 100)).clip(0, 100)
    by_route["Revenue_norm"] = (by_route["Revenue"] / by_route["Revenue"].max() * 100).fillna(0)
    by_route["Safety"] = (by_route["Safety"] * 20).clip(0, 100)
    by_route["On_time"] = by_route["On_time"].fillna(0)
    top3 = by_route.nlargest(3, "Volume")[["Speed", "Cost_eff", "Safety", "On_time", "Revenue_norm"]]
    with st.container():
        st.plotly_chart(fig_radar_multi(top3), use_container_width=True, key="radar")

# ---------- Tab 3: AI & Predictive (Violin, 3D Risk, Alerts) ----------
with tab3:
    st.subheader("Delay by Weather, 3D Risk Matrix & Predictive Maintenance Alerts")
    r3a, r3b = st.columns([1, 1])
    with r3a:
        with st.container():
            st.plotly_chart(fig_violin_weather(data[["Weather_Condition", "Delivery_Time_Hours"]].copy()), use_container_width=True, key="violin")
    with r3b:
        st.markdown("**Predictive Maintenance Alerts** — Vehicles with Health Score &lt; 40%")
        alerts = data[data["Vehicle_Health_Score_pct"] < 40][["Truck_ID", "Route", "Date", "Vehicle_Health_Score_pct", "Maintenance_Cost", "Status"]].tail(50)
        alerts["Date"] = pd.to_datetime(alerts["Date"]).dt.strftime("%Y-%m-%d")
        if alerts.empty:
            st.info("No vehicles currently below 40% health threshold.")
        else:
            st.dataframe(alerts, use_container_width=True, key="alerts_table", height=280)

    # 3D Risk Matrix: Weather Severity x Financial Impact (€) x Prob of Delay, color Route
    risk_agg = data.groupby("Route").agg(
        Weather_Severity=("Weather_Severity", "mean"),
        Prob_Delay=("Status", lambda s: 100 * (s == "Delayed").mean()),
    ).reset_index()
    cost_per_route = data.groupby("Route").apply(
        lambda g: g["Delay_Penalty"].sum() + g["Fuel_Cost"].sum() + g["Maintenance_Cost"].sum()
    )
    risk_agg["Financial_Impact"] = risk_agg["Route"].map(cost_per_route).fillna(0)
    if not risk_agg.empty:
        with st.container():
            st.plotly_chart(fig_risk_3d(risk_agg), use_container_width=True, key="risk3d")
