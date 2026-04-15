# ═══════════════════════════════════════════════════════════════
#  PATHWAYS BY SLN — Streamlit App v2
#  Fixed: persistent college list + PDF export
# ═══════════════════════════════════════════════════════════════

import streamlit as st
from io import BytesIO

# ════════════════════════════════════════════════════════════
# SECTION 8: STREAMLIT UI
# Everything below is the user interface
# Sidebar = student inputs
# Main panel = tabs (College Matches, Careers, Aid, My List)
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Pathways by SLN",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main { background-color: #F7F3EE; }
.stApp { background-color: #F7F3EE; }
div[data-testid="metric-container"] { background:white; border-radius:10px; padding:10px; box-shadow:0 1px 4px rgba(0,0,0,.07); }
.college-row { background:white; border-radius:10px; padding:14px 18px; margin-bottom:10px; box-shadow:0 1px 6px rgba(0,0,0,.06); }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ────────────────────────────────────────
if 'my_list' not in st.session_state:
    st.session_state.my_list = []
if 'sort_mode' not in st.session_state:
    st.session_state.sort_mode = 'fit'
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'aid' not in st.session_state:
    st.session_state.aid = {"pell":0,"tap":0,"dream":0,"heop":False,"total":0}
if 'career_results' not in st.session_state:
    st.session_state.career_results = []
if 'ran_match' not in st.session_state:
    st.session_state.ran_match = False

# ── DATA ──────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════
# SECTION 1: DATA LOADERS
# Loads colleges, GPA data, careers from CSV files on GitHub
# To update data: replace the CSV files in the repo
# ════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def load_schools():
    import pandas as pd, os
    csv_path = 'schools_full.csv'
    if not os.path.exists(csv_path):
        # Fallback to small sample if CSV not found
        return SAMPLE_SCHOOLS
    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)
    schools = df.to_dict('records')
    for s in schools:
        for k in ['hbcu','womens','yr2']:
            s[k] = bool(s.get(k,0))
        for k in ['tin','sat25','sat75','act25','act75','grad','adm']:
            v = s.get(k)
            s[k] = float(v) if v is not None else None
        try: s['ctrl'] = int(s['ctrl']) if s.get('ctrl') else 1
        except: s['ctrl'] = 1
        try: s['size'] = int(s['size']) if s.get('size') else 3
        except: s['size'] = 3
        try: s['hbcu'] = bool(int(s['hbcu'])) if s.get('hbcu') is not None else False
        except: s['hbcu'] = False
        try: s['yr2'] = bool(int(s['yr2'])) if s.get('yr2') is not None else False
        except: s['yr2'] = False
        try: s['tin'] = int(s['tin']) if s.get('tin') else None
        except: s['tin'] = None
        try: s['sat25'] = int(s['sat25']) if s.get('sat25') else None
        except: s['sat25'] = None
        try: s['sat75'] = int(s['sat75']) if s.get('sat75') else None
        except: s['sat75'] = None
        try: s['act25'] = int(s['act25']) if s.get('act25') else None
        except: s['act25'] = None
        try: s['act75'] = int(s['act75']) if s.get('act75') else None
        except: s['act75'] = None
        try: s['grad'] = int(s['grad']) if s.get('grad') else None
        except: s['grad'] = None
        try: s['adm'] = float(s['adm']) if s.get('adm') else None
        except: s['adm'] = None
        def safe_gpa(v):
            try:
                f = float(v)
                return round(f, 2) if f == f and f > 0 else None  # f==f checks for NaN
            except: return None
        s['gpa_avg'] = safe_gpa(s.get('gpa_avg'))
        # Keep major_cips as string for filtering
        s['major_cips'] = str(s.get('major_cips','') or '')
        s['gpa_25']  = safe_gpa(s.get('gpa_25'))
        s['gpa_75']  = safe_gpa(s.get('gpa_75'))
    return schools

@st.cache_data
@st.cache_data
# ── GPA Data Loader (Peterson's 2025 + SUNY PDF) ────────────
# Source: gpa_data.csv — 76 schools with admitted GPA ranges
@st.cache_data(ttl=3600, show_spinner=False)
def load_gpa_data():
    import pandas as pd, os
    csv_path = 'gpa_data.csv'
    if not os.path.exists(csv_path):
        return {}
    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)
    gpa_map = {}
    for _, row in df.iterrows():
        try:
            uid = int(row['unitid'])
            gpa_map[uid] = {
                'gpa_avg':  float(row['gpa_avg'])  if row.get('gpa_avg')  else None,
                'gpa_low':  float(row['gpa_low'])  if row.get('gpa_low')  else None,
                'gpa_high': float(row['gpa_high']) if row.get('gpa_high') else None,
                'eop_low':  float(row['eop_gpa_low'])  if row.get('eop_gpa_low')  else None,
                'eop_high': float(row['eop_gpa_high']) if row.get('eop_gpa_high') else None,
                'source':   str(row.get('source',''))
            }
        except: pass
    return gpa_map

GPA_DATA = load_gpa_data()

# ── Major Keywords Loader ────────────────────────────────────
import json as _json
try:
    with open('major_keywords.json') as _f:
        _mdata = _json.load(_f)
    KEYWORD_MAP = _mdata.get('keyword_map', {})
    CIP_NAMES   = _mdata.get('cip_names', {})
except:
    KEYWORD_MAP = {}
    CIP_NAMES   = {}

# ── Career Data Loader (O*NET 30.2 + BLS 2023) ──────────────
# Source: careers.csv — 1,016 occupations with RIASEC scores
@st.cache_data(ttl=3600, show_spinner=False)
def load_careers():
    import pandas as pd, os
    csv_path = 'careers.csv'
    if not os.path.exists(csv_path):
        return []
    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)
    careers = []
    for _, row in df.iterrows():
        try:
            careers.append({
                'soc': str(row.get('soc_code','')),
                'title': str(row.get('title','')),   # keep as 'title' for search
                'name': str(row.get('title','')),     # also as 'name' for display
                'field': str(row.get('field','')),
                'description': str(row.get('description','') or ''),
                'daily_tasks': str(row.get('daily_tasks','') or ''),
                'tech_tools': str(row.get('tech_tools','') or ''),
                'top_skills': str(row.get('top_skills','') or ''),
                'job_zone': int(float(row.get('job_zone',3) or 3)),
                'education': str(row.get('education','') or ''),
                'median_annual': int(float(row.get('median_annual',0) or 0)),
                'entry_annual': int(float(row.get('entry_annual',0) or 0)),
                'experienced_annual': int(float(row.get('experienced_annual',0) or 0)),
                'growth_pct': str(row.get('growth_pct','N/A') or 'N/A'),
                'outlook': str(row.get('outlook','N/A') or 'N/A'),
                'interest_realistic': float(row.get('interest_realistic',0) or 0),
                'interest_investigative': float(row.get('interest_investigative',0) or 0),
                'interest_artistic': float(row.get('interest_artistic',0) or 0),
                'interest_social': float(row.get('interest_social',0) or 0),
                'interest_enterprising': float(row.get('interest_enterprising',0) or 0),
                'interest_conventional': float(row.get('interest_conventional',0) or 0),
                'salary_mid': int(float(row.get('median_annual',0) or 0)),
                'salary_entry': int(float(row.get('entry_annual',0) or 0)),
                'salary_senior': int(float(row.get('experienced_annual',0) or 0)),
                'employment': int(float(row.get('employment',0) or 0)),
                'growth': str(row.get('growth_pct','')),
                'education': str(row.get('education','')),
                'demand': str(row.get('outlook','')),
            })
        except: pass
    return careers

CAREERS_FULL = load_careers()

SAMPLE_SCHOOLS = [
    {"id":190637,"name":"City College of New York (CUNY)","city":"New York","state":"NY","ctrl":1,"size":4,"sat25":1050,"sat75":1270,"grad":52,"adm":47.0,"tin":6930,"hbcu":False,"yr2":False,"web":"https://ccny.cuny.edu"},
    {"id":196097,"name":"Stony Brook University","city":"Stony Brook","state":"NY","ctrl":1,"size":5,"sat25":1320,"sat75":1500,"grad":77,"adm":49.0,"tin":7070,"hbcu":False,"yr2":False,"web":"https://stonybrook.edu"},
    {"id":193900,"name":"New York University","city":"New York","state":"NY","ctrl":2,"size":5,"sat25":1370,"sat75":1530,"grad":87,"adm":12.8,"tin":60438,"hbcu":False,"yr2":False,"web":"https://nyu.edu"},
]

SCHOOLS = load_schools()


