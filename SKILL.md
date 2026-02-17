---
name: parcel-tracker
description: Universal parcel/package tracking with automatic carrier detection. Use when the user wants to track shipments, add tracking numbers, check delivery status, or set up automatic tracking notifications. Triggers include phrases like "track package", "add tracking number", "check my parcel", "where is my order", "track my order", "list my parcels", "check tracking updates". Supports La Poste/Colissimo, Chronopost, Cainiao/AliExpress, UPS, FedEx, DHL, USPS, Royal Mail, DPD, GLS, Yanwen, and more. Uses FREE APIs only - no paid APIs required.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "install": [],
      },
  }
---

# Parcel Tracker

Track packages automatically with smart carrier detection and notifications. **100% free** - uses public APIs and free tiers only.

## Quick Start

```bash
# Add a parcel to track
python3 parcel-tracker/scripts/parcel_tracker.py add <tracking_number>

# Check all parcels for updates
python3 parcel-tracker/scripts/parcel_tracker.py check

# List tracked parcels
python3 parcel-tracker/scripts/parcel_tracker.py list

# Detect carrier from tracking number
python3 parcel-tracker/scripts/parcel_tracker.py detect <tracking_number>
```

## Supported Carriers (FREE APIs)

| Carrier | Detection | Tracking | Type |
|---------|-----------|----------|------|
| **La Poste / Colissimo** | ✅ | ✅ | Official API (free) |
| **Chronopost** | ✅ | ✅ | Official API (free) |
| **Cainiao / AliExpress** | ✅ | ✅ | Public API (free) |
| **GLS** | ✅ | ✅ | Official API (free) |
| **DPD** | ✅ | ✅ | Official API (free) |
| **Yanwen** | ✅ | 🟡 | Web tracking |
| **Sunyou** | ✅ | 🟡 | Web tracking |
| **4PX** | ✅ | 🟡 | Web tracking |
| **UPS** | ✅ | 🔴 | Pattern only |
| **FedEx** | ✅ | 🔴 | Pattern only |
| **DHL** | ✅ | 🔴 | Pattern only |
| **USPS** | ✅ | 🔴 | Pattern only |
| **Royal Mail** | ✅ | 🔴 | Pattern only |
| **Evri (Hermes)** | ✅ | 🔴 | Pattern only |
| **Mondial Relay** | ✅ | 🔴 | Pattern only |
| **InPost** | ✅ | 🔴 | Pattern only |
| **Amazon Logistics** | ✅ | 🔴 | Pattern only |

✅ = Full support | 🟡 = Basic support | 🔴 = Detection only (need API key for tracking)

## Web Interface

A built-in web interface is available for easy management:

```bash
# Start the web server
python3 parcel-tracker/scripts/web_app.py

# Access at http://localhost:8080
```

Features:
- 📋 View all tracked parcels with status
- ➕ Add new parcels with aliases
- 🗑️ Remove parcels
- 🔄 Check for updates with one click
- 📜 View detailed tracking history
- 📱 Responsive design (works on mobile)

### Custom Port
```bash
PORT=3000 python3 parcel-tracker/scripts/web_app.py
```

## API Keys (Optional)

The tracker works **without any API keys** for French and Chinese carriers. For other carriers, you can optionally add:

```bash
# Tracktry - 100 free requests/day (optional)
export TRACKTRY_API_KEY="your_api_key"

# 17Track - 100 free tracks/day (optional)  
export 17TRACK_API_KEY="your_api_key"
```

