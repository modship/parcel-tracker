#!/usr/bin/env python3
"""
Check parcels for updates and send notifications via OpenClaw channels.
Called by cron job or manually.
"""
import sys
import os
import subprocess

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parcel_tracker import check_updates, get_carrier_display_name

def send_openclaw_message(message):
    """Send notification via OpenClaw messaging channels."""
    try:
        result = subprocess.run(
            ["openclaw", "message", "send", "--message", message],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to send notification: {e}", file=sys.stderr)
        return False

def main():
    """Check for updates and send OpenClaw notifications."""
    updates = check_updates()
    
    if not updates:
        print("No updates to notify")
        return 0
    
    # Send one consolidated message if multiple updates
    if len(updates) == 1:
        u = updates[0]
        carrier = get_carrier_display_name(u["carrier"]) if u["carrier"] else "Unknown"
        alias_str = f" [{u['alias']}]" if u.get("alias") else ""
        
        message = f"📦 Parcel Update\n\n"
        message += f"{u['tracking_number']}{alias_str}\n"
        message += f"Carrier: {carrier}\n"
        message += f"Status: {u['status']}\n"
        if u['event'].get('description'):
            message += f"Event: {u['event']['description']}\n"
        if u['event'].get('location'):
            message += f"Location: {u['event']['location']}\n"
        if u['event'].get('date'):
            message += f"Time: {u['event']['date']}"
        
        success = send_openclaw_message(message)
    else:
        # Multiple updates - send summary
        message = f"📦 {len(updates)} Parcel Updates\n\n"
        for u in updates:
            carrier = get_carrier_display_name(u["carrier"]) if u["carrier"] else "Unknown"
            alias_str = f" [{u['alias']}]" if u.get("alias") else ""
            message += f"• {u['tracking_number']}{alias_str} ({carrier}): {u['status']}\n"
        
        success = send_openclaw_message(message)
    
    if success:
        print(f"Sent {len(updates)} notification(s) via OpenClaw")
        return 0
    else:
        # Fallback to stdout if OpenClaw fails
        print("OpenClaw messaging failed, printing to stdout:")
        for u in updates:
            carrier = get_carrier_display_name(u["carrier"]) if u["carrier"] else "Unknown"
            alias_str = f" [{u['alias']}]" if u.get("alias") else ""
            print(f"📦 {u['tracking_number']}{alias_str} ({carrier}): {u['status']}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
