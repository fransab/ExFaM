import streamlit as st 
from .roommate_sat import retrieve_mus
from .sequential_al_graph import Seq as Expl
from .explain_mus import SAT_Imp_Graph
from .display import gendic, displayDic
from .tools import order_agent_expl

from copy import deepcopy as copy

def srp_globalxp(F):
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

    text = copy(s.text)
    del text[0]

    if s is not None:
        text[0]+= " We will show that this is not possible."

    
    if st.button("Why?"):

        st.session_state.current_explanation = gendic(text, st.session_state["n"])
        st.session_state.current_preferences = F.p

        order_agent_expl(st.session_state.current_explanation)
        # raise ValueError
        # Il y a des pbs avec > 1 clause AL. 
        # Prendre une instance ou il y a un pb, voir c'est quoi avec spyder et corriger ça 
        # Attention c'est pt un probleme de gendic
        # Faire gaffe aussi aux maj genre parfois explication est pas mise a jour 

    if st.session_state.current_explanation is not None:
        container = st.container(border = True)
        with container:
            displayDic(st.session_state.current_explanation, st.session_state.current_preferences)