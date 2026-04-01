# Pathways by SLN — Developer Cheat Sheet
**For:** Kieran, Aaron, and future SLN tech team  
**Purpose:** Understand what every input does, where the logic lives, and how to edit it

---

## 1. What Each Sidebar Input Changes

| Input | What it does | Where in code |
|-------|-------------|---------------|
| **Unweighted GPA** | Used to estimate Safety/Match/Reach when no test scores | `get_fit()` function |
| **Test scores (SAT/ACT)** | Overrides GPA-based fit — more accurate | `get_fit()` function |
| **Career questions (Q1–Q8)** | Builds a trait profile → scores 30 careers by fit % | `run_career_match()` |
| **Annual household income** | Calculates Pell, TAP, Dream Act amounts | `calculate_aid()` |
| **Household size** | Affects HEOP income threshold cutoff | `calculate_aid()` |
| **NY State resident** | Unlocks TAP and Dream Act eligibility | `calculate_aid()` |
| **Immigration status** | Determines which aid programs apply | `calculate_aid()` |
| **First-generation** | Required for HEOP eligibility | `calculate_aid()` |
| **Preferred state** | Filters colleges to that state only (or Any) | `run_match()` |
| **School size** | Small (<5k), Medium (5–20k), Large (20k+) | `run_match()` |
| **School type** | Public (ctrl=1) or Private (ctrl=2) | `run_match()` |
| **Campus environment** | HBCU flag, Women's College flag | `run_match()` |
| **Years willing to study** | 2yr filters to community colleges, 4yr excludes them | `run_match()` |
| **Number of results** | How many colleges to show (5/10/15/20) | `run_match()` |

---

## 2. Filter Cutoffs

### Financial Aid (`calculate_aid()`)
| Program | Eligibility condition |
|---------|----------------------|
| **Pell Grant** | Income ≤ $60,000 + citizen or DACA |
| **NY TAP** | NY resident + citizen/DACA + income ≤ $80,000 |
| **Dream Act** | NY resident + undocumented/DACA + income ≤ $80,000 |
| **HEOP** | NY resident + first-gen + income below household threshold |

HEOP income thresholds by household size:
- 1 person: $22,400 | 2: $30,240 | 3: $38,080 | 4: $45,920 | 5: $53,760 | 6+: $61,600

### College Filtering (`run_match()`)
- **Full aid needed** (income < $50k): filters out schools with sticker price > $55,000
- **2yr only**: `yr2 == True` in schools data
- **4yr only**: `yr2 == False`
- **Default (Any)**: excludes 2-year schools unless student selects them

---

## 3. Safety / Match / Reach Logic (`get_fit()`)

**With test scores (most accurate):**
- SAT ≥ school's 75th percentile → **Safety**
- SAT between 25th–75th percentile → **Match**
- SAT below 25th percentile → **Reach**
- Same logic applies for ACT scores

**Without test scores (GPA + acceptance rate):**
| Acceptance Rate | GPA ≥ 3.0 | GPA < 3.0 |
|----------------|-----------|-----------|
| 80%+ | Safety | Safety |
| 60–80% | Safety | Match |
| 40–60% | Match | Reach |
| 20–40% | Match (if GPA ≥ 3.5) | Reach |
| Under 20% | Reach | Reach |

**No data at all:** Shows "⚠️ Limited data available"

---

## 4. Career Scoring (`score_career()`, `run_career_match()`)

Each career has 3 trait groups:
- **traits** (10 points each): people, helping, science, creativity, data, physical, leadership, outdoors
- **values** (15 points each): impact, stability, income, creativity, autonomy, prestige
- **styles** (8 points each): solo, team, variety, routine, indoors, outdoors

The student's 8 answers build a **profile** (accumulated trait scores).  
Each career is scored by comparing the profile to the career's ideal traits.  
Score = percentage of maximum possible match.  
Result: 30 careers ranked 0–100%.

---

## 5. Where Everything Lives in the Code

```
pathways_streamlit.py
│
├── load_schools()          Line ~30   — reads schools_full.csv into memory
├── CAREERS list            Line ~80   — all 30 careers with salary + trait data  
├── DEADLINES dict          Line ~350  — application deadlines by school ID
├── CAREER_MAPS dict        Line ~360  — maps dropdown answers to trait values
│
├── calculate_aid()         Line ~430  — Tool 3: Pell, TAP, Dream Act, HEOP
├── get_fit()               Line ~460  — determines Safety/Match/Reach
├── run_match()             Line ~480  — Tool 1: filters + scores colleges
├── score_career()          Line ~510  — scores one career against student profile
├── run_career_match()      Line ~525  — Tool 2: runs all 30 careers
├── generate_pdf()          Line ~535  — Tool 4: creates downloadable PDF
│
└── UI (Streamlit)
    ├── Sidebar inputs      Line ~610  — all student inputs
    ├── Tab 1: Matches      Line ~700  — college results with sort buttons
    ├── Tab 2: Careers      Line ~800  — career results with expand cards
    ├── Tab 3: Aid          Line ~850  — financial aid breakdown
    └── Tab 4: My List      Line ~880  — saved colleges + PDF download
```

---

## 6. Data Sources

| File | Source | What it contains |
|------|--------|-----------------|
| `schools_full.csv` | IPEDS 2023-24 | 3,690 US colleges — name, tuition, SAT/ACT ranges, acceptance rate, graduation rate, website |
| `pathways_streamlit.py` | Built by SLN RITA intern | All app logic |
| `requirements.txt` | — | Python packages: streamlit, reportlab, pandas |

**IPEDS files used to build schools_full.csv:**
- `hd2023.csv` — institution names, websites, HBCU status, sector
- `adm2023.csv` — SAT/ACT ranges, acceptance rates
- `ic2023_ay.csv` — in-state and out-of-state tuition
- `gr2023.csv` — graduation rates (computed as completers/cohort × 100)

**Aid thresholds:** 2025–26 federal and NY State figures. Update annually at:
- Pell: studentaid.gov
- TAP: hesc.ny.gov
- HEOP: nysed.gov

---

## 7. How to Make Common Edits

**Change the income cutoff for "full aid needed" filter:**  
Find `run_match()` → look for `income < 50000` → change the number

**Add a new career:**  
Find `CAREERS = [` → copy an existing career block → change all fields → add to list

**Update TAP amounts:**  
Find `calculate_aid()` → look for `tap = 5665` etc. → update the dollar amounts

**Change the sticker price filter:**  
Find `run_match()` → look for `tin > 55000` → change the threshold

**Add a new state option:**  
Find the `state_pref` selectbox in the sidebar → add the state abbreviation to the list

