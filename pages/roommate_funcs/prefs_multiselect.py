import streamlit as st

def prefprofile_using_multiselect(agents):
    prefs = [[] for agent in agents]
    n = len(prefs)

    for agent in agents:
        coli  = st.columns([2] + [n], width = 100 * (n+1))
        with coli[0]:
            st.write(f"Agent ${agent}$:")
        with coli[1]:
            prefs[agent] = st.multiselect(f"Preferences for agent {agent}", options = [ag for ag in agents if ag != agent]) 
    
    return prefs