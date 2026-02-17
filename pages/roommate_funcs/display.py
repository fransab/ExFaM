import streamlit as st 
from .roommate import rank, generate_preferences, random_matching
from .tools import clear_explanation
from pages.ha_funcs.tools import rename


def prefprofile_style():
    circle_style = """
    <style>
    .partner-agent {
        display: inline-block;
        border: 2px solid red;
        border-radius: 50%;
        padding: 2px 8px;
        margin: 0 2px;
    }

    .normal-agent {
        display: inline-block;
        border: 2px solid white;
        border-radius: 50%;
        padding: 2px 8px;
        margin: 0 2px;
    }

    .gray-agent {
        display: inline-block;
        border: 2px solid white;
        border-radius: 50%;
        padding: 2px 8px;
        margin: 0 2px;
        color: lightgray;
    }

    .bold-agent {
        display: inline-block;
        border: 2px solid white;
        border-radius: 2px;
        padding: 4px 6px;
        margin: 0 2px;
        color: lightgray;
        background-color: #3a3a3a
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
    """
    return circle_style

def display_preference_with_circles(preferences, cur_agent, partner=None, highlights={}):
    """
    Display a preference list with red circles around specified agents.
    
    Parameters:
    -----------
    P : list of lists
        A preference profile. 
    highlights : list, optional
        List of ranks to highlight, [1,...,n-1]
    partner: int 
        Agent <cur_agent> is matched with in the current matching

    Returns:
    --------
    str : HTML string for st.markdown
    """
    
    # Build the HTML
    html_parts = ['<div style="font-size: 18px;">']
    firstline = f'<span class="agent-label">Agent {cur_agent}:</span>' 

    html_parts.append(rename(firstline))

    for rank, agent in enumerate(preferences):
        if highlights == {}:
            if agent == partner:
                line = f'<span class="partner-agent">{agent}</span>'
            else:
                line = f'<span class="normal-agent">{agent}</span>'
        else:
            if rank+1 == highlights[0]:
                line = f'<span class="bold-agent">{agent}</span>'
            elif rank+1 < highlights[0]:
                line = f'<span class="normal-agent">{agent}</span>'
            else:
                line = f'<span class="gray-agent">{agent}</span>'
        
        html_parts.append(rename(line))
        
        # Add arrow if not the last element
        if rank < len(preferences) - 1:
            html_parts.append('<span class="preference-arrow">≻</span>')
    
    html_parts.append('</div>')
    return ''.join(html_parts)


def display_full_profile(P, highlights={},matching={}):
    """
    Display a full preference profile with optional highlights.
    
    Parameters:
    -----------
    profile : dict
        Dictionary mapping agent names to their preference lists
        e.g., {'Agent 1': ['x', 'y', 'z'], 'Agent 2': ['z', 'x', 'y']}
    highlights : dict, optional
        Dict of the type [ i:  [1,2...] ... ] => highlight 1st  and 2nd preferred agents of agent <i> 
    m : dict, optional 
        Partial or full matching {a:b,...} to show with a red circle 
    """

    fulltext = []
    fulltext.append( prefprofile_style() )

    for ag in range(len(P)):
        if not (ag in highlights or ag in matching):
            continue
        partner = None 
        highlight = {}
        if ag in matching:
            partner = matching[ag]
        if ag in highlights:
            highlight = highlights[ag]
        html = display_preference_with_circles(P[ag], ag, partner, highlight)
        fulltext.append( html )

    return "<br>".join(fulltext)

@st.dialog("Detailed explanation")
def provide_ex(texts, prof):
    for el in texts:
        st.write(el)
    st.markdown( prof, unsafe_allow_html=True )





def isatleast(te):
    return "at least" in te
def isatmost(te):
    return "cannot be matched to both" in te 
def isrkres(te):
    return te.startswith("To avoid envy on") and not "object" in te
def islef(te):
    if not (te.startswith("To avoid envy on") and "object" in te):
        return False 
        
    if te.endswith("requirement.\n"):
        return -1
    
    i = te.index("{")

    return len(eval(te[i:-2]))
    
def isassume(te):
    return te.startswith("Assume")
