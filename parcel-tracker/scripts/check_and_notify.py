#!/usr/bin/env python3
"""
Check parcels for updates and send notifications.
Called by cron job.
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parcel_tracker import check_updates, get_carrier_display_name

def main():
    """Check for updates and format output for notification."""
    updates = check_updates()
    
    if not updates:
        print("No updates")
        return 0
    
    # Output formatted for parsing by the caller
    for u in updates:
        carrier = get_carrier_display_name(u["carrier"]) if u["carrier"] else "Unknown"
        print(f"UPDATE:{u['tracking_number']}|{carrier}|{u['status']}|{u['event'].get('description', 'N/A')}")
    
    # Return 0 for success, even if updates found
    return 0

if __name__ == "__main__":
    sys.exit(main())
