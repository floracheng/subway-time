"""MTA Subway Times API for Prospect Park station."""

from datetime import datetime, timezone
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nyct_gtfs import NYCTFeed
from nyct_gtfs.compiled_gtfs import gtfs_realtime_pb2

app = FastAPI(title="Prospect Park Subway Times")

ALERTS_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts"

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Station configuration
PROSPECT_PARK_STOPS = ["D26N", "D26S"]

# Route display names and colors
ROUTE_INFO = {
    "B": {"name": "B", "color": "#FF6319"},
    "Q": {"name": "Q", "color": "#FCCC0A"},
    "FS": {"name": "S", "color": "#808183"},  # Franklin Shuttle displays as "S"
}

TARGET_ROUTES = {"B", "Q", "FS", "S"}


def get_alerts():
    """Fetch service alerts for B, Q, and S lines."""
    alerts = {"B": [], "Q": [], "S": []}

    try:
        response = requests.get(ALERTS_URL, timeout=10)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        seen_headers = set()  # Deduplicate alerts

        for entity in feed.entity:
            if entity.HasField("alert"):
                alert = entity.alert

                # Check if this alert affects our routes
                affected_routes = set()
                for informed in alert.informed_entity:
                    route_id = informed.route_id
                    if route_id in TARGET_ROUTES:
                        # Normalize FS to S for display
                        affected_routes.add("S" if route_id == "FS" else route_id)

                if not affected_routes:
                    continue

                # Get the plain text header
                header = ""
                for translation in alert.header_text.translation:
                    if translation.language == "en":
                        header = translation.text
                        break

                if not header or header in seen_headers:
                    continue
                seen_headers.add(header)

                # Add to each affected route
                for route in affected_routes:
                    alerts[route].append(header)

    except Exception as e:
        print(f"Error fetching alerts: {e}")

    return alerts


def get_arrivals():
    """Fetch arrivals from both BDFM and NQRW feeds."""
    arrivals = {"northbound": [], "southbound": [], "alerts": {}, "updated_at": None}

    # Fetch alerts
    arrivals["alerts"] = get_alerts()

    # Use local time since MTA feed returns local (NYC) times
    now = datetime.now()

    # Fetch from BDFM feed (B train and Franklin Shuttle)
    try:
        bdfm_feed = NYCTFeed("B")
        for trip in bdfm_feed.trips:
            if trip.route_id in ["B", "FS"]:
                for update in trip.stop_time_updates:
                    if update.stop_id in PROSPECT_PARK_STOPS:
                        arrival_time = update.arrival
                        if arrival_time and arrival_time > now:
                            minutes_away = int((arrival_time - now).total_seconds() / 60)
                            route_info = ROUTE_INFO.get(trip.route_id, {"name": trip.route_id, "color": "#999"})

                            entry = {
                                "route": route_info["name"],
                                "color": route_info["color"],
                                "destination": trip.headsign_text or "Unknown",
                                "arrival_time": arrival_time.isoformat(),
                                "minutes_away": max(0, minutes_away),
                            }

                            if update.stop_id.endswith("N"):
                                arrivals["northbound"].append(entry)
                            else:
                                arrivals["southbound"].append(entry)
    except Exception as e:
        print(f"Error fetching BDFM feed: {e}")

    # Fetch from NQRW feed (Q train)
    try:
        nqrw_feed = NYCTFeed("N")
        for trip in nqrw_feed.trips:
            if trip.route_id == "Q":
                for update in trip.stop_time_updates:
                    if update.stop_id in PROSPECT_PARK_STOPS:
                        arrival_time = update.arrival
                        if arrival_time and arrival_time > now:
                            minutes_away = int((arrival_time - now).total_seconds() / 60)
                            route_info = ROUTE_INFO["Q"]

                            entry = {
                                "route": route_info["name"],
                                "color": route_info["color"],
                                "destination": trip.headsign_text or "Unknown",
                                "arrival_time": arrival_time.isoformat(),
                                "minutes_away": max(0, minutes_away),
                            }

                            if update.stop_id.endswith("N"):
                                arrivals["northbound"].append(entry)
                            else:
                                arrivals["southbound"].append(entry)
    except Exception as e:
        print(f"Error fetching NQRW feed: {e}")

    # Sort by arrival time and limit to next 5 per direction
    arrivals["northbound"].sort(key=lambda x: x["minutes_away"])
    arrivals["southbound"].sort(key=lambda x: x["minutes_away"])
    arrivals["northbound"] = arrivals["northbound"][:5]
    arrivals["southbound"] = arrivals["southbound"][:5]

    arrivals["updated_at"] = datetime.now().isoformat()

    return arrivals


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "station": "Prospect Park", "lines": ["B", "Q", "S"]}


@app.get("/arrivals")
def get_prospect_park_arrivals():
    """Get upcoming arrivals at Prospect Park station."""
    return get_arrivals()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
