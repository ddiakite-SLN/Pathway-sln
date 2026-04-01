# ═══════════════════════════════════════════════════════════════
#  PATHWAYS BY SLN — Streamlit App v2
#  Fixed: persistent college list + PDF export
# ═══════════════════════════════════════════════════════════════

import streamlit as st
from io import BytesIO

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
    return schools

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
    cuts=[22400,30240,38080,45920,53760,61600]
    if ny_res and first_gen and income<=cuts[min(hsize-1,5)] and immig!='undocumented':
        heop=True
    return {"pell":pell,"tap":tap,"dream":dream,"heop":heop,"total":pell+tap+dream}

def get_fit(sat, act, s, gpa=None):
    # Test score based (most accurate)
    if sat and s.get('sat25') and s.get('sat75'):
        if sat >= s['sat75']: return 'safety'
        if sat >= s['sat25']: return 'match'
        return 'reach'
    if act and s.get('act25') and s.get('act75'):
        if act >= s['act75']: return 'safety'
        if act >= s['act25']: return 'match'
        return 'reach'
    # GPA + acceptance rate estimation
    adm = s.get('adm')
    if gpa and adm:
        if adm >= 80: return 'safety'
        if adm >= 60: return 'safety' if gpa >= 3.0 else 'match'
        if adm >= 40: return 'match' if gpa >= 2.8 else 'reach'
        if adm >= 20: return 'match' if gpa >= 3.5 else 'reach'
        return 'reach'
    if adm:
        if adm >= 80: return 'safety'
        if adm >= 50: return 'match'
        return 'reach'
    return 'unknown'

def run_match(gpa, sat, act, state, size, ctrl, need, env, study_yrs, aid, n):
    size_codes={'any':[1,2,3,4,5],'small':[1,2],'medium':[3,4],'large':[5]}.get(size,[1,2,3,4,5])
    ctrl_codes={'any':[1,2,3,'1','2','3'],'public':[1,'1'],'private':[2,'2'],'any_str':['1','2','3']}.get(ctrl,[1,2])
    results=[]
    for s in SCHOOLS:
        if state!='any' and s['state'].lower()!=state.lower(): continue
        if s['size'] not in size_codes: continue
        # Handle ctrl as both int and string
        s_ctrl = s.get('ctrl')
        try: s_ctrl = int(s_ctrl)
        except: pass
        if ctrl == 'public' and s_ctrl not in [1, '1']: continue
        if ctrl == 'private' and s_ctrl not in [2, '2']: continue
        tin = s.get('tin') or 0
        if tin <= 0: continue  # skip schools with no tuition data
        if s.get('size', 0) < 0: continue  # skip invalid size codes
        if need=='full' and tin > 55000: continue
        if env=='hbcu' and not s.get('hbcu'): continue
        # If student wants 4yr, filter out 2yr schools
        if study_yrs=='4yr' and s.get('yr2'): continue
        # If student wants 2yr, only show 2yr schools
        if study_yrs=='2yr' and not s.get('yr2'): continue
        # Default: filter out 2yr schools unless student wants them
        if study_yrs=='any' and s.get('yr2'): continue
        fit=get_fit(sat,act,s,gpa)
        net=max(0, tin - aid['total']) if tin > 0 else None
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

