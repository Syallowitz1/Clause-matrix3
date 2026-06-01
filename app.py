import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="FAR/DFARS Compliance Engine", layout="wide")

# --- Realistic Clause Database (50+ Clauses) ---
# Categorized into Statutory (Required by Gov) and Strategic (Required by Company)
REALISTIC_CLAUSES = [
    # --- STATUTORY: ETHICS & ADMIN ---
    {"id": "52.203-7", "title": "Anti-Kickback Procedures", "cat": "Statutory", "mandatory": True, "threshold": 150000, "risk": 2},
    {"id": "52.203-12", "title": "Limitation on Payments to Influence Federal Transactions", "cat": "Statutory", "mandatory": True, "threshold": 150000, "risk": 2},
    {"id": "52.203-13", "title": "Contractor Code of Business Ethics and Conduct", "cat": "Statutory", "mandatory": True, "threshold": 6000000, "risk": 3},
    {"id": "52.204-10", "title": "Reporting Executive Compensation and First-Tier Subcontract Awards", "cat": "Statutory", "mandatory": True, "threshold": 30000, "risk": 1},
    {"id": "52.204-21", "title": "Basic Safeguarding of Covered Contractor Information Systems", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "52.204-25", "title": "Prohibition on Contracting for Certain Telecommunications", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    
    # --- STATUTORY: COST & PRICING ---
    {"id": "52.215-2", "title": "Audit and Records - Negotiation", "cat": "Statutory", "mandatory": True, "threshold": 250000, "risk": 2},
    {"id": "52.215-10", "title": "Price Reduction for Defective Certified Cost or Pricing Data", "cat": "Statutory", "mandatory": True, "threshold": 2000000, "risk": 3},
    {"id": "52.215-12", "title": "Subcontractor Certified Cost or Pricing Data", "cat": "Statutory", "mandatory": True, "threshold": 2000000, "risk": 3},
    {"id": "52.215-23", "title": "Limitations on Pass-Through Charges", "cat": "Statutory", "mandatory": True, "threshold": 250000, "risk": 2},
    
    # --- STATUTORY: SOCIO-ECONOMIC ---
    {"id": "52.219-8", "title": "Utilization of Small Business Concerns", "cat": "Statutory", "mandatory": True, "threshold": 250000, "risk": 1},
    {"id": "52.219-9", "title": "Small Business Subcontracting Plan", "cat": "Statutory", "mandatory": True, "threshold": 750000, "risk": 2},
    {"id": "52.222-21", "title": "Prohibition of Segregated Facilities", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 1},
    {"id": "52.222-26", "title": "Equal Opportunity", "cat": "Statutory", "mandatory": True, "threshold": 10000, "risk": 1},
    {"id": "52.222-35", "title": "Equal Opportunity for Veterans", "cat": "Statutory", "mandatory": True, "threshold": 150000, "risk": 1},
    {"id": "52.222-36", "title": "Equal Opportunity for Workers with Disabilities", "cat": "Statutory", "mandatory": True, "threshold": 15000, "risk": 1},
    {"id": "52.222-37", "title": "Employment Reports on Veterans", "cat": "Statutory", "mandatory": True, "threshold": 150000, "risk": 1},
    {"id": "52.222-40", "title": "Notification of Employee Rights Under the NLRA", "cat": "Statutory", "mandatory": True, "threshold": 10000, "risk": 1},
    {"id": "52.222-50", "title": "Combating Trafficking in Persons", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "52.222-54", "title": "Employment Eligibility Verification (E-Verify)", "cat": "Statutory", "mandatory": True, "threshold": 3500, "risk": 2},
    
    # --- STATUTORY: DOMESTIC SOURCE & CYBER ---
    {"id": "252.204-7012", "title": "Safeguarding Covered Defense Information (CDI)", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "252.204-7019", "title": "Notice of NIST SP 800-171 DoD Assessment", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "252.204-7020", "title": "NIST SP 800-171 DoD Assessment Requirements", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "252.225-7001", "title": "Buy American and Balance of Payments Program", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 2},
    {"id": "252.225-7009", "title": "Restriction on Acquisition of Certain Articles Containing Specialty Metals", "cat": "Statutory", "mandatory": True, "threshold": 150000, "risk": 3},
    {"id": "252.225-7012", "title": "Preference for Certain Domestic Commodities", "cat": "Statutory", "mandatory": True, "threshold": 250000, "risk": 2},
    {"id": "252.225-7048", "title": "Export-Controlled Items", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    
    # --- STATUTORY: INTELLECTUAL PROPERTY & QUALITY ---
    {"id": "252.227-7013", "title": "Rights in Technical Data - Noncommercial Items", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "252.227-7014", "title": "Rights in Noncommercial Computer Software", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "252.227-7037", "title": "Validation of Restrictive Markings on Technical Data", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 2},
    {"id": "52.245-1", "title": "Government Property", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 2},
    {"id": "252.246-7003", "title": "Notification of Potential Safety Issues", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "252.246-7007", "title": "Contractor Counterfeit Electronic Part Detection and Avoidance", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    {"id": "252.246-7008", "title": "Sources of Electronic Parts", "cat": "Statutory", "mandatory": True, "threshold": 0, "risk": 3},
    
    # --- STRATEGIC: CORPORATE RISK PROTECTION ---
    # These protect the PRIME from the SUB, even if not explicitly in the Prime Contract.
    {"id": "STRAT-IP-01", "title": "Invention Disclosure & Ownership", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 0, "risk": 3},
    {"id": "STRAT-IND-01", "title": "Indemnification (General & Intellectual Property)", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 0, "risk": 3},
    {"id": "STRAT-LIAB-01", "title": "Limitation of Liability (Mutual)", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 0, "risk": 3},
    {"id": "STRAT-TERM-01", "title": "Termination for Convenience (Mirroring Prime Rights)", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 0, "risk": 2},
    {"id": "STRAT-AUD-01", "title": "Right to Audit Financials and Quality Systems", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 150000, "risk": 2},
    {"id": "STRAT-DEL-01", "title": "Liquidated Damages for Late Delivery", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 500000, "risk": 2},
    {"id": "STRAT-WAR-01", "title": "Warranty (12-Month Pass Through)", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 0, "risk": 2},
    {"id": "STRAT-INS-01", "title": "Insurance Requirements (GL, WC, Auto)", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 0, "risk": 1},
    {"id": "STRAT-DISP-01", "title": "Dispute Resolution & Governing Law", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 0, "risk": 2},
    {"id": "STRAT-FORCE-01", "title": "Force Majeure Notification Requirements", "cat": "Strategic", "mandatory": False, "recommended": True, "threshold": 0, "risk": 1},
]

# --- UI Header ---
st.title("🛡️ Government Contract Flowdown Engine")
st.markdown("Automate clause selection for Subcontracts and Purchase Orders under Federal Prime Contracts.")

# --- Layout ---
input_col, output_col = st.columns([1, 1.8], gap="large")

with input_col:
    st.header("📋 Contextual Inputs")
    with st.container(border=True):
        po_value = st.number_input("Total Subcontract/PO Value ($)", min_value=0, value=250000, step=50000)
        is_commercial = st.radio("Subcontract Type", ["Standard/Non-Commercial", "Commercial Item (FAR Part 12)"])
        has_cui = st.checkbox("Subcontractor will handle CUI/CDI?", value=True)
        is_foreign = st.checkbox("Is the Subcontractor a Foreign Entity?", value=False)
    
    st.subheader("💡 Methodology")
    st.info("""
    **Statutory Clauses:** Derived from the 'Example Navy Contract'. These are required by law to be flowed down.
    
    **Strategic Clauses:** Not explicitly in the Prime, but added by your company to mitigate risk (e.g., Indemnity, Warranty).
    """)

with output_col:
    st.header("📄 Generated Clause Matrix")
    
    # --- FILTERING LOGIC ---
    results = []
    for c in REALISTIC_CLAUSES:
        # 1. Threshold Check
        if po_value < c['threshold']:
            continue
            
        # 2. Commercial Item Filtering
        # If commercial, we only flow down a very small subset of FAR/DFARS
        if "Commercial" in is_commercial and c['cat'] == "Statutory":
            commercial_ok = ["52.203-13", "52.204-25", "52.222-26", "52.222-35", "52.222-36", "52.222-50", "252.204-7012", "52.244-6"]
            if c['id'] not in commercial_ok:
                continue
        
        # 3. Cyber/CUI Filtering
        if "Cyber" in c['title'] or "CDI" in c['title']:
            if not has_cui: continue

        results.append(c)

    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Approver Logic
    def get_approver(risk):
        if risk == 3: return "VP of Supply Chain / Legal"
        if risk == 2: return "Dept Director"
        return "Purchasing Manager"
    
    df['Approver (to Remove)'] = df['risk'].apply(get_approver)

    # --- Search Box ---
    search_query = st.text_input("🔍 Search for a specific clause (e.g., 'Ethics' or '52.222')")
    if search_query:
        df = df[df['id'].str.contains(search_query, case=False) | df['title'].str.contains(search_query, case=False)]

    # --- Display Table ---
    st.subheader(f"Total Clauses Identified: {len(df)}")
    
    # Tabs for organization
    tab1, tab2 = st.tabs(["Compliance Matrix", "Risk Analysis"])
    
    with tab1:
        st.dataframe(df[['id', 'title', 'cat', 'risk', 'Approver (to Remove)']], 
                     use_container_width=True, 
                     hide_index=True)
    
    with tab2:
        st.write("**Risk Distribution (Count of Clauses by Severity)**")
        st.bar_chart(df['risk'].value_counts().sort_index())

# --- Negotiation Logic ---
st.divider()
st.header("🤝 Negotiation Tool")
negotiate_id = st.selectbox("Select a clause to evaluate for removal:", df['id'].tolist())
clause_info = df[df['id'] == negotiate_id].iloc[0]

with st.expander("Show Negotiation Risk Assessment", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**Clause:** {clause_info['id']} - {clause_info['title']}")
        st.write(f"**Category:** {clause_info['cat']}")
        st.write(f"**Current Risk Level:** {clause_info['risk']}")
    with col_b:
        st.error(f"**Required Approver:** {clause_info['Approver (to Remove)']}")
        if clause_info['cat'] == "Statutory":
            st.markdown("⚠️ **Legal Warning:** This is a MANDATORY statutory flow-down. Striking this from the subcontract may put the company in breach of the Prime Contract and result in government penalties.")
        else:
            st.markdown("ℹ️ **Strategic Note:** This is a company-added protection. You may negotiate this away, but ensure the Purchasing Manager understands the financial liability we are assuming.")
