import streamlit as st
import base64
st.set_page_config(
    page_title="ExFaMa",
    page_icon=":material/accessibility:",
)

st.title("ExFaMa: Explaining Fair Matchings")

st.session_state["opened_ha"] = False 
st.session_state["opened_ha"] = False

st.write("This app proposes to explain the fairness or the absence of fairness, in matching under preferences.")

for _ in range(4):
    st.write("\n")
st.subheader("*Two matching settings:*")

st.session_state["opened_ha"] = False 
st.session_state["opened_ha"] = False

doc = "👨‍⚕️"
b = "👶️"
f = "👩🏻"
d ="🐶️"

bib ="🍼️"
os="🦴️"
ste = "🩺️"
ca = "🎧️"

def pref_rom():
    # <!-- Position 1: Top (0°) -->
    one = "👨‍🔬"

    # <!-- Position 2: Top-right (45°) -->
    two = "🧑🏻"

    # <!-- Position 3: Right (90°) -->
    tre = "👶"

    # <!-- Position 4: Bottom-right (135°) -->
    fore = "👩‍🦱"

    # <!-- Position 5: Bottom (180°) -->
    fiv = "👨"

    # <!-- Position 6: Bottom-left (225°) -->
    si = "🧑🏽‍🦱"

    # <!-- Position 7: Left (270°) -->
    se = "👩🏻"

    # <!-- Position 8: Top-left (315°) -->
    ei = "👨‍💼"
    from random import shuffle 
    li = [one,two,tre,fore,fiv,si,se,ei]
    for agent in li:
        lip = li[:]
        lip.remove(agent)
        shuffle(lip)
        st.write(f"$ {agent}: "+  "\succ".join(lip) + "$")

    st.write("Example Preferences")
    st.html("<p style=\"font-size: 20px;\">👨‍⚕️: 🧑🏻≻👩‍🦱≻👶≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️</p>" )
    st.html("<p style=\"font-size: 20px;\">🧑🏻: 👩🏻≻👩‍🦱≻👶≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️</p>" )
    st.html("<p style=\"font-size: 20px;\">👶: 👩🏻≻👩‍🦱≻👶≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️</p>" )
    st.html("<p style=\"font-size: 20px;\">👩‍🦱: 👩🏻≻👩‍🦱≻👶≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️</p>" )
    st.html("<p style=\"font-size: 20px;\">👨: 👩🏻≻👩‍🦱≻👶≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️</p>" )
    st.html("<p style=\"font-size: 20px;\">🧑🏽‍🦱: 👩🏻≻👩‍🦱≻👶≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️</p>" )
    st.html("<p style=\"font-size: 20px;\">👩🏻: 👩🏻≻👩‍🦱≻👶≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️</p>" )
    st.html("<p style=\"font-size: 20px;\">👨‍💼: 👩🏻≻👩‍🦱≻👶≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️≻👨‍⚕️</p>" )
    st.markdown(f"$ {one} ≻: \quad {two} \succ {fiv} \succ {se} \succ {fore} \succ {tre} \succ {ei} \succ {si}$")

settings = st.columns(2)
with settings[0]:
    st.subheader("Roommate Matching")
    #st.write("Agents are matched with each other in pairs, and have preferences on which other agents they would like to be matched with.")
    st.write("The goal is to form pairs of agents according to the agents' ordinal preferences over the other agents.")
    #st.image("assets/srp_ok.png")
    st.image("assets/rm.png")
    # pref_rom()

with settings[1]:
    st.subheader("House Allocation")
    #st.write("Agents are assigned objects, and have a preference for every object. We only consider the setting where there are as many objects as there are agents.")
    st.write("The goal is to assign one item to each agent according to the agents' ordinal preferences over the items.")
    st.image("assets/housealloc.png")

for _ in range(4):
    st.write("\n")
#st.write("Two fairness metrics are also considered")
st.subheader("*Two fairness criteria:*")
fairness = st.columns(2)

with fairness[0]:
    st.subheader("Rank envy-freeness")
    #st.write("The general metric of envy-fairness states that for every agent in a matching, they should prefer their own assignment over everybody's other. However this is not always possible. With _rank envy-freeness_ we consider there is no envy if an agent prefer's somebody's else assignment, but ranks them worse than the other agent does.")
    st.write("No agent A should prefer the assignment of another agent B whereas A ranked that element better than B did.")

with fairness[1]:
    st.subheader("Local envy-freeness")
    st.write("Given a social network representing the visibility connections among the agents, no agent should prefer the assignment of an agent who is visible to them.")
    #"With _local envy-freeness_, we strictly require every agent to prefer their assignment over anybody else's. However agents are placed in a social network, and only care about agents with whom they are connected in the network. In this way, if an agent they are not connected with has an assignment they prefer, it does not generate envy.")

st.session_state["opened_srp"] = False 
st.session_state["opened_ha"]  = False

NAMES = ["Luc","Ana","Paul","Lea","Tom","Julie","Max","Laure","Hugo","Alice"]

# pg = st.navigation([

#     st.Page("pages/roommate_xai.py", title="First page", icon="🔥"),
# #     st.Page(page2, title="Second page", icon=":material/favorite:"),
# ])
# pg.run()


st.sidebar.success("Please select a setting above.")



def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
    

logocs = img_to_base64("assets/centrale_logo.png")
logoapp = img_to_base64("assets/applepie_logo.png")
logomics = img_to_base64("assets/mics_logo.png")

footer = f"""
<style>
.footer {{
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f0f2f6;
    color: #333333;
    border-top: 1px solid #e0e0e0;
    z-index: 9999;
}}

.footer-inner {{
    max-width: 1100px;        /* matches Streamlit content width */
    margin: 0 auto;          /* centers horizontally */
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}}

.footer-left {{
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}}

.footer a {{
    color: #0066cc;
    text-decoration: none;
}}

.footer a:hover {{
    text-decoration: underline;
}}

.footer-right {{
    display: flex;
    align-items: center;
    gap: 15px;
}}

.footer-right img {{
    height: 45px;
    width: auto;
}}

.footer-left img {{
    height: 45px;
    width: auto;
    cursor: pointer;
    transition: opacity 0.3s ease;
}}

.footer a:hover img {{
    opacity: 0.8;
}}
</style>

<div class="footer">
    <div class="footer-inner">
        <div class="footer-left">
            <a href="mailto:francesco.sabatino@centralesupelec.fr">Contact</a><!-- |
            <a href="https://www.your-university.edu" target="_blank">Your University</a> |
            <a href="about">About</a>-->
            | <a href="https://www.mics.centralesupelec.fr" target="_blank"><img src="data:image/png;base64,{logomics}"></a>
            | <a href="https://www.centralesupelec.fr" target="_blank"><img src="data:image/png;base64,{logocs}"></a>
            | <a href="https://anaellewilczynski.pages.centralesupelec.fr/anr-apple-pie/" target="_blank"><img src="data:image/png;base64,{logoapp}"></a>
            | <span>Developed by Francesco Sabatino, supervised by Wassila Ouerdane and Anaëlle Wilczynski</span>
        </div>
        <!--
        <div class="footer-right">
            <img src="data:image/png;base64,{logocs}">
            <img src="data:image/png;base64,{logoapp}">
            <img src="data:image/png;base64,{logomics}">
        </div>-->
    </div>
</div>
"""


st.html(footer)

