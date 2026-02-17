import streamlit as st 
from .roommate import rk_ef, rank
from .roommate_sat import get_matching, solve, get_all_matchings
from .tools import retrieve_preferences, clear_explanation, order_agent_expl, is_fair_srp, compare_matchings
from .display import display_clickable_profile_html, make_matching, gendic, displayDic
from .tests import no_better_partner
from pages.ha_funcs.tools import agent_name, rename, gen_local_xp
from pages.roommate_funcs.cnf import FormulaSRP


@st.fragment
def srp_localxp():
    # clear_explanation()

    st.session_state["it"] = 0 

    agents = st.session_state.agents
    
    fairm = st.session_state["fairm"]

    p = retrieve_preferences()
    
    if 'user_matching' not in st.session_state:
        make_matching(len(p), fairm)


    if "show_display" not in st.session_state:
        st.session_state["show_display"] = None 

    
    display_clickable_profile_html(p)


    if st.button("Make a random matching!"):
        clear_explanation()
        make_matching(len(p))
        st.rerun(scope="fragment")


    m = st.session_state.user_matching
    g=st.session_state.get("G",None)
    if len(m) < st.session_state["n"]:
        st.info("The current matching is incomplete.")
    elif is_fair_srp(m, p, g):
        st.success("The current matching is fair.")

        agent = st.selectbox("Which agent should get a better object?", options = agents, index=None, on_change=clear_explanation,format_func=agent_name)
        
        if agent != None:
            if rank(p,agent,m[agent]) == 1:
                st.write(rename(f"Agent {agent} already has their preferred object."))

            else:
                crit = st.session_state["fair_crit"]
                k,f = None,None
                if crit == "lef":
                    f = "lef"
                elif crit =="ref":
                    k = float("inf")
                    f = "res"
                F = FormulaSRP(len(agents), p, k, f, g)
                pref_clause = F.add_pref(agent, m[agent])
                if solve(F).status:
                    st.success(rename(f"Another fair matching exists where agent {agent} gets a better partner."))
                    au= [ma for ma in get_all_matchings(F) if ma != m][0]
                    st.write("For example:", au)
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
                    text = gen_local_xp(F,agent,m[agent],m)

                    if text[0] != "\n":
                        st.write(text[0])
                    else:
                        del text[0]
                        st.error(rename(f"Agent {agent} can't be fairly matched with a partner they prefer over agent {m[agent]}"))
                        st.session_state.current_explanation = gendic(text, st.session_state["n"])
                        st.session_state.current_preferences = F.p

                    if st.session_state.current_explanation is not None:
                        container = st.container(border = True)
                        with container:
                            displayDic(st.session_state.current_explanation, st.session_state.current_preferences)
                            


    else:
        st.error("The current matching is not fair")
        matching = st.session_state.user_matching 
        p = retrieve_preferences()
        graph = st.session_state.get("G",None)
        compare_matchings(matching, fairm)

        if st.button("Come back to the fair matching!"):
            make_matching(len(fairm), fairm)
            # st.rerun(scope="fragment")