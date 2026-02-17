# Parcel Tracker - Notification Setup

## Setup Cron Job for Automatic Updates

To receive automatic notifications when parcels are updated, set up a cron job:

### Option 1: Using System Cron (Recommended)

```bash
# Edit crontab
crontab -e

# Add this line to check every 2 hours
0 */2 * * * cd ~/.openclaw/workspace && python3 parcel-tracker/scripts/check_and_notify.py >> ~/.openclaw/workspace/parcel-tracker/data/cron.log 2>&1

# Or every hour during business hours (9-18)
0 9-18 * * 1-5 cd ~/.openclaw/workspace && python3 parcel-tracker/scripts/check_and_notify.py >> ~/.openclaw/workspace/parcel-tracker/data/cron.log 2>&1
```

### Option 2: Using OpenClaw Cron (When Gateway Available)

```bash
openclaw cron add --name "parcel-tracker" --schedule "every 2 hours" \
  --command "python3 parcel-tracker/scripts/check_and_notify.py"
```

### Option 3: Manual Check

Just run when you want to check:

```bash
python3 parcel-tracker/scripts/parcel_tracker.py check
```

## Testing Notifications

```bash
# Add a test parcel (use a real tracking number)
python3 parcel-tracker/scripts/parcel_tracker.py add "CNFR9010481599571HD"

# Force a check
python3 parcel-tracker/scripts/check_and_notify.py

# View logs
tail -f ~/.openclaw/workspace/parcel-tracker/data/cron.log
```

## Database Location

Parcels are stored in:
```
~/.openclaw/workspace/parcel-tracker/data/parcels.db
```

You can query it directly:
```bash
sqlite3 ~/.openclaw/workspace/parcel-tracker/data/parcels.db "SELECT * FROM parcels;"
```

## Troubleshooting

### No updates found

1. Check if the tracking number is correct
2. Verify the carrier is detected: `python3 parcel-tracker/scripts/parcel_tracker.py detect <number>`
3. Try manual tracking: `python3 parcel-tracker/scripts/parcel_tracker.py track <number>`

### Carrier not detected

Add custom detection or use manual tracking. See api-notes.md for adding new carriers.

### Notifications not working

1. Check cron is running: `crontab -l`
2. Check logs: `tail ~/.openclaw/workspace/parcel-tracker/data/cron.log`
3. Test manually: `python3 parcel-tracker/scripts/check_and_notify.py`

## Usage Examples

```bash
# Add a Colissimo tracking number
python3 parcel-tracker/scripts/parcel_tracker.py add "8L01234567890"

# Add a UPS tracking number
python3 parcel-tracker/scripts/parcel_tracker.py add "1Z999AA10123456784"

# Add an AliExpress order
python3 parcel-tracker/scripts/parcel_tracker.py add "CNFR9010481599571HD"

# Check all parcels for updates
python3 parcel-tracker/scripts/parcel_tracker.py check

# List all tracked parcels
python3 parcel-tracker/scripts/parcel_tracker.py list

# Remove a parcel
python3 parcel-tracker/scripts/parcel_tracker.py remove "8L01234567890"

# Get full JSON for a parcel (one-time, not saved)
python3 parcel-tracker/scripts/parcel_tracker.py track "CNFR9010481599571HD"
```
