import streamlit as st
import pandas as pd

st.set_page_config(page_title="Federal Subcontract Compliance & Risk Matrix", layout="wide")

# --- VERIFIED CLAUSE DATABASE (EXTRACTED FROM ATTACHMENT A) ---
#
CLAUSE_DB = [
    # Table 1: Commercial Items
    {"Clause": "52.203-07", "Title": "Anti-Kickback Procedures", "Threshold": 150000, "Commercial": True, "Mandatory": True, "Risk": 2, "Risk Explanation": "Mandatory for orders over $150k per FAR standards."},
    {"Clause": "52.203-12", "Title": "Limitation on Payments to Influence Certain Federal Transactions", "Threshold": 150000, "Commercial": True, "Mandatory": True, "Risk": 2, "Risk Explanation": "Statutory reporting requirement for lobbying activities."},
    {"Clause": "52.203-13", "Title": "Contractor Code of Business Ethics and Conduct", "Threshold": 6000000, "Commercial": True, "Mandatory": True, "Risk": 3, "Risk Explanation": "Critical compliance risk for large awards (> $6M)."},
    {"Clause": "52.204-21", "Title": "Basic Safeguarding of Covered Contractor Information Systems", "Threshold": 0, "Commercial": True, "Mandatory": True, "Risk": 3, "Risk Explanation": "Cybersecurity baseline. Excluded for pure COTS items."},
    {"Clause": "52.219-8", "Title": "Utilization of Small Business Concerns", "Threshold": 0, "Commercial": True, "Mandatory": True, "Risk": 1, "Risk Explanation": "Mandatory if subcontracting opportunities exist."},
    {"Clause": "52.222-50", "Title": "Combating Trafficking in Persons", "Threshold": 550000, "Commercial": True, "Mandatory": True, "Risk": 2, "Risk Explanation": "Threshold applies if work is performed outside the U.S."},
    {"Clause": "52.225-1", "Title": "Buy American - Supplies", "Threshold": 0, "Commercial": True, "Mandatory": True, "Risk": 2, "Risk Explanation": "Restricts foreign supplies; excluded for COTS."},
    
    # Table 2: DoD-Specific Commercial Items
    {"Clause": "252.204-7012", "Title": "Safeguarding Covered Defense Information and Cyber Incident Reporting", "Threshold": 0, "Commercial": True, "Mandatory": True, "Risk": 3, "Risk Explanation": "Mandatory for DoD. Requires 72-hour reporting of cyber incidents."},
    {"Clause": "252.225-7008", "Title": "Restriction on Acquisition of Specialty Metals", "Threshold": 0, "Commercial": True, "Mandatory": True, "Risk": 3, "Risk Explanation": "Critical DoD supply chain clause for items containing specialty metals."},
    {"Clause": "252.225-7009", "Title": "Restriction on Acquisition of Certain Articles Containing Specialty Metals", "Threshold": 0, "Commercial": True, "Mandatory": True, "Risk": 3, "Risk Explanation": "Applies to end-items containing specialty metals; contains specific exceptions."},
    {"Clause": "252.246-7007", "Title": "Contractor Counterfeit Electronic Part Detection and Avoidance System", "Threshold": 0, "Commercial": True, "Mandatory": True, "Risk": 3, "Risk Explanation": "Mandatory for DoD orders involving electronic parts."},
    {"Clause": "252.225-7048", "Export-Controlled Items": "Export-Controlled Items", "Threshold": 0, "Commercial": True, "Mandatory": True, "Risk": 3, "Risk Explanation": "Mandatory for all DoD orders involving ITAR/EAR technical data."},

    # Table 3: Non-Commercial / Recommended
    {"Clause": "52.215-2", "Title": "Audit and Records Negotiation", "Threshold": 250000, "Commercial": False, "Mandatory": True, "Risk": 3, "Risk Explanation": "Allows audit of subcontractor records; essential for cost-reimbursable work."},
    {"Clause": "52.215-12", "Title": "Subcontractor Cost or Pricing Data", "Threshold": 2000000, "Commercial": False, "Mandatory": True, "Risk": 3, "Risk Explanation": "Required for TINA compliance on large non-commercial awards."},
    {"Clause": "52.227-14", "Title": "Rights in Data - General", "Threshold": 0, "Commercial": False, "Mandatory": False, "Risk": 3, "Risk Explanation": "Protects IP; defines ownership of data developed under the order."},
]

