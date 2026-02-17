import streamlit as st
from pages.roommate_funcs.tools import clear_explanation

def load_lef_sat(**kwargs):
    st.session_state["n"] = 4
    p =  [['A', 'B', 'D', 'C'], ['B', 'A', 'D', 'C'], ['D', 'C', 'A', 'B'], ['C', 'B', 'D', 'A']]
    g = {0: [2, 3], 1: [0, 2, 3], 2: [0, 1, 3], 3: [0]}
    for agent in range(4):
        for _rank in range(4):
            st.session_state[f"pref_{agent}_{_rank}"] = p[agent][_rank] 
    st.session_state["G"] = g

def load_lef_unsat():
    st.session_state["n"] = 4
    p =  [['D', 'C', 'A', 'B'], ['D', 'B', 'A', 'C'], ['C', 'A', 'D', 'B'], ['B', 'D', 'C', 'A']]
    g = {0: [1, 2, 3], 1: [0, 3], 2: [3], 3: [0, 2]}
    for agent in range(4):
        for _rank in range(4):
            st.session_state[f"pref_{agent}_{_rank}"] = p[agent][_rank] 
    st.session_state["G"] = g

def load_ref_sat(): 
    st.session_state["n"] = 4
    p = [['A', 'B', 'D', 'C'], ['A', 'C', 'D', 'B'], ['A', 'C', 'B', 'D'], ['B', 'D', 'A', 'C']]
    for agent in range(4):
        for _rank in range(4):
            st.session_state[f"pref_{agent}_{_rank}"] = p[agent][_rank] 

def load_ref_unsat():
    st.session_state["n"] = 4
    st.session_state[f"pref_0_0"] = -2

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


def ha_xai_demo():
    from pages.ha_funcs.prefs_ha import prefprofile_ha
    from pages.ha_funcs.lef import FormulaHA,solve, get_matching,get_all_matchings
    from pages.ha_funcs.local_graph import local_graph
    from pages.ha_funcs.ha_globalxp import ha_globalxp
    from pages.ha_funcs.ha_localxp import ha_localxp
    from pages.roommate_funcs.tools import clear_explanation ,p_is_complete
    from pages.ha_funcs.tools import clear_matching, clear_preferences, reset_global

    agents = st.session_state.agents 
    objects = st.session_state.objects

    crit = st.session_state["fair_crit"]
    
    cols = st.columns(3)
    with cols[1]:
        old = st.session_state.get("demo_choice",None)
        choice = st.radio("Choose a demo", ["sat", "unsat"], format_func=radio_label, horizontal=True, key = "demo_choice",
                           on_change=reset_global)
        if choice != old:
            st.rerun()


    # random.seed(100)

    if st.session_state.pref_0_0 == -2:
        st.info('In House Allocation, a rank-envy-free matching always exists!', icon="ℹ️")
        return

    if choice == "sat":
        st.info('With these preferences, it is possible to make a fair allocation. Later we can let users challenge it if they are not satisfied with their assignment.', icon="ℹ️")
    else:
        st.info('With these preferences, it is impossible to make a fair allocation. We can find out why in the next step.', icon="ℹ️")

    p = prefprofile_ha(agents, objects, demo = True)

    g = None
    if crit == "lef":
        g= local_graph(agents, demo = True)

    if not p_is_complete(p):
        st.info("Please provide full preferences")
    else:
        # if st.button("Explain"):

        F = FormulaHA(agents, objects, p, g,crit)
        g = solve(F)
        if g.status:

                fairm = get_matching( F, g.get_model() )
                st.session_state["fairm"] = fairm

                st.info("In the next step, users can challenge the matching to try to get a better allocation.",icon="ℹ️")
                ha_localxp()

        else:
            st.error("There is no fair allocation.")
            ha_globalxp(F)
