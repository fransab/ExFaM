# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 10:15:45 2024

@author: sabatinofr
"""
import streamlit as st
import matplotlib.pyplot as plt 
import pickle
import numpy as np
from operator import mul
from functools import reduce
import os 
import re
from .roommate import rk_ef,generate_preferences,rank
from pages.ha_funcs.names import NAMES



def agent_name(i):
    # Use custom agent names if available, otherwise use default NAMES
    custom_names = st.session_state.get("custom_agent_names", None)
    if custom_names and len(custom_names) > int(i):
        return custom_names[int(i)]
    return NAMES[int(i)]

def rename(text):
    agents = st.session_state.agents
    custom_names = st.session_state.get("custom_agent_names", None)
    
    # Use custom names if available, otherwise use default NAMES
    names_to_use = custom_names if custom_names and len(custom_names) >= len(agents) else NAMES
    
    assert len(names_to_use) >= len(agents)
    for i in agents:
        pattern = rf'\b[Aa]gent\s+{i}\b|\b{i}\b'
        text = re.sub(pattern, names_to_use[i], text)
    return text

def compare_matchings(matching,fairm):
    agents = st.session_state.agents
    p = retrieve_preferences()
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
                    if agent == ob or bagent == oa:
                        continue
                    if rank(p,agent,ob) < rank(p,agent,oa) and rank(p,agent,ob) < rank(p,bagent,ob):
                        val += f" and generates envy towards agent {bagent}."
                        break
                val += "." if val[-1] != "." else ""
            else:
                val = "the same."

            text = rename(f"- Agent {agent} gets {matching[agent]} instead of {fairm[agent]}: which is {val}")
            st.write(text)


def is_ref(o,P):
    return rk_ef(o,P)
def is_lef(p, o, g):
    for agent in o:
        oa = o[agent]
        for n in g[agent]:
            on = o[n]
            if on == agent:
                continue
            if rank(p, agent, oa) > rank(p, agent, on):
                return False 
    return True 
def is_fair_srp(m, p, g=None):
    if st.session_state.fair_crit == "lef":
        if g == None:
            raise ValueError("Missing param g")
        return is_lef(g=g,p=p,o=m)
    elif st.session_state.fair_crit == "ref":
        return is_ref(o=m, P=p)
    else:
        raise ValueError("?")
    


def load_random(**kwargs):
    clear_explanation(**kwargs)
    n = st.session_state["n"] 
    p = generate_preferences(n)
    for agent in range(n):
        for _rank in range(n-1):
            st.session_state[f"pref_{agent}_{_rank}"] = p[agent][_rank] 




def read_dimacs(filename):
    """ 
    Read a file in DIMACS format. CNF or MUS
    """
    t = None
    with open(filename,"r") as file:
        t = [line.strip() for line in file]
    
    del t[0]
    cnf = [list(map(int,el.split())) for el in t]
    for el in cnf:
        el.remove(0) # Remove EOL character
    return cnf


def ordered(x,i,j):
    if j < i:
        return x[i,j]
    elif j > i:
        return x[j,i]
    else:
        raise ValueError("j cannot be equal to i")
        
        
def cnf3_vars(n):
    agents = list(range(n))
    x = np.empty(shape=(n,n))
    val = 1
    for i in agents:
        for j in agents:
            if i > j: 
                x[i,j] = val
                val += 1
            else:
                x[i,j] = None
    return x

def store_obj(obj,fname="save"):
    f = open(PICKLE_FOLDER+fname+".pkl","wb")
    pickle.dump(obj,f)
    f.close()
def load_obj(fname="save"):
    with open(PICKLE_FOLDER+fname+".pkl","rb") as f:
        return pickle.load(f) 
    
def firstel(generator):
    for el in generator:
        return el
def liproduct(li):
    """ 
    returns product of all elements in the list 
    """
    return reduce(mul,li)


def swap(tu):
    li = list(tu)
    for i in range(1,len(tu)):
        li = list(tu)
        li[i],li[i-1] = li[i-1],li[i]
        yield tuple(li) 
def pswap(p,ag):
    """ swap agents in pref profile of agent <ag> """
    agp = p[ag]
    for ap in swap(agp):
        pp = []
        for el in p[:ag]:
            pp.append(el)
        pp.append(ap)
        for el in p[ag+1:]:
            pp.append(el)
        yield tuple(pp)

def profile_valid(p):
    n = len(p)
    return all(  [ not ( len(set(p[agent])) != n-1 or agent in p[agent] ) for agent in range(n) ] )


def order_agent_expl(d):
    # iterate over a snapshot of keys to avoid runtime errors
    first = True 
    prio = None
    for key in list(d.keys()):
        keys = key.split(" ")
        if first:
            first = False 
            if keys[2] == "should":
                prio = int(keys[1])
            elif keys[1] == "avoid":
                prio = int(keys[7])
        value = d[key]
        new_key = key
        # compute the new key

        if keys[1] == "Assume":
            i,j = int(keys[3]) , int(keys[8][:-2])
            if i!= prio:
                new_key = f"- Assume agent {j} is matched with agent {i}"

        # rename key if needed
        if new_key != key:
            d[new_key] = d.pop(key)
            key = new_key  # update reference to renamed key

        # recurse if value is a dictionary
        if isinstance(value, dict):
            order_agent_expl(value)

def p_is_complete(preferences):
    if type(preferences) == dict:
        return not any([any([pref is None or pref == -1 for pref in preferences[agent]]) for agent in preferences] )
    else:
        print("complete is", any([ [any([el is None or el == -1 for  el in line])] for line in  preferences ]))
        return not any([ [any([el is None or el == -1 for  el in line])] for line in  preferences ])
def retrieve_preferences():
    n = st.session_state["n"]
    p = {}
    keys = [key for key in st.session_state if key.startswith("pref_")]
    keys.sort()

    for key in keys:
        k = st.session_state[key]
        _,i,_ = key.split("_")
        i = int(i)

        if i not in p:
            p[i] = [k]
        else:
            if len(p[i]) == n-1:
                if len(p) == n:
                    break 
                continue
            p[i].append(k)
    return p 

def clear_explanation(with_matching = True, with_prefs = False):
    """Clear the explanation when selectbox changes"""
    st.session_state.current_explanation = None
    st.session_state.current_preferences = None

    if with_prefs:
        for key in [key for key in st.session_state if key.startswith("pref")]:
            del st.session_state[key]
            print("deleted",key)

    if with_matching and "user_matching" in st.session_state:
        del st.session_state.user_matching


def reset_agent_preferences(agentlist, agents):
    """Reset all preferences for a specific agent"""
    for agent in agentlist:
        for i in range(len(agents)-1):
            st.session_state[f"pref_{agent}_{i}"] = None