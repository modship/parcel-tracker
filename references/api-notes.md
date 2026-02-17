# Carrier API Notes

## Free APIs (No API Key Required)

### La Poste / Colissimo

**API**: `https://www.laposte.fr/ssu/sun/suivi-unifie/{tracking_number}?lang=fr_FR`

- ✅ Official API
- ✅ No API key required
- ✅ Full tracking data
- Rate limited (be reasonable)

### Chronopost

**API**: `https://www.chronopost.fr/tracking-cxf/tracking-cxf/getTrack?number={tracking_number}`

- ✅ Official API
- ✅ No API key required
- ✅ Full tracking data

### Cainiao / AliExpress

**API**: `https://global.cainiao.com/global/detail.json?mailNos={tracking_number}&lang=en-US`

- ✅ Public API
- ✅ No API key required
- ✅ Works for most AliExpress orders
- Covers: Cainiao, AliExpress Standard Shipping, many Chinese carriers

### Yanwen

**Method**: Web scraping on `http://www.yw56.com.cn/english/select-e.asp`

- 🟡 Basic web tracking
- 🟡 No API key required
- 🟡 Limited data extraction

## Optional APIs (Free Tier Available)

### Tracktry

**API**: `https://api.tracktry.com/v1/trackings/{tracking_number}`

- 100 free requests/day
- Covers 800+ carriers
- Requires free API key
- Sign up: https://www.tracktry.com

### 17Track

**API**: `https://api.17track.net/track/v2.2/gettrackinfo`

- 100 free tracks/day
- Covers 2000+ carriers
- Requires free API key
- Sign up: https://www.17track.net/en/api

## Pattern Reference

### Tracking Number Formats

| Carrier | Format | Example |
|---------|--------|---------|
| Colissimo | 11-15 digits | `8L01234567890` |
| Colissimo Int'l | XX000000000XX | `CJ012345678FR` |
| Chronopost | 13 digits | `1234567890123` |
| Cainiao | CN??00000000000?? | `CNFR9010481599571HD` |
| Cainiao | LP0000000000000 | `LP1234567890123` |
| Yanwen | 12-14 digits | `123456789012` |
| Yanwen | YT0000000000000000 | `YT1234567890123456` |
| UPS | 1Z... | `1Z999AA10123456784` |
| FedEx | 12-20 digits | `123456789012` |
| DHL | 10-11 digits | `1234567890` |
| USPS | 20-22 digits | `9400100000000000000000` |
| Royal Mail | XX000000000GB | `AB123456789GB` |
| DPD | 14 digits | `12345678901234` |
| GLS | 11-12 digits | `12345678901` |
| Evri | 16 digits | `1234567890123456` |
| Mondial Relay | 8 digits | `12345678` |
| InPost | 24 digits | `520000005203482000000001` |
| Amazon | TBA/TBC/TBM... | `TBA123456789012` |

## Adding a New Carrier

1. Research the carrier's public API or tracking page
2. Add regex pattern to `detect_carrier()`
3. Create tracking function (similar to `track_cainiao()`)
4. Add to `track_parcel()` dispatcher
5. Test with real tracking numbers

### Tips for Finding Free APIs

1. Check if the carrier has a tracking page - inspect network requests
2. Look for `.json` endpoints in browser dev tools
3. Check if there's a public API documentation
4. Search GitHub for open source tracking implementations
5. Try common patterns: `/api/track`, `/tracking/json`, `/detail.json`
