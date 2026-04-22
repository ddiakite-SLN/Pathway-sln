"""
enrich_schools.py — Run this once to patch schools_full.csv with
real CUNY/SUNY admission data. Adds/updates gpa_25, gpa_75, gpa_avg, adm
for every CUNY and SUNY school using official public sources.

Sources:
  CUNY: cuny.edu/admissions/undergraduate/apply/academic-profiles/
        Freshman Admission Profile Fall 2025
  SUNY: suny.edu/media/suny/content-assets/documents/summary-sheets/
        Admission Information Summary Sheets 2025

Run:  python3 enrich_schools.py
Output: schools_full.csv (updated in place)
"""

import pandas as pd
import numpy as np

# ── CUNY Fall 2025 (official CUNY.edu admission profile) ─────
# avg_hs_100 = average HS GPA of admitted freshman on 100-pt scale
# Convert to 4.0: gpa_4 = (avg_100 - 65) / 7.5
# gpa_25 = avg - 4 pts on 100 → in 4.0
# gpa_75 = avg + 2 pts on 100 → in 4.0 (students above avg)

def pts_to_4(pts_100):
    return round(max(0.0, min(4.0, (pts_100 - 65) / 7.5)), 2)

CUNY_2025 = {
    # unitid: (avg_100, accept_pct)
    # Community colleges — open access
    190546: (77.9, 100),   # BMCC
    190099: (77.3, 100),   # Bronx CC
    192323: (75.3, 100),   # Guttman
    190821: (77.0, 100),   # Hostos
    192439: (77.6, 100),   # Kingsborough
    192407: (77.8, 100),   # LaGuardia
    195234: (78.1, 100),   # Queensborough
    # Four-year senior colleges
    190624: (92.9, 51),    # Baruch
    190549: (90.2, 54),    # Brooklyn College
    190637: (90.3, 60),    # City College (CCNY)
    190512: (91.4, 53),    # Hunter
    190558: (89.0, 56),    # John Jay
    190576: (89.4, 68),    # Lehman
    190678: (81.7, 80),    # Medgar Evers
    190600: (91.5, 55),    # Queens College
    190615: (87.9, 98),    # College of Staten Island
    190714: (83.0, 64),    # York College
    190717: (83.5, 73),    # NYC College of Technology
    190370: (82.0, 75),    # School of Professional Studies
}

# ── SUNY 2025 (official SUNY.edu Admissions Summary Sheet) ───
# GPA ranges are on 100-pt scale (e.g. "89-96")
# These are the middle 50% of admitted students
SUNY_2025 = {
    # unitid: (gpa_low_100, gpa_high_100, accept_pct_est)
    # University Centers
    196060: (89, 96, 65),   # University at Albany
    196097: (93, 98, 40),   # Binghamton
    196105: (91, 98, 57),   # University at Buffalo
    196183: (92, 97, 49),   # Stony Brook
    # University Colleges
    196088: (86, 94, 70),   # Brockport
    196246: (83, 92, 75),   # Buffalo State
    196176: (92, 96, 66),   # Cortland
    195302: (85, 95, 78),   # Fredonia
    196200: (92, 98, 34),   # Geneseo
    196264: (90, 96, 63),   # New Paltz
    196130: (82, 92, 83),   # Old Westbury
    196158: (88, 96, 75),   # Oneonta
    196051: (88, 97, 71),   # Oswego
    196219: (83, 94, 79),   # Plattsburgh
    196006: (85, 95, 84),   # Potsdam
    195195: (88, 96, 72),   # Purchase
    # ESF
    196157: (90, 97, 55),   # SUNY ESF
    # Technology Colleges
    188429: (82, 92, 80),   # Alfred State
    196079: (82, 91, 88),   # Canton
    196105: (84, 93, 75),   # Delhi (reusing Buffalo unitid — fix)
    196251: (83, 93, 85),   # Farmingdale
    196154: (86, 95, 78),   # Maritime
    196167: (84, 95, 82),   # Morrisville
}
# Fix Delhi unitid
SUNY_2025[196108] = SUNY_2025.pop(196105, (84, 93, 75))  # Delhi = 196108
SUNY_2025[196105] = (91, 98, 57)  # Restore Buffalo

def cuny_gpa_range(avg_100, accept_pct):
    """Convert CUNY 100-pt average to 4.0 GPA 25th/75th."""
    # 25th percentile ≈ avg - 4 pts (many students below avg get in)
    # 75th percentile ≈ avg + 2 pts
    gpa_25 = pts_to_4(avg_100 - 4)
    gpa_75 = pts_to_4(avg_100 + 2)
    gpa_avg = pts_to_4(avg_100)
    return gpa_25, gpa_75, gpa_avg

def suny_gpa_range(low_100, high_100):
    """Convert SUNY 100-pt range to 4.0 GPA 25th/75th."""
    gpa_25 = pts_to_4(low_100)
    gpa_75 = pts_to_4(high_100)
    gpa_avg = round((gpa_25 + gpa_75) / 2, 2)
    return gpa_25, gpa_75, gpa_avg

# ── Main enrichment ──────────────────────────────────────────
print("Loading schools_full.csv...")
df = pd.read_csv('schools_full.csv')
df['unitid'] = pd.to_numeric(df['unitid'], errors='coerce')

print(f"Total schools: {len(df)}")
print(f"Schools with gpa_25: {df['gpa_25'].notna().sum()}")
print(f"Schools with gpa_avg: {df['gpa_avg'].notna().sum()}")

cuny_updated = 0
suny_updated = 0

for idx, row in df.iterrows():
    uid = int(row['unitid']) if pd.notna(row['unitid']) else None
    if uid is None:
        continue

    if uid in CUNY_2025:
        avg_100, accept_pct = CUNY_2025[uid]
        g25, g75, gavg = cuny_gpa_range(avg_100, accept_pct)
        df.at[idx, 'gpa_25']  = g25
        df.at[idx, 'gpa_75']  = g75
        df.at[idx, 'gpa_avg'] = gavg
        df.at[idx, 'adm']     = accept_pct
        cuny_updated += 1

    elif uid in SUNY_2025:
        lo, hi, accept_pct = SUNY_2025[uid]
        g25, g75, gavg = suny_gpa_range(lo, hi)
        # Only update if missing or clearly wrong
        if pd.isna(row.get('gpa_25')) or float(row.get('gpa_25', 0) or 0) == 0:
            df.at[idx, 'gpa_25']  = g25
            df.at[idx, 'gpa_75']  = g75
            df.at[idx, 'gpa_avg'] = gavg
        if pd.isna(row.get('adm')) or float(row.get('adm', 0) or 0) == 0:
            df.at[idx, 'adm'] = accept_pct
        suny_updated += 1

print(f"\nUpdated: {cuny_updated} CUNY schools, {suny_updated} SUNY schools")
print(f"Schools with gpa_25 after: {df['gpa_25'].notna().sum()}")

df.to_csv('schools_full.csv', index=False)
print("✅ schools_full.csv saved")
