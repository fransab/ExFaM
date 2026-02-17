import streamlit as st 
from numpy import where as find
from pages.roommate_funcs.roommate_sat import retrieve_mus, get_k_from_ij
from pages.roommate_funcs.cnf import cnf3_vars
from pages.ha_funcs.sequential_al_graph_ha import Seq as Expl
from pages.ha_funcs.explain_mus_ha import SAT_Imp_Graph
from pages.roommate_funcs.display import gendic, displayDic
from pages.roommate_funcs.tools import order_agent_expl
from copy import deepcopy as copy

def ha_globalxp(F):
    st.session_state["it"] = 0

    cnf = F.cnf
    mus = retrieve_mus(cnf)

    for el in mus:
        elo = str(sorted(el))
        if elo not in F.e:
            raise ValueError("wat")

    s = Expl(SAT_Imp_Graph(mus,F), F)
    s.start()
    text = s.text 

    del text[0]

    if s is not None:
        text[0]+= " We will show that this is not possible."

    
    if st.button("Why?"):

        print("******************************")
        print("******************************")
        print("******************************")
        st.session_state.current_explanation = gendic(text, st.session_state["n"])
        st.session_state.current_preferences = F.p

        # order_agent_expl(st.session_state.current_explanation)
        # raise ValueError
        # Il y a des pbs avec > 1 clause AL. 
        # Prendre une instance ou il y a un pb, voir c'est quoi avec spyder et corriger ça 
        # Attention c'est pt un probleme de gendic
        # Faire gaffe aussi aux maj genre parfois explication est pas mise a jour 

    if st.session_state.current_explanation is not None:
        container = st.container(border = True)
        with container:
            displayDic(st.session_state.current_explanation, st.session_state.current_preferences)
