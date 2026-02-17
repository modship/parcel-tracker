#!/usr/bin/env python3
"""
Parcel Tracker Web Interface
Lightweight web UI for managing parcels
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parcel_tracker import (
    init_db, add_parcel, remove_parcel, list_parcels, 
    check_updates, track_parcel, get_carrier_display_name, DB_PATH
)
import sqlite3
import json
from urllib.parse import parse_qs

# Simple HTTP server with HTML generation
def generate_html(title, content):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Parcel Tracker</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        header h1 {{ margin-bottom: 10px; font-size: 2em; }}
        header p {{ opacity: 0.9; }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h2 {{ 
            margin-bottom: 20px; 
            color: #667eea;
            font-size: 1.3em;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        form {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: end; }}
        .form-group {{ flex: 1; min-width: 200px; }}
        label {{ display: block; margin-bottom: 5px; font-weight: 500; color: #555; }}
        input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}
        input[type="text"]:focus {{
            outline: none;
            border-color: #667eea;
        }}
        button {{
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }}
        button:hover {{ background: #5a6fd6; transform: translateY(-1px); }}
        button.secondary {{ background: #48bb78; }}
        button.secondary:hover {{ background: #38a169; }}
        button.danger {{ background: #f56565; }}
        button.danger:hover {{ background: #e53e3e; }}
        .parcel-list {{ list-style: none; }}
        .parcel-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s;
        }}
        .parcel-item:hover {{ background: #f9f9f9; }}
        .parcel-item:last-child {{ border-bottom: none; }}
        .parcel-info {{ flex: 1; }}
        .parcel-alias {{
            font-weight: 600;
            color: #667eea;
            font-size: 1.1em;
        }}
        .parcel-number {{ 
            font-family: monospace; 
            color: #666; 
            font-size: 0.9em;
            margin-top: 3px;
        }}
        .parcel-carrier {{
            display: inline-block;
            background: #edf2f7;
            color: #4a5568;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-top: 5px;
        }}
        .parcel-status {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            margin-right: 10px;
        }}
        .status-delivered {{ background: #c6f6d5; color: #22543d; }}
        .status-delivering {{ background: #bee3f8; color: #2a4365; }}
        .status-transit {{ background: #fefcbf; color: #744210; }}
        .status-pending {{ background: #e2e8f0; color: #2d3748; }}
        .status-exception {{ background: #fed7d7; color: #742a2a; }}
        .parcel-actions {{ display: flex; gap: 5px; }}
        .parcel-actions button {{ padding: 8px 16px; font-size: 12px; }}
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #718096;
        }}
        .empty-state svg {{ 
            width: 80px; 
            height: 80px; 
            margin-bottom: 20px;
            opacity: 0.5;
        }}
        .actions-bar {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            margin-left: 5px;
        }}
        .message {{
            padding: 12px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .message.success {{ background: #c6f6d5; color: #22543d; }}
        .message.error {{ background: #fed7d7; color: #742a2a; }}
        .event-list {{
            list-style: none;
            margin-top: 15px;
        }}
        .event-item {{
            padding: 10px;
            border-left: 3px solid #667eea;
            margin-bottom: 10px;
            background: #f7fafc;
            border-radius: 0 6px 6px 0;
        }}
        .event-date {{ font-size: 0.85em; color: #718096; }}
        .event-desc {{ font-weight: 500; }}
        .event-location {{ font-size: 0.9em; color: #4a5568; }}
        @media (max-width: 600px) {{
            .parcel-item {{ flex-direction: column; align-items: flex-start; }}
            .parcel-actions {{ margin-top: 10px; width: 100%; justify-content: flex-end; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📦 Parcel Tracker</h1>
            <p>Suivi de colis universel avec détection automatique des transporteurs</p>
        </header>
        {content}
    </div>
</body>
</html>"""

def get_status_class(status):
    """Get CSS class based on status."""
    if not status:
        return "status-pending"
    status_lower = status.lower()
    if "delivered" in status_lower or "livré" in status_lower:
        return "status-delivered"
    elif "delivering" in status_lower or "distribution" in status_lower:
        return "status-delivering"
    elif "transit" in status_lower or "en cours" in status_lower:
        return "status-transit"
    elif "exception" in status_lower or "error" in status_lower:
        return "status-exception"
    return "status-pending"

def handle_request(method, path, query_string, body):
    """Handle HTTP requests and return HTML response."""
    message = ""
    
    # Parse query string
    params = parse_qs(query_string) if query_string else {}
    
    # Parse POST body
    if method == "POST" and body:
        try:
            post_data = parse_qs(body.decode('utf-8'))
        except:
            post_data = {}
    else:
        post_data = {}
    
    # Route handling
    if path == "/" or path == "/list":
        return handle_list(params, message)
    elif path == "/add":
        if method == "POST":
            tracking_number = post_data.get("tracking_number", [""])[0].strip()
            alias = post_data.get("alias", [""])[0].strip()
            if tracking_number:
                success, msg = add_parcel(tracking_number, alias if alias else None)
                message = f"<div class='message {'success' if success else 'error'}'>{msg}</div>"
            else:
                message = "<div class='message error'>Please enter a tracking number</div>"
        return handle_list(params, message)
    elif path.startswith("/remove/"):
        tracking_number = path.replace("/remove/", "")
        if tracking_number:
            success, msg = remove_parcel(tracking_number)
            message = f"<div class='message {'success' if success else 'error'}'>{msg}</div>"
        return handle_list(params, message)
    elif path == "/check":
        updates = check_updates()
        if updates:
            message = f"<div class='message success'>Found {len(updates)} update(s)!</div>"
        else:
            message = "<div class='message'>No new updates</div>"
        return handle_list(params, message)
    elif path.startswith("/track/"):
        tracking_number = path.replace("/track/", "")
        return handle_track(tracking_number)
    else:
        return handle_list(params, "")

