# ═══════════════════════════════════════════════════════════════
#  PATHWAYS BY SLN — Streamlit App v2
#  Version: APR15-FINAL — CUNY sort + career list + income dropdown
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
if 'career_selected_soc' not in st.session_state:
    st.session_state.career_selected_soc = ''
if '_profile_loaded' not in st.session_state:
    st.session_state._profile_loaded = False

# ── RESTORE PROFILE FROM URL PARAMS ──────────────────────────
# Lets students bookmark their profile — URL encodes key inputs
# Same approach used by Niche and CollegeVine
_qp = st.query_params
if not st.session_state._profile_loaded and _qp:
    try:
        if 'scale' in _qp:
            st.session_state['gpa_scale_radio'] = _qp['scale']
        if 'gpa' in _qp:
            v = float(_qp['gpa'])
            if st.session_state.get('gpa_scale_radio') == '4.0 scale':
                st.session_state['gpa_slider'] = min(4.0, max(0.0, v))
            else:
                st.session_state['gpa_slider_100'] = int(min(100, max(0, v)))
        if 'states' in _qp:
            st.session_state['states_multi'] = _qp['states'].split('|')
        if 'income' in _qp:
            st.session_state['income_bracket'] = _qp['income']
        if 'test' in _qp:
            st.session_state['test_scores'] = _qp['test']
        if 'sat' in _qp:
            st.session_state['sat_input'] = int(_qp['sat'])
        if 'act' in _qp:
            st.session_state['act_input'] = int(_qp['act'])
        if 'ny' in _qp:
            st.session_state['ny_res'] = _qp['ny'] == '1'
        if 'immig' in _qp:
            st.session_state['immig'] = _qp['immig']
        if 'fg' in _qp:
            st.session_state['first_gen'] = _qp['fg'] == '1'
        if 'size' in _qp:
            st.session_state['school_size'] = _qp['size']
        if 'type' in _qp:
            st.session_state['school_type'] = _qp['type']
        if 'yrs' in _qp:
            st.session_state['study_yrs'] = _qp['yrs']
        if 'test' in _qp:
            st.session_state['test_scores'] = _qp['test']
    except Exception:
        pass
    st.session_state._profile_loaded = True

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
        # Normalize column name: schools_full.csv uses 'unitid', code uses 'id'
        # This one line makes both work — no other changes needed anywhere
        if s.get('id') is None:
            s['id'] = s.get('unitid')
        try: s['id'] = int(s['id']) if s.get('id') is not None else None
        except: s['id'] = None
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
        try: s['roomboard'] = int(float(s['roomboard'])) if s.get('roomboard') not in (None,'','nan') else None
        except: s['roomboard'] = None
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
        # Load lat/lon for distance calculations
        # IPEDS uses LATITUDE and LONGITUD (no final E) — support both variants
        if s.get('latitude') is None and s.get('LATITUDE') is not None:
            s['latitude'] = s.get('LATITUDE')
        if s.get('longitude') is None:
            s['longitude'] = s.get('LONGITUD') or s.get('LONGITUDE')
        for coord in ['latitude','longitude']:
            v = s.get(coord)
            try: s[coord] = float(v) if v is not None and str(v).strip() not in ('','nan','None') else None
            except: s[coord] = None
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

# ── CUNY Admissions Data Loader ──────────────────────────────
# Source: CUNY.edu official Freshman Admission Profile Fall 2025
# avg_hs_100 = average HS GPA of admitted students on 100-pt scale
# Used to calibrate CUNY fit — overrides generic IPEDS logic
@st.cache_data(ttl=86400, show_spinner=False)
def load_cuny_admissions():
    import pandas as pd, os
    path = 'cuny_admissions.csv'
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    result = {}
    for _, row in df.iterrows():
        uid = int(row['unitid'])
        result[uid] = {
            'avg_100':   float(row['avg_hs_100'])         if pd.notna(row['avg_hs_100'])   else None,
            'seek_100':  float(row['seek_avg_100'])       if pd.notna(row['seek_avg_100']) else None,
            'accept_pct':float(row['accept_pct'])         if pd.notna(row['accept_pct'])   else None,
            'yr2':       bool(int(row['yr2']))             if pd.notna(row['yr2'])          else False,
        }
    return result

CUNY_ADMISSIONS = load_cuny_admissions()

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


# ── SCHOOL COORDINATES FALLBACK ──────────────────────────────
# Used when schools_full.csv doesn't include lat/lon columns
# Covers major NYC-area and common NY destination schools
# Source: known geographic coordinates
SCHOOL_COORDS_FALLBACK = {
    # CUNY
    190637: (40.8196, -73.9499),  # City College
    190512: (40.7678, -73.9645),  # Hunter College
    190549: (40.6954, -73.9874),  # Brooklyn College
    190558: (40.7484, -74.0014),  # John Jay
    190576: (40.8732, -73.8945),  # Lehman College
    190600: (40.7362, -73.8200),  # Queens College
    190615: (40.6297, -73.9547),  # Brooklyn College
    190624: (40.7405, -73.9836),  # Baruch College
    190099: (40.8521, -73.9166),  # Bronx CC
    # SUNY
    196097: (40.9257, -73.1409),  # Stony Brook
    196060: (42.6862, -73.8227),  # SUNY Albany
    196105: (42.8962, -78.8767),  # UB Buffalo
    196183: (42.8962, -78.8767),  # Stony Brook (duplicate fix)
    196200: (42.7954, -77.8245),  # Geneseo
    # Private NY
    193900: (40.7295, -73.9965),  # NYU
    190150: (40.8075, -73.9626),  # Columbia
    194824: (40.8617, -73.8855),  # Fordham
    189097: (40.8076, -73.9641),  # Barnard
    192703: (41.7701, -73.9021),  # Marist
    193016: (41.0093, -73.8585),  # Mercy
    195173: (40.6962, -73.9929),  # St. Francis Brooklyn
    # Out of state common
    212674: (39.8309, -77.2311),  # Gettysburg
    166027: (42.3770, -71.1167),  # Harvard
    130794: (41.3163, -72.9223),  # Yale
    186131: (40.3431, -74.6551),  # Princeton
    217156: (41.8268, -71.4025),  # Brown
    215062: (39.9522, -75.1932),  # UPenn
    198419: (35.9940, -78.8986),  # Duke
    221999: (36.1447, -86.8027),  # Vanderbilt
    139658: (33.7940, -84.3241),  # Emory
}