# ── PDF GENERATOR ─────────────────────────────────────────────
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
CAREER_MAPS = {
    'i1': {"Helping and healing people":{"helping":3,"people":3},"Building and engineering things":{"building":3,"science":2},"Teaching and shaping communities":{"teaching":3,"people":2},"Running businesses and managing money":{"business":3,"leadership":2},"Creating, designing and communicating":{"creating":3,"creativity":3},"Researching, analyzing and discovering":{"analyzing":3,"data":3}},
    'i2': {"High income":{"income":3,"prestige":1},"Making a real difference":{"impact":3,"helping":2},"Creative freedom":{"creativity":3,"autonomy":3},"Stability and security":{"stability":3},"Prestige and recognition":{"prestige":3,"leadership":2}},
    'i3': {"With people (patients, students, clients)":{"people":3,"helping":2},"At a desk or computer":{"data":2,"analyzing":2},"Out in the field (moving, hands-on)":{"outdoors":3,"physical":3},"In a lab, hospital, or studio":{"science":2,"creating":2},"Anywhere (remote/flexible)":{"autonomy":3}},
    'i4': {"Science or Math":{"science":3,"data":2},"English, Writing, or Communication":{"creating":2,"people":2},"Art, Music, or Design":{"creativity":3,"creating":2},"Social Studies or History":{"people":2,"teaching":2},"Technology or Computer Science":{"building":3,"data":3},"Physical Education or Health":{"physical":3,"helping":2}},
    'i5': {"1-2 years (start earning soon)":{"stability":2},"4 years (bachelor's degree)":{"income":1},"6-8 years (graduate school)":{"prestige":2,"income":2},"Whatever it takes":{"prestige":3,"income":3}},
    'i6': {"I love working with my hands":{"physical":3,"building":2},"I love understanding how people feel":{"people":3,"helping":3},"I love solving complex problems":{"analyzing":3,"data":3},"I love building or making things":{"creating":3,"building":2},"I love organizing, planning and leading":{"leadership":3,"business":2}},
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
    st.markdown(f"*Your college list, built around your life. Browsing **{len(SCHOOLS):,} US colleges** from IPEDS 2023-24.*")
with col_h2:
    st.caption("Built by SLN RITA Tech & Data Intern\nIPEDS 2023-24 · Aid thresholds 2025-26")
st.divider()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📝 Your Profile")

    st.markdown("### 📚 Academics")
    gpa = st.slider("Unweighted GPA", 0.0, 4.0, 3.0, 0.1)
    score_type = st.selectbox("Test scores", ["None (test-optional)","SAT","ACT"])
    sat = act = None
    if score_type == "SAT":
        sat = st.number_input("SAT Score", 400, 1600, 1100, 10)
    elif score_type == "ACT":
        act = st.number_input("ACT Score", 1, 36, 24, 1)

    st.markdown("### 🎯 Career Discovery")
    q1 = st.selectbox("What excites you most?",list(CAREER_MAPS['i1'].keys()))
    q2 = st.selectbox("What matters most in a career?",list(CAREER_MAPS['i2'].keys()))
    q3 = st.selectbox("Where do you want to work?",list(CAREER_MAPS['i3'].keys()))
    q4 = st.selectbox("Best subject in school?",list(CAREER_MAPS['i4'].keys()))
    q5 = st.selectbox("How long willing to study?",list(CAREER_MAPS['i5'].keys()))
    q6 = st.selectbox("Which describes you best?",list(CAREER_MAPS['i6'].keys()))
    q7 = st.selectbox("In 10 years I see myself...",list(CAREER_MAPS['i7'].keys()))
    q8 = st.selectbox("Best work environment?",list(CAREER_MAPS['i8'].keys()))

    st.markdown("### 💰 Financial Aid")
    income    = st.number_input("Annual household income ($)", 0, 500000, 42000, 1000)
    hsize     = st.slider("Household size", 1, 10, 4)
    ny_res    = st.checkbox("NY State resident (12+ months)", value=True)
    immig     = st.selectbox("Immigration/citizenship status",list(IMMIG_MAP.keys()))
    first_gen = st.checkbox("First-generation college student", value=True)

    st.markdown("### 🗺️ Preferences")
    state_pref  = st.selectbox("Preferred state",["NY","Any","CA","MA","NJ","PA","TX","FL","IL"])
    school_size = st.selectbox("School size",["Any","Small (<5k)","Medium (5-20k)","Large (20k+)"])
    school_type = st.selectbox("School type",["Any","Public","Private"])
    env_pref    = st.selectbox("Campus environment",["Any","HBCU","Women's College","Diverse"])
    study_yrs   = st.selectbox("Years willing to study",["Any","2 years (Associate)","4 years (Bachelor's+)"])
    n_results   = st.select_slider("Number of results",[5,10,15,20],10)

    run_btn = st.button("🔍 Find My Colleges", type="primary", use_container_width=True)

# ── PROCESS ───────────────────────────────────────────────────
career_answers = {
    'i1':CAREER_MAPS['i1'][q1],'i2':CAREER_MAPS['i2'][q2],
    'i3':CAREER_MAPS['i3'][q3],'i4':CAREER_MAPS['i4'][q4],
    'i5':CAREER_MAPS['i5'][q5],'i6':CAREER_MAPS['i6'][q6],
    'i7':CAREER_MAPS['i7'][q7],'i8':CAREER_MAPS['i8'][q8],
}
career_results = run_career_match(career_answers)
st.session_state.career_results = career_results
top = career_results[0] if career_results else None

aid = calculate_aid(income, hsize, ny_res, IMMIG_MAP[immig], first_gen)
st.session_state.aid = aid

if run_btn:
    state_val = "any" if state_pref=="Any" else state_pref
    need_val  = "full" if income<50000 else "some"
    matches = run_match(gpa, sat, act, state_val,
                        SIZE_MAP[school_size], CTRL_MAP[school_type],
                        need_val, ENV_MAP[env_pref], YRS_MAP[study_yrs], aid, n_results)
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
        c1.metric("Colleges Found", len(m))
        c2.metric("Est. Annual Aid", f"${aid['total']:,}")
        safety_n=sum(1 for s in m if s['fit']=='safety')
        match_n =sum(1 for s in m if s['fit']=='match')
        reach_n =sum(1 for s in m if s['fit']=='reach')
        c3.metric("Safety / Match / Reach", f"{safety_n} / {match_n} / {reach_n}")
        c4.metric("Top Career Match", top['name'] if top else "—")
        st.divider()

        # Sort buttons
        sort_col1,sort_col2,sort_col3,sort_col4 = st.columns(4)
        sort_mode = st.session_state.get('sort_mode','fit')
        with sort_col1:
            if st.button("🎯 Best Fit First", use_container_width=True,
                        type="primary" if sort_mode=='fit' else "secondary"):
                st.session_state.sort_mode='fit'; st.rerun()
        with sort_col2:
            if st.button("💚 Lowest Cost First", use_container_width=True,
                        type="primary" if sort_mode=='cost' else "secondary"):
                st.session_state.sort_mode='cost'; st.rerun()
        with sort_col3:
            if st.button("🟢 Safety First", use_container_width=True,
                        type="primary" if sort_mode=='safety' else "secondary"):
                st.session_state.sort_mode='safety'; st.rerun()
        with sort_col4:
            if st.button("🎓 Grad Rate First", use_container_width=True,
                        type="primary" if sort_mode=='grad' else "secondary"):
                st.session_state.sort_mode='grad'; st.rerun()

        # Apply sort
        sort_mode = st.session_state.get('sort_mode','fit')
        fit_order = {'safety':0,'match':1,'reach':2,'unknown':3}
        if sort_mode == 'fit':
            m = sorted(m, key=lambda x: (fit_order.get(x.get('fit','unknown'),3), x.get('net') or 999999))
        elif sort_mode == 'cost':
            m = sorted(m, key=lambda x: (x.get('net') is None, x.get('net') or 999999))
        elif sort_mode == 'safety':
            m = sorted(m, key=lambda x: fit_order.get(x.get('fit','unknown'),3))
        elif sort_mode == 'grad':
            m = sorted(m, key=lambda x: -(x.get('grad') or 0))
        st.divider()

        if not m:
            st.warning("No colleges matched. Try changing your state preference to 'Any'.")
        else:
            fit_icons={"safety":"🟢","match":"🟡","reach":"🔴","unknown":"⚪"}
            for s in m:
                fit=s.get('fit','unknown')
                net=s.get('net')
                dl=DEADLINES.get(s['id'],{"rd":"Check website"})
                in_list = any(x['id']==s['id'] for x in st.session_state.my_list)

                with st.container():
                    ca,cb,cc = st.columns([3,1.5,1])
                    with ca:
                        st.markdown(f"**{fit_icons.get(fit,'⚪')} [{s['name']}]({s.get('web','#')})**")
                        adm_val = s.get('adm'); adm_display = f"{float(adm_val):.1f}% acceptance" if adm_val and adm_val == adm_val else "Acceptance rate N/A"
                        st.caption(f"{s.get('city','')}, {s['state']} · {'Public' if s['ctrl']==1 else 'Private'} · {adm_display}" + (" · 🏛️ HBCU" if s.get('hbcu') else ""))
                        chips = f"`{fit.capitalize()}`"
                        if s.get('sat25'): chips += f"  `SAT {s['sat25']}–{s['sat75']}`"
                        if s.get('act25'): chips += f"  `ACT {s['act25']}–{s['act75']}`"
                        if aid['tap']>0 and s['state']=='NY': chips += "  `TAP eligible`"
                        if aid['heop'] and s['state']=='NY': chips += "  `HEOP`"
                        st.markdown(chips)
                    with cb:
                        sticker = int(s.get('tin') or 0)
                        st.markdown(f"**Sticker:** ${sticker:,}" if sticker else "")
                        if net==0 and aid['total']>0:
                            st.markdown("**You pay:** :green[Fully covered 🎉]")
                        elif net is not None:
                            st.markdown(f"**You pay:** :blue[${net:,}/yr]")
                        if s.get('grad'): st.markdown(f"**Grad rate:** {s['grad']}%")
                        st.markdown(f"**RD:** {dl.get('rd','?')}")
                    with cc:
                        if in_list:
                            if st.button("✓ In my list", key=f"rem_{s['id']}", use_container_width=True):
                                st.session_state.my_list = [x for x in st.session_state.my_list if x['id']!=s['id']]
                                st.rerun()
                        else:
                            if st.button("+ Add to list", key=f"add_{s['id']}", use_container_width=True, type="primary"):
                                st.session_state.my_list.append(s)
                                st.rerun()

                    if fit=='safety': st.success("Your profile is above their range. Strong safety school.")
                    elif fit=='match': st.info("Your profile is in their range. A solid application should be competitive.")
                    elif fit=='reach': st.warning("Your profile is below their range. A strong essay and story can still get you in.")
                    elif fit=='unknown': st.caption("⚠️ Limited data available for this school — visit their website to confirm fit.")
                    st.divider()

# ── TAB 2: CAREER ─────────────────────────────────────────────
with tab2:
    if not career_results:
        st.info("Answer the career questions on the left to see your matches.")
    else:
        t=career_results[0]
        st.markdown(f"""
        <div style="background:#0D1B2A;border-radius:12px;padding:22px 26px;margin-bottom:20px;color:white">
            <div style="font-size:11px;opacity:.4;margin-bottom:4px;letter-spacing:1px;text-transform:uppercase">Your best match</div>
            <div style="font-size:26px;font-family:Georgia,serif;margin-bottom:5px">{t['icon']} {t['name']}</div>
            <div style="font-size:13px;opacity:.55;margin-bottom:12px">{t['why']}</div>
            <span style="color:#E8AD58;font-size:20px;font-weight:700">${t['salary_mid']:,}/yr avg</span>
            &nbsp;&nbsp;
            <span style="background:rgba(42,96,73,.4);padding:4px 12px;border-radius:8px;font-size:12px">{t['growth']} job growth</span>
            &nbsp;
            <span style="background:rgba(255,255,255,.1);padding:4px 12px;border-radius:8px;font-size:12px">{t['demand']} demand</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Results update live as you change your answers on the left")
        for c in career_results[:10]:
            with st.expander(f"{c['icon']} {c['name']}  —  **{c['fit']}% match** · ${c['salary_mid']:,}/yr"):
                c1,c2,c3=st.columns(3)
                c1.metric("Entry",f"${c['salary_entry']:,}")
                c2.metric("Mid career",f"${c['salary_mid']:,}")
                c3.metric("Senior",f"${c['salary_senior']:,}")
                st.progress(c['fit']/100)
                st.markdown(f"**A day in the life:** {c['day']}")
                st.markdown(f"**Majors:** {', '.join(c['majors'])}")
                st.caption(f"Growth: {c['growth']} · Demand: {c['demand']}")

# ── TAB 3: AID ────────────────────────────────────────────────
with tab3:
    st.markdown("### Your financial aid eligibility")
    st.caption("Based on 2025-26 federal and NY State thresholds. Updates live.")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Pell Grant",f"${aid['pell']:,}" if aid['pell']>0 else "❌")
    c2.metric("NY TAP",f"${aid['tap']:,}" if aid['tap']>0 else "❌")
    c3.metric("Dream Act",f"${aid['dream']:,}" if aid['dream']>0 else "❌")
    c4.metric("HEOP","✅ Eligible" if aid['heop'] else "❌")
    st.divider()
    st.markdown(f"### 💵 Total estimated annual aid: **${aid['total']:,}**")
    st.caption("These are grants — they do not need to be repaid.")
    if aid['heop']:
        st.success("🎓 HEOP eligible — additional academic support at participating NY colleges.")
    st.info("💡 Complete your FAFSA at **studentaid.gov** to receive your actual award letter.")

# ── TAB 4: MY LIST ────────────────────────────────────────────
with tab4:
    st.markdown("### 📋 My College List")

    my_list = st.session_state.my_list

    if not my_list:
        st.info("Go to **College Matches** and click **+ Add to list** on any college. Your list stays saved here as you explore.")
    else:
        # Balance summary
        sn=sum(1 for s in my_list if s.get('fit')=='safety')
        mn=sum(1 for s in my_list if s.get('fit')=='match')
        rn=sum(1 for s in my_list if s.get('fit')=='reach')
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Total",len(my_list))
        c2.metric("🟢 Safety",sn)
        c3.metric("🟡 Match",mn)
        c4.metric("🔴 Reach",rn)

        if sn<2: st.warning("⚠️ Add more safety schools — schools where your profile is above their typical range.")
        elif rn<1: st.info("💡 Consider adding 1-2 reach schools. A strong application can surprise you.")
        elif mn<2: st.info("📋 Add more match schools — these tend to be your most likely admits.")
        else: st.success("✅ Great balance! Apply to all of them.")

        st.divider()

        # List with remove buttons
        for i,s in enumerate(my_list):
            fit=s.get('fit','unknown')
            net=s.get('net')
            dl=DEADLINES.get(s['id'],{"rd":"Check website"})
            early=dl.get('ed') or dl.get('ea','—')
            fit_icons={"safety":"🟢","match":"🟡","reach":"🔴","unknown":"⚪"}

            ca,cb,cc=st.columns([3,2,0.7])
            with ca:
                st.markdown(f"**{fit_icons.get(fit,'⚪')} [{s['name']}]({s.get('web','#')})**")
                st.caption(f"{s['state']} · {'Public' if s['ctrl']==1 else 'Private'} · {fit.capitalize()}")
            with cb:
                net_str = f"${net:,}/yr" if net is not None else "N/A"
                if net==0 and aid['total']>0: net_str="Fully covered 🎉"
                st.markdown(f"**You pay:** {net_str}")
                st.caption(f"RD: {dl.get('rd','?')} · Early: {early}")
            with cc:
                if st.button("✕", key=f"del_{s['id']}_{i}", help="Remove from list"):
                    st.session_state.my_list = [x for x in st.session_state.my_list if x['id']!=s['id']]
                    st.rerun()

        st.divider()

        # PDF Download
        st.markdown("### 📄 Download Your Report")
        top_name = st.session_state.career_results[0]['name'] if st.session_state.career_results else ""
        saved_gpa = st.session_state.get('gpa', gpa)
        saved_sat = st.session_state.get('sat', sat)
        saved_act = st.session_state.get('act', act)

        try:
            import reportlab
            pdf_buf = generate_pdf(my_list, aid, top_name, saved_gpa, saved_sat, saved_act)
            if pdf_buf:
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_buf,
                    file_name="Pathways_SLN_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
                st.caption("PDF includes your college list, aid eligibility, deadlines, and career match.")
            else:
                st.error("PDF generation failed. Please try again.")
        except ImportError:
            st.warning("📄 PDF export requires reportlab. Add `reportlab` to your requirements.txt to enable this feature.")

        st.caption("⚠️ Always verify deadlines on each college's official website before applying.")

st.divider()
st.caption("Pathways by SLN · IPEDS 2023-24 · Aid thresholds 2025-26 · Verify all deadlines on official college websites")
