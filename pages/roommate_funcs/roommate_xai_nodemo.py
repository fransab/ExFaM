import streamlit as st
import re
import itertools
import time 
import random

@st.fragment
def roommate_xai_nodemo():
    from pages.roommate_funcs.prefs_dropdown import prefprofile_using_dropdown as prefprofile
    from pages.roommate_funcs.cnf import FormulaSRP
    from pages.roommate_funcs.roommate_sat import solve, get_matching
    from pages.ha_funcs.local_graph import local_graph
    from pages.roommate_funcs.srp_globalxp import srp_globalxp
    from pages.roommate_funcs.srp_localxp import srp_localxp
    from pages.roommate_funcs.tools import clear_explanation ,p_is_complete, retrieve_preferences
    crit = st.session_state.fair_crit
    agents = st.session_state.agents 


    prefprofile(agents)


    if crit == "lef":
        local_graph(agents)

    p = retrieve_preferences()

    if not p_is_complete(p):
        st.info("Please provide full preferences")
    else:
        # if st.button("Explain"):

        graph = st.session_state.get("G",None)

        k,f = None,None
        if crit == "lef":
            f = "lef"
        elif crit =="ref":
            k = float("inf")
            f = "res"
        F = FormulaSRP(len(agents), p, k, f, graph)
        g = solve(F)
        if g.status:
            st.success("There is a fair matching!")
            fairm = get_matching( g.get_model() )
            st.session_state["fairm"] = fairm
            srp_localxp()
        else:
            st.error("There is no fair matching")
            srp_globalxp(F)