def get_school_coords(s):
    """Get lat/lon for a school, using CSV data or fallback dict."""
    lat = s.get('latitude')
    lon = s.get('longitude')
    if lat and lon:
        try: return float(lat), float(lon)
        except: pass
    uid = s.get('id')
    if uid and int(uid) in SCHOOL_COORDS_FALLBACK:
        return SCHOOL_COORDS_FALLBACK[int(uid)]
    return None, None

# ── DISTANCE ENGINE ──────────────────────────────────────────
import math as _math

def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = _math.radians(lat1), _math.radians(lat2)
    dphi = _math.radians(lat2 - lat1)
    dlam = _math.radians(lon2 - lon1)
    a = _math.sin(dphi/2)**2 + _math.cos(phi1)*_math.cos(phi2)*_math.sin(dlam/2)**2
    return round(R * 2 * _math.atan2(_math.sqrt(a), _math.sqrt(1-a)), 1)

# ── ENGINES ───────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════
# SECTION 2: FINANCIAL AID CALCULATOR
# Calculates Pell Grant, NY TAP, Dream Act, HEOP eligibility
# Update thresholds annually: studentaid.gov + hesc.ny.gov
# Income thresholds from SUNY PDF 2026-27
# ════════════════════════════════════════════════════════════
def calculate_aid(income, hsize, ny_res, immig, first_gen):
    pell=tap=dream=0; heop=False
    # Pell Grant — ANNUAL amounts (2025-26) · studentaid.gov
    # Household size adjustments: larger families qualify at higher incomes
    size_adj = max(0, (hsize - 4) * 2000)
    if immig in ('citizen','daca'):
        if income <= 20000 + size_adj:   pell = 7395
        elif income <= 30000 + size_adj: pell = 6195
        elif income <= 40000 + size_adj: pell = 4746
        elif income <= 50000 + size_adj: pell = 3098
        elif income <= 60000 + size_adj: pell = 1848
        elif income <= 65000 + size_adj: pell = 924
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
# ════════════════════════════════════════════════════════════
# SECTION 3: COLLEGE FIT ENGINE — Safety / Match / Reach
# ════════════════════════════════════════════════════════════
#
# DATA SOURCES (all verified, no guessing):
# • CUNY: Official Fall 2024 Freshman Admission Profile
#         cuny.edu/admissions/undergraduate/apply/academic-profiles/
#         High school average on 100-pt scale — these are AVERAGES not minimums
# • SUNY: IPEDS 2023-24 + CollegeSimply/CollegeTuitionCompare
#         GPA on 4.0 scale, SAT 25th/75th percentiles
# • Private/Other: IPEDS SAT/ACT ranges → GPA ranges from Peterson's 2025
#
# LOGIC:
# 1. CUNY schools: use official 100-pt HS average + acceptance rate
# 2. Other schools: SAT range → ACT range → GPA range → acceptance rate fallback
# 3. Community colleges (adm_rate ≥ 95%): always Safety
# ════════════════════════════════════════════════════════════

# CUNY Official Fall 2024 Freshman Profiles
# (unitid): (hs_avg_100, adm_rate_pct, sat25, sat75)
# ── CUNY profiles loaded from cuny_admissions.csv ────────────
# Source: CUNY.edu official Freshman Admission Profile Fall 2025
# No hardcoding — update the CSV to change thresholds
def _load_cuny_profiles():
    import os, csv
    profiles = {}
    path = 'cuny_admissions.csv'
    if not os.path.exists(path):
        return profiles
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            try:
                uid = int(row['unitid'])
                avg = float(row['avg_hs_100']) if row.get('avg_hs_100','') not in ('','None','nan') else None
                adm = float(row['accept_pct']) if row.get('accept_pct','') not in ('','None','nan') else 100
                yr2 = bool(int(row.get('yr2', 0)))
                profiles[uid] = (avg, adm, yr2)
            except (ValueError, KeyError):
                pass
    return profiles

_CUNY_PROFILES = _load_cuny_profiles()

def _cuny_fit(student_gpa_100, school_avg_100, adm_rate):
    """
    CUNY fit using CUNY.edu official Freshman Admission Profile Fall 2025.
    Averages not minimums — students above AND below are admitted.
    Thresholds calibrated so 3.2 GPA → match at Baruch/Hunter (selective)
    and safety at John Jay/Lehman/York (less selective).
    """
    if adm_rate >= 95:
        return 'safety'  # Open-access community colleges

    gap = school_avg_100 - student_gpa_100  # positive = student below school avg

    if adm_rate < 65:  # Selective (Baruch, Hunter, Brooklyn, Queens, CCNY)
        if gap <= 0:   return 'safety'
        if gap <= 6:   return 'match'
        if gap <= 14:  return 'reach'
        return 'reach'
    else:  # Less selective (John Jay, Lehman, York, CityTech, Medgar, CSI)
        if gap <= 4:   return 'safety'
        if gap <= 10:  return 'match'
        if gap <= 16:  return 'reach'
    if adm_rate >= 55 and gap <= 8:  return 'match'
    if adm_rate >= 50 and gap <= 4:  return 'match'
    return 'reach'

def get_env_fit(s, env_pref, school_size, school_type):
    """Returns environment descriptor tags for a school card."""
    tags = []
    # Size
    size = s.get('size', 0)
    try: size = int(size)
    except: size = 0
    size_label = {1:'Very small', 2:'Small', 3:'Medium', 4:'Large', 5:'Very large'}.get(size, '')
    if size_label:
        tags.append(size_label)
    # Control type
    ctrl = s.get('ctrl')
    try: ctrl = int(ctrl)
    except: ctrl = None
    if ctrl == 1: tags.append('Public')
    elif ctrl in (2, 3): tags.append('Private')
    # Special missions
    if s.get('hbcu'): tags.append('HBCU')
    if s.get('womens'): tags.append("Women's")
    # Grad rate
    grad = s.get('grad') or 0
    try: grad = float(grad)
    except: grad = 0
    if grad >= 80: tags.append('High grad rate')
    elif grad >= 60: tags.append('Mod grad rate')
    return tags

