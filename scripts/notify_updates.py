#!/usr/bin/env python3
"""
Notification script for parcel-tracker.
Sends formatted updates via OpenClaw messaging.
"""

import subprocess
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parcel_tracker import check_updates, get_carrier_display_name

def main():
    """Check for updates and notify if any found."""
    updates = check_updates()
    
    if not updates:
        print("No updates to notify")
        return
    
    # Build notification message
    if len(updates) == 1:
        u = updates[0]
        carrier = get_carrier_display_name(u["carrier"]) if u["carrier"] else "Unknown"
        msg = f"📦 Tracking Update\n\n"
        msg += f"{u['tracking_number']} ({carrier})\n"
        msg += f"Status: {u['status']}\n"
        msg += f"Event: {u['event'].get('description', 'N/A')}\n"
        if u['event'].get('location'):
            msg += f"Location: {u['event']['location']}\n"
        if u['event'].get('date'):
            msg += f"Time: {u['event']['date']}\n"
    else:
        msg = f"📦 {len(updates)} Tracking Updates\n\n"
        for u in updates:
            carrier = get_carrier_display_name(u["carrier"]) if u["carrier"] else "Unknown"
            msg += f"• {u['tracking_number']} ({carrier}): {u['status']}\n"
    
    # Send via openclaw message
    # This will use the configured channel
    result = subprocess.run(
        ["openclaw", "message", "send", "--message", msg],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"Notified {len(updates)} update(s)")
    else:
        print(f"Failed to send notification: {result.stderr}", file=sys.stderr)
        # Print to stdout as fallback
        print("\n" + "="*50)
        print(msg)
        print("="*50)

if __name__ == "__main__":
    main()
