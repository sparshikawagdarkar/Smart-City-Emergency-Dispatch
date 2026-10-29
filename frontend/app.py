
from pathlib import Path
from datetime import datetime
import heapq

import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

INCIDENT_FILE = DATA / "incidents.csv"
VEHICLE_FILE = DATA / "vehicles.csv"
ROAD_FILE = DATA / "roads.csv"
CITIZEN_FILE = DATA / "citizens.csv"

INCIDENT_COLS = [
    "id", "type", "severity", "people", "location", "priority",
    "priority_label", "vehicle_id", "status", "citizen_id",
    "created_at", "dispatched_at", "en_route_at", "arrived_at",
    "completed_at", "route", "distance", "eta_minutes", "details"
]

VEHICLE_COLS = [
    "vehicle_id", "type", "location", "status", "assigned_incident"
]

ROAD_COLS = ["from", "to", "distance"]

CITIZEN_COLS = [
    "citizen_id", "name", "phone", "address"
]

st.set_page_config(
    page_title="Smart City Emergency Dispatch",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# DARK THEME
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        color-scheme: dark;
    }

    .stApp {
        background: #0b1120;
        color: #e5e7eb;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #273449;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 17, 32, 0.95);
    }

    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 800 !important;
    }

    p, label, span, div {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #172238, #111827);
        border: 1px solid #2b3a52;
        border-radius: 14px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #a5b4cc !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    [data-testid="stMetricDelta"] {
        color: #34d399 !important;
    }

    .hero {
        background: linear-gradient(120deg, #172554, #172033 65%, #1e293b);
        border: 1px solid #334b76;
        border-radius: 18px;
        padding: 28px;
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 30px;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #bdc9dd;
        font-size: 14px;
    }

    .section-card {
        background: #111827;
        border: 1px solid #28364b;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .small-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .status-pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        background: #1e3a5f;
        color: #bfdbfe;
    }

    .stButton > button {
        background: #2563eb;
        color: white;
        border: 1px solid #3b82f6;
        border-radius: 9px;
        font-weight: 700;
        min-height: 42px;
        transition: 0.2s;
    }

    .stButton > button:hover {
        background: #1d4ed8;
        border-color: #60a5fa;
        color: white;
    }

    .stDownloadButton > button {
        background: #172554;
        color: #dbeafe;
        border: 1px solid #3b82f6;
        border-radius: 9px;
    }

    input, textarea {
        background-color: #111827 !important;
        color: #f8fafc !important;
    }

    [data-baseweb="select"] > div {
        background-color: #111827;
        border-color: #374151;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #28364b;
        border-radius: 10px;
        overflow: hidden;
    }

    hr {
        border-color: #28364b;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CSV HELPERS
# =========================================================
def ensure_csv(path, columns, initial_rows=None):
    if not path.exists() or path.stat().st_size == 0:
        df = pd.DataFrame(initial_rows or [], columns=columns)
        df.to_csv(path, index=False)
        return

    try:
        df = pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        df = pd.DataFrame(columns=columns)

    changed = False
    for col in columns:
        if col not in df.columns:
            df[col] = ""
            changed = True

    # Preserve extra columns if an existing CSV contains them.
    if changed:
        df.to_csv(path, index=False)


def read_csv(path, columns):
    ensure_csv(path, columns)
    df = pd.read_csv(path, dtype=str).fillna("")
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    return df


def save_csv(df, path):
    df.to_csv(path, index=False)


def seed_data():
    ensure_csv(INCIDENT_FILE, INCIDENT_COLS)

    ensure_csv(
        VEHICLE_FILE,
        VEHICLE_COLS,
        [
            ["A01", "Ambulance", "2", "Available", ""],
            ["A02", "Ambulance", "5", "Available", ""],
            ["A03", "Ambulance", "7", "En Route", "101"],
            ["F01", "Fire Engine", "3", "Available", ""],
            ["P01", "Police", "4", "Available", ""],
            ["P02", "Police", "6", "Busy", ""],
        ],
    )

    ensure_csv(
        ROAD_FILE,
        ROAD_COLS,
        [
            ["1", "2", "4"], ["1", "3", "2"], ["2", "3", "1"],
            ["2", "4", "5"], ["3", "4", "8"], ["3", "5", "10"],
            ["4", "5", "2"], ["4", "6", "6"], ["5", "6", "3"],
            ["5", "7", "4"], ["6", "7", "2"],
        ],
    )

    ensure_csv(CITIZEN_FILE, CITIZEN_COLS)


seed_data()

# =========================================================
# DATA ACCESS
# =========================================================
def get_incidents():
    return read_csv(INCIDENT_FILE, INCIDENT_COLS)


def get_vehicles():
    return read_csv(VEHICLE_FILE, VEHICLE_COLS)


def get_roads():
    return read_csv(ROAD_FILE, ROAD_COLS)


# =========================================================
# PRIORITY SCORING
# =========================================================
SEVERITY_SCORE = {
    "Critical": 50,
    "High": 35,
    "Medium": 20,
    "Low": 10,
}

def calculate_priority(severity, people):
    people_score = min(max(int(people), 1), 10) * 3
    return SEVERITY_SCORE.get(severity, 10) + people_score


def priority_label(score):
    if score >= 65:
        return "CRITICAL"
    if score >= 45:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


# =========================================================
# GRAPH + DIJKSTRA SHORTEST ROUTE
# =========================================================
def build_graph():
    graph = {}

    for _, row in get_roads().iterrows():
        try:
            a = int(float(row["from"]))
            b = int(float(row["to"]))
            distance = float(row["distance"])
        except (ValueError, TypeError):
            continue

        if distance < 0:
            continue

        graph.setdefault(a, []).append((b, distance))
        graph.setdefault(b, []).append((a, distance))

    return graph


def shortest_path(start, end):
    graph = build_graph()
    queue = [(0, start, [start])]
    best = {start: 0}

    while queue:
        distance, node, path = heapq.heappop(queue)

        if node == end:
            return path, distance

        if distance > best.get(node, float("inf")):
            continue

        for neighbor, weight in graph.get(node, []):
            new_distance = distance + weight

            if new_distance < best.get(neighbor, float("inf")):
                best[neighbor] = new_distance
                heapq.heappush(
                    queue,
                    (new_distance, neighbor, path + [neighbor])
                )

    return [], float("inf")


# =========================================================
# AUTOMATIC VEHICLE ASSIGNMENT
# =========================================================
def compatible_vehicle_types(incident_type):
    mapping = {
        "Cardiac": ["Ambulance"],
        "Medical": ["Ambulance"],
        "Fire": ["Fire Engine"],
        "Crime": ["Police"],
        "Accident": ["Ambulance", "Police"],
        "Rescue": ["Fire Engine", "Ambulance"],
        "Other": ["Ambulance", "Fire Engine", "Police"],
    }
    return mapping.get(incident_type, ["Ambulance", "Fire Engine", "Police"])


def find_nearest_vehicle(incident_type, incident_location):
    df = get_vehicles()
    allowed = compatible_vehicle_types(incident_type)
    options = []

    for idx, row in df.iterrows():
        if row["type"] not in allowed:
            continue

        if row["status"].strip().lower() != "available":
            continue

        try:
            vehicle_location = int(float(row["location"]))
        except (ValueError, TypeError):
            continue

        path, distance = shortest_path(vehicle_location, incident_location)

        if path:
            options.append((distance, str(row["vehicle_id"]), idx, path))

    options.sort(key=lambda item: (item[0], item[1]))
    return options, df


def dispatch_incident(incident_id):
    incidents_df = get_incidents()
    match = incidents_df.index[
        incidents_df["id"].astype(str) == str(incident_id)
    ]

    if len(match) == 0:
        return False, "Incident not found."

    idx = match[0]
    incident = incidents_df.loc[idx]

    if incident["status"] in ["Dispatched", "En Route", "Arrived", "Completed"]:
        return False, "This incident has already been dispatched."

    try:
        location = int(float(incident["location"]))
    except (ValueError, TypeError):
        return False, "The incident location must be a valid road node."

    options, vehicles_df = find_nearest_vehicle(incident["type"], location)

    if not options:
        return False, "No compatible available vehicle or valid route was found."

    distance, vehicle_id, vehicle_idx, path = options[0]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    route_text = " → ".join(map(str, path))
    eta = max(1, round(distance * 3))


    incidents_df.loc[idx, "vehicle_id"] = str(vehicle_id)
    incidents_df.loc[idx, "status"] = "Dispatched"
    incidents_df.loc[idx, "dispatched_at"] = str(now)
    incidents_df.loc[idx, "route"] = str(route_text) 
    incidents_df.loc[idx, "distance"] = str(round(float(distance), 2))
    incidents_df.loc[idx, "eta_minutes"] = str(eta)

    vehicles_df.loc[vehicle_idx, "status"] = "Dispatched"
    vehicles_df.loc[vehicle_idx, "assigned_incident"] = str(incident_id)

    save_csv(incidents_df, INCIDENT_FILE)
    save_csv(vehicles_df, VEHICLE_FILE)

    return True, {
        "vehicle": vehicle_id,
        "route": route_text,
        "distance": round(distance, 2),
        "eta": eta,
    }


# =========================================================
# PAGE HEADER
# =========================================================
st.sidebar.markdown("## 🚨 SMART CITY")
st.sidebar.caption("Emergency Response Control Center")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Register Emergency",
        "Incident Management",
        "Vehicle Fleet",
        "Road Network",
        "Analytics",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**System Status**")
st.sidebar.success("Application running")
st.sidebar.caption("Prototype · CSV storage")

st.markdown("""
<div class="hero">
    <div class="hero-title">🚨 Smart City Emergency Dispatch</div>
    <div class="hero-subtitle">
        Real-time incident monitoring · Automatic vehicle allocation ·
        Dijkstra shortest-path routing
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":
    incidents_df = get_incidents()
    vehicles_df = get_vehicles()

    total = len(incidents_df)
    active = len(incidents_df[
        ~incidents_df["status"].isin(["Completed", "Cancelled"])
    ])
    critical = len(incidents_df[
        incidents_df["severity"].isin(["Critical"])
        & ~incidents_df["status"].isin(["Completed", "Cancelled"])
    ])
    available = len(vehicles_df[
        vehicles_df["status"].str.lower() == "available"
    ])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", total)
    c2.metric("Active Incidents", active)
    c3.metric("Critical Incidents", critical)
    c4.metric("Available Vehicles", available)

    st.markdown("### 📡 Recent Emergency Activity")

    if incidents_df.empty:
        st.info("No incidents registered yet.")
    else:
        display = incidents_df.copy()
        display["priority"] = pd.to_numeric(
            display["priority"], errors="coerce"
        ).fillna(0)
        display = display.sort_values(
            ["priority", "id"], ascending=[False, False]
        )
        st.dataframe(
            display[
                ["id", "type", "severity", "location", "priority",
                 "vehicle_id", "status", "eta_minutes"]
            ].head(10),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### 🚑 Fleet Availability")

    if not vehicles_df.empty:
        fleet_summary = (
            vehicles_df.groupby(["type", "status"])
            .size()
            .reset_index(name="Count")
        )
        st.dataframe(fleet_summary, use_container_width=True, hide_index=True)


# =========================================================
# REGISTER EMERGENCY
# =========================================================
elif page == "Register Emergency":
    st.markdown("## 🆘 Register a New Emergency")
    st.write("Enter incident details. The system will calculate priority and try to dispatch the nearest compatible vehicle.")

    with st.form("register_emergency_form"):
        c1, c2 = st.columns(2)

        with c1:
            incident_type = st.selectbox(
                "Emergency Type",
                ["Cardiac", "Medical", "Fire", "Accident", "Crime", "Rescue", "Other"],
            )
            severity = st.selectbox(
                "Severity",
                ["Critical", "High", "Medium", "Low"],
            )
            people = st.number_input(
                "People Affected", min_value=1, max_value=1000, value=1
            )

        with c2:
            graph = build_graph()
            nodes = sorted(graph.keys()) or list(range(1, 8))
            location = st.selectbox(
                "Incident Location (Road Node)",
                nodes,
            )
            citizen_id = st.text_input("Citizen ID (optional)")
            details = st.text_area("Additional Details (optional)")

        submitted = st.form_submit_button(
            "🚨 REGISTER & DISPATCH", use_container_width=True
        )

    if submitted:
        incidents_df = get_incidents()

        existing_ids = pd.to_numeric(
            incidents_df["id"], errors="coerce"
        ).dropna()
        new_id = int(existing_ids.max()) + 1 if not existing_ids.empty else 101

        score = calculate_priority(severity, people)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_row = {col: "" for col in INCIDENT_COLS}
        new_row.update({
            "id": str(new_id),
            "type": incident_type,
            "severity": severity,
            "people": str(people),
            "location": str(location),
            "priority": str(score),
            "priority_label": priority_label(score),
            "status": "Registered",
            "citizen_id": citizen_id.strip(),
            "created_at": now,
            "details": details.strip(),
        })

        incidents_df = pd.concat(
            [incidents_df, pd.DataFrame([new_row])],
            ignore_index=True,
        )
        save_csv(incidents_df, INCIDENT_FILE)

        st.success(f"Incident #{new_id} registered successfully.")
        st.metric("Calculated Priority Score", score)

        success, result = dispatch_incident(new_id)

        if success:
            st.success("Vehicle assigned automatically!")
            a, b, c = st.columns(3)
            a.metric("Assigned Vehicle", result["vehicle"])
            b.metric("Route Distance", f'{result["distance"]} units')
            c.metric("Estimated Arrival", f'{result["eta"]} min')
            st.info(f'Shortest route: {result["route"]}')
        else:
            st.warning(f"Incident saved, but automatic dispatch was not possible: {result}")
            st.caption("Use Incident Management to retry dispatch after a compatible vehicle becomes available.")


# =========================================================
# INCIDENT MANAGEMENT
# =========================================================
elif page == "Incident Management":
    st.markdown("## 📋 Incident Management")

    df = get_incidents()

    if df.empty:
        st.info("No incidents are available.")
    else:
        st.dataframe(
    df[
        [
            "id",
            "type",
            "severity",
            "location",
            "vehicle_id",
            "status",
            "route",
            "eta_minutes",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

        st.markdown("### Update Incident Status")
        ids = df["id"].astype(str).tolist()

        selected_id = st.selectbox("Select Incident ID", ids)
        selected_rows = df[df["id"].astype(str) == selected_id]
        current_status = (
            selected_rows.iloc[0]["status"] if not selected_rows.empty else "Registered"
        )

        new_status = st.selectbox(
            "New Status",
            ["Registered", "Dispatched", "En Route", "Arrived", "Completed", "Cancelled"],
            index=(
                ["Registered", "Dispatched", "En Route", "Arrived", "Completed", "Cancelled"]
                .index(current_status)
                if current_status in ["Registered", "Dispatched", "En Route", "Arrived", "Completed", "Cancelled"]
                else 0
            ),
        )

        if st.button("Update Incident", use_container_width=True):
            if new_status == "Dispatched" and current_status == "Registered":
                ok, result = dispatch_incident(selected_id)
                if ok:
                    st.success(
                        f'Assigned {result["vehicle"]}. Route: {result["route"]}'
                    )
                else:
                    st.error(result)
            else:
                df = get_incidents()
                match = df.index[df["id"].astype(str) == selected_id]

                if len(match):
                    idx = match[0]
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    df.loc[idx, "status"] = new_status

                    timestamp_column = {
                        "En Route": "en_route_at",
                        "Arrived": "arrived_at",
                        "Completed": "completed_at",
                    }.get(new_status)

                    if timestamp_column:
                        df.loc[idx, timestamp_column] = now

                    vehicle_id = str(df.loc[idx, "vehicle_id"]).strip()
                    vehicles_df = get_vehicles()

                    if vehicle_id:
                        vehicle_match = vehicles_df.index[
                            vehicles_df["vehicle_id"].astype(str) == vehicle_id
                        ]
                        if len(vehicle_match):
                            vehicle_idx = vehicle_match[0]

                            if new_status == "Completed":
                                vehicles_df.loc[vehicle_idx, "status"] = "Available"
                                vehicles_df.loc[vehicle_idx, "assigned_incident"] = ""
                            elif new_status == "Cancelled":
                                vehicles_df.loc[vehicle_idx, "status"] = "Available"
                                vehicles_df.loc[vehicle_idx, "assigned_incident"] = ""
                            elif new_status in ["Dispatched", "En Route", "Arrived"]:
                                vehicles_df.loc[vehicle_idx, "status"] = new_status

                    save_csv(df, INCIDENT_FILE)
                    save_csv(vehicles_df, VEHICLE_FILE)
                    st.success("Incident status updated.")
                    st.rerun()


# =========================================================
# VEHICLE FLEET
# =========================================================
elif page == "Vehicle Fleet":
    st.markdown("## 🚑 Vehicle Fleet")

    df = get_vehicles()

    a, b, c = st.columns(3)
    a.metric("Total Vehicles", len(df))
    b.metric("Available", len(df[df["status"].str.lower() == "available"]))
    c.metric("Busy / Deployed", len(df[df["status"].str.lower() != "available"]))

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("### Update Vehicle")
    if not df.empty:
        selected_vehicle = st.selectbox(
            "Vehicle ID", df["vehicle_id"].astype(str).tolist()
        )
        status_options = ["Available", "Dispatched", "En Route", "Arrived", "Busy"]
        vehicle_rows = df[df["vehicle_id"].astype(str) == selected_vehicle]
        current = vehicle_rows.iloc[0]["status"] if not vehicle_rows.empty else "Available"

        new_vehicle_status = st.selectbox(
            "Vehicle Status",
            status_options,
            index=status_options.index(current) if current in status_options else 0,
        )

        if st.button("Save Vehicle Status"):
            df = get_vehicles()
            match = df.index[df["vehicle_id"].astype(str) == selected_vehicle]
            if len(match):
                df.loc[match[0], "status"] = new_vehicle_status

                if new_vehicle_status == "Available":
                    df.loc[match[0], "assigned_incident"] = ""

                save_csv(df, VEHICLE_FILE)
                st.success("Vehicle status updated.")
                st.rerun()


# =========================================================
# ROAD NETWORK
# =========================================================
elif page == "Road Network":
    st.markdown("## 🗺️ Road Network & Shortest Path")
    roads = get_roads()

    st.write("The road network is represented as an adjacency list. Dijkstra's algorithm calculates the shortest route.")
    st.dataframe(roads, use_container_width=True, hide_index=True)

    graph = build_graph()
    nodes = sorted(graph.keys())

    if nodes:
        c1, c2 = st.columns(2)
        start = c1.selectbox("Starting Node", nodes, index=0)
        end = c2.selectbox("Destination Node", nodes, index=len(nodes) - 1)

        if st.button("Calculate Shortest Route", use_container_width=True):
            path, distance = shortest_path(start, end)
            if path:
                st.success("Shortest route found.")
                st.markdown(f"**Route:** {' → '.join(map(str, path))}")
                st.metric("Total Distance", f"{distance:g} units")
                st.metric("Estimated Travel Time", f"{max(1, round(distance * 3))} minutes")
            else:
                st.error("No route exists between these nodes.")


# =========================================================
# ANALYTICS
# =========================================================
elif page == "Analytics":
    st.markdown("## 📊 Emergency Analytics")

    df = get_incidents()
    vehicles_df = get_vehicles()

    if df.empty:
        st.info("Register incidents to view analytics.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Incidents by Type")
            counts = df["type"].value_counts()
            st.bar_chart(counts)

        with c2:
            st.markdown("### Incidents by Severity")
            severity_counts = df["severity"].value_counts()
            st.bar_chart(severity_counts)

        st.markdown("### Incident Status")
        status_counts = df["status"].value_counts()
        st.bar_chart(status_counts)

        st.markdown("### Priority Ranking")
        ranking = df.copy()
        ranking["priority"] = pd.to_numeric(
            ranking["priority"], errors="coerce"
        ).fillna(0)
        ranking = ranking.sort_values("priority", ascending=False)

        st.dataframe(
            ranking[
                ["id", "type", "severity", "priority",
                 "priority_label", "vehicle_id", "status"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Export Data")
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download Incidents CSV",
            data=get_incidents().to_csv(index=False).encode("utf-8"),
            file_name="incidents_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "Download Vehicles CSV",
            data=get_vehicles().to_csv(index=False).encode("utf-8"),
            file_name="vehicles_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.markdown("---")
st.caption("Smart City Emergency Dispatch System · Academic Prototype · Dijkstra Routing · Priority Scoring")