def get_fit(sat, act, s, gpa=None):
    """
    Determine Safety / Match / Reach for a student + school.

    Priority order:
    1. CUNY schools → use official 100-pt HS average (most accurate)
    2. SAT score vs school 25th/75th percentile
    3. ACT score vs school 25th/75th percentile
    4. GPA (4.0) vs Peterson's 25th/75th percentile
    5. GPA vs Peterson's average GPA
    6. GPA vs gpa_data.csv ranges
    7. Acceptance rate (Niche-style fallback)
    8. GPA strength alone
    """
    uid = s.get('id')
    adm = s.get('adm')

    # ── 1. CUNY — use official Fall 2024 data ────────────────
    if uid and int(uid) in _CUNY_PROFILES:
        avg_100, cuny_adm, yr2 = _CUNY_PROFILES[int(uid)]
        if gpa:
            # Convert 4.0 GPA to NYC 100-pt scale
            # Calibrated to match CUNY's actual admitted student profiles:
            # 3.7→93, 3.0→85, 2.7→80, 2.3→75
            if gpa >= 3.7:    student_100 = 93 + (gpa - 3.7) / 0.05
            elif gpa >= 3.0:  student_100 = 85 + (gpa - 3.0) / 0.0875
            elif gpa >= 2.7:  student_100 = 80 + (gpa - 2.7) / 0.06
            elif gpa >= 2.3:  student_100 = 75 + (gpa - 2.3) / 0.08
            else:             student_100 = max(65, 70 + (gpa - 1.7) / 0.08)
            return _cuny_fit(student_100, avg_100, cuny_adm)
        # No GPA → use acceptance rate
        if yr2 or cuny_adm >= 95: return 'safety'  # open-access community colleges
        if cuny_adm >= 75: return 'match'
        if cuny_adm >= 55: return 'match'
        return 'reach'

    # ── 2. SAT score ─────────────────────────────────────────
    if sat and s.get('sat25') and s.get('sat75'):
        if sat >= s['sat75']: return 'safety'
        if sat >= s['sat25']: return 'match'
        # Below 25th — but high acceptance rate = still reachable
        if adm and adm >= 70 and sat >= s['sat25'] - 80: return 'reach'
        return 'reach'

    # ── 3. ACT score ─────────────────────────────────────────
    if act and s.get('act25') and s.get('act75'):
        if act >= s['act75']: return 'safety'
        if act >= s['act25']: return 'match'
        return 'reach'

    # ── 4. Peterson's GPA 25th/75th percentile ───────────────
    if gpa and s.get('gpa_25') and s.get('gpa_75'):
        if gpa >= s['gpa_75']: return 'safety'
        if gpa >= s['gpa_25']: return 'match'
        # Below 25th — high acceptance rate schools can still be match
        if adm and adm >= 75 and gpa >= s['gpa_25'] - 0.3: return 'reach'
        return 'reach'

    # ── 5. Peterson's average GPA ────────────────────────────
    if gpa and s.get('gpa_avg'):
        avg = s['gpa_avg']
        if gpa >= avg + 0.2:  return 'safety'
        if gpa >= avg - 0.2:  return 'match'
        if gpa >= avg - 0.5 and adm and adm >= 70: return 'reach'
        if gpa >= avg - 0.3:  return 'reach'
        return 'reach'

    # ── 6. gpa_data.csv ranges ───────────────────────────────
    if gpa and uid and uid in GPA_DATA:
        g = GPA_DATA[uid]
        lo = g.get('gpa_low'); hi = g.get('gpa_high')
        if lo and hi:
            if gpa >= hi: return 'safety'
            if gpa >= lo: return 'match'
            return 'reach'

    # ── 7. Acceptance rate (Niche-style fallback) ─────────────
    if adm is not None:
        if adm >= 85: return 'safety'
        if adm >= 60: return 'match'
        if adm >= 40: return 'reach'
        return 'reach'

    # ── 8. GPA strength alone ─────────────────────────────────
    if gpa:
        if gpa >= 3.7: return 'match'
        if gpa >= 3.0: return 'match'
        return 'reach'

    return 'unknown'


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
        tuition_only = tin  # save raw tuition before adding R&B
        # Add room & board to total cost of attendance (Alex feedback Apr 15)
        # Community colleges are mostly commuter (~$3k), 4-yr schools avg ~$14k
        rb = s.get('roomboard') or (3000 if s.get('yr2') else 14000)
        tin = tin + rb  # tin is now full cost of attendance
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
            'tuition_only': int(tuition_only) if tuition_only else 0,
            'roomboard_added': int(rb) if rb else 0,
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

    # Guarantee EOP/SEEK/CD schools always appear for NY students
    # Reads from eop_schools.csv via EOP_DATA — no hardcoding
    state_list_check = state if isinstance(state, list) else ([state] if state != 'any' else [])
    if 'NY' in state_list_check or not state_list_check:
        priority_ids = {int(uid) for uid in EOP_DATA.keys() if uid.isdigit()}
        selected_ids = {r.get('id') for r in selected}
        priority_in_results = [r for r in results if r.get('id') in priority_ids and r.get('id') not in selected_ids]
        for pr in priority_in_results[:4]:
            if len(selected) >= n:
                selected.pop()
            selected.append(pr)

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

