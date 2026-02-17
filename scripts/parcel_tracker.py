#!/usr/bin/env python3
"""
Parcel Tracker - Universal package tracking with auto carrier detection.
Supports: La Poste/Colissimo, Chronopost, UPS, FedEx, DHL, USPS, Royal Mail, etc.
Uses only standard library (no external dependencies).
"""

import sys
import os
import json
import sqlite3
import re
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

# Database path
DB_PATH = os.path.expanduser("~/.openclaw/workspace/parcel-tracker/data/parcels.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def http_get(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> Optional[Dict]:
    """Make HTTP GET request and return JSON response."""
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = resp.read().decode('utf-8')
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return {"raw": data}
    except Exception as e:
        print(f"HTTP GET error: {e}", file=sys.stderr)
    return None

def http_post(url: str, data: Dict, headers: Optional[Dict] = None, timeout: int = 30) -> Optional[Dict]:
    """Make HTTP POST request with JSON body."""
    try:
        req_headers = headers or {}
        req_headers['Content-Type'] = 'application/json'
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=req_headers, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"HTTP POST error: {e}", file=sys.stderr)
    return None

def init_db():
    """Initialize SQLite database for parcel tracking."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT UNIQUE NOT NULL,
            carrier TEXT,
            carrier_detected TEXT,
            status TEXT,
            last_event TEXT,
            last_update TEXT,
            destination TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            notified_events TEXT DEFAULT '[]'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parcel_id INTEGER,
            timestamp TEXT,
            status TEXT,
            location TEXT,
            description TEXT,
            FOREIGN KEY (parcel_id) REFERENCES parcels(id)
        )
    ''')
    conn.commit()
    conn.close()

def detect_carrier(tracking_number: str) -> Optional[str]:
    """
    Detect carrier from tracking number pattern.
    Returns carrier code or None if unknown.
    """
    tn = tracking_number.upper().replace(" ", "").replace("-", "")
    
    patterns = {
        # La Poste / Colissimo (France)
        "colissimo": [
            r"^\d{11,15}$",  # Standard domestic
            r"^[A-Z]{2}\d{9}[A-Z]{2}$",  # International (CJ, EK, etc.)
            r"^6P\d{9}$",  # Colissimo pickups
        ],
        # Chronopost
        "chronopost": [
            r"^\d{13}$",
            r"^XX\d{9}[A-Z]{2}$",
        ],
        # UPS
        "ups": [
            r"^1Z[A-Z0-9]{16}$",
            r"^\d{12}$",
            r"^T\d{10}$",
        ],
        # FedEx
        "fedex": [
            r"^\d{12}$",
            r"^\d{15}$",
            r"^\d{20}$",
            r"^\d{34}$",
        ],
        # DHL
        "dhl": [
            r"^\d{10}$",
            r"^\d{11}$",
            r"^JJD\d{15,25}$",
            r"^\d{20,25}$",
        ],
        # USPS
        "usps": [
            r"^(94|93|92|94|95)\d{20}$",
            r"^\d{20,22}$",
            r"^[A-Z]{2}\d{9}[A-Z]{2}$",
            r"^EA\d{9}[A-Z]{2}$",
        ],
        # Royal Mail
        "royalmail": [
            r"^[A-Z]{2}\d{9}GB$",
            r"^\d{13}$",
        ],
        # DPD
        "dpd": [
            r"^\d{14}$",
            r"^\d{18}$",
        ],
        # GLS
        "gls": [
            r"^\d{11,12}$",
            r"^\d{20}$",
        ],
        # Hermes/Evri (UK)
        "evri": [
            r"^\d{16}$",
        ],
        # Mondial Relay
        "mondialrelay": [
            r"^\d{8}$",
        ],
        # InPost
        "inpost": [
            r"^\d{24}$",
        ],
        # Amazon Logistics
        "amazon": [
            r"^TBA\d{12}$",
            r"^TBC\d{12}$",
            r"^TBM\d{12}$",
        ],
        # Cainiao / AliExpress (China)
        "cainiao": [
            r"^CN[A-Z]{2}\d{9,15}[A-Z]{2}$",  # CNFR...HD format
            r"^LP\d{14}$",  # AliExpress standard
            r"^\d{14}$",  # Chinese domestic
        ],
        # Yanwen (Chinese carrier)
        "yanwen": [
            r"^\d{12,14}$",  # Standard Yanwen
            r"^YT\d{16}$",  # YT prefix
            r"^UF\d{14}$",  # UF prefix
        ],
        # Sunyou (Chinese carrier)
        "sunyou": [
            r"^SY\d{10,14}$",
            r"^\d{11}Y$",
        ],
        # 4PX (Chinese logistics)
        "4px": [
            r"^\d{12,15}$",
            r"^LX\d{12}CN$",
        ],
    }
    
    for carrier, regexes in patterns.items():
        for pattern in regexes:
            if re.match(pattern, tn):
                return carrier
    
    return None

def get_carrier_display_name(carrier_code: str) -> str:
    """Get human-readable carrier name."""
    names = {
        "colissimo": "La Poste / Colissimo",
        "chronopost": "Chronopost",
        "ups": "UPS",
        "fedex": "FedEx",
        "dhl": "DHL",
        "usps": "USPS",
        "royalmail": "Royal Mail",
        "dpd": "DPD",
        "gls": "GLS",
        "evri": "Evri",
        "mondialrelay": "Mondial Relay",
        "inpost": "InPost",
        "amazon": "Amazon Logistics",
        "cainiao": "Cainiao / AliExpress",
        "yanwen": "Yanwen",
        "sunyou": "Sunyou",
        "4px": "4PX",
    }
    return names.get(carrier_code, carrier_code.upper())

def track_with_tracktry(tracking_number: str, carrier: Optional[str] = None) -> Optional[Dict]:
    """
    Track using Tracktry API (free tier: 100 requests/day).
    Sign up at https://www.tracktry.com
    """
    api_key = os.environ.get("TRACKTRY_API_KEY")
    if not api_key:
        return None
    
    url = f"https://api.tracktry.com/v1/trackings/{tracking_number}"
    headers = {"Tracktry-Api-Key": api_key}
    
    try:
        data = http_get(url, headers)
        if data and data.get("code") == 200:
            result = data.get("data", {})
            events = result.get("origin_info", {}).get("trackinfo", [])
            return {
                "carrier": result.get("carrier_code", carrier),
                "status": result.get("status_description"),
                "events": [
                    {
                        "date": e.get("Date"),
                        "status": e.get("StatusDescription"),
                        "location": e.get("Details", ""),
                        "description": e.get("checkpoint_status"),
                    }
                    for e in events
                ],
            }
    except Exception as e:
        print(f"Tracktry error: {e}", file=sys.stderr)
    
    return None

def format_timestamp(ts) -> str:
    """Convert timestamp to readable format."""
    if not ts:
        return ""
    try:
        # Handle milliseconds timestamp
        if isinstance(ts, (int, float)) and ts > 1000000000000:
            ts = ts / 1000
        dt = datetime.fromtimestamp(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(ts)

def track_cainiao(tracking_number: str) -> Optional[Dict]:
    """
    Track Cainiao/AliExpress parcels using the public Cainiao API.
    No API key required.
    """
    url = f"https://global.cainiao.com/global/detail.json?mailNos={tracking_number}&lang=en-US"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
        }
        data = http_get(url, headers)
        
        if data and data.get("success"):
            module = data.get("module", [])
            if module and len(module) > 0:
                detail = module[0]
                events = detail.get("detailList", [])
                
                return {
                    "carrier": "cainiao",
                    "status": detail.get("statusDesc"),
                    "events": [
                        {
                            "date": format_timestamp(e.get("time")),
                            "status": e.get("status"),
                            "location": e.get("place", ""),
                            "description": e.get("desc"),
                        }
                        for e in events
                    ],
                }
    except Exception as e:
        print(f"Cainiao error: {e}", file=sys.stderr)
    
    return None

def track_yanwen(tracking_number: str) -> Optional[Dict]:
    """
    Track Yanwen parcels using their public tracking page.
    """
    # Yanwen uses a simple tracking endpoint
    url = f"http://www.yw56.com.cn/english/select-e.asp?wen={tracking_number}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Basic parsing - look for tracking info in the HTML
            if "Destination Country" in html or "Origin Country" in html:
                # Simple heuristic extraction
                return {
                    "carrier": "yanwen",
                    "status": "Tracked (see yanwen website for details)",
                    "events": [{"date": "", "status": "Parcel found", "location": "", "description": f"Check {url} for full details"}],
                }
    except Exception as e:
        print(f"Yanwen error: {e}", file=sys.stderr)
    
    return None

def track_with_17track(tracking_number: str, carrier: Optional[str] = None) -> Optional[Dict]:
    """
    Track parcel using 17Track API (free tier available).
    Requires 17TRACK_API_KEY environment variable.
    """
    api_key = os.environ.get("17TRACK_API_KEY")
    if not api_key:
        return None
    
    url = "https://api.17track.net/track/v2.2/gettrackinfo"
    headers = {"17token": api_key}
    payload = {"number": tracking_number}
    
    try:
        data = http_post(url, payload, headers)
        if data and data.get("code") == 0 and data.get("data"):
            track_info = data["data"][0]
            providers = track_info.get("track_info", {}).get("tracking", {}).get("providers", [{}])
            events = providers[0].get("events", []) if providers else []
            
            return {
                "carrier": track_info.get("carrier", carrier),
                "status": track_info.get("track_info", {}).get("status_description"),
                "events": [
                    {
                        "date": e.get("time_iso"),
                        "status": e.get("status"),
                        "location": e.get("location"),
                        "description": e.get("description"),
                    }
                    for e in events
                ],
            }
    except Exception as e:
        print(f"17Track error: {e}", file=sys.stderr)
    
    return None

def track_colissimo(tracking_number: str) -> Optional[Dict]:
    """
    Track Colissimo/La Poste using the official API.
    No API key required for basic tracking.
    """
    url = f"https://www.laposte.fr/ssu/sun/suivi-unifie/{tracking_number}?lang=fr_FR"
    
    try:
        data = http_get(url)
        if data and "shipment" in data:
            shipment = data.get("shipment", {})
            events = shipment.get("event", [])
            
            return {
                "carrier": "colissimo",
                "status": events[0].get("label") if events else "Unknown",
                "events": [
                    {
                        "date": e.get("date"),
                        "status": e.get("label"),
                        "location": f"{e.get('siteName', '')}, {e.get('country', '')}".strip(", "),
                        "description": e.get("label"),
                    }
                    for e in events
                ],
            }
    except Exception as e:
        print(f"Colissimo error: {e}", file=sys.stderr)
    
    return None

def track_chronopost(tracking_number: str) -> Optional[Dict]:
    """Track Chronopost parcel."""
    url = f"https://www.chronopost.fr/tracking-cxf/tracking-cxf/getTrack?number={tracking_number}"
    
    try:
        data = http_get(url)
        if data and "list" in data:
            events = data.get("list", [])
            
            return {
                "carrier": "chronopost",
                "status": events[0].get("label") if events else "Unknown",
                "events": [
                    {
                        "date": e.get("eventDate"),
                        "status": e.get("label"),
                        "location": e.get("city", ""),
                        "description": e.get("label"),
                    }
                    for e in events
                ],
            }
    except Exception as e:
        print(f"Chronopost error: {e}", file=sys.stderr)
    
    return None

def track_parcel(tracking_number: str, carrier_hint: Optional[str] = None) -> Optional[Dict]:
    """
    Track a parcel using the best available method.
    Auto-detects carrier if not provided.
    Tries free APIs first, no paid APIs required.
    """
    detected = carrier_hint or detect_carrier(tracking_number)
    
    # Try carrier-specific free APIs first
    trackers = {
        "colissimo": track_colissimo,
        "chronopost": track_chronopost,
        "cainiao": track_cainiao,
        "yanwen": track_yanwen,
    }
    
    if detected and detected in trackers:
        result = trackers[detected](tracking_number)
        if result:
            result["carrier_detected"] = detected
            return result
    
    # Try free universal trackers (Tracktry has free tier)
    result = track_with_tracktry(tracking_number, detected)
    if result:
        return result
    
    # Try Cainiao as universal fallback (works for many Chinese carriers)
    result = track_cainiao(tracking_number)
    if result:
        return result
    
    # Last resort: 17Track (if user has API key)
    result = track_with_17track(tracking_number, detected)
    if result:
        return result
    
    return None

def add_parcel(tracking_number: str) -> Tuple[bool, str]:
    """Add a new parcel to tracking."""
    init_db()
    
    carrier = detect_carrier(tracking_number)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO parcels (tracking_number, carrier_detected, status)
            VALUES (?, ?, ?)
        ''', (tracking_number, carrier, "Added - pending first check"))
        conn.commit()
        
        carrier_name = get_carrier_display_name(carrier) if carrier else "Unknown"
        return True, f"Added {tracking_number} ({carrier_name})"
    except sqlite3.IntegrityError:
        return False, f"Parcel {tracking_number} is already being tracked"
    finally:
        conn.close()

def remove_parcel(tracking_number: str) -> Tuple[bool, str]:
    """Remove a parcel from tracking."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM parcels WHERE tracking_number = ?', (tracking_number,))
    if c.rowcount > 0:
        conn.commit()
        conn.close()
        return True, f"Removed {tracking_number}"
    else:
        conn.close()
        return False, f"Parcel {tracking_number} not found"

