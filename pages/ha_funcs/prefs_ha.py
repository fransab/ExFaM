import streamlit as st 
from pages.roommate_funcs.tools import p_is_complete, retrieve_preferences, clear_explanation, reset_agent_preferences
from pages.ha_funcs.tools import rename, agent_name, object_name, clear_matching
from random import shuffle

def random_ha_prefs():
    objects = st.session_state.objects 
    agents = st.session_state.agents
    for agent in agents:
        shuffle(objects)
        for r in range(len(objects)):
            st.session_state[f"pref_{agent}_{r}"]= objects[r]

def exists(pos):
    return pos in st.session_state and st.session_state[pos] != None 

def get_available_options(agent, objects):
    """Get available options for a specific agent at a specific position"""
    selected = set([st.session_state[f"pref_{agent}_{r}"] for r in range(len(objects))])
    selected.discard(None)
    return [o for o in objects if not o in selected]

def reset_preferences_ha(agentlist, objects):
    """Reset all preferences for a specific agent"""
    for agent in agentlist:
        for r in range(len(objects)):
            st.session_state[f"pref_{agent}_{r}"] = None

def prefprofile_ha(agents,objects, demo = False):
    m = len(objects)

    if f"pref_0_{m-1}" not in st.session_state:
        reset_preferences_ha(agents,objects)

    for agent in agents:
        # Create columns: agent label + (n-1) dropdowns with separators + reset button
        
        # Column layout: [agent_label, dropdown, succ, dropdown, succ, ..., dropdown, reset_button]
        col_widths = [1] + [1, 0.2] * m + [1]
        cols = st.columns(col_widths)
        
        # Agent label
        with cols[0]:
            te = f"**Agent {agent}:**"
            te = rename(te)
            st.write(te)

        # Dropdown selectors with separators
        for i in range(m):
            dropdown_col_idx = 1 + (i * 2)
            separator_col_idx = dropdown_col_idx + 1
            
            with cols[dropdown_col_idx]:
                # Get available options
                available = get_available_options(agent, objects)
                current_value = st.session_state[f"pref_{agent}_{i}"]
                
                # If there's a current value, include it in options (even if it would normally be filtered)
                if current_value is not None and current_value not in available:
                    display_options = available + [current_value]
                else:
                    display_options = available
                
                # Determine index
                if current_value is not None and current_value in display_options:
                    default_index = display_options.index(current_value)
                elif len(display_options) > 0:
                    default_index = 0
                else:
                    default_index = 0
                

                # Create selectbox
                if len(display_options) > 0:
                    choice = st.selectbox(
                        f"Preference {i+1}",
                        options=display_options,
                        index=default_index,
                        key=f"pref_{agent}_{i}",
                        label_visibility="collapsed",
                        placeholder="",
                        disabled=demo,
                        on_change=clear_explanation,
                        format_func=object_name,
                    )
                else:
                    st.write("—")
            
            # Separator (preference symbol)
            if i < m - 1:  # Don't show after last preference
                with cols[separator_col_idx]:
                    st.markdown("$\\succ$")
        
        # Reset button
        with cols[-1]:
            st.button("Reset", key=f"reset_{agent}", on_click = reset_preferences_ha, args=([agent],agents))

    st.button("Reset all", key="reset_all", on_click = reset_preferences_ha, args=(agents,agents),  type="primary")
    if not "hademo" in st.session_state or st.session_state.hademo == "secondary":
        st.button("Generate random", key = "random_ha", on_click = lambda: (random_ha_prefs(), clear_matching()))

    p = [[st.session_state[f"pref_{agent}_{i}"] for i in range(len(agents))] for agent in agents]

    st.session_state["profile_reloaded"] = True

    return {agent:[-1 if x is None else x for x in row] for agent,row in enumerate(p)}

    



def is_assigned(object):
    for agent in st.session_state.user_matching:
        if st.session_state.user_matching[agent] == object:
            return True 
    return False 
def rerunfragment():
    st.rerun(scope="fragment")


def display_clickable_profile_html(agents, objects, P):
    """
    Display preference profile with clickable agents using HTML/CSS
    """
    if 'user_matching' not in st.session_state:
        st.session_state.user_matching = {}
    if 'clicked_agent' not in st.session_state:
        st.session_state.clicked_agent = None
    
    # Custom CSS
    st.markdown("""
    <style>
    .clickable-agent {
        display: inline-block;
        border: 2px solid white;
        border-radius: 50%;
        padding: 2px 8px;
        margin: 0 2px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .clickable-agent:hover {
        background-color: #444;
        transform: scale(1.1);
    }
    
    .matched-agent {
        display: inline-block;
        border: 2px solid #ff4b4b;
        background-color: #ff4b4b;
        border-radius: 50%;
        padding: 2px 8px;
        margin: 0 2px;
        font-weight: bold;
    }
    
    .preference-arrow {
        margin: 0 8px;
        color: #666;
    }
    
    .agent-label {
        font-weight: bold;
        margin-right: 1.5em;
    }
    </style>
    """, unsafe_allow_html=True)

    st.write()
    if "user_matching" not in st.session_state:
        st.session_state["user_matching"] = {}
    # Display each agent's preferences with buttons
    for agent_idx in agents:
        # st.markdown(f'<span class="agent-label">Agent {agent_idx}:</span>', unsafe_allow_html=True)
        
        col_widths = [2] + [1, 0.5] * len(objects) + [2]
        cols = st.columns(col_widths)

        with cols[0]:
            te = f"**Agent {agent_idx}:**" 
            te = rename(te)
            st.write(te)

        for rank, object in enumerate(P[agent_idx]):
            ag_col_id = 1 + rank*2
            ag_col_sep = ag_col_id + 1
            with cols[ag_col_id]:
                is_own = st.session_state.user_matching.get(agent_idx) == object

                if is_assigned(object) or agent_idx in st.session_state.user_matching:
                    btn_label = f":grey[{object_name(object)}]"
                else:
                    btn_label = "__"+object_name(object)+"__"

                if st.button(
                    btn_label,
                    key=f"click_{agent_idx}_{object}",
                    type="primary" if is_own else "secondary",
                    on_click=clear_explanation,kwargs={"with_matching":False}
                ):

                    # Toggle matching
                    if is_own:
                        del st.session_state.user_matching[agent_idx]
                    else:
                        for agent in st.session_state.user_matching:
                            if st.session_state.user_matching[agent] == object:
                                del st.session_state.user_matching[agent]
                                break
                        st.session_state.user_matching[agent_idx] = object
                        

                    # st.rerun()
                    rerunfragment()
            
            if rank < len(P[agent_idx]) - 1:
                with cols[ag_col_sep]:
                    st.markdown("≻")

    return st.session_state.user_matching