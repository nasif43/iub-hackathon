import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

CATEGORIES = [
    "Payment",
    "Termination",
    "Data Protection",
    "Confidentiality",
    "Automatic Renewal",
    "Intellectual Property",
    "Limitation of Liability",
]

st.set_page_config(page_title="Contract Review Assistant", layout="wide")

# Sidebar navigation / page selection
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Review", "Review History", "About"])

if "last_review_result" not in st.session_state:
    st.session_state["last_review_result"] = None

# Helper functions for API calls
def fetch_contracts():
    try:
        res = requests.get(f"{BACKEND_URL}/contracts", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Failed to fetch contracts: {e}")
    return []

def fetch_contract_clauses(contract_id):
    try:
        res = requests.get(f"{BACKEND_URL}/contracts/{contract_id}/clauses", timeout=5)
        if res.status_code == 200:
            return {c["category"]: c for c in res.json()}
    except Exception:
        pass
    return {}

def run_review(contract_id, category):
    try:
        res = requests.post(
            f"{BACKEND_URL}/review",
            json={"contract_id": contract_id, "category": category},
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Error running review: {res.status_code} - {res.text}")
    except Exception as e:
        st.error(f"API request failed: {e}")
    return None

def submit_decision(review_id, status, reviewer_note):
    try:
        res = requests.post(
            f"{BACKEND_URL}/reviews/{review_id}/decision",
            json={"status": status, "reviewer_note": reviewer_note},
            timeout=5,
        )
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Failed to record decision: {res.status_code} - {res.text}")
    except Exception as e:
        st.error(f"API request failed: {e}")
    return None

def fetch_reviews(contract_id=None, status=None):
    try:
        params = {}
        if contract_id:
            params["contract_id"] = contract_id
        if status and status != "All":
            params["status"] = status
        res = requests.get(f"{BACKEND_URL}/reviews", params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Failed to fetch reviews: {e}")
    return []

# --- PAGE 1: REVIEW ---
if page == "Review":
    st.title("Contract Review")
    
    contracts = fetch_contracts()
    if not contracts:
        st.warning("No contracts available or backend mock server loading...")
        st.stop()
        
    contract_options = {f"{c['id']} - {c['title']}": c for c in contracts}
    selected_option = st.sidebar.selectbox("Select Contract", list(contract_options.keys()))
    selected_contract = contract_options[selected_option]
    st.session_state["selected_contract_id"] = selected_contract["id"]
    
    st.subheader(f"Contract: {selected_contract['title']} ({selected_contract['id']})")
    st.caption(f"Parties: {selected_contract['parties']}")
    
    clauses_map = fetch_contract_clauses(selected_contract["id"])
    
    # 7 Category Tabs
    tabs = st.tabs(CATEGORIES)
    for idx, category in enumerate(CATEGORIES):
        with tabs[idx]:
            clause_info = clauses_map.get(category, {})
            is_present = clause_info.get("present", True) # Default true if unknown
            
            if not is_present:
                st.info(f"Clause category **{category}** is NOT detected in this contract. (Click 'Run Review' to demonstrate Abstention / Not Enough Information path).")
            else:
                st.write(f"Clause Category: **{category}**")
                
            if st.button(f"Run Review for {category}", key=f"btn_{category}"):
                st.session_state["selected_category"] = category
                result = run_review(selected_contract["id"], category)
                if result:
                    st.session_state["last_review_result"] = result
                    st.rerun()

    # Result Card Rendering
    result = st.session_state.get("last_review_result")
    if result:
        st.markdown("---")
        st.header("Review Result")
        
        # Header: Contract ID + Clause Type
        st.subheader(f"Result for {result.get('contract_id')} — {result.get('category')}")
        
        # Colored risk badge
        risk = result.get("risk_level", "Unknown")
        badge_colors = {
            "Low Risk": "#28a745",
            "Medium Risk": "#ffc107",
            "High Risk": "#dc3545",
            "Not Enough Information": "#6c757d",
        }
        bg_color = badge_colors.get(risk, "#6c757d")
        text_color = "#000000" if risk == "Medium Risk" else "#ffffff"
        st.markdown(
            f'<div style="background-color: {bg_color}; color: {text_color}; padding: 8px 16px; border-radius: 4px; display: inline-block; font-weight: bold; font-size: 18px; margin-bottom: 16px;">'
            f'Risk Level: {risk}'
            '</div>',
            unsafe_allow_html=True,
        )
        
        # Contract Evidence expandable block
        evidence = result.get("contract_evidence")
        with st.expander("Contract Evidence", expanded=True):
            if evidence:
                st.markdown(f"> *{evidence}*")
            else:
                st.write("No automatic renewal clause found in this excerpt (or no clause found).")
                
        # Company Standard block
        std_id = result.get("standard_id")
        std_text = result.get("standard_text")
        with st.expander("Company Standard", expanded=True):
            if std_id or std_text:
                st.write(f"**Standard ID:** {std_id}")
                st.write(f"**Text:** {std_text}")
            else:
                st.write("N/A — not applicable")
                
        # Reason paragraph
        st.markdown("**Reason:**")
        st.write(result.get("reason", ""))
        
        # Fixed banner, always visible, never dismissible
        st.warning("**Human Review Required — this is not legal advice.**")
        
        # Review action row: Approve / Reject / Mark for review + Add feedback text input
        st.subheader("Action & Decision")
        reviewer_note = st.text_input("Add feedback / reviewer note:", key="reviewer_note_input")
        
        col1, col2, col3 = st.columns(3)
        review_id = result.get("review_id", 1)
        
        with col1:
            if st.button("Approve", key="btn_approve"):
                updated = submit_decision(review_id, "approved", reviewer_note)
                if updated:
                    st.success("Review marked as Approved!")
                    st.session_state["last_review_result"] = updated
                    st.rerun()
        with col2:
            if st.button("Reject", key="btn_reject"):
                updated = submit_decision(review_id, "rejected", reviewer_note)
                if updated:
                    st.success("Review marked as Rejected!")
                    st.session_state["last_review_result"] = updated
                    st.rerun()
        with col3:
            if st.button("Mark for review", key="btn_mark"):
                updated = submit_decision(review_id, "marked_for_review", reviewer_note)
                if updated:
                    st.success("Review marked for review!")
                    st.session_state["last_review_result"] = updated
                    st.rerun()

# --- PAGE 2: REVIEW HISTORY ---
elif page == "Review History":
    st.title("Review History (Audit Trail)")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_contract = st.text_input("Filter by Contract ID (e.g. C-001):")
    with col_f2:
        filter_status = st.selectbox("Filter by Status:", ["All", "pending", "approved", "rejected", "marked_for_review"])
        
    reviews = fetch_reviews(contract_id=filter_contract if filter_contract else None, status=filter_status)
    
    if reviews:
        st.dataframe(reviews, use_container_width=True)
    else:
        st.info("No reviews found matching filters.")

# --- PAGE 3: ABOUT / SAFETY NOTES ---
elif page == "About":
    st.title("About / Safety Notes")
    st.markdown("""
    ### Safety & Architectural Principles
    This Contract Review Assistant is **not legal advice** and is designed with a strict **human-in-the-loop** architecture.
    
    - **Evidence-Based**: All conclusions rely on verbatim extraction from contract source text and standardized company guidelines.
    - **Rule-Engine-First**: Risk levels and compliance flags are derived deterministically by code logic, ensuring transparent, reproducible, and verifiable safety guarantees without relying on ungrounded generative AI predictions.
    - **Human Control**: Every result mandates human review prior to final decision-making.
    """)