def list_parcels() -> List[Dict]:
    """List all tracked parcels."""
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT tracking_number, carrier_detected, status, last_event, last_update, destination
        FROM parcels ORDER BY created_at DESC
    ''')
    
    parcels = []
    for row in c.fetchall():
        parcels.append({
            "tracking_number": row[0],
            "carrier": row[1],
            "status": row[2],
            "last_event": row[3],
            "last_update": row[4],
            "destination": row[5],
        })
    
    conn.close()
    return parcels

def check_updates(notify: bool = True) -> List[Dict]:
    """
    Check all parcels for updates.
    Returns list of parcels with new events.
    """
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, tracking_number, carrier_detected, notified_events FROM parcels')
    
    updates = []
    
    for row in c.fetchall():
        parcel_id, tracking_number, carrier, notified_json = row
        notified = json.loads(notified_json or "[]")
        
        result = track_parcel(tracking_number, carrier)
        
        if result and result.get("events"):
            latest = result["events"][0]
            event_key = f"{latest.get('date')}_{latest.get('status')}"
            
            if event_key not in notified:
                # New event!
                updates.append({
                    "parcel_id": parcel_id,
                    "tracking_number": tracking_number,
                    "carrier": result.get("carrier", carrier),
                    "status": result.get("status"),
                    "event": latest,
                })
                
                # Update database
                notified.append(event_key)
                c.execute('''
                    UPDATE parcels 
                    SET status = ?, last_event = ?, last_update = ?, notified_events = ?
                    WHERE id = ?
                ''', (
                    result.get("status"),
                    latest.get("description"),
                    latest.get("date"),
                    json.dumps(notified),
                    parcel_id
                ))
                
                # Store event in history
                c.execute('''
                    INSERT INTO events (parcel_id, timestamp, status, location, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    parcel_id,
                    latest.get("date"),
                    latest.get("status"),
                    latest.get("location"),
                    latest.get("description"),
                ))
    
    conn.commit()
    conn.close()
    
    return updates

