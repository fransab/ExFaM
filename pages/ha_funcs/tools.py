import streamlit as st
from pages.roommate_funcs.tools import clear_explanation
from pages.roommate_funcs.roommate_sat import retrieve_mus,solve
from pages.roommate_funcs.sequential_al_graph import Seq as Expl 
from pages.ha_funcs.explain_mus_ha import SAT_Imp_Graph
from pages.roommate_funcs.explain_mus import SAT_Imp_Graph as SATGsrp
from random import shuffle
from pages.ha_funcs.lef import is_lef, is_ref,rank
from .names import NAMES
import re
from copy import deepcopy 
def retrieve_preferences_ha():
    agents = st.session_state.agents 
    m = len(st.session_state.objects)
    p = {}
    for agent in agents:
        p[agent] = [st.session_state[f"pref_{agent}_{r}"] for r in range(m)]

    return p

def is_fair_ha(m, p, g=None):
    print("Try with m",m)
    print("p is",p)
    print("g is ",g)
    if st.session_state.fair_crit == "lef":
        if g == None:
            raise ValueError("Missing a param")
        return is_lef(g=g,p=p,o=m)
    elif st.session_state.fair_crit == "ref":
        print("using rkef")
        return is_ref(o=m, P=p)
    else:
        raise ValueError("?")
    

def make_random_matching(agents, objects):
    assert len(agents) == len(objects)
    shuffle(objects)
    return {agent:object for agent,object in zip(agents,objects)}
def make_matching(o=None):
    if "user_matching" not in st.session_state:
        st.session_state.user_matching = {}
    if o == None:
        o = make_random_matching(st.session_state.agents, st.session_state.objects)
    for a in o:
        st.session_state.user_matching[a] = o[a]


def longfaircode(short):
    if short == "ref":
        return "Rank-envy-freeness"
    if short == "lef":
        return "Local envy-freeness"
    raise ValueError("Not recognized")

def generate_preferences():
    agents = st.session_state.agents
    objects = st.session_state.objects 
    p = {}
    for agent in agents:
        shuffle(objects)
        p[agent] = [o for o in objects]
    return p


def load_random(**kwargs):
    clear_explanation(**kwargs)
    n = st.session_state["n"] 
    p = generate_preferences()
    if len(p) != n:
        return ValueError
    for agent in range(n):
        for _rank in range(n-1):
            st.session_state[f"pref_{agent}_{_rank}"] = p[agent][_rank] 

from pages.roommate_funcs.roommate_sat import get_matching
from pages.roommate_funcs.tools import compare_matchings
def gen_local_xp(F,agent,obj,m=None):
    text = None 
    F.add_pref(agent, obj)
    clause = eval([clause for clause in F.e if F.e[clause][0].startswith("PREF")][0])
    g = solve(F)
    if "opened_ha" in st.session_state and st.session_state.opened_ha:
        if g.status:
            text = [f"There exists a matching where agent {agent} has a better object, sorry!"]
        else:
            mus = retrieve_mus(F)
            s = Expl(SAT_Imp_Graph(mus,F), F)
            s.start()
            text = s.text 
    else:
        if g.status:
            # text = [f"There exists a matching where agent {agent} has a better partner, sorry !"]
            st.error("There exists an alternative matching where agent {agent} has a better partner.")
            alt = get_matching(g.get_model())
            compare_matchings(alt, m)

        else:
            print(f"{agent} should get better than {obj}")

            mus = retrieve_mus(F)
            while clause not in mus:
                G = deepcopy(F)
                altc = [musclause for musclause in mus if all([v>0 for v in musclause])][0]
                G.cnf.remove(altc)
                mus = retrieve_mus(G)
            
            print([F.e[str(clause)] for clause in mus])
            print("clause list")
            for clause in mus:
                print(clause)
                print(F.e[str(clause)] )
                print('---------')
            s = Expl(SATGsrp(mus,F), F)
            g = SATGsrp(mus,F)
            print(s.mus)
           
            s.start()

            text = s.text 
            print(text)
            print("got soemthing selse")


    return text

