# ═══════════════════════════════════════════════════════════════
#  PATHWAYS BY SLN — Streamlit App
#  pip install streamlit
#  Run: streamlit run pathways_streamlit.py
# ═══════════════════════════════════════════════════════════════

import streamlit as st

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Pathways by SLN",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F7F3EE; }
    .stApp { background-color: #F7F3EE; }
    h1 { color: #0D1B2A; font-family: Georgia, serif; }
    h2 { color: #0D1B2A; font-family: Georgia, serif; }
    h3 { color: #0D1B2A; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #C9923A;
        margin-bottom: 12px;
    }
    .college-card {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .safety { border-left: 4px solid #4CAF50; }
    .match  { border-left: 4px solid #FFC107; }
    .reach  { border-left: 4px solid #EF5350; }
    .unknown{ border-left: 4px solid #ccc; }
    .big-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #C9923A;
        font-family: Georgia, serif;
    }
    .section-header {
        background: #0D1B2A;
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── COLLEGE DATA ──────────────────────────────────────────────
SCHOOLS = [
    {"id":190688,"name":"Barnard College","city":"New York","state":"NY","ctrl":2,"size":2,"sat25":1420,"sat75":1540,"act25":32,"act75":35,"grad":94,"adm":11.6,"tin":64076,"hbcu":False,"yr2":False,"web":"https://barnard.edu"},
    {"id":190150,"name":"Columbia University","city":"New York","state":"NY","ctrl":2,"size":4,"sat25":1510,"sat75":1570,"act25":34,"act75":36,"grad":96,"adm":3.9,"tin":65524,"hbcu":False,"yr2":False,"web":"https://columbia.edu"},
    {"id":193900,"name":"New York University","city":"New York","state":"NY","ctrl":2,"size":5,"sat25":1370,"sat75":1530,"act25":31,"act75":34,"grad":87,"adm":12.8,"tin":60438,"hbcu":False,"yr2":False,"web":"https://nyu.edu"},
    {"id":190415,"name":"Cornell University","city":"Ithaca","state":"NY","ctrl":2,"size":4,"sat25":1480,"sat75":1560,"act25":34,"act75":35,"grad":95,"adm":7.3,"tin":63200,"hbcu":False,"yr2":False,"web":"https://cornell.edu"},
    {"id":196413,"name":"Syracuse University","city":"Syracuse","state":"NY","ctrl":2,"size":4,"sat25":1230,"sat75":1420,"act25":28,"act75":33,"grad":83,"adm":60.0,"tin":57966,"hbcu":False,"yr2":False,"web":"https://syracuse.edu"},
    {"id":192439,"name":"Fordham University","city":"Bronx","state":"NY","ctrl":2,"size":4,"sat25":1330,"sat75":1490,"act25":30,"act75":33,"grad":83,"adm":56.3,"tin":60335,"hbcu":False,"yr2":False,"web":"https://fordham.edu"},
    {"id":196097,"name":"Stony Brook University","city":"Stony Brook","state":"NY","ctrl":1,"size":5,"sat25":1320,"sat75":1500,"act25":30,"act75":34,"grad":77,"adm":49.0,"tin":7070,"hbcu":False,"yr2":False,"web":"https://stonybrook.edu"},
    {"id":196060,"name":"Binghamton University (SUNY)","city":"Binghamton","state":"NY","ctrl":1,"size":4,"sat25":1310,"sat75":1480,"act25":29,"act75":33,"grad":83,"adm":40.0,"tin":7070,"hbcu":False,"yr2":False,"web":"https://binghamton.edu"},
    {"id":190637,"name":"City College of New York (CUNY)","city":"New York","state":"NY","ctrl":1,"size":4,"sat25":1050,"sat75":1270,"grad":52,"adm":47.0,"tin":6930,"hbcu":False,"yr2":False,"web":"https://ccny.cuny.edu"},
    {"id":190512,"name":"Brooklyn College (CUNY)","city":"Brooklyn","state":"NY","ctrl":1,"size":4,"sat25":1080,"sat75":1270,"grad":55,"adm":40.0,"tin":6930,"hbcu":False,"yr2":False,"web":"https://brooklyn.cuny.edu"},
    {"id":190549,"name":"Hunter College (CUNY)","city":"New York","state":"NY","ctrl":1,"size":4,"sat25":1110,"sat75":1310,"grad":57,"adm":32.0,"tin":6930,"hbcu":False,"yr2":False,"web":"https://hunter.cuny.edu"},
    {"id":190558,"name":"Queens College (CUNY)","city":"Queens","state":"NY","ctrl":1,"size":4,"sat25":1080,"sat75":1280,"grad":56,"adm":42.0,"tin":6930,"hbcu":False,"yr2":False,"web":"https://qc.cuny.edu"},
    {"id":196185,"name":"SUNY New Paltz","city":"New Paltz","state":"NY","ctrl":1,"size":3,"sat25":1150,"sat75":1340,"grad":73,"adm":52.0,"tin":7070,"hbcu":False,"yr2":False,"web":"https://newpaltz.edu"},
    {"id":196079,"name":"University at Buffalo (SUNY)","city":"Buffalo","state":"NY","ctrl":1,"size":5,"sat25":1200,"sat75":1390,"act25":26,"act75":31,"grad":75,"adm":55.0,"tin":7070,"hbcu":False,"yr2":False,"web":"https://buffalo.edu"},
    {"id":131520,"name":"Howard University","city":"Washington","state":"DC","ctrl":2,"size":3,"sat25":1100,"sat75":1290,"act25":22,"act75":28,"grad":67,"adm":37.0,"tin":29780,"hbcu":True,"yr2":False,"web":"https://howard.edu"},
    {"id":166027,"name":"Harvard University","city":"Cambridge","state":"MA","ctrl":2,"size":4,"sat25":1510,"sat75":1580,"act25":34,"act75":36,"grad":98,"adm":3.2,"tin":57261,"hbcu":False,"yr2":False,"web":"https://harvard.edu"},
    {"id":198419,"name":"Duke University","city":"Durham","state":"NC","ctrl":2,"size":4,"sat25":1500,"sat75":1570,"act25":34,"act75":35,"grad":95,"adm":6.0,"tin":62688,"hbcu":False,"yr2":False,"web":"https://duke.edu"},
    {"id":195003,"name":"Rochester Institute of Technology","city":"Rochester","state":"NY","ctrl":2,"size":4,"sat25":1240,"sat75":1430,"act25":28,"act75":33,"grad":70,"adm":64.0,"tin":54888,"hbcu":False,"yr2":False,"web":"https://rit.edu"},
    {"id":193353,"name":"Marist College","city":"Poughkeepsie","state":"NY","ctrl":2,"size":3,"sat25":1220,"sat75":1360,"act25":27,"act75":30,"grad":79,"adm":64.7,"tin":45330,"hbcu":False,"yr2":False,"web":"https://marist.edu"},
    {"id":192323,"name":"Hofstra University","city":"Hempstead","state":"NY","ctrl":2,"size":3,"sat25":1210,"sat75":1380,"act25":27,"act75":31,"grad":72,"adm":70.6,"tin":54335,"hbcu":False,"yr2":False,"web":"https://hofstra.edu"},
]

CAREERS = [
    {"id":"rn","name":"Registered Nurse","icon":"🏥","field":"Healthcare","cip":"51","salary_entry":55000,"salary_mid":77600,"salary_senior":100000,"growth":"6%","demand":"High","why":"You want to help people directly and build a stable career.","day":"Check on patients, administer medications, coordinate with doctors. No two days the same.","majors":["Nursing (BSN)","Health Sciences","Biology"],"traits":{"people":5,"helping":5,"science":4,"creativity":2,"data":2,"physical":3,"leadership":3,"outdoors":1},"values":{"impact":5,"stability":5,"income":3,"creativity":2,"autonomy":3,"prestige":3},"styles":{"solo":1,"team":5,"variety":4,"routine":2,"indoors":5,"outdoors":1}},
    {"id":"cs","name":"Software Developer","icon":"💻","field":"Technology","cip":"11","salary_entry":75000,"salary_mid":124200,"salary_senior":180000,"growth":"25%","demand":"Very High","why":"You like solving complex problems and want strong income.","day":"Write code, debug systems, build apps. Remote work is common.","majors":["Computer Science","Software Engineering","IT"],"traits":{"people":2,"helping":2,"science":4,"creativity":4,"data":5,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":3,"stability":4,"income":5,"creativity":4,"autonomy":5,"prestige":4},"styles":{"solo":4,"team":3,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"teacher","name":"K-12 Teacher","icon":"📚","field":"Education","cip":"13","salary_entry":42000,"salary_mid":62360,"salary_senior":82000,"growth":"1%","demand":"Steady","why":"You want to shape the next generation.","day":"Plan lessons, teach, grade work, mentor students.","majors":["Education (K-12)","English Education","Math Education"],"traits":{"people":5,"helping":5,"science":2,"creativity":4,"data":2,"physical":2,"leadership":4,"outdoors":2},"values":{"impact":5,"stability":5,"income":2,"creativity":4,"autonomy":3,"prestige":2},"styles":{"solo":2,"team":4,"variety":3,"routine":4,"indoors":5,"outdoors":2}},
    {"id":"social_worker","name":"Social Worker","icon":"🤝","field":"Social Services","cip":"19","salary_entry":38000,"salary_mid":55350,"salary_senior":75000,"growth":"7%","demand":"High","why":"You care about communities and want work that makes a real difference.","day":"Meet families in crisis, connect them to resources, advocate for their rights.","majors":["Social Work (BSW)","Psychology","Sociology"],"traits":{"people":5,"helping":5,"science":2,"creativity":3,"data":2,"physical":2,"leadership":3,"outdoors":2},"values":{"impact":5,"stability":4,"income":2,"creativity":3,"autonomy":3,"prestige":2},"styles":{"solo":2,"team":4,"variety":5,"routine":2,"indoors":4,"outdoors":3}},
    {"id":"engineer","name":"Engineer","icon":"🏗️","field":"Engineering","cip":"14","salary_entry":65000,"salary_mid":88050,"salary_senior":130000,"growth":"5%","demand":"High","why":"You want to build real things and earn strong income.","day":"Design systems, review blueprints, manage contractors, visit sites.","majors":["Civil Engineering","Mechanical Engineering","Environmental Engineering"],"traits":{"people":2,"helping":2,"science":5,"creativity":4,"data":5,"physical":3,"leadership":3,"outdoors":4},"values":{"impact":4,"stability":5,"income":4,"creativity":4,"autonomy":3,"prestige":3},"styles":{"solo":3,"team":4,"variety":4,"routine":3,"indoors":3,"outdoors":4}},
    {"id":"finance","name":"Financial Analyst","icon":"📊","field":"Business & Finance","cip":"52","salary_entry":58000,"salary_mid":95080,"salary_senior":155000,"growth":"8%","demand":"High","why":"You want financial security and a clear advancement path.","day":"Analyze data, build financial models, advise on money decisions.","majors":["Finance","Accounting","Business Administration","Economics"],"traits":{"people":2,"helping":2,"science":3,"creativity":2,"data":5,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":2,"stability":5,"income":5,"creativity":2,"autonomy":3,"prestige":4},"styles":{"solo":4,"team":3,"variety":3,"routine":4,"indoors":5,"outdoors":1}},
    {"id":"therapist","name":"Counselor / Therapist","icon":"🧠","field":"Mental Health","cip":"42","salary_entry":42000,"salary_mid":58510,"salary_senior":90000,"growth":"18%","demand":"Very High","why":"You want to help people through their hardest moments.","day":"Sit with people during difficult times, help them build coping skills.","majors":["Psychology","Counseling (MS)","Social Work (MSW)"],"traits":{"people":5,"helping":5,"science":3,"creativity":3,"data":3,"physical":1,"leadership":2,"outdoors":1},"values":{"impact":5,"stability":4,"income":3,"creativity":3,"autonomy":4,"prestige":3},"styles":{"solo":3,"team":2,"variety":3,"routine":4,"indoors":5,"outdoors":1}},
    {"id":"data_scientist","name":"Data Scientist","icon":"📈","field":"Technology & Analytics","cip":"11","salary_entry":70000,"salary_mid":105000,"salary_senior":165000,"growth":"35%","demand":"Very High","why":"You love finding patterns in data and turning numbers into decisions.","day":"Collect, clean and analyze datasets. Mix of statistics, programming, storytelling.","majors":["Data Science","Statistics","Computer Science","Mathematics"],"traits":{"people":2,"helping":2,"science":5,"creativity":4,"data":5,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":3,"stability":4,"income":5,"creativity":4,"autonomy":4,"prestige":4},"styles":{"solo":4,"team":3,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"pa","name":"Physician Assistant / NP","icon":"⚕️","field":"Healthcare","cip":"51","salary_entry":85000,"salary_mid":121530,"salary_senior":150000,"growth":"28%","demand":"Very High","why":"Top-level healthcare without a 10-year medical school commitment.","day":"Diagnose illnesses, prescribe medications, treat patients with high autonomy.","majors":["Pre-Medicine","Biology","Health Sciences","Nursing (BSN)"],"traits":{"people":4,"helping":5,"science":5,"creativity":3,"data":4,"physical":3,"leadership":4,"outdoors":1},"values":{"impact":5,"stability":4,"income":5,"creativity":3,"autonomy":4,"prestige":5},"styles":{"solo":2,"team":4,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"marketing","name":"Marketing Manager","icon":"📣","field":"Marketing","cip":"52","salary_entry":48000,"salary_mid":85000,"salary_senior":145000,"growth":"6%","demand":"Moderate","why":"You love creating and communicating.","day":"Craft campaigns, manage social media, analyze results, tell brand stories.","majors":["Marketing","Communications","Business Administration"],"traits":{"people":4,"helping":2,"science":2,"creativity":5,"data":4,"physical":1,"leadership":4,"outdoors":2},"values":{"impact":3,"stability":3,"income":4,"creativity":5,"autonomy":4,"prestige":3},"styles":{"solo":2,"team":4,"variety":5,"routine":2,"indoors":4,"outdoors":2}},
    {"id":"lawyer","name":"Attorney / Lawyer","icon":"⚖️","field":"Law & Justice","cip":"22","salary_entry":72000,"salary_mid":126000,"salary_senior":220000,"growth":"4%","demand":"Moderate","why":"You are drawn to justice and how society rules work.","day":"Research legal questions, write arguments, advise clients, negotiate deals.","majors":["Pre-Law","Political Science","Criminal Justice","English"],"traits":{"people":3,"helping":3,"science":2,"creativity":4,"data":4,"physical":1,"leadership":4,"outdoors":1},"values":{"impact":4,"stability":4,"income":5,"creativity":4,"autonomy":4,"prestige":5},"styles":{"solo":4,"team":3,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
    {"id":"cybersecurity","name":"Cybersecurity Analyst","icon":"🔐","field":"Technology","cip":"11","salary_entry":70000,"salary_mid":112000,"salary_senior":175000,"growth":"32%","demand":"Critical","why":"One of the fastest-growing and most in-demand fields in tech.","day":"Monitor networks for threats, investigate breaches, stay ahead of hackers.","majors":["Cybersecurity","Computer Science","Information Technology"],"traits":{"people":2,"helping":3,"science":4,"creativity":4,"data":5,"physical":1,"leadership":3,"outdoors":1},"values":{"impact":4,"stability":5,"income":5,"creativity":4,"autonomy":4,"prestige":4},"styles":{"solo":4,"team":3,"variety":4,"routine":3,"indoors":5,"outdoors":1}},
]

DEADLINES = {
    190637:{"rd":"Feb 1","ea":"Nov 21","sys":"CUNY"},190512:{"rd":"Feb 1","ea":"Nov 21","sys":"CUNY"},
    190549:{"rd":"Feb 1","ea":"Nov 21","sys":"CUNY"},190558:{"rd":"Feb 1","ea":"Nov 21","sys":"CUNY"},
    196097:{"rd":"Feb 1","ea":"Nov 1","sys":"SUNY"},196060:{"rd":"Rolling","ea":"Nov 15","sys":"SUNY"},
    196079:{"rd":"Rolling","sys":"SUNY"},196185:{"rd":"Rolling","ea":"Nov 15","sys":"SUNY"},
    192439:{"rd":"Jan 3","ed":"Nov 1"},193900:{"rd":"Jan 1","ed":"Nov 1"},
    190688:{"rd":"Jan 1","ed":"Nov 1"},190150:{"rd":"Jan 1","ed":"Nov 1"},
    190415:{"rd":"Jan 2","ed":"Nov 1"},166027:{"rd":"Jan 1","ea":"Nov 1"},
    131520:{"rd":"Feb 15","ed":"Nov 1"},198419:{"rd":"Jan 5","ed":"Nov 3"},
}

# ── CORE ENGINES ──────────────────────────────────────────────
def calculate_aid(income, hsize, ny_res, immig, first_gen):
    pell = tap = dream = 0
    heop = False
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
    cuts=[22400,30240,38080,45920,53760,61600]
    if ny_res and first_gen and income<=cuts[min(hsize-1,5)] and immig!='undocumented':
        heop=True
    return {"pell":pell,"tap":tap,"dream":dream,"heop":heop,"total":pell+tap+dream}

def get_fit(sat, act, s):
    if sat and s.get('sat25') and s.get('sat75'):
        if sat>=s['sat75']: return 'safety'
        if sat>=s['sat25']: return 'match'
        return 'reach'
    if act and s.get('act25') and s.get('act75'):
        if act>=s['act75']: return 'safety'
        if act>=s['act25']: return 'match'
        return 'reach'
    adm=s.get('adm')
    if adm:
        if adm>70: return 'safety'
        if adm>40: return 'match'
        return 'reach'
    return 'unknown'

def run_match(gpa, sat, act, state, size, ctrl, need, env, study_yrs, aid, n):
    size_codes={'any':[1,2,3,4,5],'small':[1,2],'medium':[3,4],'large':[5]}.get(size,[1,2,3,4,5])
    ctrl_codes={'any':[1,2],'public':[1],'private':[2]}.get(ctrl,[1,2])
    results=[]
    for s in SCHOOLS:
        if state!='any' and s['state'].lower()!=state.lower(): continue
        if s['size'] not in size_codes: continue
        if s['ctrl'] not in ctrl_codes: continue
        if need=='full' and s['tin']>55000: continue
        if env=='hbcu' and not s.get('hbcu'): continue
        if study_yrs=='2yr' and not s.get('yr2'): continue
        if study_yrs=='4yr' and s.get('yr2'): continue
        fit=get_fit(sat,act,s)
        net=max(0,s['tin']-aid['total']) if s.get('tin') else None
        results.append({**s,'fit':fit,'net':net})
    results.sort(key=lambda x:(x['net'] is None, x['net'] or 999999))
    return results[:n]

def score_career(career, profile):
    score=0.0; max_score=0.0
    for key,w in [('traits',10),('values',15),('styles',8)]:
        for k,cv in career[key].items():
            pv=profile.get(k,0); max_score+=w
            score+=(1-abs(min(pv/15.0,1.0)-cv/5.0))*w
    return round((score/max_score)*100) if max_score>0 else 0

def run_career_match(answers):
    profile={}
    for vals in answers.values():
        for k,v in vals.items(): profile[k]=profile.get(k,0)+v
    scored=[{**c,'fit':score_career(c,profile)} for c in CAREERS]
    return sorted(scored,key=lambda x:x['fit'],reverse=True)

# ── STREAMLIT APP ─────────────────────────────────────────────

# Header
col1, col2 = st.columns([3,1])
with col1:
    st.markdown("# 🎓 Pathways by SLN")
    st.markdown("*Your college list, built around your life.*")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Built by SLN RITA Tech & Data Intern")

st.divider()

# Sidebar — all inputs
with st.sidebar:
    st.markdown("## 📝 Your Profile")
    st.caption("Fill in your info — results update automatically")

    # STEP 1: Academics
    st.markdown("### 📚 Step 1 — Academics")
    gpa = st.slider("Unweighted GPA", 0.0, 4.0, 3.0, 0.1)

    score_type = st.selectbox("Test scores", ["None (test-optional)", "SAT", "ACT"])
    sat = act = None
    if score_type == "SAT":
        sat = st.number_input("SAT Score", 400, 1600, 1100, 10)
    elif score_type == "ACT":
        act = st.number_input("ACT Score", 1, 36, 24, 1)

    # STEP 2: Career
    st.markdown("### 🎯 Step 2 — Career Discovery")
    st.caption("Answer all 8 questions to get your career matches")

    q_answers = {}

    q_answers['i1'] = st.selectbox("What excites you most?", [
        "Helping and healing people",
        "Building and engineering things",
        "Teaching and shaping communities",
        "Running businesses and managing money",
        "Creating, designing and communicating",
        "Researching, analyzing and discovering",
    ])
    q_answers['i2'] = st.selectbox("What matters most in a career?", [
        "High income",
        "Making a real difference",
        "Creative freedom",
        "Stability and security",
        "Prestige and recognition",
    ])
    q_answers['i3'] = st.selectbox("Where do you want to work?", [
        "With people (patients, students, clients)",
        "At a desk or computer",
        "Out in the field (moving, hands-on)",
        "In a lab, hospital, or studio",
        "Anywhere (remote/flexible)",
    ])
    q_answers['i4'] = st.selectbox("Best subject in school?", [
        "Science or Math",
        "English, Writing, or Communication",
        "Art, Music, or Design",
        "Social Studies or History",
        "Technology or Computer Science",
        "Physical Education or Health",
    ])
    q_answers['i5'] = st.selectbox("How long willing to study?", [
        "1-2 years (start earning soon)",
        "4 years (bachelor's degree)",
        "6-8 years (graduate school)",
        "Whatever it takes",
    ])
    q_answers['i6'] = st.selectbox("Which describes you best?", [
        "I love working with my hands",
        "I love understanding how people feel",
        "I love solving complex problems",
        "I love building or making things",
        "I love organizing, planning and leading",
    ])
    q_answers['i7'] = st.selectbox("In 10 years I see myself...", [
        "Running my own business",
        "Recognized expert in my field",
        "Making a meaningful community impact",
        "Financially secure",
        "Doing creative work I am proud of",
    ])
    q_answers['i8'] = st.selectbox("Best work environment?", [
        "Fast-paced with new challenges",
        "Steady and predictable",
        "Collaborative team work",
        "Independent, working alone",
        "Helping individuals one-on-one",
    ])

    # STEP 3: Financial Aid
    st.markdown("### 💰 Step 3 — Financial Aid")
    st.caption("Your answers are private — used only to estimate aid")

    income = st.number_input("Annual household income ($)", 0, 500000, 42000, 1000)
    hsize  = st.slider("Household size", 1, 10, 4)
    ny_res = st.checkbox("NY State resident (12+ months)", value=True)
    immig  = st.selectbox("Immigration/citizenship status", [
        "US Citizen or Green Card",
        "DACA",
        "Undocumented",
        "Visa or other status",
    ])
    first_gen = st.checkbox("First-generation college student", value=True)

    # STEP 4: Preferences
    st.markdown("### 🗺️ Step 4 — Preferences")

    state_pref = st.selectbox("Preferred state", ["NY","Any","CA","MA","NJ","PA","TX","FL","IL"])
    school_size = st.selectbox("School size", ["Any","Small (<5k)","Medium (5-20k)","Large (20k+)"])
    school_type = st.selectbox("School type", ["Any","Public","Private"])
    env_pref   = st.selectbox("Campus environment", ["Any","HBCU","Women's College","Diverse"])
    study_yrs  = st.selectbox("Years willing to study", ["Any","2 years (Associate)","4 years (Bachelor's+)"])
    n_results  = st.select_slider("Number of results", [5,10,15,20], 10)

    run_btn = st.button("🔍 Find My Colleges", type="primary", use_container_width=True)

# ── PROCESS INPUTS ────────────────────────────────────────────

# Map dropdown answers to profile values
CAREER_MAPS = {
    'i1': {
        "Helping and healing people":            {"helping":3,"people":3},
        "Building and engineering things":       {"building":3,"science":2},
        "Teaching and shaping communities":      {"teaching":3,"people":2},
        "Running businesses and managing money": {"business":3,"leadership":2},
        "Creating, designing and communicating": {"creating":3,"creativity":3},
        "Researching, analyzing and discovering":{"analyzing":3,"data":3},
    },
    'i2': {
        "High income":               {"income":3,"prestige":1},
        "Making a real difference":  {"impact":3,"helping":2},
        "Creative freedom":          {"creativity":3,"autonomy":3},
        "Stability and security":    {"stability":3},
        "Prestige and recognition":  {"prestige":3,"leadership":2},
    },
    'i3': {
        "With people (patients, students, clients)":{"people":3,"helping":2},
        "At a desk or computer":                    {"data":2,"analyzing":2},
        "Out in the field (moving, hands-on)":      {"outdoors":3,"physical":3},
        "In a lab, hospital, or studio":            {"science":2,"creating":2},
        "Anywhere (remote/flexible)":               {"autonomy":3},
    },
    'i4': {
        "Science or Math":                     {"science":3,"data":2},
        "English, Writing, or Communication":  {"creating":2,"people":2},
        "Art, Music, or Design":               {"creativity":3,"creating":2},
        "Social Studies or History":           {"people":2,"teaching":2},
        "Technology or Computer Science":      {"building":3,"data":3},
        "Physical Education or Health":        {"physical":3,"helping":2},
    },
    'i5': {
        "1-2 years (start earning soon)":  {"stability":2},
        "4 years (bachelor's degree)":     {"income":1},
        "6-8 years (graduate school)":     {"prestige":2,"income":2},
        "Whatever it takes":               {"prestige":3,"income":3},
    },
    'i6': {
        "I love working with my hands":            {"physical":3,"building":2},
        "I love understanding how people feel":    {"people":3,"helping":3},
        "I love solving complex problems":         {"analyzing":3,"data":3},
        "I love building or making things":        {"creating":3,"building":2},
        "I love organizing, planning and leading": {"leadership":3,"business":2},
    },
    'i7': {
        "Running my own business":              {"autonomy":3,"leadership":3},
        "Recognized expert in my field":        {"prestige":3,"science":2},
        "Making a meaningful community impact": {"impact":3,"helping":3},
        "Financially secure":                   {"stability":3,"income":3},
        "Doing creative work I am proud of":    {"creativity":3,"creating":3},
    },
    'i8': {
        "Fast-paced with new challenges":  {"variety":3,"leadership":2},
        "Steady and predictable":          {"stability":3,"routine":2},
        "Collaborative team work":         {"people":2,"team":3},
        "Independent, working alone":      {"autonomy":3,"analyzing":2},
        "Helping individuals one-on-one":  {"helping":3,"people":3},
    },
}

# Map UI values to engine values
immig_map = {
    "US Citizen or Green Card":"citizen",
    "DACA":"daca",
    "Undocumented":"undocumented",
    "Visa or other status":"other"
}
size_map = {"Any":"any","Small (<5k)":"small","Medium (5-20k)":"medium","Large (20k+)":"large"}
ctrl_map = {"Any":"any","Public":"public","Private":"private"}
env_map  = {"Any":"any","HBCU":"hbcu","Women's College":"womens","Diverse":"diverse"}
yrs_map  = {"Any":"any","2 years (Associate)":"2yr","4 years (Bachelor's+)":"4yr"}

# Always compute career results (live)
career_answers = {k: CAREER_MAPS[k][v] for k,v in q_answers.items()}
career_results = run_career_match(career_answers)
top = career_results[0]

# Compute aid always
immig_val = immig_map[immig]
aid = calculate_aid(income, hsize, ny_res, immig_val, first_gen)

# ── MAIN RESULTS AREA ─────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "🏫 College Matches",
    "🎯 Career Results",
    "💰 Aid Eligibility",
    "📋 My List"
])

# ── TAB 1: COLLEGE MATCHES ────────────────────────────────────
with tab1:
    if not run_btn:
        st.info("👈 Fill in your profile on the left, then click **Find My Colleges** to see your matches.")
    else:
        state_val = "any" if state_pref == "Any" else state_pref
        need_val  = "full" if income < 50000 else "some"
        matches = run_match(
            gpa, sat, act,
            state_val,
            size_map[school_size],
            ctrl_map[school_type],
            need_val,
            env_map[env_pref],
            yrs_map[study_yrs],
            aid,
            n_results
        )

        # Summary row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Colleges Found", len(matches))
        with c2:
            st.metric("Est. Annual Aid", f"${aid['total']:,}")
        with c3:
            safety_n = sum(1 for s in matches if s['fit']=='safety')
            match_n  = sum(1 for s in matches if s['fit']=='match')
            reach_n  = sum(1 for s in matches if s['fit']=='reach')
            st.metric("Safety / Match / Reach", f"{safety_n} / {match_n} / {reach_n}")
        with c4:
            st.metric("Top Career Match", top['name'])

        st.divider()

        if not matches:
            st.warning("No colleges matched your filters. Try changing your state preference to 'Any'.")
        else:
            fit_colors = {"safety":"🟢","match":"🟡","reach":"🔴","unknown":"⚪"}
            for s in matches:
                fit = s.get('fit','unknown')
                net = s.get('net')
                sticker = s.get('tin',0)
                dl = DEADLINES.get(s['id'],{"rd":"Check website"})

                with st.container():
                    col_a, col_b, col_c = st.columns([3,1,1])
                    with col_a:
                        st.markdown(f"**{fit_colors.get(fit,'⚪')} [{s['name']}]({s.get('web','#')})**")
                        st.caption(f"{s.get('city','')}, {s['state']} · {'Public' if s['ctrl']==1 else 'Private'} · {s.get('adm','')}% acceptance" + (" · 🏛️ HBCU" if s.get('hbcu') else ""))
                        # Chips
                        chips = f"`{fit.capitalize()}` "
                        if s.get('sat25'): chips += f"`SAT {s['sat25']}–{s['sat75']}` "
                        if s.get('act25'): chips += f"`ACT {s['act25']}–{s['act75']}` "
                        if aid['tap']>0 and s['state']=='NY': chips += "`TAP eligible` "
                        if aid['heop'] and s['state']=='NY': chips += "`HEOP` "
                        st.markdown(chips)
                    with col_b:
                        st.markdown(f"**Sticker:** ${sticker:,}" if sticker else "N/A")
                        if net is not None:
                            color = "green" if net == 0 else "blue"
                            label = "Fully covered! 🎉" if net == 0 else f"${net:,}/yr"
                            st.markdown(f"**You pay:** :{color}[{label}]")
                    with col_c:
                        st.markdown(f"**RD:** {dl.get('rd','?')}")
                        early = dl.get('ed') or dl.get('ea','')
                        if early: st.markdown(f"**Early:** {early}")
                        if s.get('grad'): st.markdown(f"**Grad rate:** {s['grad']}%")
                    # Counselor note
                    if fit == 'safety':
                        st.success("Your profile is above their range. Strong safety school — apply with confidence.")
                    elif fit == 'match':
                        st.info("Your profile is in their range. A solid application should be competitive.")
                    elif fit == 'reach':
                        st.warning("Your profile is below their range. A strong essay and story can still get you in.")
                    st.divider()

# ── TAB 2: CAREER RESULTS ─────────────────────────────────────
with tab2:
    st.markdown(f"### Your top career matches")
    st.caption("Results update live as you change your answers on the left")

    # Top match banner
    st.markdown(f"""
    <div style="background:#0D1B2A;border-radius:12px;padding:24px;margin-bottom:20px;color:white">
        <div style="font-size:12px;opacity:.5;margin-bottom:4px">YOUR BEST MATCH</div>
        <div style="font-size:28px;font-family:Georgia,serif;margin-bottom:6px">{top['icon']} {top['name']}</div>
        <div style="font-size:14px;opacity:.6;margin-bottom:12px">{top['why']}</div>
        <div style="display:flex;gap:20px;flex-wrap:wrap">
            <span style="color:#E8AD58;font-size:20px;font-weight:700">${top['salary_mid']:,}/yr avg</span>
            <span style="background:rgba(42,96,73,.4);padding:4px 12px;border-radius:8px;font-size:13px">{top['growth']} job growth</span>
            <span style="background:rgba(255,255,255,.1);padding:4px 12px;border-radius:8px;font-size:13px">{top['demand']} demand</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Career cards grid
    for i, c in enumerate(career_results[:10], 1):
        pct = c['fit']
        color = "#2A6049" if pct>=70 else "#C9923A" if pct>=50 else "#9E9E9E"
        with st.expander(f"{c['icon']} {c['name']}  —  **{pct}% match** · ${c['salary_mid']:,}/yr avg"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Entry Salary", f"${c['salary_entry']:,}")
            col2.metric("Mid Career", f"${c['salary_mid']:,}")
            col3.metric("Senior Level", f"${c['salary_senior']:,}")
            st.progress(pct / 100)
            st.markdown(f"**A day in the life:** {c['day']}")
            st.markdown(f"**Majors that lead here:** {', '.join(c['majors'])}")
            st.markdown(f"**Job growth:** {c['growth']} · **Demand:** {c['demand']}")

# ── TAB 3: AID ELIGIBILITY ────────────────────────────────────
with tab3:
    st.markdown("### Your financial aid eligibility")
    st.caption("Based on 2025-26 federal and NY State thresholds")

    col1, col2 = st.columns([2,1])
    with col1:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Pell Grant", f"${aid['pell']:,}" if aid['pell']>0 else "❌", delta="Eligible" if aid['pell']>0 else None)
        c2.metric("NY TAP", f"${aid['tap']:,}" if aid['tap']>0 else "❌", delta="Eligible" if aid['tap']>0 else None)
        c3.metric("Dream Act", f"${aid['dream']:,}" if aid['dream']>0 else "❌", delta="Eligible" if aid['dream']>0 else None)
        c4.metric("HEOP", "✅ Eligible" if aid['heop'] else "❌", delta="NY schools" if aid['heop'] else None)

        st.divider()
        total = aid['total']
        st.markdown(f"### 💵 Total estimated annual aid: ${total:,}")
        st.caption("These are grants — they do not need to be repaid.")

        if aid['heop']:
            st.success("🎓 You are HEOP eligible — this provides additional support at participating NY colleges including tutoring, counseling, and academic resources.")

    with col2:
        st.markdown("**What each program is:**")
        st.markdown("""
        - **Pell Grant** — Federal free money for low-income students
        - **TAP** — NY State tuition assistance (NY residents only)
        - **Dream Act** — TAP-equivalent for undocumented/DACA students
        - **HEOP** — Additional NY support for first-gen, low-income students
        """)
        st.info("💡 Complete your FAFSA at **studentaid.gov** to receive your actual aid award.")

# ── TAB 4: MY LIST ────────────────────────────────────────────
with tab4:
    st.markdown("### Build your college list")
    st.caption("Run College Matches first, then come back here to build your balanced list")

    if run_btn:
        state_val = "any" if state_pref == "Any" else state_pref
        need_val  = "full" if income < 50000 else "some"
        matches = run_match(gpa, sat, act, state_val, size_map[school_size],
                           ctrl_map[school_type], need_val, env_map[env_pref],
                           yrs_map[study_yrs], aid, 20)

        if matches:
            st.markdown("**Select colleges for your list:**")
            selected = []
            cols = st.columns(2)
            for i, s in enumerate(matches[:12]):
                fit = s.get('fit','unknown')
                icons = {"safety":"🟢","match":"🟡","reach":"🔴","unknown":"⚪"}
                net = f"${s['net']:,}" if s.get('net') is not None else "N/A"
                with cols[i % 2]:
                    if st.checkbox(f"{icons.get(fit,'⚪')} {s['name']} — {fit.capitalize()} — {net}/yr", key=f"sel_{s['id']}"):
                        selected.append(s)

            if selected:
                st.divider()
                st.markdown(f"### Your list: {len(selected)} colleges")
                safety_n = sum(1 for s in selected if s['fit']=='safety')
                match_n  = sum(1 for s in selected if s['fit']=='match')
                reach_n  = sum(1 for s in selected if s['fit']=='reach')

                c1,c2,c3 = st.columns(3)
                c1.metric("Safety", safety_n)
                c2.metric("Match", match_n)
                c3.metric("Reach", reach_n)

                if safety_n < 2:
                    st.warning("⚠️ Add more safety schools — where your scores are above their typical range.")
                elif reach_n < 1:
                    st.info("💡 Consider adding 1-2 reach schools. A strong application can surprise you.")
                elif match_n < 2:
                    st.info("📋 Add more match schools — these tend to be your most likely admits.")
                else:
                    st.success("✅ Great balance! Apply to all of them.")

                st.markdown("**Your list with deadlines:**")
                for s in selected:
                    dl = DEADLINES.get(s['id'],{"rd":"Check website"})
                    net = f"${s['net']:,}" if s.get('net') is not None else "N/A"
                    fit = s.get('fit','unknown').capitalize()
                    early = dl.get('ed') or dl.get('ea','N/A')
                    st.markdown(f"- **{s['name']}** — {fit} — {net}/yr — RD: {dl.get('rd','?')} — Early: {early} — [Apply ↗]({s.get('web','#')})")
    else:
        st.info("👈 Click **Find My Colleges** first to see your matches here.")

# Footer
st.divider()
st.caption("Pathways by SLN · Built on IPEDS 2023-24 Federal Data · Aid thresholds: 2025-26 · Always verify deadlines on official college websites")