def main():
    if len(sys.argv) < 2:
        print("Usage: parcel_tracker.py <command> [args]")
        print("")
        print("Commands:")
        print("  add <tracking_number>     Add a parcel to track")
        print("  remove <tracking_number>  Remove a parcel")
        print("  list                      List all tracked parcels")
        print("  check                     Check for updates")
        print("  detect <tracking_number>  Detect carrier from tracking number")
        print("")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: parcel_tracker.py add <tracking_number>")
            sys.exit(1)
        success, msg = add_parcel(sys.argv[2])
        print(msg)
        sys.exit(0 if success else 1)
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Usage: parcel_tracker.py remove <tracking_number>")
            sys.exit(1)
        success, msg = remove_parcel(sys.argv[2])
        print(msg)
        sys.exit(0 if success else 1)
    
    elif command == "list":
        parcels = list_parcels()
        if not parcels:
            print("No parcels being tracked")
        else:
            print(f"{'Tracking #':<20} {'Carrier':<20} {'Status':<30} {'Last Update'}")
            print("-" * 90)
            for p in parcels:
                carrier = get_carrier_display_name(p["carrier"]) if p["carrier"] else "Unknown"
                status = (p["status"] or "Pending")[:28]
                last = p["last_update"] or "Never"
                print(f"{p['tracking_number']:<20} {carrier:<20} {status:<30} {last}")
        sys.exit(0)
    
    elif command == "check":
        updates = check_updates()
        if updates:
            print(f"Found {len(updates)} update(s):")
            for u in updates:
                carrier = get_carrier_display_name(u["carrier"]) if u["carrier"] else "Unknown"
                print(f"\n📦 {u['tracking_number']} ({carrier})")
                print(f"   Status: {u['status']}")
                print(f"   Event: {u['event'].get('description')}")
                print(f"   Location: {u['event'].get('location', 'N/A')}")
                print(f"   Time: {u['event'].get('date')}")
        else:
            print("No new updates")
        sys.exit(0)
    
    elif command == "detect":
        if len(sys.argv) < 3:
            print("Usage: parcel_tracker.py detect <tracking_number>")
            sys.exit(1)
        carrier = detect_carrier(sys.argv[2])
        if carrier:
            print(f"Detected carrier: {get_carrier_display_name(carrier)} ({carrier})")
        else:
            print("Could not detect carrier from tracking number pattern")
            print("Will try universal tracking APIs when checking")
        sys.exit(0)
    
    elif command == "track":
        if len(sys.argv) < 3:
            print("Usage: parcel_tracker.py track <tracking_number>")
            sys.exit(1)
        result = track_parcel(sys.argv[2])
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Could not track parcel")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
