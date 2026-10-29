# Smart City Emergency Dispatch System

A student project with a **C backend** (binary max heap, linked-list vehicle representation, adjacency-list road graph, Dijkstra shortest path, sorting/search commands) and a **Streamlit/Python interface** for the complete dispatch workflow. Incident, citizen, vehicle, and road data are stored in CSV files under `data/`.

## Features
- Dashboard metrics and active incident view
- Incident registration with unique IDs, citizen linking, validation, timestamps, and persistent CSV storage
- Citizen lookup by ID, name, contact, or address and linked incident history
- Priority score normalized to 0–100
- Compatible-vehicle recommendation using shortest graph distance
- Dispatch confirmation and protection against assigning vehicles that are no longer available
- Incident lifecycle: Registered → Dispatched → En Route → Arrived → Completed
- Vehicle status/location updates and vehicle release at completion
- Dijkstra route finder, distance breakdown, and estimated travel time
- Incident search, full records, status tracking, charts, fleet analytics, and completion-time metrics
- Pastel interface styling

## Requirements
- Python 3.10+ (tested design target)
- GCC/MinGW if you also want to run the C command-line demonstrations

## Run on Windows
1. Extract this project folder.
2. Open the folder and double-click `run_app.bat`, or open Command Prompt in the folder.
3. Run:
   ```bat
   python -m pip install -r requirements.txt
   python -m streamlit run frontend\app.py
   ```
4. Open the local URL shown by Streamlit (usually http://localhost:8501).

The app can still run its main workflow without GCC. The C command-line backend is retained for the DSA demonstration and is compiled by the launcher when GCC is available.

## Workflow
1. Register an incident and optionally link a citizen.
2. Open **Dispatch Center** to see compatible available vehicles ranked by graph distance and select one.
3. In **Incident Records**, advance the incident one status at a time: Dispatched → En Route → Arrived → Completed.
4. The assigned vehicle is released and marked Available at the incident location when the incident is completed.
5. Use **Analytics**, **Citizen Lookup**, and **Search Incident** to review records and outcomes.

## Priority scoring
Severity contributes a base score (Critical 70, High 50, Medium 30, Low 10), with up to 30 additional points based on the number of people affected. The score is capped at 100.

## Route and ETA
Routes are calculated using Dijkstra's algorithm over the undirected weighted graph in `data/roads.csv`. The ETA is a simple project estimate of 3 minutes per distance unit, not live traffic data. To integrate a real map provider, add geocoded node coordinates and configure a provider API key separately; do not commit API keys to source control.

## Data files
- `incidents.csv`: incident records and lifecycle timestamps
- `vehicles.csv`: fleet status, current node, and assignment
- `citizens.csv`: citizen records
- `roads.csv`: weighted road graph

Back up the `data/` directory before replacing project files. CSVs are local project storage, not a multi-user production database.
