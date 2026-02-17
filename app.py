import streamlit as st
NAMES  = []
st.set_page_config(page_title="My App", page_icon="✨")

pages = {
     "": 
     [st.Page("home.py", title="Home", icon="🧭")],
    "Settings": 
    [
        st.Page("pages/roommate_xai.py", title="Roommate Matching", icon="🧑‍🤝‍🧑"),
        st.Page("pages/ha_xai.py", title="House Allocation", icon="🏘️")
    ]
}


if __name__=="__main__":
    pg = st.navigation(pages)
    pg.run()