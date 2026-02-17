import streamlit as st 
from pages.roommate_funcs.roommate_xai_demo import roommate_xai_demo
from pages.roommate_funcs.roommate_xai_nodemo import roommate_xai_nodemo

from pages.roommate_funcs.tools import clear_explanation
from pages.ha_funcs.tools import longfaircode , reset_local_graph, clear_preferences, reset_global, clear_matching
from pages.roommate_funcs.roommate_xai_demo import load_correct_instance

st.set_page_config(page_title="Roommate Matching XAI", page_icon=":material/person_book:", layout="wide")

# Initialize session state at the top
if 'current_explanation' not in st.session_state:
    st.session_state.current_explanation = None
if 'current_preferences' not in st.session_state:
    st.session_state.current_preferences = None


st.session_state["opened_srp"] = True 
if st.session_state.get("opened_ha",False):
    st.session_state["opened_ha"] = False

st.session_state["it"] = 0 # To fix widgets IDs bc of reruns when clicking buttons


if not "srpnormal" in st.session_state:
    st.session_state["srpnormal"] = "primary"
if not "srpdemo" in st.session_state:
    st.session_state["srpdemo"] = "secondary"

if st.session_state.srpdemo == "primary":
    load_correct_instance()

st.title("Explanations for the Roommate Matching Problem")
print("*******************")
print("running")

lbl = "Please enter the number of agents in your instance"
colun = st.columns(3)
with colun[1]:
    oldn = st.session_state.get("n",-1)
    n = st.number_input(label = lbl, min_value = 4, step=1, value=6, key="n",kwargs={'with_prefs':True}, disabled = st.session_state.srpdemo == "primary")
    
    # Custom agent names input
    custom_names = st.multiselect(
        "If you wish, you can enter custom agent names", 
        accept_new_options=True,
        options=[],
        max_selections=n,
        key="custom_agent_names_input",
        help=f"Enter {n} custom names for the agents (or leave empty to use default names)"
    )
    
    # Store custom names in session state or clear to use defaults
    if len(custom_names) == n:
        st.session_state["custom_agent_names"] = custom_names
    elif len(custom_names) == 0:
        # User cleared the widget - fall back to default names
        st.session_state["custom_agent_names"] = None
    else:
        # Invalid number of names - show warning and clear
        st.warning(f"Please enter exactly {n} agent names, currently you have {len(custom_names)}")
        st.session_state["custom_agent_names"] = None
    
    st.radio("Please choose a fairness criterion", options = ["ref","lef" ],format_func=longfaircode,key='fair_crit',horizontal=True, 
             on_change= lambda: (clear_explanation(), clear_matching()) )
    if oldn != n:
        reset_global()


agents = [i for i in range(n)]

st.session_state["agents"] = agents




cols = st.columns([3,2,2,3])
with cols[1]:
    if st.button("Build your own instance!",type = st.session_state["srpnormal"], on_click=clear_explanation, kwargs={"with_matching":True}):
        st.session_state["srpnormal"] = "primary"
        st.session_state["srpdemo"] = "secondary"

        clear_preferences()
        if st.session_state.fair_crit == "lef":
            reset_local_graph()
        st.rerun()

with cols[2]:
    if st.button("Explore a demo instance 🙂",type = st.session_state["srpdemo"], on_click=clear_explanation):
        if st.session_state["srpdemo"] == "secondary":
            st.session_state["srpnormal"] = "secondary"
            st.session_state["srpdemo"] = "primary"
        else:
            clear_preferences()
            st.session_state["srpnormal"] = "primary"
            st.session_state["srpdemo"] = "secondary"
        st.rerun()

B1 = st.session_state["srpnormal"]
B2 = st.session_state["srpdemo"]

if B1 == "primary":
    roommate_xai_nodemo()
else:
    roommate_xai_demo()