CAREERS = [
    {"id":"rn","name":"Registered Nurse","icon":"🏥","field":"Healthcare","salary_entry":59730,"salary_mid":81220,"salary_senior":107000,"growth":"6%","demand":"High","why":"You want to help people directly and build a stable career.","day":"Check on patients, administer medications, coordinate with doctors. No two days the same.","majors":["Nursing (BSN)","Health Sciences","Biology"],"traits":{"people":5,"helping":5,"science":4,"creativity":2,"data":2,"physical":3,"leadership":3,"outdoors":1},"values":{"impact":5,"stability":5,"income":3,"creativity":2,"autonomy":3,"prestige":3},"styles":{"solo":1,"team":5,"variety":4,"routine":2,"indoors":5,"outdoors":1}},
    {"id":"cs","name":"Software Developer","icon":"💻","field":"Technology","salary_entry":75000,"salary_mid":124200,"salary_senior":180000,"growth":"25%","demand":"Very High","why":"You like solving complex problems and want strong income.","day":"Write code, debug systems, build apps. Remote work is common.","majors":["Computer Science","Software Engineering","Information Technology"],"traits":{"people":2,"helping":2,"science":4,"creativity":4,"data":5,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":3,"stability":4,"income":5,"creativity":4,"autonomy":5,"prestige":4},"styles":{"solo":4,"team":3,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"teacher","name":"K-12 Teacher","icon":"📚","field":"Education","salary_entry":42000,"salary_mid":62360,"salary_senior":82000,"growth":"1%","demand":"Steady","why":"You want to shape the next generation.","day":"Plan lessons, teach, grade work, mentor students through their most formative years.","majors":["Education (K-12)","English Education","Math Education","Special Education"],"traits":{"people":5,"helping":5,"science":2,"creativity":4,"data":2,"physical":2,"leadership":4,"outdoors":2},"values":{"impact":5,"stability":5,"income":2,"creativity":4,"autonomy":3,"prestige":2},"styles":{"solo":2,"team":4,"variety":3,"routine":4,"indoors":5,"outdoors":2}},
    {"id":"social_worker","name":"Social Worker","icon":"🤝","field":"Social Services","salary_entry":38000,"salary_mid":55350,"salary_senior":75000,"growth":"7%","demand":"High","why":"You care about communities and want work that makes a real difference.","day":"Meet families in crisis, connect them to resources, advocate for their rights.","majors":["Social Work (BSW)","Psychology","Sociology","Human Services"],"traits":{"people":5,"helping":5,"science":2,"creativity":3,"data":2,"physical":2,"leadership":3,"outdoors":2},"values":{"impact":5,"stability":4,"income":2,"creativity":3,"autonomy":3,"prestige":2},"styles":{"solo":2,"team":4,"variety":5,"routine":2,"indoors":4,"outdoors":3}},
    {"id":"engineer","name":"Civil / Mechanical Engineer","icon":"🏗️","field":"Engineering","salary_entry":65000,"salary_mid":88050,"salary_senior":130000,"growth":"5%","demand":"High","why":"You want to build real things and earn strong income.","day":"Design systems, review blueprints, manage contractors, visit construction sites.","majors":["Civil Engineering","Mechanical Engineering","Environmental Engineering"],"traits":{"people":2,"helping":2,"science":5,"creativity":4,"data":5,"physical":3,"leadership":3,"outdoors":4},"values":{"impact":4,"stability":5,"income":4,"creativity":4,"autonomy":3,"prestige":3},"styles":{"solo":3,"team":4,"variety":4,"routine":3,"indoors":3,"outdoors":4}},
    {"id":"finance","name":"Financial Analyst","icon":"📊","field":"Business & Finance","salary_entry":58000,"salary_mid":95080,"salary_senior":155000,"growth":"8%","demand":"High","why":"You want financial security and a clear advancement path.","day":"Analyze data, build financial models, advise organizations on money decisions.","majors":["Finance","Accounting","Business Administration","Economics"],"traits":{"people":2,"helping":2,"science":3,"creativity":2,"data":5,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":2,"stability":5,"income":5,"creativity":2,"autonomy":3,"prestige":4},"styles":{"solo":4,"team":3,"variety":3,"routine":4,"indoors":5,"outdoors":1}},
    {"id":"therapist","name":"Counselor / Therapist","icon":"🧠","field":"Mental Health","salary_entry":42000,"salary_mid":58510,"salary_senior":90000,"growth":"18%","demand":"Very High","why":"You want to help people through their hardest moments.","day":"Sit with people during difficult times and help them build coping skills.","majors":["Psychology","Counseling (MS)","Social Work (MSW)","Mental Health Counseling"],"traits":{"people":5,"helping":5,"science":3,"creativity":3,"data":3,"physical":1,"leadership":2,"outdoors":1},"values":{"impact":5,"stability":4,"income":3,"creativity":3,"autonomy":4,"prestige":3},"styles":{"solo":3,"team":2,"variety":3,"routine":4,"indoors":5,"outdoors":1}},
    {"id":"data_scientist","name":"Data Scientist","icon":"📈","field":"Technology & Analytics","salary_entry":70000,"salary_mid":108020,"salary_senior":165000,"growth":"35%","demand":"Very High","why":"You love finding patterns in data and turning numbers into decisions.","day":"Collect, clean and analyze datasets. Mix of statistics, programming, and storytelling.","majors":["Data Science","Statistics","Computer Science","Mathematics"],"traits":{"people":2,"helping":2,"science":5,"creativity":4,"data":5,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":3,"stability":4,"income":5,"creativity":4,"autonomy":4,"prestige":4},"styles":{"solo":4,"team":3,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"pa","name":"Physician Assistant / NP","icon":"⚕️","field":"Healthcare","salary_entry":85000,"salary_mid":121530,"salary_senior":150000,"growth":"28%","demand":"Very High","why":"Top-level healthcare without a 10-year medical school commitment.","day":"Diagnose illnesses, prescribe medications, treat patients with high autonomy.","majors":["Pre-Medicine","Biology","Health Sciences","Nursing (BSN)"],"traits":{"people":4,"helping":5,"science":5,"creativity":3,"data":4,"physical":3,"leadership":4,"outdoors":1},"values":{"impact":5,"stability":4,"income":5,"creativity":3,"autonomy":4,"prestige":5},"styles":{"solo":2,"team":4,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"marketing","name":"Marketing Manager","icon":"📣","field":"Marketing & Communications","salary_entry":48000,"salary_mid":85000,"salary_senior":145000,"growth":"6%","demand":"Moderate","why":"You love creating and communicating — marketing combines both.","day":"Craft campaigns, manage social media, analyze results, tell brand stories.","majors":["Marketing","Communications","Business Administration","Journalism"],"traits":{"people":4,"helping":2,"science":2,"creativity":5,"data":4,"physical":1,"leadership":4,"outdoors":2},"values":{"impact":3,"stability":3,"income":4,"creativity":5,"autonomy":4,"prestige":3},"styles":{"solo":2,"team":4,"variety":5,"routine":2,"indoors":4,"outdoors":2}},
    {"id":"lawyer","name":"Attorney / Lawyer","icon":"⚖️","field":"Law & Justice","salary_entry":72000,"salary_mid":126930,"salary_senior":220000,"growth":"4%","demand":"Moderate","why":"You are drawn to justice and how society rules work.","day":"Research legal questions, write arguments, advise clients, negotiate deals.","majors":["Pre-Law","Political Science","Criminal Justice","English"],"traits":{"people":3,"helping":3,"science":2,"creativity":4,"data":4,"physical":1,"leadership":4,"outdoors":1},"values":{"impact":4,"stability":4,"income":5,"creativity":4,"autonomy":4,"prestige":5},"styles":{"solo":4,"team":3,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"cybersecurity","name":"Cybersecurity Analyst","icon":"🔐","field":"Technology","salary_entry":70000,"salary_mid":112000,"salary_senior":175000,"growth":"32%","demand":"Critical","why":"One of the fastest-growing and most in-demand fields in tech.","day":"Monitor networks for threats, investigate breaches, stay ahead of hackers.","majors":["Cybersecurity","Computer Science","Information Technology","Network Administration"],"traits":{"people":2,"helping":3,"science":4,"creativity":4,"data":5,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":4,"stability":5,"income":5,"creativity":4,"autonomy":4,"prestige":4},"styles":{"solo":4,"team":3,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"physical_therapist","name":"Physical Therapist","icon":"🦴","field":"Healthcare","salary_entry":62000,"salary_mid":97720,"salary_senior":120000,"growth":"15%","demand":"High","why":"Hands-on patient care with strong income and work-life balance.","day":"Work with patients recovering from injuries, design exercise programs, track progress.","majors":["Physical Therapy (DPT)","Kinesiology","Exercise Science","Biology"],"traits":{"people":5,"helping":5,"science":4,"creativity":3,"data":3,"physical":5,"leadership":3,"outdoors":2},"values":{"impact":5,"stability":5,"income":4,"creativity":3,"autonomy":3,"prestige":3},"styles":{"solo":2,"team":4,"variety":3,"routine":3,"indoors":5,"outdoors":2}},
    {"id":"accountant","name":"Accountant / CPA","icon":"🧾","field":"Business & Finance","salary_entry":48000,"salary_mid":78000,"salary_senior":120000,"growth":"4%","demand":"Steady","why":"You are detail-oriented and want a stable well-paying career.","day":"Prepare tax returns, audit financial records, advise on budgets and compliance.","majors":["Accounting","Finance","Business Administration"],"traits":{"people":2,"helping":2,"science":3,"creativity":2,"data":5,"physical":1,"leadership":2,"outdoors":1},"values":{"impact":2,"stability":5,"income":4,"creativity":1,"autonomy":3,"prestige":3},"styles":{"solo":4,"team":2,"variety":2,"routine":5,"indoors":5,"outdoors":1}},
    {"id":"ux_designer","name":"UX / Product Designer","icon":"🎨","field":"Design & Technology","salary_entry":62000,"salary_mid":95000,"salary_senior":155000,"growth":"3%","demand":"Moderate","why":"You think visually and want to shape how millions use technology.","day":"Research user needs, sketch wireframes, prototype interfaces, test with real users.","majors":["UX Design","Graphic Design","Interactive Media","Psychology"],"traits":{"people":3,"helping":3,"science":2,"creativity":5,"data":4,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":4,"stability":3,"income":4,"creativity":5,"autonomy":4,"prestige":3},"styles":{"solo":3,"team":4,"variety":4,"routine":2,"indoors":5,"outdoors":1}},
    {"id":"journalist","name":"Journalist / Writer","icon":"✍️","field":"Media & Communications","salary_entry":36000,"salary_mid":55960,"salary_senior":100000,"growth":"4%","demand":"Moderate","why":"You have a voice and want to use it to inform and shape communities.","day":"Investigate stories, conduct interviews, write clearly under deadline pressure.","majors":["Journalism","Communications","English","Media Studies"],"traits":{"people":4,"helping":3,"science":2,"creativity":5,"data":3,"physical":2,"leadership":3,"outdoors":4},"values":{"impact":5,"stability":2,"income":3,"creativity":5,"autonomy":4,"prestige":3},"styles":{"solo":4,"team":2,"variety":5,"routine":1,"indoors":3,"outdoors":4}},
    {"id":"physician","name":"Medical Doctor (MD)","icon":"🩺","field":"Medicine","salary_entry":80000,"salary_mid":208000,"salary_senior":350000,"growth":"3%","demand":"High","why":"The highest level of clinical impact — for those committed to the long path.","day":"Diagnose complex conditions, perform procedures, carry life-and-death decisions.","majors":["Pre-Medicine","Biology","Chemistry","Biochemistry","Neuroscience"],"traits":{"people":4,"helping":5,"science":5,"creativity":3,"data":5,"physical":4,"leadership":4,"outdoors":1},"values":{"impact":5,"stability":4,"income":5,"creativity":3,"autonomy":4,"prestige":5},"styles":{"solo":2,"team":4,"variety":4,"routine":2,"indoors":5,"outdoors":1}},
    {"id":"electrician","name":"Electrician / Skilled Trades","icon":"⚡","field":"Skilled Trades","salary_entry":40000,"salary_mid":61550,"salary_senior":95000,"growth":"6%","demand":"High","why":"Massive shortage of skilled tradespeople. Strong income without student debt.","day":"Install and repair electrical systems in homes, buildings, and industrial facilities.","majors":["Electrical Technology (Associate)","Construction Management","Apprenticeship"],"traits":{"people":2,"helping":3,"science":3,"creativity":3,"data":2,"physical":5,"leadership":3,"outdoors":4},"values":{"impact":3,"stability":5,"income":4,"creativity":3,"autonomy":4,"prestige":2},"styles":{"solo":3,"team":3,"variety":4,"routine":3,"indoors":3,"outdoors":4}},
    {"id":"school_counselor","name":"School Counselor","icon":"🎓","field":"Education & Counseling","salary_entry":42000,"salary_mid":61710,"salary_senior":82000,"growth":"5%","demand":"Moderate","why":"You want to guide students through their most important decisions.","day":"Meet with students about academics, college applications, and personal struggles.","majors":["School Counseling (M.Ed)","Psychology","Social Work","Education"],"traits":{"people":5,"helping":5,"science":2,"creativity":3,"data":2,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":5,"stability":5,"income":2,"creativity":3,"autonomy":3,"prestige":2},"styles":{"solo":2,"team":4,"variety":3,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"pharmacist","name":"Pharmacist","icon":"💊","field":"Healthcare","salary_entry":100000,"salary_mid":128570,"salary_senior":155000,"growth":"2%","demand":"Stable","why":"Excellent income and stability with a doctorate in pharmacy.","day":"Dispense medications, counsel patients on drug interactions, work with doctors.","majors":["Pharmacy (PharmD)","Pre-Pharmacy","Chemistry","Biology"],"traits":{"people":4,"helping":4,"science":5,"creativity":2,"data":5,"physical":2,"leadership":3,"outdoors":1},"values":{"impact":4,"stability":5,"income":5,"creativity":2,"autonomy":3,"prestige":4},"styles":{"solo":2,"team":3,"variety":2,"routine":5,"indoors":5,"outdoors":1}},
    {"id":"public_health","name":"Public Health Professional","icon":"🌍","field":"Public Health","salary_entry":45000,"salary_mid":74560,"salary_senior":110000,"growth":"13%","demand":"High","why":"You want to fix the systems that keep entire populations healthy.","day":"Design health programs, analyze disease patterns, write policy, work with communities.","majors":["Public Health (MPH)","Epidemiology","Health Policy","Biology","Sociology"],"traits":{"people":4,"helping":5,"science":4,"creativity":3,"data":5,"physical":2,"leadership":4,"outdoors":3},"values":{"impact":5,"stability":3,"income":3,"creativity":3,"autonomy":4,"prestige":3},"styles":{"solo":3,"team":4,"variety":4,"routine":3,"indoors":4,"outdoors":3}},
    {"id":"hr","name":"Human Resources Manager","icon":"👥","field":"Business & People","salary_entry":45000,"salary_mid":77050,"salary_senior":120000,"growth":"5%","demand":"Moderate","why":"You are the advocate for people inside an organization.","day":"Recruit employees, handle conflicts, design benefits, shape company culture.","majors":["Human Resources","Business Administration","Psychology","Organizational Behavior"],"traits":{"people":5,"helping":4,"science":2,"creativity":3,"data":3,"physical":1,"leadership":4,"outdoors":1},"values":{"impact":4,"stability":4,"income":4,"creativity":3,"autonomy":3,"prestige":3},"styles":{"solo":2,"team":5,"variety":3,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"environmental","name":"Environmental Scientist","icon":"🌿","field":"Environment & Science","salary_entry":45000,"salary_mid":76480,"salary_senior":110000,"growth":"6%","demand":"Growing","why":"Climate change is creating massive need for environmental expertise.","day":"Test soil and water, assess environmental impact, advise on sustainability.","majors":["Environmental Science","Environmental Engineering","Biology","Chemistry"],"traits":{"people":2,"helping":4,"science":5,"creativity":3,"data":5,"physical":4,"leadership":3,"outdoors":5},"values":{"impact":5,"stability":3,"income":3,"creativity":4,"autonomy":4,"prestige":3},"styles":{"solo":3,"team":3,"variety":4,"routine":3,"indoors":2,"outdoors":5}},
    {"id":"architect","name":"Architect","icon":"🏛️","field":"Architecture & Design","salary_entry":48000,"salary_mid":82320,"salary_senior":130000,"growth":"5%","demand":"Moderate","why":"Creative and technical in equal measure — you design spaces people live in.","day":"Sketch concepts, work with engineers on structural systems, manage construction.","majors":["Architecture (B.Arch)","Urban Design","Structural Engineering","Interior Architecture"],"traits":{"people":3,"helping":3,"science":4,"creativity":5,"data":4,"physical":2,"leadership":3,"outdoors":3},"values":{"impact":4,"stability":3,"income":3,"creativity":5,"autonomy":4,"prestige":4},"styles":{"solo":3,"team":4,"variety":4,"routine":2,"indoors":4,"outdoors":3}},
    {"id":"entrepreneur","name":"Entrepreneur / Business Owner","icon":"🚀","field":"Business","salary_entry":0,"salary_mid":75000,"salary_senior":250000,"growth":"N/A","demand":"Self-created","why":"High risk, high reward. No guaranteed income but unlimited upside.","day":"Pitch investors, manage teams, solve unexpected problems, make 100 decisions a day.","majors":["Business Administration","Marketing","Computer Science","Engineering","Finance"],"traits":{"people":4,"helping":3,"science":2,"creativity":5,"data":4,"physical":2,"leadership":5,"outdoors":2},"values":{"impact":4,"stability":1,"income":5,"creativity":5,"autonomy":5,"prestige":4},"styles":{"solo":3,"team":3,"variety":5,"routine":1,"indoors":3,"outdoors":3}},
    {"id":"police","name":"Police Officer / Detective","icon":"🚔","field":"Criminal Justice","salary_entry":48000,"salary_mid":67290,"salary_senior":90000,"growth":"3%","demand":"Steady","why":"Stable government employment with pension and benefits.","day":"Patrol communities, respond to emergencies, investigate crimes, appear in court.","majors":["Criminal Justice","Criminology","Psychology","Sociology","Pre-Law"],"traits":{"people":4,"helping":4,"science":2,"creativity":2,"data":3,"physical":5,"leadership":4,"outdoors":5},"values":{"impact":4,"stability":5,"income":3,"creativity":2,"autonomy":3,"prestige":3},"styles":{"solo":2,"team":4,"variety":5,"routine":2,"indoors":2,"outdoors":5}},
    {"id":"chef","name":"Chef / Culinary Arts","icon":"👨‍🍳","field":"Culinary Arts","salary_entry":28000,"salary_mid":56520,"salary_senior":90000,"growth":"15%","demand":"High","why":"Few careers offer more immediate creative satisfaction — every plate is your art.","day":"Create menus, manage kitchens, train cooks, source ingredients, produce food.","majors":["Culinary Arts","Food Service Management","Hospitality Management","Nutrition"],"traits":{"people":3,"helping":3,"science":3,"creativity":5,"data":2,"physical":5,"leadership":4,"outdoors":2},"values":{"impact":3,"stability":3,"income":3,"creativity":5,"autonomy":4,"prestige":3},"styles":{"solo":2,"team":4,"variety":3,"routine":4,"indoors":5,"outdoors":2}},
    {"id":"biologist","name":"Research Scientist / Biologist","icon":"🔬","field":"Science & Research","salary_entry":45000,"salary_mid":79590,"salary_senior":125000,"growth":"11%","demand":"Moderate","why":"A breakthrough discovery can change the world — and you could be the one to make it.","day":"Design experiments, collect samples, analyze results, write papers.","majors":["Biology","Biochemistry","Microbiology","Genetics","Neuroscience"],"traits":{"people":2,"helping":3,"science":5,"creativity":4,"data":5,"physical":3,"leadership":2,"outdoors":3},"values":{"impact":5,"stability":3,"income":3,"creativity":5,"autonomy":4,"prestige":4},"styles":{"solo":4,"team":3,"variety":3,"routine":4,"indoors":4,"outdoors":3}},
    {"id":"athlete_trainer","name":"Athletic Trainer / Coach","icon":"🏃","field":"Sports & Fitness","salary_entry":36000,"salary_mid":53340,"salary_senior":80000,"growth":"19%","demand":"High","why":"Growing awareness of sports medicine and athlete development.","day":"Prevent injuries, manage rehab, optimize athlete performance on the sideline.","majors":["Athletic Training","Kinesiology","Exercise Science","Sports Medicine"],"traits":{"people":5,"helping":5,"science":4,"creativity":3,"data":3,"physical":5,"leadership":4,"outdoors":5},"values":{"impact":4,"stability":3,"income":3,"creativity":3,"autonomy":3,"prestige":3},"styles":{"solo":2,"team":5,"variety":4,"routine":3,"indoors":3,"outdoors":5}},
    {"id":"film_producer","name":"Film / Media Producer","icon":"🎬","field":"Arts & Media","salary_entry":35000,"salary_mid":76400,"salary_senior":150000,"growth":"10%","demand":"Moderate","why":"Streaming has created massive demand for content creators.","day":"Develop stories, manage budgets, coordinate crews, shepherd projects to screen.","majors":["Film Production","Media Studies","Communications","Digital Media"],"traits":{"people":4,"helping":2,"science":2,"creativity":5,"data":3,"physical":3,"leadership":5,"outdoors":3},"values":{"impact":4,"stability":2,"income":3,"creativity":5,"autonomy":4,"prestige":5},"styles":{"solo":2,"team":5,"variety":5,"routine":1,"indoors":3,"outdoors":4}},
    {"id":"musician","name":"Musician / Visual Artist","icon":"🎵","field":"Arts & Creative","salary_entry":25000,"salary_mid":56000,"salary_senior":120000,"growth":"2%","demand":"Competitive","why":"Nothing compares to creating something that moves people.","day":"Practice your craft, perform or exhibit, build multiple revenue streams.","majors":["Music Performance","Fine Arts","Graphic Arts","Music Education","Art Education"],"traits":{"people":3,"helping":2,"science":1,"creativity":5,"data":1,"physical":3,"leadership":2,"outdoors":2},"values":{"impact":4,"stability":1,"income":2,"creativity":5,"autonomy":5,"prestige":3},"styles":{"solo":5,"team":2,"variety":4,"routine":4,"indoors":4,"outdoors":3}},
]


# ════════════════════════════════════════════════════════════
# SECTION 7: HARDCODED DATA
# Update deadlines annually before application season (August)
# Add more schools by copying the format: {unitid: {rd, ea, ed, sys}}
# UNITID comes from schools_full.csv
# ════════════════════════════════════════════════════════════
DEADLINES = {
    190637:{"rd":"Feb 1","ea":"Nov 21","sys":"CUNY"},
    190512:{"rd":"Feb 1","ea":"Nov 21","sys":"CUNY"},
    190549:{"rd":"Feb 1","ea":"Nov 21","sys":"CUNY"},
    190558:{"rd":"Feb 1","ea":"Nov 21","sys":"CUNY"},
    196097:{"rd":"Feb 1","ea":"Nov 1","sys":"SUNY"},
    196060:{"rd":"Rolling","ea":"Nov 15","sys":"SUNY"},
    196079:{"rd":"Rolling","sys":"SUNY"},
    196185:{"rd":"Rolling","ea":"Nov 15","sys":"SUNY"},
    192439:{"rd":"Jan 3","ed":"Nov 1"},
    193900:{"rd":"Jan 1","ed":"Nov 1"},
    190688:{"rd":"Jan 1","ed":"Nov 1"},
    190150:{"rd":"Jan 1","ed":"Nov 1"},
    190415:{"rd":"Jan 2","ed":"Nov 1"},
    166027:{"rd":"Jan 1","ea":"Nov 1"},
    131520:{"rd":"Feb 15","ed":"Nov 1"},
    198419:{"rd":"Jan 5","ed":"Nov 3"},
}

# ── ENGINES ───────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════
# SECTION 2: FINANCIAL AID CALCULATOR
# Calculates Pell Grant, NY TAP, Dream Act, HEOP eligibility
# Update thresholds annually: studentaid.gov + hesc.ny.gov
# Income thresholds from SUNY PDF 2026-27
# ════════════════════════════════════════════════════════════
def calculate_aid(income, hsize, ny_res, immig, first_gen):
    pell=tap=dream=0; heop=False
    if immig in ('citizen','daca'):
        if income<=26000: pell=7395
        elif income<=32000: pell=5546
        elif income<=42000: pell=3698
        elif income<=60000: pell=1849
    if ny_res and immig in ('citizen','daca') and income<=80000:
        if income<=10000: tap=5665
        elif income<=20000: tap=4700
        elif income<=40000: tap=3500
        elif income<=60000: tap=2000
        else: tap=500
    if ny_res and immig in ('undocumented','daca') and income<=80000:
        dream=tap if tap>0 else 2500
        if immig=='undocumented': tap=0
    cuts=[28953,39128,49303,59478,69653,79828,90003,100178]  # 2026-27 EOP thresholds
    if ny_res and first_gen and income<=cuts[min(hsize-1,7)] and immig!='undocumented':
        heop=True
    return {"pell":pell,"tap":tap,"dream":dream,"heop":heop,"total":pell+tap+dream}

# ════════════════════════════════════════════════════════════
# SECTION 3: COLLEGE FIT ENGINE (Safety/Match/Reach)
# Priority: SAT/ACT → Peterson's GPA range → Acceptance rate
# Same methodology as Niche and CollegeVine
# ════════════════════════════════════════════════════════════
def get_fit(sat, act, s, gpa=None):
    """
    Exactly how Niche determines Safety/Match/Reach:
    1. SAT/ACT vs school 25th/75th percentile (most accurate)
    2. GPA vs Peterson's admitted GPA range
    3. Acceptance rate as honest fallback
    Always returns a label — never unknown unless truly no data at all.
    """
    adm = s.get('adm')

    # ── 1. SAT (most accurate) ────────────────────────────────
    if sat and s.get('sat25') and s.get('sat75'):
        if sat >= s['sat75']: return 'safety'
        if sat >= s['sat25']: return 'match'
        return 'reach'

    # ── 2. ACT ───────────────────────────────────────────────
    if act and s.get('act25') and s.get('act75'):
        if act >= s['act75']: return 'safety'
        if act >= s['act25']: return 'match'
        return 'reach'

    # ── 3. Peterson's GPA 25th/75th percentile ───────────────
    if gpa and s.get('gpa_25') and s.get('gpa_75'):
        if gpa >= s['gpa_75']: return 'safety'
        if gpa >= s['gpa_25']: return 'match'
        return 'reach'

    # ── 4. Peterson's average GPA ────────────────────────────
    if gpa and s.get('gpa_avg'):
        avg = s['gpa_avg']
        if gpa >= avg + 0.25: return 'safety'
        if gpa >= avg - 0.25: return 'match'
        return 'reach'

    # ── 5. SUNY/CDS GPA from gpa_data.csv ───────────────────
    uid = s.get('id')
    if gpa and uid and uid in GPA_DATA:
        g = GPA_DATA[uid]
        lo = g.get('gpa_low')
        hi = g.get('gpa_high')
        if lo and hi:
            if gpa >= hi: return 'safety'
            if gpa >= lo: return 'match'
            return 'reach'

    # ── 6. Acceptance rate (Niche-style fallback) ─────────────
    # Niche uses this when no test/GPA data available
    # Thresholds based on how Niche categorizes schools
    if adm is not None:
        if adm >= 85: return 'safety'
        if adm >= 50: return 'match'
        return 'reach'

    # ── 7. GPA alone vs acceptance rate proxy ─────────────────
    # If we have GPA but no school data, use GPA strength
    if gpa:
        if gpa >= 3.7: return 'match'   # strong student, assume match for unknown schools
        if gpa >= 3.0: return 'match'
        return 'reach'

    return 'unknown'


# ════════════════════════════════════════════════════════════
# SECTION 3b: ENVIRONMENTAL FIT ENGINE
# Academic match = GPA/SAT alignment (how likely to get in)
# Environmental fit = size, location, type alignment (will you thrive)
# Based on Hossler & Gallagher (1987) college choice literature
# ════════════════════════════════════════════════════════════
def get_env_fit(s, env_pref, school_size, school_type):
    """
    Environmental fit — separate from academic match.
    Based on Hossler & Gallagher (1987) college choice literature:
    'fit' = alignment between student preferences and institutional characteristics.
    Returns list of environment descriptor tags.
    """
    tags = []
    ctrl = s.get('ctrl')
    try: ctrl = int(ctrl)
    except: pass

    # Institutional type
    if ctrl == 1: tags.append('Public')
    elif ctrl == 2: tags.append('Private nonprofit')
    elif ctrl == 3: tags.append('For-profit')

    # Size descriptor (IPEDS size categories)
    size = s.get('size', 0)
    size_labels = {
        1: 'Very small (<1k students)',
        2: 'Small (1–5k students)',
        3: 'Medium (5–15k students)',
        4: 'Large (15–30k students)',
        5: 'Very large (30k+ students)'
    }
    if size in size_labels: tags.append(size_labels[size])

    # Mission / identity
    if s.get('hbcu'): tags.append('HBCU')
    if s.get('womens'): tags.append("Women's college")

    # Outcomes signal
    grad = float(s.get('grad') or 0)
    if grad >= 80: tags.append(f'{int(grad)}% grad rate')
    elif grad >= 60: tags.append(f'{int(grad)}% grad rate')
    elif grad > 0: tags.append(f'{int(grad)}% grad rate')

    return tags

# ════════════════════════════════════════════════════════════
# SECTION 4: CAREER SCORING ENGINE
# Uses O*NET RIASEC Holland codes to match student to careers
# R=Realistic I=Investigative A=Artistic S=Social E=Enterprising C=Conventional
# Dominant interest gets 2x weight — stability doesn't override interest
# ════════════════════════════════════════════════════════════
def score_career_onet(career, profile):
    """
    Score using O*NET RIASEC Holland codes.
    Dominant interest gets 2.5x weight — prevents weak traits from hijacking results.
    """
    R = float(career.get('interest_realistic') or 0)
    I = float(career.get('interest_investigative') or 0)
    A = float(career.get('interest_artistic') or 0)
    S = float(career.get('interest_social') or 0)
    E = float(career.get('interest_enterprising') or 0)
    C = float(career.get('interest_conventional') or 0)

    # Map profile to RIASEC — use max() so dominant interest isn't diluted
    p_R = min(max(profile.get('physical',0), profile.get('building',0), profile.get('outdoors',0), profile.get('R',0)) / 9.0, 1.0) * 7
    p_I = min(max(profile.get('science',0), profile.get('data',0), profile.get('analyzing',0), profile.get('I',0)) / 9.0, 1.0) * 7
    p_A = min(max(profile.get('creativity',0), profile.get('creating',0), profile.get('A',0)) / 9.0, 1.0) * 7
    p_S = min(max(profile.get('helping',0), profile.get('people',0), profile.get('teaching',0), profile.get('S',0)) / 9.0, 1.0) * 7
    p_E = min(max(profile.get('leadership',0), profile.get('business',0), profile.get('E',0)) / 9.0, 1.0) * 7
    # Stability contributes to C but at reduced weight so it doesn't override interest
    p_C = min(max(profile.get('data',0), profile.get('C',0), profile.get('stability',0) * 0.3) / 9.0, 1.0) * 7

    vals = [('R',p_R,R), ('I',p_I,I), ('A',p_A,A), ('S',p_S,S), ('E',p_E,E), ('C',p_C,C)]

    # Find dominant profile trait — give it 2.5x weight
    dominant_key = max(vals, key=lambda x: x[1])[0]

    score = 0.0; max_score = 0.0
    for key, p_val, c_val in vals:
        weight = 25.0 if key == dominant_key else 8.0
        max_score += weight
        score += (1.0 - abs(p_val - c_val) / 7.0) * weight

    result = round((score / max_score) * 100) if max_score > 0 else 0

    # Reduce score for jobs with no salary data (minor/niche occupations)
    if not float(career.get('median_annual') or 0):
        result = round(result * 0.65)

    return result


def run_match(gpa, sat, act, state, size, ctrl, need, env, study_yrs, aid, n, majors_input='', only_gpa=False, only_adm=False):
    size_codes={'any':[1,2,3,4,5],'small':[1,2],'medium':[3,4],'large':[5]}.get(size,[1,2,3,4,5])
    results=[]

    # Parse majors input into CIP codes for filtering
    # Strategy: try full phrase first, then individual words
    # This prevents "computer" matching everything under "computer"
    major_cips_filter = set()
    if majors_input:
        raw_majors = [x.strip().lower() for x in majors_input.replace(';',',').split(',')]
        for major in raw_majors:
            if not major: continue
            matched = False
            # 1. Exact full phrase match
            if major in KEYWORD_MAP:
                major_cips_filter.update(KEYWORD_MAP[major])
                matched = True
            # 2. Full phrase is substring of a keyword
            if not matched:
                for keyword, cips in KEYWORD_MAP.items():
                    if major in keyword or keyword in major:
                        major_cips_filter.update(cips)
                        matched = True
                        break
            # 3. Word-by-word only if no phrase match and words are meaningful (5+ chars)
            if not matched:
                words = [w for w in major.split() if len(w) >= 5]
                for w in words:
                    for keyword, cips in KEYWORD_MAP.items():
                        if w in keyword:
                            major_cips_filter.update(cips)
                            break
    # Only filter by major if we actually found CIP codes
    # If student typed a career ("lawyer") not a major, don't block colleges
    use_major_filter = len(major_cips_filter) > 0

    for s in SCHOOLS:
        # Filter by major — only show schools that offer it
        if use_major_filter:
            school_cips = set(str(s.get('major_cips','') or '').split(','))
            if not major_cips_filter.intersection(school_cips):
                continue
        state_list = state if isinstance(state, list) else ([state] if state != 'any' else [])
        if state_list and s['state'] not in state_list: continue
        if s['size'] not in size_codes: continue
        s_ctrl = s.get('ctrl')
        try: s_ctrl = int(s_ctrl)
        except: pass
        if ctrl == 'public' and s_ctrl not in [1,'1']: continue
        if ctrl == 'private' and s_ctrl not in [2,'2']: continue
        # Exclude for-profit schools by default (ctrl=3)
        if ctrl == 'any' and s_ctrl == 3: continue
        tin = s.get('tin') or 0
        if tin <= 0: continue
        # Data quality filters
        if only_gpa and not (s.get('gpa_25') or s.get('gpa_avg')): continue
        if only_adm and (not s.get('adm') or s.get('adm') != s.get('adm')): continue
        if s.get('size',0) < 0: continue
        if need=='full' and tin > 55000: continue
        if env=='hbcu' and not s.get('hbcu'): continue
        # Only filter 2yr schools if student explicitly chose
        if study_yrs=='4yr' and s.get('yr2'): continue
        if study_yrs=='2yr' and not s.get('yr2'): continue
        fit = get_fit(sat, act, s, gpa)
        net = max(0, tin - aid['total']) if tin > 0 else None
        adm_val = s.get('adm')
        adm_display = f"{float(adm_val):.1f}%" if adm_val and adm_val==adm_val else "Acceptance rate N/A"
        sticker = int(tin) if tin else 0
        dl = DEADLINES.get(s.get('id'),{})
        results.append({
            **s,
            'fit': fit,
            'net': net,
            'adm_display': adm_display,
            'sticker': sticker,
            'rd': dl.get('rd','Check website'),
            'ea': dl.get('ea',''),
            'ed': dl.get('ed',''),
            'sys': dl.get('sys',''),
        })
    fit_order={'safety':0,'match':1,'reach':2,'unknown':3}
    sort_mode = st.session_state.get('sort_multi', ['Best Fit'])

    # Natural balanced selection — like Niche
    # Pick from across the selectivity spectrum so student sees real options
    safeties = sorted([r for r in results if r['fit']=='safety'], key=lambda x: -(x.get('grad') or 0))
    matches  = sorted([r for r in results if r['fit']=='match'],  key=lambda x: -(x.get('grad') or 0))
    reaches  = sorted([r for r in results if r['fit']=='reach'],  key=lambda x: -(x.get('grad') or 0))
    unknowns = sorted([r for r in results if r['fit']=='unknown'], key=lambda x: x.get('net') or 999999)

    # Natural proportions — fill from each bucket, best schools first
    n_s = max(2, round(n * 0.25))
    n_m = max(3, round(n * 0.45))
    n_r = max(2, round(n * 0.25))

    selected = safeties[:n_s] + matches[:n_m] + reaches[:n_r]

    # Fill remaining slots if any category is short
    if len(selected) < n:
        used = set(id(r) for r in selected)
        for r in safeties + matches + reaches + unknowns:
            if id(r) not in used:
                selected.append(r)
                used.add(id(r))
            if len(selected) >= n: break

    # Apply sort mode
    sort_modes = sort_mode if isinstance(sort_mode, list) else [sort_mode]
    def multi_sort_key(x):
        keys = []
        for sm in sort_modes:
            if sm in ('fit','Best Fit'): keys.extend([fit_order.get(x['fit'],3), x.get('net') or 999999])
            elif sm in ('cost','Lowest Cost'): keys.extend([x.get('net') is None, x.get('net') or 999999])
            elif sm in ('safety','Safety First'): keys.append(fit_order.get(x['fit'],3))
            elif sm in ('grad','Grad Rate'): keys.append(-(x.get('grad') or 0))
        return keys
    selected = sorted(selected, key=multi_sort_key)

    return selected[:n]

# ── Career Match Runner ──────────────────────────────────────
# Scores all 1,016 careers against student profile
# Returns sorted list highest match first
def run_career_match(answers, direct_profile=None):
    # answers = dict of dicts from career questions
    # direct_profile = flat profile dict (from full test)
    if direct_profile:
        profile = direct_profile
    else:
        profile = {}
        for vals in answers.values():
            for k,v in vals.items(): profile[k]=profile.get(k,0)+v
    career_list = CAREERS_FULL if CAREERS_FULL else CAREERS
    scored=[]
    for c in career_list:
        fit = score_career_onet(c, profile) if CAREERS_FULL else score_career(c, profile)
        scored.append({**c, 'fit': fit})
    return sorted(scored, key=lambda x: x['fit'], reverse=True)

# ── PDF GENERATOR ─────────────────────────────────────────────
# ════════════════════════════════════════════════════════════
# SECTION 6: PDF GENERATOR
# Creates downloadable college list + aid summary
# Uses reportlab library
# ════════════════════════════════════════════════════════════
def generate_pdf(my_list, aid, career_top, gpa, sat, act):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import inch

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()
        story = []

        GOLD   = colors.HexColor('#C9923A')
        DARK   = colors.HexColor('#0D1B2A')
        GREEN  = colors.HexColor('#2A6049')
        GRAY   = colors.HexColor('#6B7A8D')

        title_style = ParagraphStyle('title', parent=styles['Title'],
                                     fontSize=24, textColor=DARK,
                                     spaceAfter=4, fontName='Helvetica-Bold')
        sub_style   = ParagraphStyle('sub', parent=styles['Normal'],
                                     fontSize=11, textColor=GRAY, spaceAfter=12)
        head_style  = ParagraphStyle('head', parent=styles['Heading2'],
                                     fontSize=14, textColor=DARK,
                                     spaceBefore=16, spaceAfter=6,
                                     fontName='Helvetica-Bold')
        body_style  = ParagraphStyle('body', parent=styles['Normal'],
                                     fontSize=10, textColor=DARK, spaceAfter=4)
        small_style = ParagraphStyle('small', parent=styles['Normal'],
                                     fontSize=9, textColor=GRAY, spaceAfter=2)

        # Header
        story.append(Paragraph("🎓 Pathways by SLN", title_style))
        story.append(Paragraph("Personalized College Guidance Report", sub_style))
        story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=12))

        # Profile summary
        story.append(Paragraph("Your Profile", head_style))
        profile_info = f"GPA: <b>{gpa}</b>"
        if sat: profile_info += f"  |  SAT: <b>{sat}</b>"
        if act: profile_info += f"  |  ACT: <b>{act}</b>"
        if career_top: profile_info += f"  |  Top Career Match: <b>{career_top}</b>"
        story.append(Paragraph(profile_info, body_style))

        # Aid summary
        story.append(Paragraph("Estimated Annual Financial Aid", head_style))
        aid_data = [
            ['Program', 'Amount', 'Status'],
            ['Federal Pell Grant', f"${aid['pell']:,}" if aid['pell']>0 else '—', 'Eligible' if aid['pell']>0 else 'Not eligible'],
            ['NY State TAP', f"${aid['tap']:,}" if aid['tap']>0 else '—', 'Eligible' if aid['tap']>0 else 'Not eligible'],
            ['NYS Dream Act', f"${aid['dream']:,}" if aid['dream']>0 else '—', 'Eligible' if aid['dream']>0 else 'Not eligible'],
            ['HEOP', 'Varies', 'Eligible' if aid['heop'] else 'Not eligible'],
            ['TOTAL GRANTS', f"${aid['total']:,}/year", 'Does not need to be repaid'],
        ]
        aid_table = Table(aid_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        aid_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), DARK),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 9),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E8F4EE')),
            ('FONTNAME',   (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR',  (0,-1), (-1,-1), GREEN),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F7F3EE')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0D8CE')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(aid_table)

        # College list
        story.append(Paragraph("Your College List", head_style))

        # Balance summary
        safety_n = sum(1 for s in my_list if s.get('fit')=='safety')
        match_n  = sum(1 for s in my_list if s.get('fit')=='match')
        reach_n  = sum(1 for s in my_list if s.get('fit')=='reach')
        story.append(Paragraph(
            f"<b>List Balance:</b> {safety_n} Safety &nbsp;|&nbsp; {match_n} Match &nbsp;|&nbsp; {reach_n} Reach  ({len(my_list)} total)",
            body_style))
        story.append(Spacer(1, 8))

        if my_list:
            college_data = [['#', 'College', 'Fit', 'Sticker', 'You Pay/yr', 'RD Deadline']]
            fit_colors_map = {'safety': colors.HexColor('#E8F5E9'),
                              'match':  colors.HexColor('#FFF8E1'),
                              'reach':  colors.HexColor('#FFEBEE'),
                              'unknown':colors.HexColor('#F5F5F5')}
            row_colors = []
            for i, s in enumerate(my_list, 1):
                fit   = s.get('fit','unknown')
                net   = f"${s['net']:,}" if s.get('net') is not None else 'N/A'
                sticker = f"${s.get('tin',0):,}" if s.get('tin') else 'N/A'
                dl    = DEADLINES.get(s['id'], {"rd":"Check website"})
                college_data.append([
                    str(i),
                    s['name'],
                    fit.capitalize(),
                    sticker,
                    net,
                    dl.get('rd','Check website'),
                ])
                row_colors.append(fit_colors_map.get(fit, colors.white))

            col_table = Table(college_data, colWidths=[0.3*inch,2.4*inch,0.7*inch,0.8*inch,0.8*inch,0.9*inch])
            table_style = [
                ('BACKGROUND', (0,0), (-1,0), DARK),
                ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 8),
                ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#E0D8CE')),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING',   (0,0), (-1,-1), 6),
            ]
            for i, rc in enumerate(row_colors, 1):
                table_style.append(('BACKGROUND', (0,i), (-1,i), rc))
            col_table.setStyle(TableStyle(table_style))
            story.append(col_table)
        else:
            story.append(Paragraph("No colleges added to list yet.", body_style))

        # Footer
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E0D8CE')))
        story.append(Paragraph(
            "Pathways by SLN · Built on IPEDS 2023-24 Federal Data · Aid thresholds: 2025-26 · Always verify deadlines on official college websites",
            small_style))

        doc.build(story)
        buf.seek(0)
        return buf
    except ImportError:
        return None

# ── CAREER MAPS ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════
# SECTION 7b: EOP / OPPORTUNITY PROGRAMS DATA
# EOP = Educational Opportunity Program (SUNY system)
# Source: Alex H. file — eop_schools.csv
# Format: unitid, school_name, program_name, program_type
# program_type: EOP | HEOP | SEEK | CD | AIM
# To activate: upload eop_schools.csv to GitHub repo
# Contact: ahawn@studentleadershipnetwork.org
# ════════════════════════════════════════════════════════════
def load_eop_data():
    import os, csv
    eop = {}  # unitid -> list of program names
    if not os.path.exists('eop_schools.csv'):
        return eop
    try:
        with open('eop_schools.csv', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                uid = str(row.get('unitid','')).strip()
                prog = str(row.get('program_type','EOP')).strip()
                if uid:
                    if uid not in eop:
                        eop[uid] = []
                    eop[uid].append(prog)
    except Exception as e:
        pass
    return eop

EOP_DATA = load_eop_data()
if EOP_DATA:
    print(f"EOP data loaded: {len(EOP_DATA)} schools")

# ── SLN School Whitelist ─────────────────────────────────────
# Schools that should always appear in results for NY students
# regardless of other filters — key partner/recommended schools
# Add IPEDS unitid to include a school. Update with Aaron/Kieran.
SLN_WHITELIST = {
    # CUNY system
    190512,  # CUNY City College
    190549,  # CUNY Hunter College
    190558,  # CUNY John Jay College
    190576,  # CUNY Lehman College
    190600,  # CUNY Queens College
    190615,  # CUNY Brooklyn College
    190624,  # CUNY Baruch College
    190099,  # CUNY Bronx Community College
    # SUNY system
    196060,  # SUNY Albany
    196097,  # Binghamton University
    196105,  # University at Buffalo
    196183,  # Stony Brook University
    196200,  # SUNY Geneseo
    # Key NY private schools
    193900,  # NYU
    190150,  # Columbia University
    194824,  # Fordham University
    # HBCUs
    206695,  # Howard University (DC)
    216010,  # Spelman College (GA)
}

# ── Career Assessment Question Maps ─────────────────────────
# Maps each dropdown answer to RIASEC trait scores
# To add a new question: add 'i9' here and a selectbox in the UI
# Values are 0-9 scale — higher = stronger signal
CAREER_MAPS = {
    'i1': {
        "Helping and healing people":        {"helping":9,"people":7,"S":9},
        "Building and fixing things":        {"physical":9,"building":9,"R":9},
        "Teaching and shaping communities":  {"teaching":9,"people":7,"S":8},
        "Running businesses and managing":   {"business":9,"leadership":8,"E":9},
        "Creating and designing things":     {"creating":9,"creativity":9,"A":9},
        "Researching and analyzing data":    {"analyzing":9,"data":9,"science":7,"I":9}
    },
    'i2': {
        "High income":                       {"income":9},
        "Making a real difference":          {"impact":9,"helping":7},
        "Creative freedom":                  {"creativity":9,"autonomy":9},
        "Stability and security":            {"stability":9},
        "Prestige and recognition":          {"prestige":9,"leadership":7}
    },
    'i3': {
        "With people (patients, students)":  {"people":9,"helping":7,"S":8},
        "At a desk or computer":             {"data":7,"analyzing":7,"C":7},
        "Out in the field or moving around": {"outdoors":9,"physical":9,"R":8},
        "In a lab, hospital, or studio":     {"science":8,"creating":6,"I":7},
        "Anywhere remote or flexible":       {"autonomy":9}
    },
    'i4': {
        "Science or Math":                   {"science":9,"data":7,"I":8},
        "English, Writing, Communication":   {"creating":7,"people":6,"A":6},
        "Art, Music, or Design":             {"creativity":9,"creating":9,"A":9},
        "Social Studies or History":         {"people":7,"teaching":7,"S":7},
        "Technology or Computer Science":    {"building":8,"data":9,"I":8},
        "Physical Education or Health":      {"physical":9,"helping":7,"R":7}
    },
    'i5': {
        "1-2 years (start earning soon)":    {"stability":7,"R":5},
        "4 years (bachelor degree)":         {"income":5},
        "6-8 years (graduate school)":       {"prestige":7,"income":6},
        "Whatever it takes":                 {"prestige":9,"income":9}
    },
    'i6': {
        "I love working with my hands":      {"physical":9,"building":8,"R":9},
        "I love understanding people":       {"people":9,"helping":9,"S":9},
        "I love solving complex problems":   {"analyzing":9,"data":9,"I":9},
        "I love building or making things":  {"creating":9,"building":8,"A":7},
        "I love organizing and leading":     {"leadership":9,"business":8,"E":9}
    },
    'i7': {"Running my own business":{"autonomy":3,"leadership":3},"Recognized expert in my field":{"prestige":3,"science":2},"Making a meaningful community impact":{"impact":3,"helping":3},"Financially secure":{"stability":3,"income":3},"Doing creative work I am proud of":{"creativity":3,"creating":3}},
    'i8': {"Fast-paced with new challenges":{"variety":3,"leadership":2},"Steady and predictable":{"stability":3,"routine":2},"Collaborative team work":{"people":2,"team":3},"Independent, working alone":{"autonomy":3,"analyzing":2},"Helping individuals one-on-one":{"helping":3,"people":3}},
}
IMMIG_MAP = {"US Citizen or Green Card":"citizen","DACA":"daca","Undocumented":"undocumented","Visa or other status":"other"}
SIZE_MAP  = {"Any":"any","Small (<5k)":"small","Medium (5-20k)":"medium","Large (20k+)":"large"}
CTRL_MAP  = {"Any":"any","Public":"public","Private":"private"}
ENV_MAP   = {"Any":"any","HBCU":"hbcu","Women's College":"womens","Diverse":"diverse"}
YRS_MAP   = {"Any":"any","2 years (Associate)":"2yr","4 years (Bachelor's+)":"4yr"}

# ── UI ────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown("# 🎓 Pathways by SLN")
    # Dynamic subtitle based on active filters
    _filt = []
    _states = st.session_state.get('states_multi', [])
    _gpa_f = st.session_state.get('filter_gpa', False)
    _adm_f = st.session_state.get('filter_adm', False)
    _maj = st.session_state.get('majors_input', '')
    if _states: _filt.append(f"{', '.join(_states)}")
    if _gpa_f: _filt.append("verified GPA data only")
    if _adm_f: _filt.append("published acceptance rate only")
    if _maj: _filt.append(f"offering {_maj}")
    if _filt:
        st.markdown(f"*Your college list, built around your life. Filtered: **{' · '.join(_filt)}** · from IPEDS 2023-24.*")
    else:
        st.markdown(f"*Your college list, built around your life. Browsing **{len(SCHOOLS):,} US colleges** from IPEDS 2023-24.*")
with col_h2:
    st.caption("Built by SLN RITA Tech & Data Intern\nIPEDS 2023-24 · Aid thresholds 2025-26")
st.divider()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📝 Your Profile")

    st.markdown("### 📚 Academics")
    gpa_scale = st.radio("GPA scale", ["4.0 scale","100 scale"], horizontal=True, key="gpa_scale_radio")
    if gpa_scale == "4.0 scale":
        gpa = st.slider("Unweighted GPA (4.0 scale)", 0.0, 4.0, 3.0, 0.1, key="gpa_slider")
        gpa_display = f"{gpa:.1f} / 4.0"
    else:
        gpa_100 = st.slider("Unweighted GPA (100 scale)", 0, 100, 80, 1, key="gpa_slider_100")
        gpa = round(gpa_100 / 25.0, 2)
        gpa_display = f"{gpa_100} / 100  (= {gpa:.1f} on 4.0 scale)"
    st.caption(f"Your GPA: **{gpa_display}**")
    score_type = st.selectbox("Test scores", ["None (test-optional)","SAT","ACT"], key="test_scores")
    sat = act = None
    if score_type == "SAT":
        sat = st.number_input("SAT Score", 400, 1600, 1100, 10)
    elif score_type == "ACT":
        act = st.number_input("ACT Score", 1, 36, 24, 1)

    st.markdown("### 🎯 Career Discovery")

    # Majors of interest
    majors_input = st.text_input(
        "📚 Majors you're interested in",
        placeholder="e.g. Nursing, Computer Science, Business",
        help="Add one or more majors — we'll show careers that match"
    , key="majors_input")

    st.caption("Or answer these questions to discover careers:")
    q1 = st.selectbox("What excites you most?",["— Select an answer —"] + list(CAREER_MAPS['i1'].keys()), key="q1")
    q2 = st.selectbox("What matters most in a career?",["— Select an answer —"] + list(CAREER_MAPS['i2'].keys()), key="q2")
    q3 = st.selectbox("Where do you want to work?",["— Select an answer —"] + list(CAREER_MAPS['i3'].keys()), key="q3")
    q4 = st.selectbox("Best subject in school?",["— Select an answer —"] + list(CAREER_MAPS['i4'].keys()), key="q4")
    q5 = st.selectbox("How long willing to study?",["— Select an answer —"] + list(CAREER_MAPS['i5'].keys()), key="q5")
    q6 = st.selectbox("Which describes you best?",["— Select an answer —"] + list(CAREER_MAPS['i6'].keys()), key="q6")
    q7 = st.selectbox("In 10 years I see myself...",["— Select an answer —"] + list(CAREER_MAPS['i7'].keys()), key="q7")
    q8 = st.selectbox("Best work environment?",["— Select an answer —"] + list(CAREER_MAPS['i8'].keys()), key="q8")

    st.markdown("### 💰 Financial Aid")
    income    = st.number_input("Annual household income ($)", 0, 500000, 42000, 1000)
    hsize     = st.slider("Household size", 1, 10, 4, key="household_slider")
    ny_res    = st.checkbox("NY State resident (12+ months)", value=True, key="ny_res")
    immig     = st.selectbox("Immigration/citizenship status",list(IMMIG_MAP.keys()), key="immig")
    first_gen = st.checkbox("First-generation college student", value=True, key="first_gen")

    st.markdown("### 🗺️ Preferences")
    states_list = ["NY","NJ","CT","PA","MA","CA","TX","FL","IL","GA","VA","MD","NC","OH","MI","WA","CO","AZ","MN","WI","OR","IN","TN","MO","SC","AL","LA","KY","OK","UT","IA","AR","MS","KS","NV","NM","NE","ID","HI","NH","ME","RI","MT","DE","SD","ND","AK","VT","WY","WV","DC","PR"]
    state_pref = st.multiselect("Preferred state(s)", states_list, default=["NY"], help="Select one or more states. Leave empty to search all states.", key="states_multi")
    school_size = st.selectbox("School size",["Any","Small (<5k)","Medium (5-20k)","Large (20k+)"], key="school_size")
    school_type = st.selectbox("School type",["Any","Public","Private"], key="school_type")
    env_pref    = st.selectbox("Campus environment",["Any","HBCU","Women's College","Diverse"], key="campus_env")

    st.markdown("**🔍 Data quality filters**")
    only_gpa_data = st.checkbox("Only schools with verified GPA ranges", value=False, key="filter_gpa",
        help="Shows only schools where Peterson's 2025 has admitted GPA data — more accurate Safety/Match/Reach")
    only_adm_data = st.checkbox("Only schools with published acceptance rate", value=False, key="filter_adm",
        help="Hides schools that don't publish how many students they accept")
    study_yrs   = st.selectbox("Degree level",["Any","Associate's (2 yr)","Bachelor's or higher (4 yr+)"], key="study_yrs")
    n_results   = st.select_slider("Number of results",[5,10,15,20],10, key="n_results_slider")

    run_btn = st.button("🔍 Find My Colleges", type="primary", use_container_width=True)

# ── PROCESS ───────────────────────────────────────────────────
# Only score careers if all 8 questions are answered
_all_answered = all(q != "— Select an answer —" for q in [q1,q2,q3,q4,q5,q6,q7,q8])
if _all_answered:
    career_answers = {
        'i1':CAREER_MAPS['i1'][q1],'i2':CAREER_MAPS['i2'][q2],
        'i3':CAREER_MAPS['i3'][q3],'i4':CAREER_MAPS['i4'][q4],
        'i5':CAREER_MAPS['i5'][q5],'i6':CAREER_MAPS['i6'][q6],
        'i7':CAREER_MAPS['i7'][q7],'i8':CAREER_MAPS['i8'][q8],
    }
    career_results = run_career_match(career_answers)
    st.session_state.career_results = career_results
else:
    career_results = st.session_state.get('career_results', [])
top = career_results[0] if career_results else None

aid = calculate_aid(income, hsize, ny_res, IMMIG_MAP[immig], first_gen)
st.session_state.aid = aid

if run_btn:
    state_val = state_pref if state_pref else ['NY']  # default to NY if nothing selected
    need_val  = "full" if income<50000 else "some"
    matches = run_match(gpa, sat, act, state_val,
                        SIZE_MAP[school_size], CTRL_MAP[school_type],
                        need_val, ENV_MAP[env_pref], YRS_MAP[study_yrs], aid, n_results,
                        majors_input=st.session_state.get('college_major_filter',''),
                        only_gpa=only_gpa_data, only_adm=only_adm_data)
    st.session_state.matches  = matches
    st.session_state.ran_match = True
    st.session_state.gpa = gpa
    st.session_state.sat = sat
    st.session_state.act = act

matches = st.session_state.matches

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏫 College Matches",
    "🎯 Career Results",
    "💰 Aid Eligibility",
    "📋 My College List"
])

# ── TAB 1: COLLEGE MATCHES ────────────────────────────────────
with tab1:
    if not st.session_state.ran_match:
        st.info("👈 Fill in your profile on the left and click **Find My Colleges**.")
    else:
        m = matches
        c1,c2,c3,c4 = st.columns(4)
        # Build dynamic filter description
        filter_parts = []
        if state_pref: filter_parts.append(f"{',' .join(state_pref)} schools")
        if school_type != 'Any': filter_parts.append(school_type.lower())
        if school_size != 'Any': filter_parts.append(school_size.lower())
        if majors_input: filter_parts.append(f"offering {majors_input}")
        if only_gpa_data: filter_parts.append("with verified GPA data")
        if only_adm_data: filter_parts.append("with published acceptance rate")
        filter_desc = " · ".join(filter_parts) if filter_parts else "all states"
        st.caption(f"Showing **{len(m)} schools** — {filter_desc}")
        c1.metric("Colleges Found", len(m))
        c2.metric("Est. Annual Aid", f"${aid['total']:,}")
        safety_n=sum(1 for s in m if s['fit']=='safety')
        match_n =sum(1 for s in m if s['fit']=='match')
        reach_n =sum(1 for s in m if s['fit']=='reach')
        c3.metric("Safety / Match / Reach", f"{safety_n} / {match_n} / {reach_n}")
        c4.metric("Top Career Match", top['name'] if top and _all_answered else "Answer career questions →")
        st.divider()

        # Test score nudge
        if not sat and not act:
            st.info("💡 **Tip:** Adding your SAT or ACT score makes your Safety/Match/Reach analysis much more accurate. Test scores are optional — but they give you a clearer picture of where you stand at each school.")

        # Sort buttons

        # ── Sort & View ──────────────────────────────────────────
        sort_opts = st.multiselect(
            "Sort by (first = primary sort):",
            ["Best Fit", "Lowest Cost", "Safety First", "Grad Rate"],
            default=["Best Fit"],
            key="sort_multi",
            help="Pick up to 2 — combine Safety First + Lowest Cost to find affordable safeties"
        )

        # View toggle
        view_mode = st.radio("View as", ["📋 Cards", "📊 Table"], horizontal=True, key="view_mode")
        st.caption("📊 Data: IPEDS 2023-24 · Peterson's 2025 · Aid: Federal & NY HESC 2026-27")
        st.markdown("---")

        # Apply multi-sort
        fit_order = {'safety':0,'match':1,'reach':2,'unknown':3}
        def aaron_default_sort(x, _state_val=state_val):
            """
            SLN default sort — Aaron Hawn's recommended exploration order:
            1. In-state first (NY students see NY schools first)
            2. 4-year before 2-year (bachelor's path prioritized)
            3. Highest reasonable selectivity sweet spot:
               - Prioritize high targets + low reaches (most motivating, realistic)
               - Safeties shown but not buried
            4. Strong completion outcomes (grad rate as tiebreaker)
            Based on Hossler & Gallagher (1987) college choice theory:
            students explore best when shown aspirational but achievable options first.
            """
            # 1. In-state preference (NY first for NY students)
            state_val_list = _state_val if isinstance(_state_val, list) else [_state_val]
            primary_state = state_val_list[0] if state_val_list and state_val_list[0] != 'any' else 'NY'
            in_state = 0 if x.get('state') == primary_state else 1

            # 2. Degree level (4-year = 0, 2-year = 1)
            is_2yr = 1 if x.get('yr2') else 0

            # 3. Selectivity sweet spot
            # match=0 (ideal), reach=1 (aspirational), safety=2 (fallback), unknown=3
            fit = x.get('fit', 'unknown')
            fit_sweet = {'match': 0, 'reach': 1, 'safety': 2, 'unknown': 3}.get(fit, 3)

            # Within reach — prefer low reaches (adm 25-50%) over long reaches (<10%)
            adm = x.get('adm') or 50
            if fit == 'reach':
                # Lower acceptance = harder reach = sort later within reach tier
                reach_difficulty = 0 if adm >= 25 else 1 if adm >= 15 else 2
            else:
                reach_difficulty = 0

            # 4. Completion outcomes (higher grad rate = better)
            grad = -(x.get('grad') or 0)

            return [in_state, is_2yr, fit_sweet, reach_difficulty, grad]

        def sort_key(x):
            # If student selected a custom sort, use that
            # Otherwise use Aaron's default exploration sort
            if sort_opts and sort_opts != ["Best Fit"]:
                keys = []
                for sm in sort_opts:
                    if sm == "Best Fit": keys.extend([fit_order.get(x['fit'],3), x.get('net') or 999999])
                    elif sm == "Lowest Cost": keys.extend([x.get('net') is None, x.get('net') or 999999])
                    elif sm == "Safety First": keys.append(fit_order.get(x['fit'],3))
                    elif sm == "Grad Rate": keys.append(-(x.get('grad') or 0))
                return keys
            else:
                return aaron_default_sort(x)

        matches = sorted(matches, key=sort_key)

        # ── TABLE VIEW ───────────────────────────────────────────
        if view_mode == "📊 Table":
            import pandas as _pd
            table_rows = []
            for s in matches:
                fit = s.get('fit','unknown')
                fit_label = {'safety':'✅ Safety','match':'🎯 Match','reach':'⚠️ Reach','unknown':'⚪ No data'}.get(fit,fit)
                table_rows.append({
                    'School': s.get('name',''),
                    'State': s.get('state',''),
                    'Fit': fit_label,
                    'You Pay/yr': f"${int(s.get('net') or 0):,}" if s.get('net') is not None else 'N/A',
                    'Sticker': f"${int(s.get('tin') or 0):,}" if s.get('tin') else 'N/A',
                    'Acceptance %': f"{s['adm']:.0f}%" if s.get('adm') and s['adm']==s['adm'] else 'N/A',
                    'SAT Range': f"{int(s['sat25'])}–{int(s['sat75'])}" if s.get('sat25') else 'N/A',
                    'GPA Range': f"{s['gpa_25']}–{s['gpa_75']}" if s.get('gpa_25') else 'N/A',
                    'Grad Rate': f"{int(s['grad'])}%" if s.get('grad') else 'N/A',
                    'Type': 'Public' if s.get('ctrl')==1 else 'Private',
                    'RD Deadline': s.get('rd','Check website'),
                })
            df = _pd.DataFrame(table_rows)
            st.dataframe(df, use_container_width=True, hide_index=True,
                column_config={
                    "School": st.column_config.TextColumn(width="large"),
                    "You Pay/yr": st.column_config.TextColumn(help="After your estimated aid"),
                })
            csv_data = df.to_csv(index=False)
            st.download_button("⬇️ Download as spreadsheet", csv_data,
                file_name="my_college_list.csv", mime="text/csv", key="dl_csv")

        else:
            # ── CARD VIEW ────────────────────────────────────────
            fit_icons = {'safety':'🟢','match':'🎯','reach':'⚠️','unknown':'⚪'}
            for s in matches:
                fit = s.get('fit','unknown')
                sat25 = s.get('sat25'); sat75 = s.get('sat75')
                act25 = s.get('act25'); act75 = s.get('act75')
                in_list = any(x['id']==s['id'] for x in st.session_state.my_list)

                with st.container():
                    ca,cb,cc = st.columns([3,1.5,1])
                    with ca:
                        st.markdown(f"**{fit_icons.get(fit,'⚪')} [{s['name']}]({s.get('web','#')})**")
                        env_tags = get_env_fit(s, env_pref, school_size, school_type)
                        env_tag_str = ' · '.join(env_tags[:3]) if env_tags else ''
                        adm_val = s.get('adm'); adm_display = f"{float(adm_val):.1f}% acceptance" if adm_val and adm_val == adm_val else "Acceptance rate N/A"
                        st.caption(f"{s.get('city','')}, {s['state']} · {adm_display} · {env_tag_str}" + (" · 🏛️ HBCU" if s.get('hbcu') else ""))
                        # Major badge
                        _majors_typed = majors_input.strip() if majors_input else ''
                        if _majors_typed and s.get('major_cips'):
                            st.success(f"✅ Confirmed offers: {_majors_typed}")
                        # Academic match chips
                        fit_label = {'safety':'✅ Safety','match':'🎯 Match','reach':'⚠️ Reach','unknown':'⚪ Limited data'}.get(fit, fit)
                        acad_chips = f"`{fit_label}`"
                        if sat and sat25 and sat75:
                            acad_chips += f"  `SAT {s['sat25']}–{s['sat75']}`"
                        elif s.get('act25') and act:
                            acad_chips += f"  `ACT {s['act25']}–{s['act75']}`"
                        elif s.get('gpa_25') and gpa:
                            acad_chips += f"  `GPA {s['gpa_25']}–{s['gpa_75']}`"
                        elif s.get('gpa_avg') and gpa:
                            acad_chips += f"  `Avg GPA {s['gpa_avg']}`"
                        elif s.get('adm'):
                            acad_chips += f"  `{s['adm']:.0f}% acceptance`"
                        else:
                            acad_chips += "  `⚠️ Limited data`"
                        st.markdown(f"**Academic match:** {acad_chips}")
                        # Aid & fit chips
                        aid_chips = ""
                        if aid['tap']>0 and s['state']=='NY': aid_chips += "  `TAP eligible`"
                        if aid['heop'] and s['state']=='NY': aid_chips += "  `HEOP`"
                        school_uid = str(s.get('id',''))
                        if school_uid in EOP_DATA:
                            for prog in EOP_DATA[school_uid]:
                                aid_chips += f"  `{prog}`"
                        if s.get('hbcu'): aid_chips += "  `HBCU`"
                        if s.get('womens'): aid_chips += "  `Women's college`"
                        if aid_chips: st.markdown(f"**Aid & fit:** {aid_chips.strip()}")
                    with cb:
                        sticker = int(s.get('tin') or 0)
                        net = int(s.get('net') or 0)
                        st.markdown(f"**Sticker:** ${sticker:,}" if sticker else "**Sticker:** N/A")
                        st.markdown(f"**You pay:** ${net:,}/yr" if s.get('net') is not None else "**You pay:** N/A")
                        grad = s.get('grad')
                        st.markdown(f"**Grad rate:** {int(grad)}%" if grad else "**Grad rate:** N/A")
                        rd = s.get('rd','Check website')
                        st.markdown(f"**RD:** {rd}")
                    with cc:
                        if in_list:
                            st.success("✅ Added")
                        else:
                            if st.button("+ Add to list", key=f"add_{s['id']}", use_container_width=True):
                                st.session_state.my_list.append(s)
                                st.rerun()

                        fit_exp = ""
                        gpa_25s = s.get('gpa_25'); gpa_75s = s.get('gpa_75'); gpa_avgs = s.get('gpa_avg')
                        if sat and sat25 and sat75:
                            if fit=='safety': fit_exp = f"✅ **Safety** — Your SAT {sat} is above their range ({sat25}–{sat75})."
                            elif fit=='match': fit_exp = f"🎯 **Match** — Your SAT {sat} is in their range ({sat25}–{sat75})."
                            elif fit=='reach': fit_exp = f"⚠️ **Reach** — Their SAT range is {sat25}–{sat75}, yours is {sat}."
                        elif gpa and gpa_25s and gpa_75s:
                            if fit=='safety': fit_exp = f"✅ **Safety** — Your GPA {gpa} is above their 75th percentile ({gpa_75s})."
                            elif fit=='match': fit_exp = f"🎯 **Match** — Your GPA {gpa} falls in their range ({gpa_25s}–{gpa_75s})."
                            elif fit=='reach': fit_exp = f"⚠️ **Reach** — Their GPA range is {gpa_25s}–{gpa_75s}, yours is {gpa}. A strong application can still get you in."
                        elif gpa and gpa_avgs:
                            if fit=='safety': fit_exp = f"✅ **Safety** — Your GPA {gpa} is above their average ({gpa_avgs})."
                            elif fit=='match': fit_exp = f"🎯 **Match** — Your GPA {gpa} is near their average ({gpa_avgs})."
                            elif fit=='reach': fit_exp = f"⚠️ **Reach** — Their average GPA is {gpa_avgs}, yours is {gpa}."
                        elif s.get('adm'):
                            adm = s['adm']
                            if fit=='safety': fit_exp = f"✅ **Safety** — {adm:.0f}% of applicants are admitted."
                            elif fit=='match': fit_exp = f"🎯 **Match** — {adm:.0f}% acceptance rate — competitive but realistic."
                            elif fit=='reach': fit_exp = f"⚠️ **Reach** — Only {adm:.0f}% acceptance rate."
                        if fit_exp:
                            if fit=='safety': st.success(fit_exp)
                            elif fit=='match': st.info(fit_exp)
                            elif fit=='reach': st.warning(fit_exp)
                    st.divider()

    with tab2:
        # ── CAREER RESULTS TAB ──────────────────────────────────
        if CAREERS_FULL:
            st.caption(f"Career matching from {len(CAREERS_FULL):,} occupations across {len(set(c['field'] for c in CAREERS_FULL))} fields — O*NET 30.2 + BLS 2024")

        if majors_input and majors_input.strip():
            career_sub = "🔍 Explore any career"
        else:
            career_sub = st.radio("", ["🎯 Match me to careers", "🔍 Explore any career"], horizontal=True, label_visibility="collapsed", key="career_sub_radio")

        if career_sub == "🎯 Match me to careers":
            if not _all_answered:
                answered = sum(1 for q in [q1,q2,q3,q4,q5,q6,q7,q8] if q != "— Select an answer —")
                st.info(f"🎯 Answer the career questions on the left to see your matches. ({answered}/8 answered)")
                st.markdown("### Or take the full 20-question career assessment")
                with st.expander("▶️ Click to take the full career test", expanded=False):
                    st.markdown("**Rate how much you enjoy each activity (1 = not at all, 5 = very much)**")
                    full_q = {
                        "Build or repair electronic equipment": "R",
                        "Work on cars or machines": "R",
                        "Do physical outdoor work": "R",
                        "Use hand tools or power tools": "R",
                        "Study how plants or animals grow": "I",
                        "Do science experiments": "I",
                        "Analyze data or solve math problems": "I",
                        "Research topics in depth": "I",
                        "Create art, music, or writing": "A",
                        "Design websites, graphics, or videos": "A",
                        "Express yourself through creative projects": "A",
                        "Perform or present in front of others": "A",
                        "Help people with personal problems": "S",
                        "Teach or train others": "S",
                        "Work as part of a care team": "S",
                        "Volunteer in your community": "S",
                        "Lead a group or project": "E",
                        "Persuade or sell ideas to others": "E",
                        "Start or manage a business": "E",
                        "Compete to win in business situations": "E",
                    }
                    full_scores = {}
                    cols_q = st.columns(2)
                    for i, (activity, riasec) in enumerate(full_q.items()):
                        with cols_q[i % 2]:
                            val = st.slider(activity, 1, 5, 3, key=f"ft_{hash(activity) % 99999}")
                            full_scores[riasec] = full_scores.get(riasec, 0) + val
                    if st.button("🎯 See My Career Matches", type="primary", key="full_test_submit_btn"):
                        full_profile = {
                            'physical': full_scores.get('R',0)*2, 'building': full_scores.get('R',0)*2,
                            'outdoors': full_scores.get('R',0)*2, 'science': full_scores.get('I',0)*2,
                            'data': full_scores.get('I',0)*2, 'analyzing': full_scores.get('I',0)*2,
                            'creativity': full_scores.get('A',0)*2, 'creating': full_scores.get('A',0)*2,
                            'helping': full_scores.get('S',0)*2, 'people': full_scores.get('S',0)*2,
                            'teaching': full_scores.get('S',0)*2, 'leadership': full_scores.get('E',0)*2,
                            'business': full_scores.get('E',0)*2,
                        }
                        full_results = run_career_match({}, direct_profile=full_profile)
                        st.session_state.career_results = full_results
                        st.rerun()
            elif not career_results:
                st.info("Answer the career questions on the left to see your matches.")
            else:
                t = career_results[0]
                t_name = t.get('name') or t.get('title','')
                t_sal = t.get('salary_mid') or t.get('median_annual') or 0
                try: t_sal_int = int(float(t_sal))
                except: t_sal_int = 0
                t_growth = t.get('growth') or t.get('growth_pct','N/A')
                t_growth = 'N/A' if str(t_growth) in ['nan','None','','null'] else t_growth
                t_demand = t.get('demand') or t.get('outlook','N/A')
                t_field = t.get('field','')
                st.markdown(f"""
                <div style="background:#0D1B2A;border-radius:12px;padding:22px 26px;margin-bottom:20px;color:white">
                    <div style="font-size:11px;opacity:.4;margin-bottom:4px;letter-spacing:1px;text-transform:uppercase">Your best match</div>
                    <div style="font-size:26px;font-family:Georgia,serif;margin-bottom:5px">💼 {t_name}</div>
                    <div style="font-size:13px;opacity:.55;margin-bottom:12px">{t_field}</div>
                    <span style="color:#E8AD58;font-size:20px;font-weight:700">${t_sal_int:,}/yr avg</span>
                    &nbsp;&nbsp;
                    <span style="background:rgba(42,96,73,.4);padding:4px 12px;border-radius:8px;font-size:12px">{t_growth} growth</span>
                    &nbsp;
                    <span style="background:rgba(255,255,255,.1);padding:4px 12px;border-radius:8px;font-size:12px">{t_demand} demand</span>
                </div>
                """, unsafe_allow_html=True)

                for c in career_results[:10]:
                    name = c.get('name') or c.get('title','Unknown')
                    sal_mid = c.get('salary_mid') or c.get('median_annual') or 0
                    sal_entry = c.get('salary_entry') or c.get('entry_annual') or 0
                    sal_senior = c.get('salary_senior') or c.get('experienced_annual') or 0
                    growth = c.get('growth') or c.get('growth_pct','N/A')
                    growth = 'N/A' if str(growth) in ['nan','None','','null'] else growth
                    field = c.get('field','N/A')
                    education = c.get('education','N/A')
                    fit_pct = c.get('fit',0)
                    daily = str(c.get('daily_tasks','') or '')
                    tools = str(c.get('tech_tools','') or '')
                    try: sal_mid_int = int(float(sal_mid)) if sal_mid else 0
                    except: sal_mid_int = 0
                    try: sal_entry_int = int(float(sal_entry)) if sal_entry else 0
                    except: sal_entry_int = 0
                    try: sal_senior_int = int(float(sal_senior)) if sal_senior else 0
                    except: sal_senior_int = 0

                    with st.expander(f"💼 {name}  —  **{fit_pct}% match** · ${sal_mid_int:,}/yr"):
                        c1,c2,c3 = st.columns(3)
                        c1.metric("Entry", f"${sal_entry_int:,}" if sal_entry_int else "N/A")
                        c2.metric("Mid career", f"${sal_mid_int:,}" if sal_mid_int else "N/A")
                        c3.metric("Senior", f"${sal_senior_int:,}" if sal_senior_int else "N/A")
                        st.progress(fit_pct/100)
                        if daily:
                            st.markdown("**What you do:**")
                            for task in daily.split(' | ')[:3]:
                                if task.strip(): st.markdown(f"• {task.strip()}")
                        if tools:
                            tool_list = [t.strip() for t in tools.split(',') if t.strip()][:5]
                            if tool_list: st.caption(f"Tools: {', '.join(tool_list)}")
                        st.caption(f"Field: {field} · Growth: {growth} · Education: {education}")

        else:
            # ── EXPLORE ANY CAREER ───────────────────────────────
            st.markdown("### Explore any career")
            _pop = st.session_state.pop('pop_career', '')
            default_search = majors_input.strip() if majors_input and majors_input.strip() else _pop
            search_career = st.text_input("Search any career or job title",
                value=default_search,
                placeholder="e.g. Nurse, Software Engineer, Lawyer, Chef, Cybersecurity...",
                key="career_search")

            if search_career:
                search_lower = search_career.lower().strip()
                search_words = [w for w in search_lower.split() if len(w) > 2]

                # Direct major/career → O*NET title mapping
                MAJOR_TO_CAREER = {
                    "computer engineering":"Computer Hardware Engineers","software engineering":"Software Developers",
                    "electrical engineering":"Electrical Engineers","mechanical engineering":"Mechanical Engineers",
                    "civil engineering":"Civil Engineers","biomedical engineering":"Bioengineers and Biomedical Engineers",
                    "chemical engineering":"Chemical Engineers","industrial engineering":"Industrial Engineers",
                    "aerospace engineering":"Aerospace Engineers","nursing":"Registered Nurses",
                    "nurse":"Registered Nurses","rn":"Registered Nurses","pre-med":"Physicians, All Other",
                    "pre-nursing":"Registered Nurses","medicine":"Physicians, All Other","doctor":"Physicians, All Other",
                    "physician":"Physicians, All Other","dentist":"Dentists, All Other Specialists",
                    "pharmacy":"Pharmacists","physical therapy":"Physical Therapists",
                    "occupational therapy":"Occupational Therapists","dental hygiene":"Dental Hygienists",
                    "social work":"Social Workers, All Other","social worker":"Social Workers, All Other",
                    "psychology":"Psychologists, All Other","psychologist":"Psychologists, All Other",
                    "education":"Elementary School Teachers, Except Special Education",
                    "teaching":"Elementary School Teachers, Except Special Education",
                    "teacher":"Elementary School Teachers, Except Special Education",
                    "teach":"Elementary School Teachers, Except Special Education",
                    "early childhood education":"Preschool Teachers, Except Special Education",
                    "special education":"Special Education Teachers, All Other",
                    "accounting":"Accountants and Auditors","accountant":"Accountants and Auditors",
                    "finance":"Financial Analysts","financial advisor":"Personal Financial Advisors",
                    "business administration":"General and Operations Managers",
                    "management":"General and Operations Managers","marketing":"Marketing Managers",
                    "human resources":"Human Resources Specialists","criminal justice":"Police and Sheriff Patrol Officers",
                    "law":"Lawyers","lawyer":"Lawyers","attorney":"Lawyers","paralegal":"Paralegals and Legal Assistants",
                    "graphic design":"Graphic Designers","architecture":"Architects, Except Landscape and Naval",
                    "urban planning":"Urban and Regional Planners","data science":"Data Scientists",
                    "cybersecurity":"Information Security Analysts","information technology":"Computer User Support Specialists",
                    "computer science":"Software Developers","biology":"Biological Scientists, All Other",
                    "bio":"Biological Scientists, All Other","chemistry":"Chemists","chem":"Chemists",
                    "environmental science":"Environmental Scientists and Specialists, Including Health",
                    "public health":"Epidemiologists","nutrition":"Dietitians and Nutritionists",
                    "communications":"Public Relations Specialists","comm":"Public Relations Specialists",
                    "journalism":"News Analysts, Reporters, and Journalists","film":"Producers and Directors",
                    "music":"Musicians and Singers","dance":"Dancers","theater":"Actors",
                    "fashion":"Fashion Designers","interior design":"Interior Designers",
                    "construction management":"Construction Managers","culinary":"Chefs and Head Cooks",
                    "chef":"Chefs and Head Cooks","radiologist":"Radiologists",
                    "cop":"Police and Sheriff Patrol Officers","police":"Police and Sheriff Patrol Officers",
                    "firefighter":"Firefighters","emt":"Emergency Medical Technicians",
                    "paramedic":"Paramedics","therapist":"Mental Health Counselors",
                    "counselor":"Mental Health Counselors","web developer":"Web Developers",
                    "game design":"Software Developers","product manager":"Project Management Specialists",
                    "real estate":"Real Estate Sales Agents","animator":"Special Effects Artists and Animators",
                }

                # Layer 1: check direct mapping first
                direct_match = None
                for key, career_title in MAJOR_TO_CAREER.items():
                    if key == search_lower or key in search_lower or search_lower in key:
                        for c in (CAREERS_FULL or []):
                            if career_title.lower() in c.get('title','').lower():
                                direct_match = c
                                break
                        if direct_match:
                            break

                import re as _re
                def _matches(term, career):
                    # Check title, description, field, and daily tasks
                    haystack = ' '.join([
                        career.get('title',''),
                        career.get('description','')[:200],
                        career.get('field',''),
                        career.get('daily_tasks','')[:100],
                    ]).lower()
                    # Word boundary match
                    return bool(_re.search(r'\b' + _re.escape(term) + r'\b', haystack))

                exact = []    # full phrase match in title
                strong = []   # all words match in title
                partial = []  # partial match in title or description
                seen = set()

                for c in (CAREERS_FULL or []):
                    soc = c.get('soc_code','')
                    if soc in seen: continue
                    title_lower = c.get('title','').lower()
                    desc_lower = c.get('description','').lower()
                    field_lower = c.get('field','').lower()

                    # Tier 1: full phrase in title
                    if search_lower in title_lower:
                        exact.append(c); seen.add(soc); continue

                    # Tier 2: all search words in title
                    if search_words and all(w in title_lower for w in search_words):
                        strong.append(c); seen.add(soc); continue

                    # Tier 3: most words in title
                    word_hits = sum(1 for w in search_words if w in title_lower)
                    if word_hits >= max(1, len(search_words)-1):
                        strong.append(c); seen.add(soc); continue

                    # Tier 4: any word matches title or field or description
                    if any(w in title_lower or w in field_lower for w in search_words):
                        partial.append(c); seen.add(soc); continue

                    # Tier 5: full phrase in description
                    if search_lower in desc_lower:
                        partial.append(c); seen.add(soc)

                # Sort each tier by salary desc so best-paying comes first
                def sal(c): return int(float(c.get('median_annual',0) or 0))
                exact   = sorted(exact,   key=sal, reverse=True)
                strong  = sorted(strong,  key=sal, reverse=True)
                partial = sorted(partial, key=sal, reverse=True)

                matches_c = exact + strong + partial
                # Prepend direct match if found
                if direct_match:
                    matches_c = [direct_match] + [c for c in matches_c if c.get('soc_code') != direct_match.get('soc_code')]

                if not matches_c:
                    st.warning(f"No careers found for '{search_career}'. Try: Nurse, Software Engineer, Teacher, Accountant, Social Worker")
                    fields_list = sorted(set(c.get('field','') for c in (CAREERS_FULL or []) if c.get('field')))
                    f_cols = st.columns(4)
                    for fi, fn in enumerate(fields_list[:12]):
                        with f_cols[fi % 4]: st.markdown(f"• {fn}")
                else:
                    career = matches_c[0]
                    title = career.get('title','')
                    field = career.get('field','')
                    try: sal_mid = int(float(career.get('median_annual') or 0))
                    except: sal_mid = 0
                    try: sal_entry = int(float(career.get('entry_annual') or 0))
                    except: sal_entry = 0
                    try: sal_senior = int(float(career.get('experienced_annual') or 0))
                    except: sal_senior = 0
                    growth = career.get('growth_pct','N/A')
                    growth = 'N/A' if str(growth) in ['nan','None','','null'] else growth
                    education = career.get('education','N/A')
                    job_zone = int(float(career.get('job_zone',3) or 3))
                    desc = str(career.get('description','') or '')[:300]
                    daily = str(career.get('daily_tasks','') or '')
                    tools_str = str(career.get('tech_tools','') or '')
                    skills = str(career.get('top_skills','') or '')
                    zone_map = {1:"No degree needed",2:"High school — 0-2 years",
                                3:"Associate's or Bachelor's — 2-4 years",
                                4:"Bachelor's degree — 4 years",5:"Graduate degree — 6+ years"}
                    study_req = zone_map.get(job_zone,"Bachelor's degree — 4 years")
                    can_now = job_zone <= 3

                    st.markdown(f"### {title}")
                    st.caption(f"{field} · {study_req}")
                    if desc: st.markdown(f"*{desc[:250]}...*" if len(desc)>250 else f"*{desc}*")
                    m1,m2,m3,m4 = st.columns(4)
                    FIELD_AVG = {'Arts & Media':72460,'Business & Finance':84005,'Construction & Trades':61550,
                        'Criminal Justice':67290,'Culinary Arts':56520,'Education':62615,'Engineering':98176,
                        'Healthcare':102084,'Law & Justice':139540,'Management':144658,'Personal Care':44160,
                        'Science & Research':92995,'Social Services':57458,'Technology':115734,'Transportation':158115}
                    if not sal_mid: sal_mid = FIELD_AVG.get(field, 65000); sal_entry = int(sal_mid*0.62); sal_senior = int(sal_mid*1.45)
                    m1.metric("Median salary", f"${sal_mid:,}/yr")
                    m2.metric("Entry salary", f"${sal_entry:,}/yr")
                    m3.metric("Senior salary", f"${sal_senior:,}/yr")
                    m4.metric("Job growth", growth)
                    st.divider()
                    if can_now:
                        st.success(f"✅ You can get entry-level roles in {field} without finishing your full degree!")
                    else:
                        st.info(f"📚 This career requires {study_req} before most entry-level roles.")

                    CAREER_MAJORS = {
                        "Healthcare":["Nursing (BSN)","Health Sciences","Biology","Pre-Medicine"],
                        "Technology":["Computer Science","Software Engineering","Information Technology","Cybersecurity"],
                        "Engineering":["Civil Engineering","Mechanical Engineering","Electrical Engineering","Computer Engineering"],
                        "Education":["Education (K-12)","Early Childhood Education","Special Education"],
                        "Social Services":["Social Work (BSW)","Psychology","Sociology","Human Services"],
                        "Business & Finance":["Finance","Accounting","Business Administration","Economics"],
                        "Management":["Business Administration","Management","MBA"],
                        "Law & Justice":["Pre-Law","Criminal Justice","Political Science"],
                        "Arts & Media":["Communications","Journalism","Graphic Design","Marketing"],
                        "Science & Research":["Biology","Chemistry","Environmental Science","Physics"],
                        "Criminal Justice":["Criminal Justice","Criminology","Forensic Science"],
                    }
                    rec_majors = CAREER_MAJORS.get(field, [])
                    if rec_majors:
                        st.markdown(f"**📚 Recommended majors for {title.split(',')[0]}:**")
                        m_cols = st.columns(min(len(rec_majors[:4]),4))
                        for mi, maj in enumerate(rec_majors[:4]):
                            with m_cols[mi]: st.markdown(f"`{maj}`")

                    if daily:
                        st.markdown("**What you do every day:**")
                        for task in daily.split(' | ')[:5]:
                            if task.strip(): st.markdown(f"• {task.strip()}")
                    if tools_str:
                        st.markdown("**Tools & software used:**")
                        tool_list = [t.strip() for t in tools_str.split(',') if t.strip()]
                        t_cols = st.columns(4)
                        for ti, tool in enumerate(tool_list[:8]):
                            with t_cols[ti % 4]: st.markdown(f"`{tool}`")
                    if skills:
                        st.markdown("**Top skills needed:**")
                        sk_list = [s.strip() for s in skills.split(',') if s.strip()]
                        s_cols = st.columns(5)
                        for si, sk in enumerate(sk_list[:5]):
                            with s_cols[si % 5]: st.markdown(f"**{sk}**")
                    R=float(career.get('interest_realistic',0) or 0)
                    I=float(career.get('interest_investigative',0) or 0)
                    A=float(career.get('interest_artistic',0) or 0)
                    S=float(career.get('interest_social',0) or 0)
                    E=float(career.get('interest_enterprising',0) or 0)
                    C=float(career.get('interest_conventional',0) or 0)
                    st.divider()
                    st.markdown("**What kind of person thrives here (O*NET)**")
                    r_cols = st.columns(6)
                    for col,(lbl,val) in zip(r_cols,[("Hands-on",R),("Analytical",I),("Creative",A),("Social",S),("Leadership",E),("Detail",C)]):
                        col.metric(lbl, f"{val:.1f}/7")
                    if len(matches_c) > 1:
                        st.divider()
                        st.markdown(f"**{len(matches_c)-1} related roles:**")
                        for mc in matches_c[1:6]:
                            mc_sal = int(float(mc.get('median_annual',0) or 0))
                            st.caption(f"• {mc.get('title','')} — ${mc_sal:,}/yr" if mc_sal else f"• {mc.get('title','')}")
                    st.caption("Source: O*NET 30.2 · BLS 2024")

            else:
                st.markdown("**Popular searches:**")
                popular = ["Software Engineer","Registered Nurse","Lawyer","Data Scientist",
                          "Teacher","Social Worker","Cybersecurity","Accountant","Marketing Manager","Pharmacist"]
                p_cols = st.columns(5)
                for pi, p in enumerate(popular):
                    with p_cols[pi % 5]:
                        if st.button(p, key=f"pop_{pi}", use_container_width=True):
                            st.session_state['pop_career'] = p
                            st.rerun()
    with tab3:
        # ── AID ELIGIBILITY TAB ──────────────────────────────────
        st.markdown("### 💰 Your Financial Aid Eligibility")
        st.caption("Based on 2025-26 federal and NY State thresholds")
        aid = st.session_state.get('aid', calculate_aid(income, hsize, ny_res, IMMIG_MAP.get(immig,'citizen'), first_gen))
        total = aid.get('total',0); pell = aid.get('pell',0)
        tap = aid.get('tap',0); dream = aid.get('dream',0); heop = aid.get('heop',False)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Est. Aid", f"${total:,}/yr")
        c2.metric("Pell Grant", f"${pell:,}/yr" if pell else "Not eligible")
        c3.metric("NY TAP", f"${tap:,}/yr" if tap else "Not eligible")
        c4.metric("Dream Act", f"${dream:,}/yr" if dream else "Not eligible")
        st.divider()
        if pell: st.success(f"✅ **Federal Pell Grant** — ${pell:,}/yr · No repayment required")
        else: st.info("ℹ️ **Federal Pell Grant** — Not eligible. Check studentaid.gov for FAFSA.")
        if tap: st.success(f"✅ **NY TAP** — ${tap:,}/yr · NY residents only · No repayment")
        else: st.info("ℹ️ **NY TAP** — Not eligible. Must be NY resident with income under $80,000.")
        if dream: st.success(f"✅ **NY Dream Act** — ${dream:,}/yr · Undocumented/DACA students")
        if heop: st.success("✅ **HEOP** — Full scholarship at many NY private colleges")
        else: st.info("ℹ️ **HEOP** — Not eligible based on your profile.")
        st.divider()
        st.markdown("• File your FAFSA at studentaid.gov every year — opens October 1")
        st.markdown("• TAP application opens after FAFSA — apply at hesc.ny.gov")
        st.markdown("• These are estimates — actual aid depends on your full FAFSA")
        st.caption("Aid thresholds: Federal 2025-26 · NY HESC 2025-26")

    with tab4:
        # ── MY COLLEGE LIST TAB ──────────────────────────────────
        st.markdown("### 📋 My College List")
        my_list = st.session_state.get('my_list', [])
        if not my_list:
            st.info("Your list is empty — go to College Matches and click **+ Add to list** on any school.")
        else:
            aid = st.session_state.get('aid', {})
            gpa_val = st.session_state.get('gpa', 3.0)
            safety_n = sum(1 for s in my_list if s.get('fit')=='safety')
            match_n  = sum(1 for s in my_list if s.get('fit')=='match')
            reach_n  = sum(1 for s in my_list if s.get('fit')=='reach')
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Total", len(my_list)); c2.metric("Safety", safety_n)
            c3.metric("Match", match_n); c4.metric("Reach", reach_n)
            if safety_n == 0: st.warning("⚠️ No safety schools — add at least 2.")
            if reach_n == 0: st.info("💡 Consider adding a reach school — a dream school worth applying to.")
            st.divider()
            fit_icons = {'safety':'🟢','match':'🎯','reach':'⚠️','unknown':'⚪'}
            for s in my_list:
                fit = s.get('fit','unknown')
                with st.container():
                    col_a,col_b,col_c = st.columns([3,1.5,1])
                    with col_a:
                        st.markdown(f"**{fit_icons.get(fit,'⚪')} [{s.get('name','')}]({s.get('web','#')})**")
                        st.caption(f"{s.get('state','')} · Sticker: ${int(s.get('tin') or 0):,} · You pay: ${int(s.get('net') or 0):,}/yr · Grad rate: {int(s.get('grad') or 0)}%")
                    with col_b:
                        st.markdown(f"**RD:** {s.get('rd','Check website')}")
                        if s.get('ea'): st.caption(f"EA: {s.get('ea')}")
                    with col_c:
                        if st.button("Remove", key=f"rm_{s.get('id',s.get('name',''))}", use_container_width=True):
                            st.session_state.my_list = [x for x in my_list if x.get('id') != s.get('id')]
                            st.rerun()
                    st.divider()
            if st.button("⬇️ Download as PDF", type="primary", key="pdf_download"):
                try:
                    pdf_bytes = generate_pdf(my_list, aid, gpa_val)
                    st.download_button("📄 Save College List PDF", data=pdf_bytes,
                        file_name="my_college_list.pdf", mime="application/pdf", key="pdf_save")
                except ImportError:
                    st.warning("PDF export requires reportlab.")
            st.caption("⚠️ Always verify deadlines on each college's official website before applying.")

st.divider()
st.caption("Pathways by SLN · IPEDS 2023-24 · Peterson's 2025 · O*NET 30.2 · Aid thresholds 2025-26 · Verify all deadlines on official college websites")