Get free API keys:
- [Tracktry](https://www.tracktry.com) - 100 requests/day free
- [17Track](https://www.17track.net/en/api) - 100 tracks/day free

## Automatic Notifications

Notifications are sent via **OpenClaw channels** (Telegram, WhatsApp, Signal, etc.) when parcel updates are detected.

### System Cron (Recommended)

```bash
# Edit crontab
crontab -e

# Add this line to check every 2 hours
0 */2 * * * cd ~/.openclaw/workspace && python3 parcel-tracker/scripts/check_and_notify.py >> ~/.openclaw/workspace/parcel-tracker/data/cron.log 2>&1
```

### OpenClaw Cron (When Gateway Connected)

```bash
openclaw cron add --name parcel-tracker --schedule "every 2 hours" \
  --command "cd ~/.openclaw/workspace && python3 parcel-tracker/scripts/check_and_notify.py"
```

**Note:** Notifications require a connected OpenClaw Gateway with configured channels (Telegram, WhatsApp, etc.)

## Commands

| Command | Description |
|---------|-------------|
| `add <tracking_number> [alias]` | Add a new parcel to tracking (with optional alias) |
| `remove <tracking_number>` | Remove a parcel from tracking |
| `list` | Show all tracked parcels with status and aliases |
| `check` | Check all parcels for new events |
| `detect <tracking_number>` | Detect carrier from tracking number |
| `track <tracking_number>` | One-time track (returns JSON) |

## Example Session

```bash
# Add an AliExpress order with alias
$ python3 parcel-tracker/scripts/parcel_tracker.py add "CNFR9010481599571HD" "USB Charger"
Added CNFR9010481599571HD [USB Charger] (Cainiao / AliExpress)

# Add a GLS parcel
$ python3 parcel-tracker/scripts/parcel_tracker.py add "12345678901" "Book"
Added 12345678901 [Book] (GLS)

# Add a DPD parcel
$ python3 parcel-tracker/scripts/parcel_tracker.py add "12345678901234" "Gift"
Added 12345678901234 [Gift] (DPD)

# Check for updates (uses free APIs)
$ python3 parcel-tracker/scripts/parcel_tracker.py check
Found 1 update(s):

📦 CNFR9010481599571HD [USB Charger] (Cainiao / AliExpress)
   Status: Delivering
   Event: Received by local delivery company
   Time: 2026-02-17 01:35:22

# List all parcels
$ python3 parcel-tracker/scripts/parcel_tracker.py list
Tracking #             Alias        Carrier            Status         Last Update
-----------------------------------------------------------------------------------
12345678901            Book         GLS                In transit     2026-02-17 10:30
12345678901234         Gift         DPD                Delivered      2026-02-16 14:22
CNFR9010481599571HD    USB Charger  Cainiao / AliExpress Delivering   2026-02-17 01:35
```

## How It Works

1. **Carrier Detection**: Pattern matching on tracking number format
2. **Free APIs First**: Tries carrier-specific free APIs (La Poste, Cainiao, etc.)
3. **Fallback Trackers**: Optional Tracktry/17Track if API keys provided
4. **Update Tracking**: Stores event history, only reports new events
5. **Notifications**: Cron job calls check_and_notify.py

## Adding New Carriers

To add a new carrier:
1. Add detection pattern to `detect_carrier()`
2. Add tracking function (check carrier's public API/docs)
3. Add to `track_parcel()` dispatcher
4. Update display name in `get_carrier_display_name()`

See [references/api-notes.md](references/api-notes.md) for carrier API details.

## OpenClaw Integration

This skill is designed to be used directly from OpenClaw conversations. Use natural language:

### Adding a Parcel
- "Add tracking number CNFR9010481599571HD"
- "Track this package: 1Z999AA10123456784"
- "Add parcel 8L01234567890"
- "Track parcel CJ123456789FR"

### Adding with Alias
- "Add tracking number CNFR9010481599571HD as USB Charger"
- "Track this package 1Z999AA10123456784 - Mom's Gift"
- "Add parcel 8L01234567890: Clothes"

Aliases make it easier to identify parcels in the list view instead of just seeing tracking numbers.

### Checking Updates
- "Check my parcels"
- "Any updates on my tracking numbers?"
- "Check for parcel updates"
- "Any news on my packages?"

### Listing Parcels
- "List my tracked parcels"
- "Show all my packages"
- "List my parcels"
- "My ongoing deliveries"

### Removing a Parcel
- "Remove tracking number CNFR9010481599571HD"
- "Stop tracking 1Z999AA10123456784"
- "Remove parcel CJ123456789FR"

### Implementation

When triggered, execute the appropriate command:

```python
# Add parcel (with optional alias)
exec(f"python3 parcel-tracker/scripts/parcel_tracker.py add '{tracking_number}' '{alias}'")

# Check updates
exec("python3 parcel-tracker/scripts/parcel_tracker.py check")

# List parcels  
exec("python3 parcel-tracker/scripts/parcel_tracker.py list")

# Remove parcel
exec(f"python3 parcel-tracker/scripts/parcel_tracker.py remove '{tracking_number}'")
```

The script will auto-detect the carrier and store the parcel in the database.
