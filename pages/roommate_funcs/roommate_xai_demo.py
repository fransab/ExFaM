import streamlit as st
from pages.roommate_funcs.tools import clear_explanation

def load_lef_sat():
    st.session_state["n"] = 6
    p = ((3, 2, 4, 1, 5), (2, 0, 5, 4, 3), (4, 1, 3, 0, 5), (0, 5, 1, 2, 4), (5, 0, 3, 2, 1), (4, 2, 0, 1, 3))
    g = {0: [1, 5], 1: [0, 4, 5], 2: [0, 1, 3, 4], 3: [2, 4, 5], 4: [0, 1, 3, 5], 5: [0, 1]}
    for agent in range(6):
        for _rank in range(5):
            st.session_state[f"pref_{agent}_{_rank}"] = p[agent][_rank] 
    st.session_state["G"] = g

def load_lef_unsat():
    st.session_state["n"] = 6
    p = ((2, 5, 1, 3, 4), (3, 5, 2, 0, 4), (5, 3, 0, 1, 4), (4, 5, 0, 2, 1), (0, 1, 3, 2, 5), (0, 1, 2, 3, 4))
    g = {0: [1,2,4,5], 1:[2,3,5], 2:[0,4,5], 3:[0,1,2,4,5], 4:[0,1,3], 5:[0,1,2,3]}

    for agent in range(6):
        for _rank in range(5):
            st.session_state[f"pref_{agent}_{_rank}"] = p[agent][_rank] 
    st.session_state["G"] = g


def load_ref_sat():
    st.session_state["n"] = 6
    satp =  ((4, 1, 5, 3, 2),(0, 2, 3, 4, 5),(4, 3, 5, 1, 0),(1, 2, 0, 4, 5),(2, 5, 1, 0, 3),(0, 1, 2, 4, 3))
    for agent in range(6):
        for _rank in range(5):
            st.session_state[f"pref_{agent}_{_rank}"] = satp[agent][_rank] 

def load_ref_unsat():
    st.session_state["n"] = 6
    unsatp =  ((5, 3, 1, 4, 2),(0, 3, 2, 5, 4),(1, 4, 3, 5, 0),(2, 4, 1, 0, 5),(0, 5, 2, 1, 3),(3, 4, 2, 1, 0))
    for agent in range(6):
        for _rank in range(5):
            st.session_state[f"pref_{agent}_{_rank}"] = unsatp[agent][_rank] 

def radio_label(label): # Display chose of demo by user
    if label == "sat":
        return "I want to see a fair matching!"
    elif label == "unsat":
        return "I want to see an instance with no fair matching!"
    raise ValueError("Option not understood")
def load_correct_instance():
    crit = st.session_state.get("fair_crit","ref")
    demo = st.session_state.get("demo_choice","sat")

    if crit == "lef" and demo == "sat":
        load_lef_sat() 
    elif crit == "lef" and demo == "unsat":
        load_lef_unsat()
    elif crit == "ref" and demo == "sat":
        load_ref_sat()
    elif crit == "ref" and demo == "unsat":
        load_ref_unsat()
    else:
        raise ValueError("Unknown") 


def roommate_xai_demo():
    from pages.ha_funcs.tools import clear_matching, clear_preferences, reset_global
    from pages.roommate_funcs.prefs_dropdown import prefprofile_using_dropdown as prefprofile
    from pages.roommate_funcs.cnf import FormulaSRP
    from pages.roommate_funcs.roommate_sat import solve, get_matching
    from pages.ha_funcs.local_graph import local_graph
    from pages.roommate_funcs.srp_globalxp import srp_globalxp
    from pages.roommate_funcs.srp_localxp import srp_localxp
    from pages.roommate_funcs.tools import clear_explanation ,p_is_complete, retrieve_preferences

    agents = st.session_state.agents 

    crit = st.session_state["fair_crit"]
    
    cols = st.columns(3)
    with cols[1]:
        old = st.session_state.get("demo_choice",None)
        choice = st.radio("Choose a demo", ["sat", "unsat"], format_func=radio_label, horizontal=True, key = "demo_choice",
                           on_change=reset_global)
        if choice != old:
            st.rerun()


    # random.seed(100)


    if choice == "sat":
        st.info('With these preferences, it is possible to make a fair matching. Later we can let users challenge it if they are not satisfied with their assignment.', icon="ℹ️")
    else:
        st.info('With these preferences, it is impossible to make a fair matching. We can find out why in the next step.', icon="ℹ️")

    prefprofile(agents, demo = True)

    if crit == "lef":
        local_graph(agents, demo = True)

    p = retrieve_preferences()
    if not p_is_complete(p):
        st.info("Please provide full preferences")
    else:
        # if st.button("Explain"):

        F = FormulaSRP(n = len(agents), 
                       p = p,
                       k = float("inf") if crit == "ref" else None, 
                       f = "lef" if crit=="lef" else 'res', 
                       g = st.session_state.G if crit=="lef" else None)
        g = solve(F)
        if g.status:
                fairm = get_matching( g.get_model() )
                st.session_state["fairm"] = fairm

                st.info("In the next step, users can challenge the matching to try to get a better partner.",icon="ℹ️")
                srp_localxp()

        else:
            st.error("There is no fair matching.")
            srp_globalxp(F)