def compare_matchings(matching,fairm):
    agents = st.session_state.agents
    faircrit = st.session_state["fair_crit"]
    g = st.session_state.get("G",{})
    p = retrieve_preferences_ha()
    with st.container(border=True):
        for agent in agents:
            rm = rank(p,agent,matching[agent])
            rf = rank(p,agent,fairm[agent])
            val = None
            add = None 
            if rm < rf:
                val = "better."
            elif rm > rf:
                val = "worse"
                for bagent in agents:
                    oa = matching[agent]
                    ob = matching[bagent]
                    if faircrit == "lef " and bagent in g[agent] and rank(p,agent,ob) < rank(p,agent,oa) or \
                          faircrit == "ref" and rank(p,agent,ob) < rank(p,agent,oa) and rank(p,agent,ob) < rank(p,bagent,ob): 
                        val += f" and makes agent {agent} envious of agent {bagent}."
                        break
                val += "." if val[-1] != "." else ""
            else:
                val = "the same."

            text = rename(f"- Agent {agent} gets {matching[agent]} instead of {fairm[agent]}: which is {val}")
            st.write(text)


def reset_local_graph():
    if "G" in st.session_state:
        del st.session_state.G

def agent_name(i):
    # Use custom agent names if available, otherwise use default NAMES
    custom_names = st.session_state.get("custom_agent_names", None)
    if custom_names and len(custom_names) > int(i):
        return custom_names[int(i)]
    return NAMES[int(i)]

def object_name(obj):
    # Use custom object names if available, otherwise use default letter names (A, B, C, ...)
    # Handle both letter input ('A', 'B', 'C') and index input (0, 1, 2)
    if isinstance(obj, str) and len(obj) == 1 and obj.isalpha() and obj.isupper():
        # Convert letter to index
        i = ord(obj) - ord('A')
    else:
        i = int(obj)
    
    custom_objects = st.session_state.get("custom_object_names", None)
    if custom_objects and len(custom_objects) > i:
        return custom_objects[i]
    return chr(ord('A') + i)

def rename(text):
    agents = st.session_state.agents
    objects = st.session_state.get("objects", [])
    custom_agent_names = st.session_state.get("custom_agent_names", None)
    custom_object_names = st.session_state.get("custom_object_names", None)
    
    # Use custom names if available, otherwise use default NAMES
    agent_names_to_use = custom_agent_names if custom_agent_names and len(custom_agent_names) >= len(agents) else NAMES
    
    # Replace agent names
    assert len(agent_names_to_use) >= len(agents)
    for i in agents:
        pattern = rf'\b[Aa]gent\s+{i}\b|\b{i}\b'
        text = re.sub(pattern, agent_names_to_use[i], text)
    
    # Replace object names
    if custom_object_names and len(custom_object_names) >= len(objects):
        for i in range(len(objects)):
            default_letter = chr(ord('A') + i)
            pattern = rf'\b[Oo]bject\s+{default_letter}\b|\b{default_letter}\b'
            text = re.sub(pattern, custom_object_names[i], text)
    
    return text

def clear_preferences():
    mkeys = [key for key in st.session_state if key.startswith("pref_")]
    for key in mkeys:
        del st.session_state[key]
def clear_matching():
    if "user_matching" in st.session_state:
        del st.session_state.user_matching

def reset_global():
    clear_preferences()
    clear_matching()
    clear_explanation(with_matching=False)
    # Clear custom agent names if they don't match current number of agents
    if "custom_agent_names" in st.session_state:
        custom_names = st.session_state.get("custom_agent_names")
        if custom_names and len(custom_names) != st.session_state.get("n"):
            del st.session_state["custom_agent_names"]
    # Clear custom object names if they don't match current number of objects
    if "custom_object_names" in st.session_state:
        custom_objects = st.session_state.get("custom_object_names")
        if custom_objects and len(custom_objects) != st.session_state.get("n"):
            del st.session_state["custom_object_names"]
    if st.session_state.get("fair_crit",False) == "lef":
        reset_local_graph()
