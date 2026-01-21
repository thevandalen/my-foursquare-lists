# My Foursquare Lists

Foursquare lists converted to CSV format for import into Google My Maps.

## Contents

- `google_maps_lists/` - 54 CSV files, one per Foursquare list
- `lists.json` - Original Foursquare lists data export
- `convert_to_google_maps.py` - Python script to convert Foursquare export to CSV

## How to Import to Google My Maps

1. Go to [Google My Maps](https://www.google.com/maps/d/)
2. Click **Create a new map**
3. Click **Import** under a layer
4. Upload a CSV file from `google_maps_lists/`
5. Select **Latitude** and **Longitude** columns for positioning
6. Select **Name** column for place titles
7. Repeat for each list you want to import

## Notes

- Places with coordinates will appear on the map automatically
- Places without coordinates can be searched by name in Google Maps
- See `google_maps_lists/_SUMMARY.txt` for a full list of converted lists

## Converting Your Own Foursquare Data

1. Export your data from [Foursquare Settings](https://foursquare.com/settings)
2. Extract `lists.json` and `checkins*.json` files to this directory
3. Run the conversion script:
   ```bash
   python3 convert_to_google_maps.py
   ```
4. Find your CSV files in `google_maps_lists/`

The script uses check-in history to add coordinates to list items (Foursquare's export doesn't include coordinates in lists).
