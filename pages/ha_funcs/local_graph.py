import streamlit as st 
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from .tools import reset_local_graph, rename, agent_name
def draw_graph(G):
    fig, ax = plt.subplots(figsize=(6, 5))

    # kamada_kawai tends to minimize edge crossings and overlaps nicely
    pos = nx.kamada_kawai_layout(G)
    pos = nx.circular_layout(G)

    border = Rectangle((-1.4, -1.4), 2.8, 2.8, 
                      fill=False, 
                      edgecolor='#e0e0e0', 
                      linewidth=3)
    ax.add_patch(border)
    m = {i:agent_name(i) for i in G.nodes}
    nx.draw(
        G, pos, ax=ax,
        labels = m,
        with_labels=True,
        node_color="#c3d8eb",
        font_color='black',
        font_weight='bold',
        edge_color='#adb5bd',
        width=1.5
    )

    ax.set_axis_off()
    ax.margins(0.05) 
    ax.autoscale_view()
    plt.tight_layout()
    st.pyplot(fig)

def random_graph(agents,p):
    return nx.erdos_renyi_graph(len(agents),p = p, directed=True)
def local_graph(agents, demo=False):
    st.markdown("""
<style>
.agent-label {
    display: flex;
    align-items: center;
    height: 100%;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)
    
    if not "G" in st.session_state:
        G = nx.DiGraph()
        G.add_nodes_from(agents)
        st.session_state["G"] = G
    elif type(st.session_state.G) == dict:
        G = nx.DiGraph()
        for x in st.session_state.G:
            G.add_edges_from([(x,y) for y in st.session_state.G[x]])
        st.session_state.G = G 
    
    G = st.session_state.G

    cols_a = st.columns(3)
    with cols_a[1]:
        if demo:
            st.info('Here you can choose how agents perceive each other. Agents will not be envious of agents they can\'t see', icon="ℹ️")
    with cols_a[0]:
        st.write("Below, you can input the social network for the agents.")
    bigcols = st.columns( 2 )

    with bigcols[0]:
        cols = st.columns([1,3])

        for agent in agents:
            with cols[0]:
                with st.container(height = 70, vertical_alignment="center",horizontal_alignment="right", border=False):
                    text = f"Agent {agent}:"
                    text = rename(text)
                    
                    st.markdown(
                    f'<div class="agent-label">{text}</div>',
                    unsafe_allow_html=True
                )
            with cols[1]:
                with st.container(border=False, horizontal_alignment="left"):
                    choices = st.multiselect("select", 
                                label_visibility="hidden",
                                placeholder="Select visible agents",
                                default = list(G[agent]) if agent in G else None,
                                disabled=demo,
                                options=[agent2 for agent2 in agents if agent2 != agent],
                                format_func=agent_name)
                    print(G.edges)
                    if agent in G and len(G[agent]) != 0:
                        G.remove_edges_from([(agent,j) for j in G[agent]])
                    G.add_edges_from([(agent,y) for y in choices])

        st.session_state["G"] = G

    with bigcols[1]:
        draw_graph(G)


    if not demo:
        coli = st.columns(3)
        with coli[0]:
            pi = st.slider("Select the expected density of the social network",min_value=0.,max_value = 1.,step=.01,value=.5)

        
        if st.button("Generate random graph"):
            rg = random_graph(agents, pi)
            st.session_state["G"] = rg
            st.rerun(scope="fragment")

    return G