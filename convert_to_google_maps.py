#!/usr/bin/env python3
"""
Convert Foursquare lists export to Google Maps importable format.
Creates CSV files for each list that can be imported to Google My Maps.
"""

import json
import csv
import os
import re
from pathlib import Path

# Directory setup
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'google_maps_lists'
OUTPUT_DIR.mkdir(exist_ok=True)

def sanitize_filename(name):
    """Convert list name to safe filename."""
    # Remove or replace problematic characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name)
    name = name.strip('_')
    return name[:50]  # Limit length

def build_venue_location_map():
    """Build a map of venue IDs to lat/lng from checkins."""
    venue_map = {}

    for i in range(1, 14):
        checkin_file = BASE_DIR / f'checkins{i}.json'
        if checkin_file.exists():
            with open(checkin_file, 'r') as f:
                data = json.load(f)
                for item in data.get('items', []):
                    venue = item.get('venue', {})
                    venue_id = venue.get('id')
                    lat = item.get('lat')
                    lng = item.get('lng')
                    if venue_id and lat and lng:
                        # Keep the first (most recent) location for each venue
                        if venue_id not in venue_map:
                            venue_map[venue_id] = {
                                'lat': lat,
                                'lng': lng,
                                'name': venue.get('name', '')
                            }

    print(f"Built location map for {len(venue_map)} venues from checkins")
    return venue_map

def convert_lists_to_csv(venue_map):
    """Convert each Foursquare list to a CSV file."""
    with open(BASE_DIR / 'lists.json', 'r') as f:
        lists_data = json.load(f)

    summary = []

    for lst in lists_data['items']:
        list_name = lst.get('name', 'Unknown')
        list_items = lst.get('listItems', {}).get('items', [])

        if not list_items:
            continue

        filename = sanitize_filename(list_name) + '.csv'
        filepath = OUTPUT_DIR / filename

        venues_with_coords = 0
        venues_without_coords = 0

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Google My Maps CSV format
            writer.writerow(['Name', 'Latitude', 'Longitude', 'Description', 'Foursquare URL'])

            for item in list_items:
                venue = item.get('venue', {})
                venue_id = venue.get('id', '')
                venue_name = venue.get('name', 'Unknown')
                venue_url = venue.get('url', '')

                # Look up coordinates
                location = venue_map.get(venue_id, {})
                lat = location.get('lat', '')
                lng = location.get('lng', '')

                if lat and lng:
                    venues_with_coords += 1
                else:
                    venues_without_coords += 1

                writer.writerow([
                    venue_name,
                    lat,
                    lng,
                    f'From Foursquare list: {list_name}',
                    venue_url
                ])

        summary.append({
            'name': list_name,
            'filename': filename,
            'total': len(list_items),
            'with_coords': venues_with_coords,
            'without_coords': venues_without_coords
        })
        print(f"Created: {filename} ({venues_with_coords}/{len(list_items)} with coordinates)")

    return summary

def create_summary(summary):
    """Create a summary file."""
    with open(OUTPUT_DIR / '_SUMMARY.txt', 'w') as f:
        f.write("FOURSQUARE TO GOOGLE MAPS CONVERSION SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total lists: {len(summary)}\n")
        total_places = sum(s['total'] for s in summary)
        total_with_coords = sum(s['with_coords'] for s in summary)
        f.write(f"Total places: {total_places}\n")
        f.write(f"Places with coordinates: {total_with_coords}\n")
        f.write(f"Places without coordinates: {total_places - total_with_coords}\n\n")
        f.write("HOW TO IMPORT TO GOOGLE MY MAPS:\n")
        f.write("-" * 50 + "\n")
        f.write("1. Go to https://www.google.com/maps/d/\n")
        f.write("2. Click 'Create a new map'\n")
        f.write("3. Click 'Import' under a layer\n")
        f.write("4. Upload the CSV file for the list you want\n")
        f.write("5. Select 'Latitude' and 'Longitude' columns for positioning\n")
        f.write("6. Select 'Name' column for place titles\n")
        f.write("7. Repeat for each list\n\n")
        f.write("NOTE: Places without coordinates will need to be added manually.\n")
        f.write("You can search for them in Google Maps using the venue name.\n\n")
        f.write("LISTS:\n")
        f.write("-" * 50 + "\n")
        for s in sorted(summary, key=lambda x: x['name']):
            coords_info = f"{s['with_coords']}/{s['total']} with coords"
            f.write(f"  {s['name']}\n")
            f.write(f"    File: {s['filename']}\n")
            f.write(f"    Places: {coords_info}\n\n")

def main():
    print("Building venue location map from checkins...")
    venue_map = build_venue_location_map()

    print("\nConverting lists to CSV...")
    summary = convert_lists_to_csv(venue_map)

    print("\nCreating summary...")
    create_summary(summary)

    print(f"\nDone! Files created in: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
