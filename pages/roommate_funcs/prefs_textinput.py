import streamlit as st 


def prefprofile_using_textinput(agents, stder):
    n = len(agents)
    prefs = [[-1 for _ in range(n-1)] for agent in agents]
    widget = [[-1 for _ in range(n-1)] for agent in agents]
    for agent in agents:
        cols = st.columns([2] + [1]* (2*n-3),width = 100 * (n+1) )
        with cols[0]:
            st.write(f"Agent ${agent}$:")
        for i in range(1,2*(n-1)):
            with cols[i]:
                if i%2 != 0:
                    widget[agent][(i-1)//2] = st.text_input(
                        label=f"Pref {i+1}",
                        value = "",
                        key=f"pref_{agent}_{(i-1) // 2}",
                        label_visibility="collapsed",
                        placeholder=None,
                        width=30,
                    )
                    if widget[agent][(i-1)//2] == "":
                        prefs[agent][(i-1)//2] = -1 
                    elif not widget[agent][(i-1)//2].isnumeric():
                        prefs[agent][(i-1)//2] = widget[agent][(i-1)//2]
                    else:
                        prefs[agent][(i-1)//2] = int(widget[agent][(i-1)//2])
                else:
                    st.markdown(r"$\succ$")
    
    errs = []
    wids = []
    for agent in agents:
        if any([pref == -1 for pref in prefs[agent]]):
            errs.append(f"Agent {agent}: preference list is not complete")
        if any([prefs[agent].count(ag) > 1 for ag in agents]):
            errs.append(f"Agent {agent}: agents in {str(set([prefs[agent].count(ag) > 1 for ag in agents]))} appear multiple times in the preference list")
        if any([ag not in agents and ag != -1 for ag in prefs[agent]]):
            errs.append(f"Agent {agent}: agents in {str(set([ag for ag in prefs[agent] if ag!=-1 and ag not in agents]))} do not exist.")
        if agent in prefs[agent]:
            errs.append(f"Agent {agent}: agent appears in its own preference list")
    
    if len(errs) > 0:
        stder = st.empty()
        with stder.container():
            st.error("The current preference profile is invalid")
            with st.popover("See errors"):
                st.warning("\n\n".join(errs))
    else:
        stder = st.empty()
    return prefs
    