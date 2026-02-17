import streamlit as st 
from pages.ha_funcs.ha_xai_demo import ha_xai_demo
from pages.ha_funcs.ha_xai_nodemo import ha_xai_nodemo
from pages.ha_funcs.names import NAMES
from pages.roommate_funcs.tools import clear_explanation, reset_agent_preferences
from pages.ha_funcs.tools import longfaircode , reset_local_graph, clear_preferences, reset_global
from pages.ha_funcs.ha_xai_demo import load_correct_instance

st.set_page_config(page_title="House Allocation XAI", page_icon=":material/person_book:", layout="wide")

# Initialize session state at the top
if 'current_explanation' not in st.session_state:
    st.session_state.current_explanation = None
if 'current_preferences' not in st.session_state:
    st.session_state.current_preferences = None


st.session_state["opened_ha"] = True 
if st.session_state.get("opened_srp",False):
    st.session_state["opened_srp"] = False
    

st.session_state["it"] = 0 # To fix widgets IDs bc of reruns when clicking buttons


if not "hanormal" in st.session_state:
    st.session_state["hanormal"] = "primary"
if not "hademo" in st.session_state:
    st.session_state["hademo"] = "secondary"

if st.session_state.hademo == "primary":
    load_correct_instance()

st.title("Explanations for the House Allocation Problem")

lbl = "Please enter the number of agents in your instance"
colun = st.columns(3)
with colun[1]:
    oldn = st.session_state.get("n",-1)
    oldfair = st.session_state.get("fair_crit",-1)
    n = st.number_input(label = lbl, min_value = 4, max_value=26, step=1, value=6, key="n", on_change=clear_explanation,kwargs={'with_prefs':True}, disabled = st.session_state.hademo == "primary")

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

    # Custom object names input
    custom_objects = st.multiselect(
        "If you wish, you can enter custom object names", 
        accept_new_options=True,
        options=[],
        max_selections=n,
        key="custom_object_names_input",
        help=f"Enter {n} custom names for the objects (or leave empty to use default names)"
    )
    
    # Store custom object names in session state or clear to use defaults
    if len(custom_objects) == n:
        st.session_state["custom_object_names"] = custom_objects
    elif len(custom_objects) == 0:
        # User cleared the widget - fall back to default names
        st.session_state["custom_object_names"] = None
    else:
        # Invalid number of names - show warning and clear
        st.warning(f"Please enter exactly {n} object names, currently you have {len(custom_objects)}")
        st.session_state["custom_object_names"] = None

    fair = st.radio("Please choose a fairness criterion", options = ["ref","lef" ],format_func=longfaircode,key='fair_crit',horizontal=True, 
             on_change=reset_global )
    if oldn != n or oldfair != fair:
        st.rerun()

m = n
agents = [i for i in range(n)]
objects = [chr(ord('A') + i) for i in range(m)]
st.session_state["agents"] = agents
st.session_state["objects"] = objects



cols = st.columns([3,2,2,3])
with cols[1]:
    if st.button("Build your own instance!",type = st.session_state["hanormal"], on_click=clear_explanation, kwargs={"with_matching":True}):
        st.session_state["hanormal"] = "primary"
        st.session_state["hademo"] = "secondary"

        clear_preferences()
        if st.session_state.fair_crit == "lef":
            reset_local_graph()
        st.rerun()

with cols[2]:
    if st.button("Explore a demo instance 🙂",type = st.session_state["hademo"], on_click=clear_explanation):
        if st.session_state["hademo"] == "secondary":
            st.session_state["hanormal"] = "secondary"
            st.session_state["hademo"] = "primary"
        else:
            clear_preferences()
            st.session_state["hanormal"] = "primary"
            st.session_state["hademo"] = "secondary"
        st.rerun()

B1 = st.session_state["hanormal"]
B2 = st.session_state["hademo"]

if B1 == "primary":
    ha_xai_nodemo()
else:
    ha_xai_demo()