def lenrkresset(te):
    if not isrkres(te):
        raise ValueError("Not a rkef res clause")
    if "However, no other agent satisfies that requirement." in te:
        return 0
    i = te.index("one among:") + 10 

    return len(eval(te[i:-2]))
def ispref(te):
    if te.endswith("over their previous assignment."):
        print("all good !")
    else:
        print("no good :( )")
    return te.endswith("over their previous assignment.\n")
def retrieve_info_rkres_empty(text):
    tab = text.split(" ")
    i,j,p = int(tab[5][:-1]), int(tab[7]), tab[15][:-1]
    if p == "prefe":
        p = tab[17][:-1]
    return i,j,p
def retrieve_info_rkres_notempty(text):
    i,j,p = retrieve_info_rkres_empty(text)
    te = text[ text.index("one among:")+10 : -1 ]
    if te[-1] == ".":
        te = te[:-1]
    _set = eval(te)
    return i,j,p,_set
def firstkey(dic):
    return next(iter(dic))
def lastkey(dic):
    return next(reversed(dic))



def completedic(dic,n): # If a dictionary contains an explanation that is complete i.e. no missing steps
    first = firstkey(dic)
    if isatleast(first):
        if "opened_srp" in st.session_state and st.session_state["opened_srp"]:
            return len(dic) == n
        else: 
            return len(dic) == n+1
    if isrkres(first) and (len(dic) < lenrkresset(first) + 1 or len(dic)==1):
        return False
    if ispref(first): # and not len(dic) == st.session_state["lenpref"]: 
        # it should never be complete in avoid to avoid it being removed from the stack
        return False
    if islef(first) and (len(dic) < islef(first) + 1 or len(dic)==1):
        return False

    print("dic")
    print(dic.keys())
    print("is complete")
    return True

def gendic(text,n):
    stack = [{}]
    print("*******************")
    print(text)
    for _ in range(4):
        print("*******************")

    
    for line in text:
        cur = stack[-1]
        print(line)
        if isassume(line):
            print("is assume")
            line = "- " + line
            cur[line] = {} 
            # if len(cur) > 0:
            #     last_key = lastkey(cur)
            #     cur[last_key][line] = {}
            # else:
            #     # If current dict is empty, add directly
            #     cur[line] = {}
            print("stack is")
            print(stack[-1])

        if isatleast(line) or (isrkres(line) and lenrkresset(line)>0) or ispref(line) or islef(line) > 0:
            print("is at least")
            stack.append({line:{}})
            print("stack is")
            print(stack[-1])

        if isatmost(line) or isrkres(line) and lenrkresset(line)==0 or islef(line)==-1:
            print("is stop")

            if line != "Contradiction":
                cur[lastkey(cur)] = {line:{}}
                print("line will be put to ",lastkey(cur))

            print("stack is")
            print(stack[-1])
            print("keys are")
            stack[-1].keys()
            while completedic(cur,n) and len(stack) > 2:
                lastdic = stack.pop()
                print("after pop stack is")
                print(stack[-1])
                k = lastkey( stack[-1] )
                stack[-1][k] = lastdic 
                cur = stack[-1]
                print("scaled one")
            print("now stack is")
            print(stack[-1])
        print("====================")




    return stack[1]


