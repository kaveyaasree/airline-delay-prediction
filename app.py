import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="✈️ Airline Dashboard", layout="wide")

# ---------------- GLASSMORPHISM STYLE ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}
.block-container {
    padding-top: 2rem;
}
.kpi {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 30px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    flights = pd.read_csv("flights.csv")
    airlines = pd.read_csv("airlines.csv")
    airports = pd.read_csv("airports.csv")

    flights = flights.merge(airlines, left_on="AIRLINE", right_on="IATA_CODE", how="left")
    flights = flights.merge(airports, left_on="ORIGIN_AIRPORT", right_on="IATA_CODE", how="left")

    return flights

flights = load_data()

# CLEAN
flights = flights[flights["CANCELLED"] == 0]
flights = flights.fillna(0)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🔎 Filters")
selected_month = st.sidebar.selectbox("Month", sorted(flights["MONTH"].unique()))
selected_airline = st.sidebar.selectbox("Airline", flights["AIRLINE_y"].dropna().unique())

filtered_df = flights[(flights["MONTH"] == selected_month) & (flights["AIRLINE_y"] == selected_airline)]

# ---------------- TITLE ----------------
st.title("✈️ Airline Delay Analysis Dashboard")
# st.markdown("### Interactive insights with modern UI")

# ---------------- KPI CARDS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<div class="kpi">Avg Departure Delay<br><h2>{round(filtered_df["DEPARTURE_DELAY"].mean(),2)} min</h2></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="kpi">Avg Arrival Delay<br><h2>{round(filtered_df["ARRIVAL_DELAY"].mean(),2)} min</h2></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="kpi">Total Flights<br><h2>{len(filtered_df)}</h2></div>', unsafe_allow_html=True)

st.divider()

# ---------------- TREND CHART ----------------
st.subheader("📈 Flight Delay Trend")

monthly_delay = flights.groupby("MONTH")["DEPARTURE_DELAY"].mean().reset_index()

fig1 = px.line(monthly_delay, x="MONTH", y="DEPARTURE_DELAY", markers=True)
fig1.update_traces(line=dict(width=4))
st.plotly_chart(fig1, use_container_width=True)

# ---------------- ROUTE INSIGHTS ----------------
st.subheader("🛫 Route Performance")

route_delay = filtered_df.groupby(["ORIGIN_AIRPORT", "DESTINATION_AIRPORT"])["ARRIVAL_DELAY"].mean().reset_index()
route_delay = route_delay.sort_values(by="ARRIVAL_DELAY", ascending=False).head(10)
route_delay["ROUTE"] = route_delay["ORIGIN_AIRPORT"].astype(str) + " → " + route_delay["DESTINATION_AIRPORT"].astype(str)

fig2 = px.bar(route_delay, x="ARRIVAL_DELAY", y="ROUTE", orientation='h', color="ARRIVAL_DELAY")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- DELAY CAUSES ----------------
st.subheader("📊 Delay Causes")

causes = {
    "Air System": filtered_df["AIR_SYSTEM_DELAY"].sum(),
    "Security": filtered_df["SECURITY_DELAY"].sum(),
    "Airline": filtered_df["AIRLINE_DELAY"].sum(),
    "Late Aircraft": filtered_df["LATE_AIRCRAFT_DELAY"].sum(),
    "Weather": filtered_df["WEATHER_DELAY"].sum()
}

cause_df = pd.DataFrame(list(causes.items()), columns=["Cause", "Value"])
fig3 = px.pie(cause_df, names="Cause", values="Value", hole=0.5)
st.plotly_chart(fig3, use_container_width=True)

# ---------------- MAP VISUALIZATION ----------------
st.subheader("🌍 Flight Routes Map")

map_df = filtered_df[["LATITUDE", "LONGITUDE"]].dropna()

fig_map = px.scatter_mapbox(
    map_df,
    lat="LATITUDE",
    lon="LONGITUDE",
    zoom=3,
    height=400
)

fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)

# ---------------- DAY ANALYSIS ----------------
st.subheader("📅 Day-wise Delay")

weekday_delay = filtered_df.groupby("DAY_OF_WEEK")["DEPARTURE_DELAY"].mean().reset_index()
fig5 = px.line(weekday_delay, x="DAY_OF_WEEK", y="DEPARTURE_DELAY", markers=True)
st.plotly_chart(fig5, use_container_width=True)

# ---------------- FOOTER ----------------
st.divider()
st.markdown("✨ Built with Streamlit | Advanced Airline Dashboard")