# ── Partner Schools Loader ───────────────────────────────────
# Source: partner_schools.csv — maintained by Aaron/Kieran
# Format: unitid, school_name, badges (comma-separated)
# Example badges: QuestBridge, Posse, SLN Partner
# To add/remove schools: edit the CSV — no code changes needed
def load_partner_data():
    import os, csv
    partners = {}
    if not os.path.exists('partner_schools.csv'):
        return partners
    try:
        with open('partner_schools.csv', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                uid = str(row.get('unitid','')).strip()
                badges = [b.strip() for b in str(row.get('badges','')).split(',') if b.strip()]
                if uid and badges:
                    if uid not in partners:
                        partners[uid] = []
                    partners[uid].extend(badges)
    except: pass
    return partners

PARTNER_DATA = load_partner_data()

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
    st.caption("Built by SLN RITA Tech & Data Intern\nIPEDS 2023-24 · Aid thresholds 2025-26\n`v APR15-FINAL`")
st.divider()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📝 Your Profile")

    st.markdown("### 📚 Academics")
    gpa_scale = st.radio("GPA scale", ["100 scale","4.0 scale"], horizontal=True, key="gpa_scale_radio")
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
        sat = st.number_input("SAT Score", 400, 1600, st.session_state.get("sat_input", 1100), 10, key="sat_input")
    elif score_type == "ACT":
        act = st.number_input("ACT Score", 1, 36, st.session_state.get("act_input", 24), 1, key="act_input")

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
    INCOME_BRACKETS = {
        "Under $20,000": 10000,
        "$20,000 – $30,000": 25000,
        "$30,000 – $40,000": 35000,
        "$40,000 – $50,000": 45000,
        "$50,000 – $60,000": 55000,
        "$60,000 – $75,000": 67500,
        "$75,000 – $100,000": 87500,
        "Over $100,000": 120000,
        "Prefer not to say": 42000,
    }
    income_label = st.selectbox(
        "Annual household income",
        list(INCOME_BRACKETS.keys()),
        index=3,
        help="Used to estimate Pell Grant, TAP, and Dream Act eligibility",
        key="income_bracket"
    )
    income = INCOME_BRACKETS[income_label]
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

    st.markdown("### 📍 Distance from You")
    _glat = st.session_state.get("student_lat")
    if _glat:
        _loc_name = st.session_state.get("student_location_name", "")
        if _loc_name:
            st.caption(f"✅ Location set: **{_loc_name}** — distances show on cards & map")
        else:
            st.caption("✅ Location set (GPS) — distances show on cards & map")
        if st.button("✕ Clear location", key="clear_geo"):
            st.session_state.pop("student_lat", None)
            st.session_state.pop("student_lon", None)
            st.session_state.pop("student_zip", None)
            st.session_state.pop("student_location_name", None)
            st.rerun()
    else:
        # Two options: browser GPS or zip code
        _loc_col1, _loc_col2 = st.columns([1, 1])
        with _loc_col1:
            if st.button("📍 Use My Location", key="geo_btn", use_container_width=True,
                         help="Uses your browser's GPS — nothing is stored"):
                st.session_state["_request_geo"] = True
        with _loc_col2:
            _zip_val = st.text_input("or ZIP code", placeholder="e.g. 10031",
                                     max_chars=5, label_visibility="collapsed",
                                     key="zip_input")
        if _zip_val and len(_zip_val) == 5 and _zip_val.isdigit():
            # Geocode zip via Nominatim (free, no key)
            try:
                import urllib.request as _ur, json as _jz
                _zurl = f"https://nominatim.openstreetmap.org/search?postalcode={_zip_val}&country=US&format=json&limit=1"
                _zreq = _ur.Request(_zurl, headers={"User-Agent":"PathwaysSLN/1.0"})
                with _ur.urlopen(_zreq, timeout=3) as _zr:
                    _zd = _jz.loads(_zr.read())
                if _zd:
                    st.session_state["student_lat"] = float(_zd[0]["lat"])
                    st.session_state["student_lon"] = float(_zd[0]["lon"])
                    st.session_state["student_zip"] = _zip_val
                    st.session_state["student_location_name"] = _zd[0].get("display_name","").split(",")[0] + f" ({_zip_val})"
                    st.rerun()
                else:
                    st.caption("⚠️ ZIP not found")
            except Exception:
                st.caption("⚠️ Could not geocode zip")

    run_btn = st.button("🔍 Find My Colleges", type="primary", use_container_width=True)
    st.caption("🔗 Your profile auto-saves to the URL — bookmark to return to these settings")

# ── CONTINUOUS PROFILE SAVE TO URL ──────────────────────────
# Runs every render so URL always reflects current sidebar state
# Student can bookmark or copy URL at any time to save their profile
try:
    _sp = {
        'scale': gpa_scale,
        'states': '|'.join(state_pref) if state_pref else 'NY',
        'income': income_label,
        'ny':     '1' if ny_res else '0',
        'immig':  immig,
        'fg':     '1' if first_gen else '0',
        'size':   school_size,
        'type':   school_type,
        'yrs':    study_yrs,
    }
    if gpa_scale == '4.0 scale':
        _sp['gpa'] = str(round(gpa, 1))
    else:
        _sp['gpa'] = str(gpa_100)
    if score_type == 'SAT' and sat:
        _sp['test'] = 'SAT'; _sp['sat'] = str(sat)
    elif score_type == 'ACT' and act:
        _sp['test'] = 'ACT'; _sp['act'] = str(act)
    st.query_params.update(_sp)
except Exception:
    pass

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

# Browser geolocation via streamlit-js-eval
if st.session_state.get("_request_geo"):
    try:
        from streamlit_js_eval import get_geolocation
        _geo = get_geolocation()
        if _geo and _geo.get("coords"):
            _glat2 = _geo["coords"]["latitude"]
            _glon2 = _geo["coords"]["longitude"]
            st.session_state["student_lat"] = _glat2
            st.session_state["student_lon"] = _glon2
            # Reverse geocode to get neighborhood/city name
            try:
                import urllib.request as _ur2, json as _jz2
                _rurl = f"https://nominatim.openstreetmap.org/reverse?lat={_glat2}&lon={_glon2}&format=json"
                _rreq = _ur2.Request(_rurl, headers={"User-Agent":"PathwaysSLN/1.0"})
                with _ur2.urlopen(_rreq, timeout=3) as _rr:
                    _rd = _jz2.loads(_rr.read())
                _addr = _rd.get("address", {})
                _city = _addr.get("neighbourhood") or _addr.get("suburb") or _addr.get("city") or _addr.get("town","")
                _pcode = _addr.get("postcode","")
                st.session_state["student_location_name"] = f"{_city} ({_pcode})" if _city else f"GPS ({_pcode})"
            except Exception:
                st.session_state["student_location_name"] = "Your location (GPS)"
            st.session_state.pop("_request_geo", None)
            st.rerun()
    except Exception:
        st.session_state.pop("_request_geo", None)

if run_btn:
    state_val = state_pref if state_pref else ['NY']  # default to NY if nothing selected
    need_val  = "full" if income<50000 else "some"
    matches = run_match(gpa, sat, act, state_val,
                        SIZE_MAP[school_size], CTRL_MAP[school_type],
                        need_val, ENV_MAP[env_pref], YRS_MAP[study_yrs], aid, n_results,
                        majors_input=majors_input,
                        only_gpa=only_gpa_data, only_adm=only_adm_data)
    st.session_state.matches  = matches
    st.session_state.ran_match = True
    st.session_state.gpa = gpa
    st.session_state.sat = sat
    st.session_state.act = act

matches = st.session_state.matches

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏫 College Matches",
    "🎯 Career Results",
    "💰 Aid Eligibility",
    "📋 My College List",
    "🗺️ Map"
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
        _has_zip = bool(st.session_state.get("student_lat"))
        _sort_choices = ["Best Fit", "Lowest Cost", "Safety First", "Grad Rate"]
        if _has_zip:
            _sort_choices.append("Closest to Me")
        sort_opts = st.multiselect(
            "Sort by (first = primary sort):",
            _sort_choices,
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
        def aaron_default_sort(x):
            """
            SLN default sort — Aaron Hawn's recommended exploration order:
            1. In-state first (NY students see NY schools first)
            2. 4-year before 2-year (bachelor's path prioritized)
            3. Highest reasonable selectivity sweet spot
            4. Strong completion outcomes (grad rate as tiebreaker)
            Based on Hossler & Gallagher (1987) college choice theory.
            """
            # 1. In-state preference — read state from session_state directly
            _sv = st.session_state.get('states_multi', ['NY']) or ['NY']
            primary_state = _sv[0] if isinstance(_sv, list) and _sv else 'NY'
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

            # CUNY first, SUNY second, other public, private last
            # Uses real CUNY unitids from official Fall 2024 profiles
            # + eop_schools.csv for additional coverage
            sid = x.get('id', 0)
            try: sid = int(sid)
            except: sid = 0
            eop_progs = EOP_DATA.get(str(sid), [])

            # All CUNY colleges (from official cuny.edu roster)
            CUNY_IDS = {
                190624,190512,190549,190637,190558,190576,190600,
                190691,190646,190710,193231,  # 4-year CUNYs
                190099,190044,190213,190372,190678,190045,190046,  # CCs
                190589,190615,  # additional CUNY campuses
            }
            # Core SUNY 4-year campuses
            SUNY_IDS = {
                196079,196097,196105,196060,196200,196167,196246,
                196219,196149,196185,196264,196051,196176,196088,
                196130,196006,196113,196158,196302,
            }

            if sid in CUNY_IDS or any(p in ['SEEK','CD'] for p in eop_progs):
                sys_order = 0   # CUNY always first for NYC students
            elif sid in SUNY_IDS or any(p in ['EOP'] for p in eop_progs):
                sys_order = 1   # SUNY second
            elif x.get('ctrl') == 1:
                sys_order = 2   # Other public
            else:
                sys_order = 3   # Private last
            return [sys_order, in_state, is_2yr, fit_sweet, reach_difficulty, grad]

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
                    elif sm == "Closest to Me":
                        _slat2 = st.session_state.get("student_lat")
                        _slon2 = st.session_state.get("student_lon")
                        if _slat2:
                            try:
                                _cx, _cy = get_school_coords(x)
                                keys.append(haversine_miles(_slat2, _slon2, _cx, _cy) if _cx else 9999)
                            except Exception:
                                keys.append(9999)
                        else:
                            keys.append(9999)
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
                        # Distance from student zip
                        _slat = st.session_state.get("student_lat")
                        _slon = st.session_state.get("student_lon")
                        _dist_str = ""
                        if _slat:
                            try:
                                _clat, _clon = get_school_coords(s)
                                if _clat:
                                    _dm = haversine_miles(_slat, _slon, _clat, _clon)
                                    _dist_str = f"  📍 {_dm:.0f} mi"
                            except Exception:
                                pass
                        st.markdown(f"**{fit_icons.get(fit,'⚪')} [{s['name']}]({s.get('web','#')})**{_dist_str}")
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
                        school_uid = str(s.get('id',''))
                        # ── Row 1: Aid eligibility (student-specific) ────────
                        aid_chips = ""
                        if aid.get('pell', 0) > 0: aid_chips += "  `💰 Pell eligible`"
                        if aid.get('tap', 0) > 0 and s['state'] == 'NY': aid_chips += "  `💰 TAP eligible`"
                        if aid.get('dream', 0) > 0 and s['state'] == 'NY': aid_chips += "  `💰 Dream Act`"
                        if aid.get('heop') and s['state'] == 'NY': aid_chips += "  `🎓 HEOP eligible`"
                        if aid_chips: st.markdown(f"**Your aid here:** {aid_chips.strip()}")
                        # ── Row 2: Program & identity badges ─────────────────
                        prog_chips = ""
                        if school_uid in EOP_DATA:
                            for prog in EOP_DATA[school_uid]:
                                prog_chips += f"  `{prog}`"
                        if s.get('hbcu'): prog_chips += "  `🏛️ HBCU`"
                        if s.get('womens'): prog_chips += "  `👩 Women's college`"
                        for badge in PARTNER_DATA.get(str(s.get('id', 0)), []):
                            if badge == 'QuestBridge': prog_chips += "  `🔷 QuestBridge`"
                            elif badge == 'Posse': prog_chips += "  `🔶 Posse`"
                            elif badge == 'SLN Partner': prog_chips += "  `⭐ SLN Partner`"
                            else: prog_chips += f"  `{badge}`"
                        if prog_chips: st.markdown(f"**Programs:** {prog_chips.strip()}")
                    with cb:
                        tuition_only = int(s.get('tuition_only') or 0)
                        rb_added = int(s.get('roomboard_added') or 0)
                        sticker = int(s.get('sticker') or 0)
                        s_net = s.get('net')
                        net = int(s_net) if s_net is not None else None

                        _aid = st.session_state.get('aid', {})
                        _pell  = int(_aid.get('pell') or 0)
                        # TAP: student must be NY resident + income eligible
                        #      college must be NY state (all degree-granting NY schools are TAP-approved)
                        _school_in_ny = s.get('state') == 'NY'
                        _tap_student  = int(_aid.get('tap') or 0)
                        _tap          = _tap_student if _school_in_ny else 0
                        _dream        = int(_aid.get('dream') or 0) if _school_in_ny else 0
                        _total_aid    = _pell + _tap + _dream

                        if tuition_only:
                            st.markdown(f"**Tuition:** ${tuition_only:,}/yr")
                            st.markdown(f"**Room & Board:** ~${rb_added:,}/yr")
                            st.markdown(f"**Total Cost:** ${sticker:,}/yr")
                        else:
                            st.markdown("**Cost:** N/A")

                        if _total_aid or sticker:
                            st.markdown("---")
                        if _pell:
                            st.markdown(f"✅ Pell Grant &nbsp;−&nbsp; **${_pell:,}/yr**")
                        if _tap:
                            st.markdown(f"✅ NY TAP &nbsp;−&nbsp; **${_tap:,}/yr** *(you & this school qualify)*")
                        elif _tap_student and not _school_in_ny:
                            st.markdown(f"⚠️ NY TAP &nbsp;−&nbsp; **you qualify** but this school is out-of-state *(not eligible here)*")
                        if _dream:
                            st.markdown(f"✅ Dream Act &nbsp;−&nbsp; **${_dream:,}/yr**")

                        if net is not None and sticker:
                            st.markdown("---")
                            st.markdown(f"**🎓 You pay: ${net:,}/yr**")
                            st.caption(f"${sticker:,} total cost − ${_total_aid:,} in grants")
                        elif net is not None:
                            st.markdown(f"**🎓 You pay: ${net:,}/yr**")
                        else:
                            st.markdown("**You pay:** N/A")

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
            elif not career_results and _all_answered:
                # Questions answered but results empty — recompute now
                career_answers_now = {
                    'i1':CAREER_MAPS['i1'][q1],'i2':CAREER_MAPS['i2'][q2],
                    'i3':CAREER_MAPS['i3'][q3],'i4':CAREER_MAPS['i4'][q4],
                    'i5':CAREER_MAPS['i5'][q5],'i6':CAREER_MAPS['i6'][q6],
                    'i7':CAREER_MAPS['i7'][q7],'i8':CAREER_MAPS['i8'][q8],
                }
                career_results = run_career_match(career_answers_now)
                st.session_state.career_results = career_results
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
            # Clear selected career when search term changes
            if search_career != st.session_state.get('_last_career_search',''):
                st.session_state['career_selected_soc'] = ''
                st.session_state['_last_career_search'] = search_career

            if search_career:
                search_lower = search_career.lower().strip()

                # SEARCH_STEMS: maps broad student terms → O*NET title keywords
                # This is what makes "nursing" find RN, LPN, NP, CRNA, Nursing Instructor
                # instead of just one exact match.
                SEARCH_STEMS = {
                    "nursing":      ["nurse","nursing"],
                    "nurse":        ["nurse","nursing"],
                    "doctor":       ["physician","surgeon","psychiatrist","internist","radiolog"],
                    "medicine":     ["physician","surgeon","anesthesiolog","radiolog","pediatric","internist"],
                    "teacher":      ["teacher","instructor","educator"],
                    "teaching":     ["teacher","instructor","educator"],
                    "engineer":     ["engineer","engineering"],
                    "engineering":  ["engineer","engineering"],
                    "computer":     ["software","computer","programmer","developer","systems analyst"],
                    "tech":         ["software","developer","computer","technician","systems"],
                    "law":          ["lawyer","attorney","legal","paralegal","judge"],
                    "lawyer":       ["lawyer","attorney","legal"],
                    "social work":  ["social worker","social service","community service"],
                    "social worker":["social worker","social service"],
                    "psychology":   ["psychologist","counselor","therapist","behavioral"],
                    "therapist":    ["therapist","counselor","therapy"],
                    "counselor":    ["counselor","therapist","advisor","guidance"],
                    "business":     ["manager","administrator","executive","operations","officer"],
                    "finance":      ["financial","accountant","analyst","banker","economist","budget"],
                    "accounting":   ["accountant","auditor","tax","bookkeeper"],
                    "marketing":    ["marketing","advertising","brand","public relations","promotions"],
                    "design":       ["designer","design","art director","creative director"],
                    "art":          ["artist","designer","art director","illustrator","animator","sculptor"],
                    "science":      ["scientist","researcher","biologist","chemist","physicist","geoscientist"],
                    "biology":      ["biologist","biological","microbiolog","geneticist","ecologist"],
                    "health":       ["health","medical","clinical","patient","care","therapist","technician"],
                    "criminal justice":["detective","officer","investigator","correctional","probation","parole"],
                    "police":       ["police","detective","investigator","patrol"],
                    "education":    ["teacher","instructor","principal","educator","school counselor"],
                    "data":         ["data scientist","data analyst","statistician","database","machine learning"],
                    "cyber":        ["cybersecurity","information security","network security","penetration"],
                    "construction": ["construction","contractor","carpenter","electrician","plumber","mason"],
                    "culinary":     ["chef","cook","food","culinary","baker","pastry"],
                    "film":         ["producer","director","editor","filmmaker","cinematographer"],
                    "music":        ["musician","singer","composer","music","conductor"],
                    "public health":["epidemiologist","health educator","public health","environmental health"],
                    "pharmacy":     ["pharmacist","pharmacy","pharmaceutical"],
                    "dental":       ["dentist","dental","orthodontist","periodontist"],
                    "physical therapy":["physical therapist","physiotherapist"],
                    "occupational": ["occupational therapist"],
                    "architecture": ["architect","architectural","urban planner"],
                    "accounting":   ["accountant","auditor","tax preparer","bookkeeper"],
                    "hr":           ["human resources","recruiting","talent","labor relations"],
                    "human resources":["human resources","recruiting","talent","labor relations"],
                    "writing":      ["writer","editor","author","journalist","copywriter","content"],
                    "journalism":   ["journalist","reporter","news","editor","correspondent"],
                    "environment":  ["environmental","ecologist","conservation","wildlife","geoscientist"],
                    "aviation":     ["pilot","air traffic","flight","aviation"],
                    "military":     ["military","army","navy","air force","officer","enlisted"],
                }

                import re as _re

                def career_search_results(term, career_list):
                    """Return ranked O*NET careers for a search term using stems + word matching."""
                    tl = term.lower().strip()
                    stems = SEARCH_STEMS.get(tl, [])
                    # Also try partial key matches (e.g. "physical therapy" matches "physical")
                    if not stems:
                        for key, kstems in SEARCH_STEMS.items():
                            if tl in key or key in tl:
                                stems = kstems
                                break
                    raw_words = [w for w in tl.split() if len(w) > 2]

                    seen = set()
                    exact, strong, partial = [], [], []

                    for c in career_list:
                        soc = c.get('soc','')
                        if soc in seen: continue
                        title_l = c.get('title','').lower()
                        desc_l  = (c.get('description','') or '')[:300].lower()
                        field_l = c.get('field','').lower()

                        # Tier 1: exact phrase in title (highest confidence)
                        if tl in title_l:
                            exact.append(c); seen.add(soc); continue

                        # Tier 2: stem keywords match title (e.g. nursing→nurse)
                        if stems and any(s in title_l for s in stems):
                            strong.append(c); seen.add(soc); continue

                        # Tier 3: all raw words in title
                        if raw_words and all(w in title_l for w in raw_words):
                            strong.append(c); seen.add(soc); continue

                        # Tier 4: any word in title or field
                        if raw_words and any(w in title_l or w in field_l for w in raw_words):
                            partial.append(c); seen.add(soc); continue

                        # Tier 5: stem in description
                        if stems and any(s in desc_l for s in stems):
                            partial.append(c); seen.add(soc)

                    def sal(c): return int(float(c.get('median_annual', 0) or 0))
                    return (
                        sorted(exact,   key=sal, reverse=True) +
                        sorted(strong,  key=sal, reverse=True) +
                        sorted(partial, key=sal, reverse=True)
                    )

                matches_c = career_search_results(search_lower, CAREERS_FULL or [])

                if not matches_c:
                    st.warning(f"No careers found for '{search_career}'. Try: Nurse, Software Engineer, Teacher, Social Worker, Accountant")
                    fields_list = sorted(set(c.get('field','') for c in (CAREERS_FULL or []) if c.get('field')))
                    f_cols = st.columns(4)
                    for fi, fn in enumerate(fields_list[:12]):
                        with f_cols[fi % 4]: st.markdown(f"• {fn}")
                elif not st.session_state.get('career_selected_soc',''):
                    # Show list first — student picks which one before seeing detail
                    top_careers = matches_c[:10]
                    st.markdown(f"**Found {len(top_careers)} {'roles' if len(top_careers)>1 else 'role'} matching '{search_career}'** — pick one to explore:")
                    for idx_c, mc in enumerate(top_careers):
                        mc_sal = int(float(mc.get('median_annual', 0) or 0))
                        mc_field = mc.get('field', '')
                        mc_edu   = mc.get('education', '')
                        col_a, col_b = st.columns([4, 1])
                        with col_a:
                            if st.button(
                                f"{mc.get('title','')}  ·  {mc_field}",
                                key=f"sel_{idx_c}",
                                use_container_width=True
                            ):
                                st.session_state['career_selected_soc'] = mc.get('soc','') or '__single__'
                                st.rerun()
                        with col_b:
                            st.caption(f"${mc_sal:,}/yr" if mc_sal else mc_edu)
                    st.caption("Source: O*NET 30.2 · BLS 2024")
                else:
                    # User picked from list — show detail card
                    selected_soc = st.session_state.get('career_selected_soc', '')
                    career = next((c for c in matches_c if c.get('soc') == selected_soc), matches_c[0])
                    if st.button("← Back to results", key="back_career"):
                        st.session_state['career_selected_soc'] = ''
                        st.rerun()
                    title = career.get('title', '')
                    field = career.get('field', '')
                    try: sal_mid = int(float(career.get('median_annual') or 0))
                    except: sal_mid = 0
                    try: sal_entry = int(float(career.get('entry_annual') or 0))
                    except: sal_entry = 0
                    try: sal_senior = int(float(career.get('experienced_annual') or 0))
                    except: sal_senior = 0
                    growth = career.get('growth_pct', 'N/A')
                    growth = 'N/A' if str(growth) in ['nan','None','','null'] else growth
                    education = career.get('education', 'N/A')
                    job_zone = int(float(career.get('job_zone', 3) or 3))
                    desc = str(career.get('description', '') or '')[:300]
                    daily = str(career.get('daily_tasks', '') or '')
                    tools_str = str(career.get('tech_tools', '') or '')
                    skills = str(career.get('top_skills', '') or '')
                    zone_map = {1:"No degree needed", 2:"High school — 0-2 years",
                                3:"Associate's or Bachelor's — 2-4 years",
                                4:"Bachelor's degree — 4 years", 5:"Graduate degree — 6+ years"}
                    study_req = zone_map.get(job_zone, "Bachelor's degree — 4 years")
                    can_now = job_zone <= 3

                    st.markdown(f"### {title}")
                    st.caption(f"{field} · {study_req}")
                    if desc: st.markdown(f"*{desc[:250]}...*" if len(desc) > 250 else f"*{desc}*")
                    m1, m2, m3, m4 = st.columns(4)
                    FIELD_AVG = {'Arts & Media':72460,'Business & Finance':84005,'Construction & Trades':61550,
                        'Criminal Justice':67290,'Culinary Arts':56520,'Education':62615,'Engineering':98176,
                        'Healthcare':102084,'Law & Justice':139540,'Management':144658,'Personal Care':44160,
                        'Science & Research':92995,'Social Services':57458,'Technology':115734,'Transportation':158115}
                    if not sal_mid:
                        sal_mid = FIELD_AVG.get(field, 65000)
                        sal_entry = int(sal_mid * 0.62)
                        sal_senior = int(sal_mid * 1.45)
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
                        m_cols = st.columns(min(len(rec_majors[:4]), 4))
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
                    R = float(career.get('interest_realistic', 0) or 0)
                    I = float(career.get('interest_investigative', 0) or 0)
                    A = float(career.get('interest_artistic', 0) or 0)
                    S = float(career.get('interest_social', 0) or 0)
                    E = float(career.get('interest_enterprising', 0) or 0)
                    C = float(career.get('interest_conventional', 0) or 0)
                    st.divider()
                    st.markdown("**What kind of person thrives here (O*NET)**")
                    r_cols = st.columns(6)
                    for col, (lbl, val) in zip(r_cols, [("Hands-on",R),("Analytical",I),("Creative",A),("Social",S),("Leadership",E),("Detail",C)]):
                        col.metric(lbl, f"{val:.1f}/7")
                    if len(matches_c) > 1:
                        st.divider()
                        st.markdown(f"**{len(matches_c)-1} related roles:**")
                        for mc in matches_c[1:6]:
                            mc_sal = int(float(mc.get('median_annual', 0) or 0))
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
            # ── Balance Checker ─────────────────────────────────
            st.markdown("#### 📊 List Balance Check")
            total_n = len(my_list)
            col_s, col_m, col_r = st.columns(3)
            col_s.metric("🟢 Safety", safety_n, help="Schools very likely to admit you")
            col_m.metric("🎯 Match", match_n, help="Schools where you're a realistic candidate")
            col_r.metric("⚠️ Reach", reach_n, help="Aspirational schools — worth applying to")

            # Advice based on balance
            advice = []
            if safety_n == 0:
                advice.append("⚠️ **No safety schools.** Add at least 2 schools where you're very likely to get in.")
            elif safety_n < 2:
                advice.append("💡 Consider adding one more safety school — having 2+ gives you a real backup.")
            if match_n < 2:
                advice.append("⚠️ **Not enough match schools.** Add 2–4 schools where your GPA/scores are in their range.")
            if reach_n == 0:
                advice.append("💡 **No reach schools.** Add at least 1 dream school — you might get in!")
            if total_n < 5:
                advice.append("💡 Counselors recommend applying to at least 5–8 schools for the best odds.")
            if total_n >= 5 and safety_n >= 1 and match_n >= 2 and reach_n >= 1:
                advice.append("✅ **Solid list!** Good mix of safety, match, and reach schools.")

            for a in advice:
                st.markdown(a)
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

with tab5:
    st.markdown("### 🗺️ Colleges on the Map")
    _map_matches = st.session_state.get("matches", [])
    _slat = st.session_state.get("student_lat")
    _slon = st.session_state.get("student_lon")
    _szip = st.session_state.get("student_zip", "")

    if not _map_matches:
        st.info("👈 Run a college search first — your results will appear on the map.")
    else:
        if not _slat:
            st.info("💡 Click **📍 Use My Location** in the sidebar — your browser will ask permission once, then distances and your pin appear on the map.")

        try:
            import pydeck as pdk
            import pandas as _pd

            map_rows = []
            for s in _map_matches:
                lat, lon = get_school_coords(s)
                if not lat or not lon:
                    continue
                fit = s.get("fit", "unknown")
                color = {
                    "safety": [46, 160, 87, 230],   # green
                    "match":  [13, 110, 253, 220],  # blue
                    "reach":  [255, 140, 0, 220],   # orange
                }.get(fit, [108, 117, 125, 160])
                dist = ""
                if _slat:
                    try:
                        dm = haversine_miles(_slat, _slon, lat, lon)
                        dist = f" · {dm:.0f} mi"
                    except Exception:
                        pass
                net = s.get("net")
                tuition = s.get("tuition_only", 0) or 0
                map_rows.append({
                    "name": s.get("name", ""),
                    "city": s.get("city", ""),
                    "state": s.get("state", ""),
                    "fit": fit.capitalize(),
                    "net": f"${int(net):,}/yr" if net is not None else "N/A",
                    "tuition": f"${int(tuition):,}" if tuition else "N/A",
                    "dist": dist,
                    "lat": lat,
                    "lon": lon,
                    "color": color,
                    "radius": 12000,
                    "tooltip": f"{s.get('name','')} · {fit.capitalize()}{dist}",
                })

            if _slat:
                map_rows.append({
                    "name": "📍 You", "city": "", "state": "",
                    "fit": "You", "net": "", "tuition": "", "dist": "",
                    "lat": _slat, "lon": _slon,
                    "color": [255, 82, 82, 230],   # red, not black
                    "radius": 6000,                  # much smaller than schools
                    "tooltip": "Your location",
                })

            df_map = _pd.DataFrame(map_rows)

            # Legend
            lc1, lc2, lc3, lc4 = st.columns(4)
            lc1.markdown("🟢 **Safety**")
            lc2.markdown("🔵 **Match**")
            lc3.markdown("🟠 **Reach**")
            if _slat: lc4.markdown("🔴 **You**")

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position=["lon", "lat"],
                get_fill_color="color",
                get_radius="radius",
                pickable=True,
                auto_highlight=True,
            )

            # Center map - guard against empty df_map
            if _slat:
                view_lat, view_lon, zoom = _slat, _slon, 5
            elif len(df_map) > 0 and df_map["lat"].notna().any():
                view_lat = df_map["lat"].dropna().mean()
                view_lon = df_map["lon"].dropna().mean()
                zoom = 5
            else:
                # Default to NYC if no coordinates at all
                view_lat, view_lon, zoom = 40.7128, -74.0060, 6

            view = pdk.ViewState(latitude=view_lat, longitude=view_lon, zoom=zoom, pitch=0)
            tooltip = {"html": "<b>{name}</b><br/>{fit} · {net}<br/>{city}, {state}{dist}",
                       "style": {"background": "#0D1B2A", "color": "white", "fontSize": "13px", "padding": "8px"}}

            if len(df_map) == 0:
                st.warning("⚠️ No coordinate data found for these schools. Make sure schools_full.csv includes latitude/longitude columns from IPEDS.")
            else:
                st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip,
                    map_style="road"))

            # Distance table if zip entered
            if _slat:
                st.markdown("#### 📏 Distance from your zip code")
                dist_rows = []
                for s in _map_matches:
                    lat, lon = get_school_coords(s)
                    if not lat or not lon: continue
                    try:
                        dm = haversine_miles(_slat, _slon, lat, lon)
                        dist_rows.append({
                            "College": s.get("name",""),
                            "Miles": dm,
                            "Fit": s.get("fit","").capitalize(),
                            "You Pay/yr": f"${int(s.get('net') or 0):,}" if s.get("net") is not None else "N/A",
                            "State": s.get("state",""),
                        })
                    except Exception:
                        pass
                dist_rows.sort(key=lambda x: x["Miles"])
                df_dist = _pd.DataFrame(dist_rows)
                df_dist["Miles"] = df_dist["Miles"].apply(lambda x: f"{x:.0f} mi")
                st.dataframe(df_dist, use_container_width=True, hide_index=True,
                    column_config={"College": st.column_config.TextColumn(width="large")})

        except ImportError:
            # pydeck not available — show simple table fallback
            st.warning("Map requires pydeck. Add `pydeck` to requirements.txt.")
            if _map_matches:
                import pandas as _pd
                rows = [{"College": s.get("name",""), "City": s.get("city",""),
                         "State": s.get("state",""), "Fit": s.get("fit","").capitalize()}
                        for s in _map_matches]
                st.dataframe(_pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()
st.caption("Pathways by SLN · IPEDS 2023-24 · Peterson's 2025 · O*NET 30.2 · Aid thresholds 2025-26 · Verify all deadlines on official college websites")