def gen_expprof(text,P):
    print("===================")
    print("text is")
    print(text)
    print("P is")
    print(P)
    if isrkres(text) or islef(text):
        if isrkres(text):
            print("isrkres")
            if lenrkresset(text) == 0:
                print("is empty")
                i,j,p = retrieve_info_rkres_empty(text)
                print("ijp are")
                print(i, j, p)
                # expl = f"We see that agent {j} ranks agent {p} better than agent {i} does, so they should have a partner they prefer over {p}, which is impossible since it is already their first choice."
                expl = f"Agent {i} is matched with agent {p}, even though agent {j} ranks {p} better than {i} does. So agent {j} should have an agent they prefer over {p}, which is impossible since they are their first choice."
            else:
                print("is not empty")
                i,j,p,s = retrieve_info_rkres_notempty(text)
                expl = f"Agent {i} is matched with agent {p}, even though agent {j} ranks {p} better than {i} does. So agent {j} should have an agent they prefer over {p}."
        else:
            print("is lef")
            i,j,p = retrieve_info_rkres_empty(text)
            if p[-1] == ".":
                p = p[:-1]


            if islef(text) == -1:
                expl = f"Agent {i} is given object {p}, even though agent {j} ranks {p} better than {i} does. So agent {j} should have an object they prefer over {p}, which is impossible since it is their first choice."
            else:
                expl = f"Agent {i} is matched with agent {p}, even though agent {j} ranks {p} better than {i} does. So agent {j} should have an agent they prefer over {p}."

        val = "pressed_" + str(st.session_state["it"])
        btnkey = 'button_' + str(st.session_state["it"])

        if not val in st.session_state:
            st.session_state[val] = False

        if st.button("Check",key = btnkey ):
            st.session_state[val] = True

        if st.session_state[val]:
            expl = rename(expl)
            if st.session_state.opened_srp:
                p = int(p)
            else:
                p = str(p)
            provide_ex([expl], display_full_profile(P, highlights={j:[rank(P,j,p)]}, matching={i:p}))

            st.session_state[val] = False

        st.session_state["it"] += 1


def displayDic(dico, preferences):
    if dico == {}:
        return 

    for el in dico:
        st.markdown(rename(el))

        gen_expprof(el, preferences)

        if dico[el] != {}:
            with st.expander("Why is that not possible ?"):
                displayDic(dico[el], preferences)



def is_matched(agent):
    if not agent in st.session_state.user_matching or st.session_state.user_matching[agent] is None:
        return False 
    return True 

def make_matching(n,o = None):
    if 'user_matching' not in st.session_state:
        st.session_state.user_matching = {}

    if o is None:
        o = random_matching(n)
    for i in o:
        st.session_state.user_matching[i] = o[i]
def rerunfragment():
    st.rerun(scope="fragment")

def display_clickable_profile_html(P):
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
    
    # Display each agent's preferences with buttons
    for agent_idx in range(len(P)):
        # st.markdown(f'<span class="agent-label">Agent {agent_idx}:</span>', unsafe_allow_html=True)
        
        col_widths = [2] + [1, 0.5] * (len(P)-1) + [2]
        cols = st.columns(col_widths)

        with cols[0]:
            text = f"**Agent {agent_idx}:**"
            text = rename(text)
            st.write(text)
        
        for rank, other_agent in enumerate(P[agent_idx]):
            ag_col_id = 1 + rank*2
            ag_col_sep = ag_col_id + 1
            with cols[ag_col_id]:
                is_partner = st.session_state.user_matching.get(agent_idx) == other_agent

                if is_matched(other_agent) or is_matched(agent_idx):
                    btn_label = f":grey[{rename(str(other_agent))}]" #Keep rename here bc  doesn't work else
                else:
                    btn_label = "__"+rename(str(other_agent))+"__"

                if st.button(
                    btn_label,
                    key=f"click_{agent_idx}_{other_agent}",
                    type="primary" if is_partner else "secondary",
                    on_click=clear_explanation,kwargs={"with_matching":False}
                ):

                    # Toggle matching
                    if is_partner:
                        del st.session_state.user_matching[agent_idx]
                        del st.session_state.user_matching[other_agent]
                    else:
                        # Clear old matchings
                        if agent_idx in st.session_state.user_matching:
                            old = st.session_state.user_matching[agent_idx]
                            if old in st.session_state.user_matching:
                                del st.session_state.user_matching[old]
                        if other_agent in st.session_state.user_matching:
                            old = st.session_state.user_matching[other_agent]
                            if old in st.session_state.user_matching:
                                del st.session_state.user_matching[old]

                        
                        # Set new matching
                        st.session_state.user_matching[agent_idx] = other_agent
                        st.session_state.user_matching[other_agent] = agent_idx
                    # st.rerun()
                    rerunfragment()
            
            if rank < len(P[agent_idx]) - 1:
                with cols[ag_col_sep]:
                    st.markdown("≻")
    
    return st.session_state.user_matching