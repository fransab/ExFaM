import streamlit as st 
# from pages.roommate_funcs.roommate import rk_ef, rank
# from pages.roommate_funcs.roommate_sat import get_matching
from pages.roommate_funcs.tools import clear_explanation, order_agent_expl
from pages.roommate_funcs.display import gendic, displayDic
from pages.roommate_funcs.tests import no_better_partner
from pages.ha_funcs.prefs_ha import display_clickable_profile_html
from pages.ha_funcs.tools import is_fair_ha, make_matching, retrieve_preferences_ha, gen_local_xp, compare_matchings, rename, agent_name
from pages.ha_funcs.lef import rank, FormulaHA, solve, retrieve_mus, exists_unique_eff_matching,get_all_matchings
@st.fragment
def ha_localxp():
    # clear_explanation()

    st.session_state["it"] = 0 

    agents = st.session_state.agents
    objects = st.session_state.objects
    
    fairm = st.session_state["fairm"]

    p = retrieve_preferences_ha()
    
    if 'user_matching' not in st.session_state:
        make_matching(fairm)


    if "show_display" not in st.session_state:
        st.session_state["show_display"] = None 

    
    display_clickable_profile_html(agents, objects, P=p)


    if st.button("Make a random matching!"):
        clear_explanation()
        make_matching()
        st.rerun(scope="fragment")


    m = st.session_state.user_matching
    g=st.session_state.get("G",None)
    if len(m) < st.session_state["n"]:
        st.info("The current matching is incomplete.")
    elif is_fair_ha(m, p, g):
        st.success("The current matching is fair.")

        agent = st.selectbox("Which agent should get a better object?", options = agents, index=None, on_change=clear_explanation,format_func=agent_name)
        
        if agent != None:
            if rank(p,agent,m[agent]) == 1:
                st.write(rename(f"Agent {agent} already has their preferred object."))

            else:
                F = FormulaHA(agents, objects, p, g, st.session_state["fair_crit"])
                F.add_pref(agent, m[agent])
                if solve(F).status:
                    st.success(rename(f"Another fair matching exists where agent {agent} gets a better object."))
                    au= [ma for ma in get_all_matchings(F) if ma != m][0]
                    st.write("For example:", {rename(str(i)):au[i] for i in au})
                    compare_matchings(au, m)

                    if st.button("I prefer this new matching", type="primary"):
                        st.session_state.fairm = au
                        st.session_state.user_matching = au
                    
                    # altm = exists_unique_eff_matching(F)
                    # if altm == False:
                    #     st.write("Multiple really fair matchings")
                    #     pass
                    #     # compare_matchings(m, )
                    # else:
                    #     st.success("Alors peut etre")

                else:
                    # ça ne va jamais arriver
                    text = gen_local_xp(F=F,agent=agent,obj=m[agent])
                    st.subheader("The text")
                    st.write(text)
                    raise ValueError("Investigate")
            


    else:
        st.error("The current matching is not fair")
        matching = st.session_state.user_matching 
        p = retrieve_preferences_ha()
        graph = st.session_state.get("G",None)
        compare_matchings(matching, fairm)

        if st.button("Come back to the fair matching!"):
            make_matching(fairm)
            st.rerun(scope="fragment")