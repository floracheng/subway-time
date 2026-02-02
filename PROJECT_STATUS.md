# Subway Time Display - Project Status

## Overview
A real-time MTA subway arrival display for Prospect Park station (Brooklyn), optimized for an iPad mounted near the door.

## Live URL
Deployed on Netlify (auto-deploys from GitHub)

## Features

### Current Functionality
- **Real-time arrivals** for B, Q, and Franklin Ave Shuttle (S) trains
- **Two directions**: Manhattan-bound and Brooklyn-bound (Coney Island)
- **Frontend-only** - no backend server required
- **Direct MTA feed access** using protobuf.js to parse GTFS-RT data
- **Auto-refresh** every 30 seconds
- **Wake refresh** - updates when iPad screen wakes from sleep
- **Responsive design** - scales to fill iPad screen in landscape mode
- **Smart visibility** - hides lines with no service (e.g., B train on weekends)
- **Analytics** - GoatCounter for privacy-friendly page view tracking

### Data Sources
- **BDFM Feed**: B trains and Franklin Shuttle (FS)
- **NQRW Feed**: Q trains
- **Station ID**: D26N (northbound), D26S (southbound) - shared platform for all lines

## Technical Implementation

### Stack
- Single HTML file with embedded CSS and JavaScript
- protobuf.js (CDN) for parsing MTA GTFS-RT protocol buffers
- No build step, no dependencies to install

### Key Files
- `index.html` - The complete application

### MTA Feed URLs (no API key required)
```
BDFM: https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm
NQRW: https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw
```

## Design Decisions

### Layout
- Subtle "Prospect Park" title at top with separator line
- 3 rows maximum: Manhattan, Brooklyn, Franklin Ave
- B and Q trains combined per direction, sorted by arrival time
- Up to 3 upcoming trains shown per row
- Direction labels on left, arrivals on right with line badges

### Sizing (viewport-relative for responsiveness)
- Times: 8vw
- Line badges: 7vw
- Direction labels: 2.5vw

### Colors
- Title: #aaa (subtle)
- Direction labels: #666
- Times: #222
- Updated timestamp: #999
- B train badge: #FF6319 (orange)
- Q train badge: #FCCC0A (yellow)
- S train badge: #808183 (gray)

## iPad Setup

1. Open the Netlify URL in Safari
2. Tap Share → "Add to Home Screen" (full-screen, app-like)
3. Use landscape orientation for best readability
4. Settings recommendations:
   - Auto-Lock: Never
   - Guided Access: Enable to lock to this app
   - Keep iPad plugged in

## Development History

1. **Initial version**: Python backend (FastAPI) + frontend calling API
2. **Iteration**: Added service alerts support (later removed - too noisy)
3. **Simplification**: Moved to frontend-only using protobuf.js
4. **Refinement**: Fixed timing differences (Math.floor vs Math.round)
5. **iPad optimization**:
   - Combined B/Q into single rows
   - Responsive viewport-based sizing
   - Fixed iOS rotation zoom issue
   - Increased text sizes for readability
6. **Polish**:
   - Added subtle "Prospect Park" title for sharing with neighbors
   - Added GoatCounter analytics

## Removed/Deprecated
- `main.py` - Python backend (no longer needed)
- `requirements.txt` - Python dependencies (no longer needed)
- `mta-display-browser.html` - Proof of concept (merged into index.html)
- Service alerts feature - Showed misleading info for non-running trains

## Repository
https://github.com/floracheng/subway-time
