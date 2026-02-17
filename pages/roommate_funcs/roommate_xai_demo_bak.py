import streamlit as st
from pages.roommate_funcs.tools import load_random
from pages.roommate_funcs.tools import clear_explanation
from pages.ha_funcs.local_graph import local_graph

def load_unsat(**kwargs):
    clear_explanation(**kwargs)
    st.session_state["n"] = 6
    unsatp =  ((5, 3, 1, 4, 2),(0, 3, 2, 5, 4),(1, 4, 3, 5, 0),(2, 4, 1, 0, 5),(0, 5, 2, 1, 3),(3, 4, 2, 1, 0))
    for agent in range(6):
        for _rank in range(5):
            st.session_state[f"pref_{agent}_{_rank}"] = unsatp[agent][_rank] 

def load_sat(**kwargs):
    clear_explanation(**kwargs)
    if "n" in st.session_state:
        del st.session_state["n"]
    st.session_state["n"] = 6
    satp =  ((4, 1, 5, 3, 2),(0, 2, 3, 4, 5),(4, 3, 5, 1, 0),(1, 2, 0, 4, 5),(2, 5, 1, 0, 3),(0, 1, 2, 4, 3))
    for agent in range(6):
        for _rank in range(5):
            st.session_state[f"pref_{agent}_{_rank}"] = satp[agent][_rank] 


def radio_label(label): # Display chose of demo by user
    if label == "sat":
        return "I want to see a fair matching!"
    elif label == "unsat":
        return "I want to see an instance with no fair matching!"
    raise ValueError("Option not understood")
def load_correct_instance():
    crit = st.session_state.get("fair_crit","ref")
    demo = st.session_state.get("demo_choice","sat")

    if demo == "sat":
        load_sat(with_matching=False)
    else:
        load_unsat(with_matching=False)
def roommate_xai_demo():
    
    from pages.roommate_funcs.roommate_sat import solve ,get_matching 
    from pages.roommate_funcs.cnf import FormulaSRP

    
    from pages.roommate_funcs.srp_globalxp import srp_globalxp
    from pages.roommate_funcs.srp_localxp import srp_localxp
    from pages.roommate_funcs.tools import retrieve_preferences, p_is_complete, clear_explanation
    from pages.roommate_funcs.prefs_dropdown import prefprofile_using_dropdown


    st.set_page_config(page_title="Roommate Matching XAI", page_icon=":material/person_book:", layout="wide")


    cols = st.columns(3)
    with cols[1]:
        choice = st.radio("Choose a demo", ["sat", "unsat"], format_func=radio_label, horizontal=True, key = "demo_choice", on_change=load_correct_instance)


    st.session_state["it"] = 0 # To fix widgets IDs bc of reruns when clicking buttons

    # Initialize session state at the top

    if 'current_explanation' not in st.session_state:
        st.session_state.current_explanation = None
    if 'current_preferences' not in st.session_state:
        st.session_state.current_preferences = None

    agents = st.session_state.agents

    if choice == "sat":
        st.info('With these preferences, it is possible to make a fair matching. Later we can let users challenge it if they are not satisfied with their partner.', icon="ℹ️")
    else:
        st.info('With these preferences, it is impossible to make a fair matching. We can find out why in the next step.', icon="ℹ️")

    pdd = prefprofile_using_dropdown(agents, demo = True)

    if st.session_state.fair_crit ==  "lef":
        local_graph(agents,demo=True)
    

    p = retrieve_preferences()

    if not p_is_complete(p):
        st.error("Please fill the preferences before proceeding.")

    else:
        cnfr = FormulaSRP(len(p), p,float("inf"),"res")
        g = solve(cnfr)
        
        if st.button("What's the best matching?"):
            clear_explanation()
            if g.status == False:
                st.error("With these preferences, it is impossible to have a fair matching.")
                st.info("In the next step, we can use our explanation algorithm to find out why there can be no fair matching.",icon="ℹ️")
                srp_globalxp(cnfr)
            else:
                refm = get_matching( g.get_model() )
                st.session_state["refm"] = refm
                st.success("A fair matching was found!")
                st.info("In the next step, users can challenge the matching to try to get a better partner.",icon="ℹ️")
                srp_localxp()