def handle_list(params, message):
    """Display list of parcels."""
    parcels = list_parcels()
    
    # Build parcel list HTML
    if parcels:
        parcel_html = '<ul class="parcel-list">'
        for p in parcels:
            carrier = get_carrier_display_name(p["carrier"]) if p["carrier"] else "Unknown"
            alias_display = p["alias"] if p["alias"] else "Untitled"
            status_class = get_status_class(p["status"])
            status_display = p["status"] if p["status"] else "Pending"
            last_update = p["last_update"] if p["last_update"] else "Never"
            
            parcel_html += f'''
            <li class="parcel-item">
                <div class="parcel-info">
                    <div class="parcel-alias">{alias_display}</div>
                    <div class="parcel-number">{p["tracking_number"]}</div>
                    <span class="parcel-carrier">{carrier}</span>
                </div>
                <div>
                    <span class="parcel-status {status_class}">{status_display}</span>
                </div>
                <div class="parcel-actions">
                    <button onclick="location.href='/track/{p["tracking_number"]}'" class="secondary">Details</button>
                    <button onclick="if(confirm('Remove this parcel?')) location.href='/remove/{p["tracking_number"]}'" class="danger">Remove</button>
                </div>
            </li>
            '''
        parcel_html += '</ul>'
    else:
        parcel_html = '''
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            </svg>
            <p>No parcels being tracked yet.</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Add your first parcel below!</p>
        </div>
        '''
    
    content = f'''
    {message}
    <div class="card">
        <h2>Add New Parcel</h2>
        <form method="POST" action="/add">
            <div class="form-group">
                <label for="tracking_number">Tracking Number</label>
                <input type="text" id="tracking_number" name="tracking_number" placeholder="e.g., CNFR9010481599571HD" required>
            </div>
            <div class="form-group">
                <label for="alias">Alias (optional)</label>
                <input type="text" id="alias" name="alias" placeholder="e.g., Chargeur USB">
            </div>
            <button type="submit">Add Parcel</button>
        </form>
    </div>
    
    <div class="actions-bar">
        <button onclick="location.href='/check'" class="secondary">🔄 Check for Updates</button>
        <button onclick="location.href='/list'">📋 Refresh List</button>
    </div>
    
    <div class="card">
        <h2>Tracked Parcels <span class="badge">{len(parcels)}</span></h2>
        {parcel_html}
    </div>
    '''
    
    return generate_html("Dashboard", content)

def handle_track(tracking_number):
    """Display detailed tracking information for a parcel."""
    result = track_parcel(tracking_number)
    
    if not result:
        content = f'''
        <div class="card">
            <h2>Tracking Details</h2>
            <div class="message error">Could not track parcel: {tracking_number}</div>
            <button onclick="location.href='/list'">← Back to List</button>
        </div>
        '''
        return generate_html("Tracking Details", content)
    
    carrier = get_carrier_display_name(result.get("carrier", "Unknown"))
    status = result.get("status", "Unknown")
    events = result.get("events", [])
    
    events_html = ""
    if events:
        events_html = '<ul class="event-list">'
        for event in events:
            date = event.get("date", "N/A")
            desc = event.get("description", event.get("status", "No description"))
            location = event.get("location", "")
            location_str = f'<div class="event-location">📍 {location}</div>' if location else ""
            events_html += f'''
            <li class="event-item">
                <div class="event-date">{date}</div>
                <div class="event-desc">{desc}</div>
                {location_str}
            </li>
            '''
        events_html += '</ul>'
    else:
        events_html = '<p style="color: #718096; padding: 20px;">No tracking events available.</p>'
    
    content = f'''
    <div class="card">
        <h2>📦 Tracking Details</h2>
        <p style="margin-bottom: 20px;">
            <strong>Tracking Number:</strong> <code>{tracking_number}</code><br>
            <strong>Carrier:</strong> {carrier}<br>
            <strong>Status:</strong> <span class="parcel-status {get_status_class(status)}">{status}</span>
        </p>
        
        <h3 style="margin-top: 30px; margin-bottom: 15px;">📜 Event History</h3>
        {events_html}
        
        <div style="margin-top: 30px;">
            <button onclick="location.href='/list'">← Back to List</button>
        </div>
    </div>
    '''
    
    return generate_html(f"Track {tracking_number}", content)

# HTTP Server
from http.server import HTTPServer, BaseHTTPRequestHandler

class ParcelHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_GET(self):
        path = self.path.split("?")[0]
        query = self.path.split("?")[1] if "?" in self.path else ""
        
        html = handle_request("GET", path, query, None)
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
    
    def do_POST(self):
        path = self.path.split("?")[0]
        query = self.path.split("?")[1] if "?" in self.path else ""
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        html = handle_request("POST", path, query, body)
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

def main():
    """Start the web server."""
    init_db()
    
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    server = HTTPServer((host, port), ParcelHandler)
    print(f"🚀 Parcel Tracker Web Interface")
    print(f"📍 http://localhost:{port}")
    print(f"📍 http://{host}:{port}")
    print(f"\nPress Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
