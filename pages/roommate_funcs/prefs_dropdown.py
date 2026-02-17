import streamlit as st 
from .tools import p_is_complete, retrieve_preferences, clear_explanation, reset_agent_preferences, load_random
from pages.ha_funcs.tools import rename, agent_name,clear_matching
def get_available_options(agent, position, agents):
    """Get available options for a specific agent at a specific position"""

    selected_by_agent = set()
    for i in range(len(agents) - 1):
        if i != position:  # Don't include current position
            value = st.session_state.get(f"pref_{agent}_{i}")

            if value is not None:
                selected_by_agent.add(value)
    
    # Available options are all agents except self and already selected
    available = [ag for ag in agents if ag != agent and ag not in selected_by_agent]
    
    return available


def prefprofile_using_dropdown(agents, demo = False):
    for agent in agents:
        if f"pref_{agent}_{len(agents)-2}" not in st.session_state:
            reset_agent_preferences([agent], agents)
        # Create columns: agent label + (n-1) dropdowns with separators + reset button
        n_prefs = len(agents) - 1
        # Column layout: [agent_label, dropdown, succ, dropdown, succ, ..., dropdown, reset_button]
        col_widths = [1] + [1, 0.2] * n_prefs + [1]
        cols = st.columns(col_widths)
        
        # Agent label
        with cols[0]:
            st.write(rename(f"**Agent {agent}:**"))

        # Dropdown selectors with separators
        for i in range(n_prefs):
            dropdown_col_idx = 1 + (i * 2)
            separator_col_idx = dropdown_col_idx + 1
            
            with cols[dropdown_col_idx]:
                # Get available options
                available = get_available_options(agent, i, agents)
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
                        on_change=clear_explanation,
                        format_func=agent_name,
                        disabled = demo,

                    )
                else:
                    st.write("—")
            
            # Separator (preference symbol)
            if i < n_prefs - 1:  # Don't show after last preference
                with cols[separator_col_idx]:
                    st.markdown("$\\succ$")
        
        # Reset button
        with cols[-1]:
            st.button("Reset", key=f"reset_{agent}", on_click = reset_agent_preferences, args=([agent],agents))

    st.button("Reset all", key="reset_all", on_click = reset_agent_preferences, args=(agents,agents),  type="primary")

    if not "srpdemo" in st.session_state or st.session_state.srpdemo == "secondary":
        st.button("Generate random", key = "random_srp", on_click = lambda: (load_random(), clear_matching()))

    p = [[st.session_state[f"pref_{agent}_{i}"] for i in range(len(agents)-1)] for agent in agents]

    st.session_state["profile_reloaded"] = True

    return [[-1 if x is None else x for x in row] for row in p]
