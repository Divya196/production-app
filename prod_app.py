import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import json

st.set_page_config(page_title="Facilities Asset Data Capture", layout="wide", initial_sidebar_state="collapsed")
st.error("🔴 DEBUG: This is the NEW version - 2024-11-27 v2")
st.write("If you see this debug message, the new code is running!")

st.markdown("""
<style>
.main > div {padding-top: 1rem;}
.stButton>button {width: 100%; padding: 0.5rem;}
h1 {text-align: center; color: #1f77b4; font-size: 1.8em; margin-bottom: 1rem;}
.highlight {background-color: #ffeb3b; padding: 12px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 1.5em; margin: 15px 0;}
.asset-name {font-size: 1.1em; font-weight: 700; text-transform: uppercase; color: #333; margin: 8px 0;}
.mandatory {color: #ff0000; font-weight: bold; font-size: 1.2em;}
.stRadio > label {font-size: 1.05em;}
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('facilities_asset_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id TEXT, employee_name TEXT,
                  reporting_manager TEXT, business_unit TEXT, project_name TEXT, project_code TEXT,
                  office_store_gh_together TEXT, office_store_together TEXT, office_gh_together TEXT,
                  num_guesthouses INTEGER, submission_datetime TEXT, is_complete INTEGER,
                  current_step INTEGER, saved_state TEXT, UNIQUE(employee_id, project_code))''')
    c.execute('''CREATE TABLE IF NOT EXISTS guesthouses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, submission_id INTEGER, guesthouse_number INTEGER,
                  number_of_persons INTEGER, gmap_link TEXT, FOREIGN KEY (submission_id) REFERENCES submissions(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS assets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, submission_id INTEGER, guesthouse_id INTEGER,
                  asset_location TEXT, asset_name TEXT, asset_count INTEGER, asset_group TEXT,
                  asset_category TEXT, asset_subcategory TEXT, FOREIGN KEY (submission_id) REFERENCES submissions(id))''')
    conn.commit()
    conn.close()

init_db()

B2G = {"SR_Siemens_Chennai_MSDAC":"PROJ/00006","NSPCL_RITES_Rourkela":"PROJ/00008","MMRCL_Alstom_Mumbai_PSD":"PROJ/00012","NFR_RITES_Lumding":"PROJ/00013","SWR_RITES_Kadur":"PROJ/00014","NR_Nizamuddin":"PROJ/00015","SWR_RITES_Dharmavaram_O":"PROJ/00016","JVUNL_RITES_Etah":"PROJ/00017","SCR_Kakinada_COA":"PROJ/00018","WR_Adrajmoti":"PROJ/00020","WCR_Kota":"PROJ/00021","SWR_Hosur_HSRA7":"PROJ/00022","SWR_RITES_Dharmavaram_I":"PROJ/00023","SWR_Whitefield":"PROJ/00024","SR_Jolarpettai_09":"PROJ/00025","SR_Buddireddippati_10":"PROJ/00026","SR_Salem_11":"PROJ/00027","SCR_Makudi_EPC":"PROJ/00028","SR_Arakkonam":"PROJ/00029","ECR_Manpur_Bonding":"PROJ/00030","ECR_Nokha_RFO":"PROJ/00035","SR_Kannur_MAQ":"PROJ/00038","SCR_RVNL_Ghatkesar_JV":"PROJ/00039","SR_Palakkad_9MSDAC":"PROJ/00040","SR_Nagari":"PROJ/00041","NR_Ludhiana":"PROJ/00047","SR_Ollur":"PROJ/00049","SWR_Puttaparthi_SSPN":"PROJ/00050","NER_Chhapra":"PROJ/00052"}
B2B = {"NCR_PGIPL_Jhansi_003":"PROJ/00011","Adani_Bhatapara_005":"PROJ/00032","Adani_Sankrail_007":"PROJ/00033","SCR_HEIPL_Mandamari_008":"PROJ/00034","Adani_Haldia_010":"PROJ/00036","Adani_Raigarh_009":"PROJ/00037","JSW_Dolvi_015":"PROJ/00042","UTCL_Aligarh_012":"PROJ/00044","Adani_Mundra_013":"PROJ/00046","Adani_Surta_014":"PROJ/00048","Adani_Mundra_016":"PROJ/00051","Adani_Surta_017":"PROJ/00053","Adani_Dhamra1_018":"PROJ/00056","Adani_Bhatapara2_019":"PROJ/00057","Adani_Dhamra2_020":"PROJ/00058","HITACHI_Hydmetro":"PROJ/00062"}

OFF_ST=[("OFFICE PORTACABIN","Portable Structures","Buildings & Structures"),("COMPUTER TABLE","Office Furniture","Furniture & Fixtures"),("PLASTIC/WOOD CHAIR","Office Furniture","Furniture & Fixtures"),("VISITOR CHAIR","Office Furniture","Furniture & Fixtures"),("EXECUTIVE CHAIR","Office Furniture","Furniture & Fixtures"),("ALMIRAH","Office Furniture","Furniture & Fixtures"),("FILING CABINET","Office Furniture","Furniture & Fixtures"),("NOTICE BOARD","Office Furniture","Furniture & Fixtures"),("EMERGENCY LIGHT","Office Equipment","Furniture & Fixtures"),("FAN","Office Equipment","Furniture & Fixtures"),("STABILIZER","Office Equipment","Furniture & Fixtures"),("UPS + BATTERIES","Power Equipment","Plant & Machinery"),("GENERATOR","Power Equipment","Plant & Machinery"),("LAPTOP","Computing Devices","IT Hardware"),("DESKTOP","Computing Devices","IT Hardware"),("MONITOR","Computing Devices","IT Hardware"),("CPU","Computing Devices","IT Hardware"),("EXTERNAL HARD DISK","Computing Devices","IT Hardware"),("PRINTER","Peripherals & Imaging","IT Hardware"),("MFD","Peripherals & Imaging","IT Hardware"),("PROJECTOR","Peripherals & Imaging","IT Hardware"),("EBIKE","Light Vehicles","Transport Vehicles"),("2 WHEELER","Light Vehicles","Transport Vehicles"),("4 WHEELER","Light Vehicles","Transport Vehicles"),("CCTV + DVR","CCTV Systems","Security & Surveillance")]

GH=[("WOODEN DINING TABLE","Guest House Furniture","Furniture & Fixtures"),("DINING CHAIR","Guest House Furniture","Furniture & Fixtures"),("PLASTIC CHAIR","Guest House Furniture","Furniture & Fixtures"),("EXECUTIVE CHAIR","Guest House Furniture","Furniture & Fixtures"),("CENTRE TABLE","Guest House Furniture","Furniture & Fixtures"),("SOFA 3-SEAT","Guest House Furniture","Furniture & Fixtures"),("SOFA 1-SEAT","Guest House Furniture","Furniture & Fixtures"),("WOODEN COT","Guest House Furniture","Furniture & Fixtures"),("IRON COT","Guest House Furniture","Furniture & Fixtures"),("MATTRESS","Bedding & Amenities","Housekeeping Supplies"),("PILLOW","Bedding & Amenities","Housekeeping Supplies"),("BUCKET WITH MUG","Bedding & Amenities","Housekeeping Supplies"),("GAS STOVE","Kitchen Equipment","Plant & Machinery"),("INDUCTION","Kitchen Equipment","Plant & Machinery"),("UPS + BATTERIES","Power Equipment","Plant & Machinery"),("GENERATOR","Power Equipment","Plant & Machinery"),("REFRIGERATOR","Major Appliances","Appliances"),("WASHING MACHINE","Major Appliances","Appliances"),("AC","Major Appliances","Appliances"),("COOLER","Major Appliances","Appliances"),("RO","Minor Appliances","Appliances"),("FAN","Minor Appliances","Appliances"),("WATER DISPENSER","Minor Appliances","Appliances"),("UTENSILS SET","Utensils & Cookware","Kitchen Supplies"),("CCTV + DVR","CCTV Systems","Security & Surveillance"),("LPG CYLINDER","LPG Cylinders","Gas Cylinders")]

def tc(t):
    return ' '.join(w.capitalize() for w in t.split())

def save():
    if 'fd' not in st.session_state:
        return
    try:
        conn=sqlite3.connect('facilities_asset_data.db')
        c=conn.cursor()
        state={'fd':st.session_state.fd,'os':st.session_state.get('os',{}),'oc':st.session_state.get('oc',{}),'ss':st.session_state.get('ss',{}),'sc':st.session_state.get('sc',{}),'gs':st.session_state.get('gs',{}),'gc':st.session_state.get('gc',{}),'gp':st.session_state.get('gp',{}),'gl':st.session_state.get('gl',{}),'op':st.session_state.get('op','select'),'sp':st.session_state.get('sp','select'),'ghp':st.session_state.get('ghp','select'),'cgh':st.session_state.get('cgh',1),'oa':st.session_state.get('oa',{'office':[],'store':[],'guesthouse':{}})}
        fd=st.session_state.fd
        c.execute('''INSERT OR REPLACE INTO submissions 
                     (employee_id,employee_name,reporting_manager,business_unit,project_name,project_code,
                      office_store_gh_together,office_store_together,office_gh_together,num_guesthouses,
                      submission_datetime,is_complete,current_step,saved_state)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,0,?,?)''',
                  (fd.get('ei',''),fd.get('en',''),fd.get('rm',''),fd.get('bu',''),fd.get('pn',''),fd.get('pc',''),
                   fd.get('q1',''),fd.get('q2',''),fd.get('q3',''),fd.get('ngh',0),
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),st.session_state.get('step',1),json.dumps(state)))
        conn.commit()
        conn.close()
        st.success("✅ Saved!")
    except Exception as e:
        st.error(f"Save error: {str(e)}")

def load(ei,pc):
    try:
        conn=sqlite3.connect('facilities_asset_data.db')
        c=conn.cursor()
        c.execute('SELECT * FROM submissions WHERE employee_id=? AND project_code=? AND is_complete=0',(ei,pc))
        r=c.fetchone()
        conn.close()
        if r and r[14]:
            state=json.loads(r[14])
            st.session_state.fd=state.get('fd',{})
            st.session_state.os=state.get('os',{})
            st.session_state.oc=state.get('oc',{})
            st.session_state.ss=state.get('ss',{})
            st.session_state.sc=state.get('sc',{})
            st.session_state.gs=state.get('gs',{})
            st.session_state.gc=state.get('gc',{})
            st.session_state.gp=state.get('gp',{})
            st.session_state.gl=state.get('gl',{})
            st.session_state.op=state.get('op','select')
            st.session_state.sp=state.get('sp','select')
            st.session_state.ghp=state.get('ghp','select')
            st.session_state.cgh=state.get('cgh',1)
            st.session_state.oa=state.get('oa',{'office':[],'store':[],'guesthouse':{}})
            st.session_state.step=r[13]
            return True
        return False
    except Exception as e:
        st.error(f"Load error: {str(e)}")
        return False

if 'step' not in st.session_state:
    st.session_state.step=0
if 'fd' not in st.session_state:
    st.session_state.fd={}
if 'os' not in st.session_state:
    st.session_state.os={}
if 'oc' not in st.session_state:
    st.session_state.oc={}
if 'ss' not in st.session_state:
    st.session_state.ss={}
if 'sc' not in st.session_state:
    st.session_state.sc={}
if 'gs' not in st.session_state:
    st.session_state.gs={}
if 'gc' not in st.session_state:
    st.session_state.gc={}
if 'gp' not in st.session_state:
    st.session_state.gp={}
if 'gl' not in st.session_state:
    st.session_state.gl={}
if 'op' not in st.session_state:
    st.session_state.op='select'
if 'sp' not in st.session_state:
    st.session_state.sp='select'
if 'ghp' not in st.session_state:
    st.session_state.ghp='select'
if 'cgh' not in st.session_state:
    st.session_state.cgh=1
if 'oa' not in st.session_state:
    st.session_state.oa={'office':[],'store':[],'guesthouse':{}}

st.markdown("<h1>🏢 Facilities - Asset Data Capture System</h1>",unsafe_allow_html=True)

if st.session_state.step>0:
    st.progress(min(st.session_state.step/8,1.0))
    st.markdown("---")

if st.session_state.step==0:
    st.header("🔄 Welcome!")
    res=st.radio("Are you a returning user?",["New Submission","Resume Previous Work"])
    if res=="Resume Previous Work":
        ei=st.text_input("Employee ID (10 chars)",max_chars=10,key="rei").upper()
        if len(ei)==10:
            conn=sqlite3.connect('facilities_asset_data.db')
            c=conn.cursor()
            c.execute('SELECT project_code,is_complete FROM submissions WHERE employee_id=?',(ei,))
            rs=c.fetchall()
            conn.close()
            if rs:
                st.write("**Found:**")
                for p,ic in rs:
                    st.write(f"- {p}: {'✅ Complete' if ic else '⏸️ In Progress'}")
                pc=st.text_input("Project Code ",key="rpc")
                if pc and st.button("Load",type="primary"):
                    if load(ei,pc):
                        st.success("✅ Loaded!")
                        st.rerun()
                    else:
                        st.error("Not found or error loading")
            else:
                st.info("No submissions. Start new...")
    else:
        if st.button("Start New",type="primary"):
            st.session_state.step=1
            st.rerun()

elif st.session_state.step==1:
    st.header("👤 Employee Details")
    c1,c2=st.columns(2)
    with c1:
        ei=st.text_input("Employee ID (10 chars)",value=st.session_state.fd.get('ei',''),max_chars=10,key="ei").upper()
        en=st.text_input("Employee Name ",value=st.session_state.fd.get('en',''),key="en")
    with c2:
        rm=st.text_input("Reporting Manager ",value=st.session_state.fd.get('rm',''),key="rm")
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        if st.button("💾 Save"):
            if ei and en and rm:
                st.session_state.fd.update({'ei':ei,'en':tc(en),'rm':tc(rm)})
                save()
    with c2:
        if st.button("Next →",type="primary"):
            if len(ei)==10 and en and rm:
                st.session_state.fd.update({'ei':ei,'en':tc(en),'rm':tc(rm)})
                st.session_state.step=2
                st.rerun()
            else:
                st.error("All mandatory. ID=10 chars")

elif st.session_state.step==2:
    st.header("📋 Project Details")
    c1,c2=st.columns(2)
    with c1:
        bu=st.selectbox("Business Unit ",["","B2G","B2B"],index=["","B2G","B2B"].index(st.session_state.fd.get('bu','')),key="bu")
        if bu:
            pr=B2G if bu=="B2G" else B2B
            pl=[""]+ list(pr.keys())
            cu=st.session_state.fd.get('pn','')
            ix=pl.index(cu) if cu in pl else 0
            pn=st.selectbox("Project Name ",pl,index=ix,key="pn")
            if pn:
                pc=pr[pn]
    with c2:
        if bu and pn:
            st.text_input("Project Code",value=pc,disabled=True)
    st.markdown("---")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("← Back"):
            st.session_state.step=1
            st.rerun()
    with c2:
        if st.button("💾 Save"):
            if bu and pn:
                st.session_state.fd.update({'bu':bu,'pn':pn,'pc':pc})
                save()
    with c3:
        if st.button("Next →",type="primary"):
            if bu and pn:
                st.session_state.fd.update({'bu':bu,'pn':pn,'pc':pc})
                st.session_state.step=3
                st.rerun()
            else:
                st.error("All mandatory")

elif st.session_state.step==3:
    st.header("📍 Location Details")
    st.subheader("Configuration")
    q1=st.radio("Office+Store+GH together? ",["Yes","No"],index=0 if st.session_state.fd.get('q1')=='Yes' else 1,key="q1")
    if q1=="No":
        q2=st.radio("Office+Store together? ",["Yes","No"],index=0 if st.session_state.fd.get('q2')=='Yes' else 1,key="q2")
        q3=st.radio("Office+GH together? ",["Yes","No"],index=0 if st.session_state.fd.get('q3')=='Yes' else 1,key="q3")
    else:
        q2,q3="No","No"
        st.markdown("*Office+Store:* **N/A**")
        st.markdown("*Office+GH:* **N/A**")
    st.markdown("---")
    st.subheader("Guesthouse Details")
    st.write(f"**Project:** {st.session_state.fd.get('pn','')}")
    ngh=st.number_input("Guesthouses (Min 0- Max 3)",min_value=0,max_value=3,value=st.session_state.fd.get('ngh',0),step=1,key="ngh")
    for i in range(1,ngh+1):
        st.markdown(f"### GH {i}")
        c1,c2=st.columns(2)
        with c1:
            p=st.number_input(f"Persons ",min_value=0,value=st.session_state.gp.get(i,0),step=1,key=f"gp{i}")
            st.session_state.gp[i]=p
        with c2:
            l=st.text_input(f"Maps link ",value=st.session_state.gl.get(i,''),key=f"gl{i}")
            st.session_state.gl[i]=l
    st.markdown("---")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("← Back"):
            st.session_state.step=2
            st.rerun()
    with c2:
        if st.button("💾 Save"):
            st.session_state.fd.update({'q1':q1,'q2':q2,'q3':q3,'ngh':ngh})
            save()
    with c3:
        ok=True
        if ngh>0:
            for i in range(1,ngh+1):
                if not st.session_state.gl.get(i):
                    ok=False
                    st.error(f"GH {i} link required")
                    break
        if st.button("Next →",type="primary",disabled=not ok):
            st.session_state.fd.update({'q1':q1,'q2':q2,'q3':q3,'ngh':ngh})
            st.session_state.step=4
            st.rerun()

elif st.session_state.step==4:
    if st.session_state.op=='select':
        st.markdown("<div class='highlight'>📍 OFFICE ASSETS</div>",unsafe_allow_html=True)
        st.markdown("---")
        for a,cat,grp in OFF_ST:
            st.markdown(f"<div class='asset-name'>{a}</div>",unsafe_allow_html=True)
            s=st.radio(a,["Yes","No"],index=0 if st.session_state.os.get(a,False) else 1,key=f"os{a}",horizontal=True,label_visibility="collapsed")
            st.session_state.os[a]=(s=="Yes")
            st.markdown("---")
        st.subheader("Other Assets (Optional)")
        for i in range(3):
            c1,c2=st.columns([2,1])
            with c1:
                on=st.text_input(f"Other {i+1}",key=f"oon{i}")
            with c2:
                oc=st.number_input("Count",min_value=0,step=1,key=f"ooc{i}")
            if on:
                while len(st.session_state.oa['office'])<=i:
                    st.session_state.oa['office'].append(('',0))
                st.session_state.oa['office'][i]=(on.upper(),oc)
        st.markdown("---")
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("← Back"):
                st.session_state.step=3
                st.rerun()
        with c2:
            if st.button("💾 Save"):
                save()
        with c3:
            if st.button("Next →",type="primary"):
                st.session_state.op='count'
                st.rerun()
    elif st.session_state.op=='count':
        st.markdown("<div class='highlight'>📍 OFFICE - Counts</div>",unsafe_allow_html=True)
        st.markdown("---")
        sel=[n for n in st.session_state.os if st.session_state.os[n]]
        if not sel:
            st.warning("None selected")
            st.session_state.op='review'
            st.rerun()
        for a in sel:
            st.markdown(f"<div class='asset-name'>{a}</div>",unsafe_allow_html=True)
            c=st.number_input(f"Count ",min_value=0,value=st.session_state.oc.get(a,0),step=1,key=f"oc{a}")
            st.session_state.oc[a]=c
            st.markdown("---")
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("← Back"):
                st.session_state.op='select'
                st.rerun()
        with c2:
            if st.button("💾 Save"):
                save()
        with c3:
            if st.button("Review →",type="primary"):
                st.session_state.op='review'
                st.rerun()
    else:
        st.markdown("<div class='highlight'>✅ OFFICE - Review</div>",unsafe_allow_html=True)
        st.markdown("---")
        d=[]
        for a in st.session_state.os:
            if st.session_state.os[a]:
                d.append({"Asset":a,"Count":st.session_state.oc.get(a,0)})
        for n,c in st.session_state.oa.get('office',[]):
            if n:
                d.append({"Asset":f"{n} (Other)","Count":c})
        if d:
            st.dataframe(pd.DataFrame(d),use_container_width=True,hide_index=True)
        else:
            st.info("No Office assets")
        st.markdown("---")
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("← Edit"):
                st.session_state.op='count'
                st.rerun()
        with c2:
            if st.button("💾 Save"):
                save()
        with c3:
            if st.button("✅ Confirm",type="primary"):
                st.session_state.step=5
                st.session_state.cgh=1
                st.session_state.ghp='select'
                st.rerun()

elif st.session_state.step==5:
    ngh=st.session_state.fd.get('ngh',0)
    if ngh==0:
        st.info("No GH. Going to Store...")
        if st.button("Continue →",type="primary"):
            st.session_state.step=6
            st.rerun()
    else:
        cgh=st.session_state.cgh
        if cgh>ngh:
            st.success(f"✅ All {ngh} GH done!")
            if st.button("Continue to Store →",type="primary"):
                st.session_state.step=6
                st.rerun()
        else:
            if st.session_state.ghp=='select':
                st.markdown(f"<div class='highlight'>🏠 GUESTHOUSE {cgh}</div>",unsafe_allow_html=True)
                st.write(f"**Persons:** {st.session_state.gp.get(cgh,0)} | **Location:** {st.session_state.gl.get(cgh,'')}")
                st.markdown("---")
                for a,cat,grp in GH:
                    st.markdown(f"<div class='asset-name'>{a}</div>",unsafe_allow_html=True)
                    if cgh not in st.session_state.gs:
                        st.session_state.gs[cgh]={}
                    s=st.radio(a,["Yes","No"],index=0 if st.session_state.gs[cgh].get(a,False) else 1,key=f"gs{cgh}{a}",horizontal=True,label_visibility="collapsed")
                    st.session_state.gs[cgh][a]=(s=="Yes")
                    st.markdown("---")
                st.subheader("Other Assets (Optional)")
                for i in range(3):
                    c1,c2=st.columns([2,1])
                    with c1:
                        on=st.text_input(f"Other {i+1}",key=f"gon{cgh}{i}")
                    with c2:
                        oc=st.number_input("Count",min_value=0,step=1,key=f"goc{cgh}{i}")
                    if on:
                        if cgh not in st.session_state.oa['guesthouse']:
                            st.session_state.oa['guesthouse'][cgh]=[]
                        while len(st.session_state.oa['guesthouse'][cgh])<=i:
                            st.session_state.oa['guesthouse'][cgh].append(('',0))
                        st.session_state.oa['guesthouse'][cgh][i]=(on.upper(),oc)
                st.markdown("---")
                c1,c2,c3=st.columns(3)
                with c1:
                    if cgh==1:
                        if st.button("← Back"):
                            st.session_state.step=4
                            st.session_state.op='review'
                            st.rerun()
                    else:
                        if st.button("← Prev GH"):
                            st.session_state.cgh-=1
                            st.session_state.ghp='review'
                            st.rerun()
                with c2:
                    if st.button("💾 Save"):
                        save()
                with c3:
                    if st.button("Next →",type="primary"):
                        st.session_state.ghp='count'
                        st.rerun()
            elif st.session_state.ghp=='count':
                st.markdown(f"<div class='highlight'>🏠 GH {cgh} - Counts</div>",unsafe_allow_html=True)
                st.markdown("---")
                sel=[n for n in st.session_state.gs[cgh] if st.session_state.gs[cgh][n]]
                if not sel:
                    st.warning("None")
                    st.session_state.ghp='review'
                    st.rerun()
                if cgh not in st.session_state.gc:
                    st.session_state.gc[cgh]={}
                for a in sel:
                    st.markdown(f"<div class='asset-name'>{a}</div>",unsafe_allow_html=True)
                    c=st.number_input(f"Count ",min_value=0,value=st.session_state.gc[cgh].get(a,0),step=1,key=f"gc{cgh}{a}")
                    st.session_state.gc[cgh][a]=c
                    st.markdown("---")
                c1,c2,c3=st.columns(3)
                with c1:
                    if st.button("← Back"):
                        st.session_state.ghp='select'
                        st.rerun()
                with c2:
                    if st.button("💾 Save"):
                        save()
                with c3:
                    if st.button("Review →",type="primary"):
                        st.session_state.ghp='review'
                        st.rerun()
            else:
                st.markdown(f"<div class='highlight'>✅ GH {cgh} - Review</div>",unsafe_allow_html=True)
                st.markdown("---")
                d=[]
                if cgh in st.session_state.gs:
                    for a in st.session_state.gs[cgh]:
                        if st.session_state.gs[cgh][a]:
                            d.append({"Asset":a,"Count":st.session_state.gc.get(cgh,{}).get(a,0)})
                for n,c in st.session_state.oa.get('guesthouse',{}).get(cgh,[]):
                    if n:
                        d.append({"Asset":f"{n} (Other)","Count":c})
                if d:
                    st.dataframe(pd.DataFrame(d),use_container_width=True,hide_index=True)
                else:
                    st.info(f"No GH {cgh} assets")
                st.markdown("---")
                c1,c2,c3=st.columns(3)
                with c1:
                    if st.button("← Edit"):
                        st.session_state.ghp='count'
                        st.rerun()
                with c2:
                    if st.button("💾 Save"):
                        save()
                with c3:
                    if st.button(f"✅ Confirm GH {cgh}",type="primary"):
                        st.session_state.cgh+=1
                        st.session_state.ghp='select'
                        st.rerun()

elif st.session_state.step==6:
    if st.session_state.sp=='select':
        st.markdown("<div class='highlight'>🏪 STORE ASSETS</div>",unsafe_allow_html=True)
        st.markdown("---")
        for a,cat,grp in OFF_ST:
            st.markdown(f"<div class='asset-name'>{a}</div>",unsafe_allow_html=True)
            s=st.radio(a,["Yes","No"],index=0 if st.session_state.ss.get(a,False) else 1,key=f"ss{a}",horizontal=True,label_visibility="collapsed")
            st.session_state.ss[a]=(s=="Yes")
            st.markdown("---")
        st.subheader("Other Assets (Optional)")
        for i in range(3):
            c1,c2=st.columns([2,1])
            with c1:
                on=st.text_input(f"Other {i+1}",key=f"son{i}")
            with c2:
                oc=st.number_input("Count",min_value=0,step=1,key=f"soc{i}")
            if on:
                while len(st.session_state.oa['store'])<=i:
                    st.session_state.oa['store'].append(('',0))
                st.session_state.oa['store'][i]=(on.upper(),oc)
        st.markdown("---")
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("← Back"):
                st.session_state.step=5
                st.session_state.ghp='review'
                st.rerun()
        with c2:
            if st.button("💾 Save"):
                save()
        with c3:
            if st.button("Next →",type="primary"):
                st.session_state.sp='count'
                st.rerun()
    elif st.session_state.sp=='count':
        st.markdown("<div class='highlight'>🏪 STORE - Counts</div>",unsafe_allow_html=True)
        st.markdown("---")
        sel=[n for n in st.session_state.ss if st.session_state.ss[n]]
        if not sel:
            st.warning("None")
            st.session_state.sp='review'
            st.rerun()
        for a in sel:
            st.markdown(f"<div class='asset-name'>{a}</div>",unsafe_allow_html=True)
            c=st.number_input(f"Count ",min_value=0,value=st.session_state.sc.get(a,0),step=1,key=f"sc{a}")
            st.session_state.sc[a]=c
            st.markdown("---")
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("← Back"):
                st.session_state.sp='select'
                st.rerun()
        with c2:
            if st.button("💾 Save"):
                save()
        with c3:
            if st.button("Review →",type="primary"):
                st.session_state.sp='review'
                st.rerun()
    else:
        st.markdown("<div class='highlight'>✅ STORE - Review</div>",unsafe_allow_html=True)
        st.markdown("---")
        d=[]
        for a in st.session_state.ss:
            if st.session_state.ss[a]:
                d.append({"Asset":a,"Count":st.session_state.sc.get(a,0)})
        for n,c in st.session_state.oa.get('store',[]):
            if n:
                d.append({"Asset":f"{n} (Other)","Count":c})
        if d:
            st.dataframe(pd.DataFrame(d),use_container_width=True,hide_index=True)
        else:
            st.info("No Store assets")
        st.markdown("---")
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("← Edit"):
                st.session_state.sp='count'
                st.rerun()
        with c2:
            if st.button("💾 Save"):
                save()
        with c3:
            if st.button("✅ Confirm",type="primary"):
                st.session_state.step=7
                st.rerun()

elif st.session_state.step==7:
    st.markdown("<div class='highlight'>📊 FINAL REVIEW</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("👤 Employee & Project")
    st.write(f"**ID:** {st.session_state.fd.get('ei')}")
    st.write(f"**Name:** {st.session_state.fd.get('en')}")
    st.write(f"**Manager:** {st.session_state.fd.get('rm')}")
    st.write(f"**BU:** {st.session_state.fd.get('bu')}")
    st.write(f"**Project:** {st.session_state.fd.get('pn')} ({st.session_state.fd.get('pc')})")
    st.markdown("---")
    st.subheader("📍 OFFICE")
    od=[{"Asset":a,"Count":st.session_state.oc.get(a,0)} for a in st.session_state.os if st.session_state.os[a]]
    for n,c in st.session_state.oa.get('office',[]):
        if n:
            od.append({"Asset":f"{n} (Other)","Count":c})
    if od:
        st.dataframe(pd.DataFrame(od),use_container_width=True,hide_index=True)
        st.metric("Total",len(od))
    else:
        st.info("No Office assets")
    st.markdown("---")
    ngh=st.session_state.fd.get('ngh',0)
    st.subheader(f"🏠 GUESTHOUSE ({ngh})")
    if ngh>0:
        for g in range(1,ngh+1):
            st.write(f"**GH {g}** | Persons: {st.session_state.gp.get(g,0)}")
            gd=[]
            if g in st.session_state.gs:
                for a in st.session_state.gs[g]:
                    if st.session_state.gs[g][a]:
                        gd.append({"Asset":a,"Count":st.session_state.gc.get(g,{}).get(a,0)})
            for n,c in st.session_state.oa.get('guesthouse',{}).get(g,[]):
                if n:
                    gd.append({"Asset":f"{n} (Other)","Count":c})
            if gd:
                st.dataframe(pd.DataFrame(gd),use_container_width=True,hide_index=True)
            else:
                st.info(f"No GH {g} assets")
            st.markdown("---")
    else:
        st.info("No GH")
    st.subheader("🏪 STORE")
    sd=[{"Asset":a,"Count":st.session_state.sc.get(a,0)} for a in st.session_state.ss if st.session_state.ss[a]]
    for n,c in st.session_state.oa.get('store',[]):
        if n:
            sd.append({"Asset":f"{n} (Other)","Count":c})
    if sd:
        st.dataframe(pd.DataFrame(sd),use_container_width=True,hide_index=True)
        st.metric("Total",len(sd))
    else:
        st.info("No Store assets")
    st.markdown("---")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("← Back"):
            st.session_state.step=6
            st.session_state.sp='review'
            st.rerun()
    with c2:
        if st.button("💾 Save"):
            save()
    with c3:
        if st.button("✅ FINAL SUBMIT",type="primary"):
            st.session_state.step=8
            st.rerun()

elif st.session_state.step==8:
    try:
        conn=sqlite3.connect('facilities_asset_data.db')
        c=conn.cursor()
        fd=st.session_state.fd
        c.execute('''INSERT OR REPLACE INTO submissions 
                     (employee_id,employee_name,reporting_manager,business_unit,project_name,project_code,
                      office_store_gh_together,office_store_together,office_gh_together,num_guesthouses,
                      submission_datetime,is_complete,current_step,saved_state)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,1,8,'')''',
                  (fd['ei'],fd['en'],fd['rm'],fd['bu'],fd['pn'],fd['pc'],
                   fd.get('q1',''),fd.get('q2',''),fd.get('q3',''),fd.get('ngh',0),
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        sid=c.lastrowid
        c.execute('DELETE FROM assets WHERE submission_id=?',(sid,))
        c.execute('DELETE FROM guesthouses WHERE submission_id=?',(sid,))
        gid={}
        for g in range(1,fd.get('ngh',0)+1):
            c.execute('INSERT INTO guesthouses (submission_id,guesthouse_number,number_of_persons,gmap_link) VALUES (?,?,?,?)',
                      (sid,g,st.session_state.gp.get(g,0),st.session_state.gl.get(g,'')))
            gid[g]=c.lastrowid
        for a,cat,grp in OFF_ST:
            if st.session_state.os.get(a):
                c.execute('INSERT INTO assets (submission_id,guesthouse_id,asset_location,asset_name,asset_count,asset_group,asset_category,asset_subcategory) VALUES (?,NULL,?,?,?,?,?,?)',
                          (sid,'Office',a,st.session_state.oc.get(a,0),grp,cat,a))
        for n,cnt in st.session_state.oa.get('office',[]):
            if n:
                c.execute('INSERT INTO assets (submission_id,guesthouse_id,asset_location,asset_name,asset_count,asset_group,asset_category,asset_subcategory) VALUES (?,NULL,?,?,?,?,?,?)',
                          (sid,'Office',n,cnt,'Other','Other','Other'))
        for g in range(1,fd.get('ngh',0)+1):
            if g in st.session_state.gs:
                for a,cat,grp in GH:
                    if st.session_state.gs[g].get(a):
                        c.execute('INSERT INTO assets (submission_id,guesthouse_id,asset_location,asset_name,asset_count,asset_group,asset_category,asset_subcategory) VALUES (?,?,?,?,?,?,?,?)',
                                  (sid,gid.get(g),f'Guesthouse {g}',a,st.session_state.gc.get(g,{}).get(a,0),grp,cat,a))
            for n,cnt in st.session_state.oa.get('guesthouse',{}).get(g,[]):
                if n:
                    c.execute('INSERT INTO assets (submission_id,guesthouse_id,asset_location,asset_name,asset_count,asset_group,asset_category,asset_subcategory) VALUES (?,?,?,?,?,?,?,?)',
                              (sid,gid.get(g),f'Guesthouse {g}',n,cnt,'Other','Other','Other'))
        for a,cat,grp in OFF_ST:
            if st.session_state.ss.get(a):
                c.execute('INSERT INTO assets (submission_id,guesthouse_id,asset_location,asset_name,asset_count,asset_group,asset_category,asset_subcategory) VALUES (?,NULL,?,?,?,?,?,?)',
                          (sid,'Store',a,st.session_state.sc.get(a,0),grp,cat,a))
        for n,cnt in st.session_state.oa.get('store',[]):
            if n:
                c.execute('INSERT INTO assets (submission_id,guesthouse_id,asset_location,asset_name,asset_count,asset_group,asset_category,asset_subcategory) VALUES (?,NULL,?,?,?,?,?,?)',
                          (sid,'Store',n,cnt,'Other','Other','Other'))
        conn.commit()
        conn.close()
        st.success("🎉 SUBMISSION SUCCESSFUL!")
        st.balloons()
        st.markdown("---")
        st.subheader("✅ Data Recorded")
        st.write(f"**Employee:** {fd['ei']} - {fd['en']}")
        st.write(f"**Project:** {fd['pn']} ({fd['pc']})")
        st.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("---")
        st.info("Thank you! Your data is in the system.")
        if st.button("🔄 New Submission"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.caption("Facilities Asset Data Capture System v1.0 | Production | Developed by Divya")