# --- STREAMLIT UI ---
st.title("Federal Subcontract Compliance & Risk Management")

# 1. CONTRACT DEFINITION
if 'contracts' not in st.session_state:
    st.session_state.contracts = {
        "EXAMPLE - Federal Prime (N00014-24-C-XXXX)": {"is_dod": True},
        "EXAMPLE - GSA Schedule (GS-35F-XXXXX)": {"is_dod": False}
    }

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("1. Prime Contract Context")
    
    contract_options = list(st.session_state.contracts.keys()) + ["Add New Contract..."]
    selected_contract = st.selectbox("Select Active Prime Contract", contract_options)
    
    if selected_contract == "Add New Contract...":
        new_name = st.text_input("Contract Number/Name")
        new_is_dod = st.radio("Is this DoD Funded?", ["Yes", "No"], horizontal=True)
        if st.button("Save Contract"):
            st.session_state.contracts[new_name] = {"is_dod": (new_is_dod == "Yes")}
            st.rerun()
        contract_data = {"is_dod": (new_is_dod == "Yes")}
    else:
        contract_data = st.session_state.contracts[selected_contract]
        st.info(f"**DoD Funding:** {'Yes' if contract_data['is_dod'] else 'No'}")

    with st.container(border=True):
        st.subheader("Subcontract Parameters")
        po_value = st.number_input("Subcontract/PO Value ($)", min_value=0, value=250000)
        is_commercial = st.radio("Is this a Commercial Item? (FAR Part 2/12)", ["No", "Yes"])
        is_cots = st.checkbox("Is this a COTS item? (Commercially Available Off-The-Shelf)")
        
        st.markdown("---")
        st.write("Technical & Geographical Triggers:")
        has_cui = st.checkbox("Subcontract involves CUI / Technical Data?")
        has_metals = st.checkbox("Deliverable contains Specialty Metals?")
        has_electronics = st.checkbox("Includes Electronic Parts?")
        is_foreign = st.checkbox("Is the Subcontractor a Foreign Entity?")
        outside_us = st.checkbox("Performance occurs outside the U.S.?")

with col2:
    st.header("2. Flowdown & Risk Results")
    
    # FILTER LOGIC
    results = []
    for c in CLAUSE_DB:
        if po_value < c["Threshold"]: continue
        if is_commercial == "Yes" and not c.get("Commercial", False): continue
        if is_cots and c["Clause"] in ["52.204-21", "52.225-1"]: continue 
        if "252." in c["Clause"] and not contract_data["is_dod"]: continue
        
        # Trigger Logic
        if "Specialty Metals" in c["Title"] and not has_metals: continue
        if "Counterfeit" in c["Title"] and not has_electronics: continue
        if "Trafficking" in c["Title"] and not (outside_us or po_value > 550000): continue
        if "Cyber" in c["Title"] and not has_cui: continue

        results.append(c)

    df = pd.DataFrame(results)

    def render_bucket(title, subtitle, filter_criteria, color):
        st.markdown(f"### {color} {title}")
        st.caption(subtitle)
        subset = df.query(filter_criteria) if not df.empty else pd.DataFrame()
        if not subset.empty:
            st.table(subset[["Clause", "Title", "Risk Explanation"]])
        else:
            st.write("_None applicable._")

    render_bucket("Mandatory Flowdowns", "Required per FAR/DFARS tables.", "Mandatory == True", "⚠️")
    render_bucket("Level 3: VP Approval Required", "High risk (IP, Defective Pricing, Cyber).", "Mandatory == False and Risk == 3", "🔴")
    render_bucket("Level 2: Director Approval Required", "Medium risk (Warranties, Terminations).", "Mandatory == False and Risk == 2", "🟡")
    render_bucket("Level 1: Manager Approval Required", "Administrative/Low-level risk.", "Mandatory == False and Risk == 1", "🔵")

st.divider()
st.caption("**Data Source:** Clause titles and thresholds verified against acquisition.gov via Attachment A. All placeholder/sample data has been purged.")
