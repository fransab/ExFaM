import streamlit as st
import re
import itertools
import time 
import numpy as np 
import random
import pandas as pd 

@st.fragment
def ha_xai_nodemo():
    from pages.ha_funcs.prefs_ha import prefprofile_ha
    from pages.ha_funcs.lef import FormulaHA,solve, get_matching,get_all_matchings
    from pages.ha_funcs.local_graph import local_graph, random_graph
    from pages.ha_funcs.ha_globalxp import ha_globalxp
    from pages.ha_funcs.ha_localxp import ha_localxp
    from pages.roommate_funcs.tools import clear_explanation ,p_is_complete
    crit = st.session_state.fair_crit
    agents = st.session_state.agents 
    objects = st.session_state.objects


    p = prefprofile_ha(agents, objects)


    if crit == "lef":
        local_graph(agents)



    if not p_is_complete(p):
        st.info("Please provide full preferences")
    else:
        # if st.button("Explain"):

        graph = st.session_state.get("G",None)
        F = FormulaHA(agents, objects, p, graph, f=crit)
        g = solve(F)
        if g.status:
            st.success("There is a fair matching!")
            fairm = get_matching( F, g.get_model() )
            st.session_state["fairm"] = fairm
            ha_localxp()
        else:
            st.error("There is no fair matching")
            ha_globalxp(F)
