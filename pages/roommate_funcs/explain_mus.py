# -*- pyding: utf-8 -*-
"""
Created on Mon Mar  4 12:16:55 2024

@author: sabatinofr
"""

from pysat.solvers import Glucose3

from pysat.formula import CNF 

from pysat.examples.optux import OptUx 

from .roommate_sat import get_ij_from_k
from .roommate_sat import sort_cnf
from .tools import PICKLE_FOLDER

import matplotlib.pyplot as plt
from time import sleep
from time import perf_counter as clock
from copy import deepcopy
import networkx as nx
from itertools import product
from random import shuffle,seed,randint
import os 


class SAT_Imp_Graph:
    def __init__(self,mus,F):
        self.mus = mus 
        self.e = F.e 
        self.p = F.p
        self.g = make_satimpgraph(self.mus, self.e)
        
        self.log = {"LENGTH":-1, "DEPTH":0, "BREADTH":0, "TIME":0, "COMP":0}

        self.prunesets = []
        self.pruned = []
        self.prune = False
        
        self.show_steps = False
        self.drawpause = 0.2
        
        self.savefig = False
        self.savepath = None 
        
        self.mkrandom = True 
        self.rseed = randint( int(10e8) , int(9*10e8) )
        # print("using seed",self.rseed)

        self.controlextend = False 
        self.extend = []
        
        self.textual = False
        self.e = []
        
        self.timeout = 15



    def reset(self):
        self.prunesets = []
        self.pruned = []
        self.log = {"LENGTH":-1, "DEPTH":0, "BREADTH":0, "TIME":0, "COMP":0}
        if self.savefig: raise ValueError("Can't reset and save figure")
        
        
    def propagate(self):
        if self.savefig and not self.show_steps: raise ValueError("Les figures vont pas se voir")
        if self.savefig: self.make_savefigparams()
        t1 = clock()
        self.start = t1
        assert self.rec_propagate()
        t2 = clock()
        self.log["TIME"] = t2-t1 
        return True
    
    
    def rec_propagate(self,frontier=["T"], old_active=None, extending_vars=True, depth=0):
        if old_active is None: old_active = {node:0 for node in self.g.nodes}
       
        # if self.log["LENGTH"]%100==0 and self.timeout and clock() - self.start > self.timeout:
        #     raise RuntimeError
        
        self.log["LENGTH"] += 1
        
        active = deepcopy(old_active)
        newfrontier = []
        
        for node in frontier:
            # We are dealing with variables
            if extending_vars:
                if active[node] == 1:
                    continue
                if node == "B":
                    active["B"]= 1
                    self.log["BREADTH"] += 1
                    self.log["DEPTH"] = max(self.log["DEPTH"],depth)
                    self.log["COMP"] += 1
                    if self.show_steps: self.draw(coloring=make_color(active))
                    if self.prune     : self.build_active_tree(active)
                    if self.textual: ex=text_expl(node, self.p); self.e.append(ex)

                    return True
                
                active[node] = 1
                
                for clause in self.g.successors(node):
                    if active[clause] == 1:
                        continue
                    newfrontier.append(clause)
                    
            # We are dealing with clauses
            else:
                activate = True
                for var in self.g.predecessors(node):
                    if active[var] == 0:
                        activate = False
                        break
                if not activate: continue 
                active[node] = 1
                extend = list(self.g.successors(node))
                # if len(extend) == 1:
                #     if self.textual: ex=text_expl(node, self.p); self.e.append(ex)
                #     lasti = frontier.index(node)
                #     for i in range(lasti):
                #         active[ frontier[i] ] = 0
                #     newfrontier = extend + [el for el in frontier if el != node]
                #     extending_vars = False
                #     print(newfrontier)
                #     break
                if self.mkrandom:
                    seed(self.rseed)
                    shuffle(extend)
                newfrontier.append(extend) 

        self.log["COMP"] += len([1 for node in active if not old_active[node] and active[node]])
        if self.show_steps: self.draw(coloring=make_color(active))
                
        if self.prune:
            if any([eliciter.issubset( active_nodes(active,onlyvars=True).union(frontier) ) for eliciter in self.prunesets]):
                self.pruned.append(frontier)
                
                if self.show_steps:
                    for node in frontier:
                        active[node] = 2 
                    self.draw(coloring = make_color(active))
                    
                return True
            
        if self.mkrandom:
            seed(self.rseed)
            shuffle(newfrontier)
        
        # self.draw(coloring = make_color(active))
        

        
        if self.textual:
            new_active = {node for node in active if old_active[node]==0 and active[node]==1}
            self.e.append( text_expl(new_active, self.p) )
        
        if newfrontier == []:
            return False
        elif extending_vars: # We extended vars, so we are extending clauses 
            assert self.rec_propagate(newfrontier,active, extending_vars=False,depth=depth+1)
        else:
            if len(newfrontier[0]) > 1 and self.controlextend:
                    extend = self.extend
            else:
                extend = product(*newfrontier) 
            for alt_frontier in sorted(extend):
                assert self.rec_propagate(alt_frontier,active,extending_vars=True,depth=depth+1)  
                
        return True 
    

    def build_active_tree(self,active):
        found_new = False 
        sub = self.g.subgraph( active_nodes(active) ).copy()
        sub.remove_nodes_from( list(sub.successors("T")) )
        sub.remove_node("T")

        sub = sub.reverse()
        final = sub.subgraph(["B"] + [node for u,node in nx.bfs_edges(sub,"B")])
        # if len(list(nx.weakly_connected_components(sub))) > 1:
        #     draw_satimp(sub)
        #     draw_satimp(final)
        #     raise ValueError
        build_subsets(final)

        groups = {}
        for node in final.nodes:
            if len(final[node]) == 0:
                for group in final.nodes[node]["groups"]:
                    if not group in groups:
                        groups[group] = set([node])
                    else:
                        groups[group].add(node)

        addgroups = []                        
        for group in groups:
            if any([eliciter.issubset(groups[group]) for eliciter in self.prunesets]): continue
            addgroups.append( groups[group] )
            # self.prunesets.append(groups[group])
            found_new = True 
                
        choice = randint(0,len(addgroups)-1)
        self.prunesets.append(addgroups[choice])
        
        # print("choice proba", 1 / len(addgroups))

        return found_new

    def lead_to_unsat(self,nodes_subset):
        """ 
        check if the subset of nodes alone leads to an unsat graph
        """
        return self.propagate(self.g,frontier=nodes_subset)
            
    
    def draw(self, fancy_labels = 2,coloring=None, text = None, big = False, ratio = 1 ): 
        """ 
        fancy_labels = 0 : On garde les noms des noeuds 
        fancy_labels = 1 : noeuds variables restent en k 
        fancy_labels = 2 : tout en latex joli 
        """ 
        print("labels option",fancy_labels)
        if fancy_labels != 0:
            removevar = fancy_labels == 1
            fancy_labels = make_labels(self.g)
            if removevar:
                for node in fancy_labels:
                    if type(node)==int:
                        fancy_labels[node] = node
        else:
            fancy_labels = None
        draw_satimp(self.g, fancy_labels,coloring,self.savefig,text, big, ratio)
        sleep(self.drawpause)
        
    def showparams(self):
        print("prune",self.prune)
        print("show_steps",self.show_steps)
        print("savefig",self.savefig)
    
    def make_savefigparams(self):
        self.figcounter = 0
        path = PICKLE_FOLDER + "figures/"
        if not os.path.exists(path): raise ValueError("Il faut remettre le dossier figures")
        
        savefoldid = 0
        path += "Figures_"
        while os.path.exists(path+str(savefoldid)):
            savefoldid += 1 
        self.savepath = path + str(savefoldid) + "/" 
        os.makedirs(self.savepath)
        

def draw_satimp(g, fancy_labels = None,coloring=None,save = False,text = None,big = False,ratio = 1):
    big = True
    
    if big:
        plt.figure(figsize=(15,15))
        pos=nx.multipartite_layout(g,subset_key="level") 
        
        nx.draw_networkx(g,pos,node_color=coloring, with_labels = False ) 
        # label_pos = {node: (x, y + 0.05) for node, (x, y) in pos.items()}
        # label_pos = pos
        # nx.draw_networkx_labels(g,label_pos,fancy_labels,font_size=20)
        
        if fancy_labels != None:
            for node, (x, y) in pos.items():
                nodlbl = fancy_labels[node]
                plt.text(x, y + 0.01, nodlbl,
                        ha='center',        # horizontal alignment
                        va='center',        # vertical alignment: text appears above
                        fontsize=23)

    else:
        pos=nx.multipartite_layout(g,subset_key="level") 
        nx.draw_networkx(g,pos,node_color=coloring, labels=fancy_labels, with_labels = True ) 
        
    
    if text: 
        plt.text(-1,1,text)
    if save:
        pass # TODO: Gérer ça 
        # plt.savefig(DOWNLOAD_FOLDER+"test.png", dpi=400)
        
        # if self.savefig:
        #     fname = "fig_" + str(self.figcounter) + ".png" 
        #     plt.savefig(self.savepath+fname, dpi = 300)
        #     self.figcounter += 1
    # sf = DOWNLOAD_FOLDER + "figures\\"
    # maxi = 0 
    # files = list(os.listdir(sf)) 
    # files.sort()

    # if files != []:
    #     vals = [eval(val[:-4]) for val in files]
    #     maxi = max(vals) + 1
    # fn =sf +  str(maxi) + ".png"
    # print("=========================")
    # print(fn)
    # plt.savefig(fn,dpi = 400)

    # plt.close()
    plt.tight_layout()
    plt.show()

def make_satimpgraph(mus,e):
    g = nx.DiGraph()

    g.add_node("T", level=0,nodetype="var")
    g.add_node("B",nodetype="var")
    for clause in mus:

        sig = e[str(clause)][0]
        clause = list(map(abs,clause))

        if sig.startswith("AL") or sig.startswith("ref") or sig.startswith("PREF") or sig.startswith("haAL"):
            g.add_node(sig,nodetype="clause")
            g.add_edge("T",sig)
            for var in clause:
                g.add_node(var,nodetype="var")
                g.add_edge(sig,var)
                
                
        elif sig.startswith("AM") or sig.startswith("rkefdir") or sig.startswith("haAM"):
            if sig.startswith("haAM"):
                print("---------")
                print(sig)
                print(clause)
                print("-----------")
            g.add_node(sig,nodetype="clause")
            g.add_node(clause[0],nodetype="var")
            g.add_node(clause[1],nodetype="var")
            g.add_edge(clause[0],sig)
            g.add_edge(clause[1],sig)
            g.add_edge(sig,"B")
            
            
        elif sig.startswith("rkefres") or sig.startswith("rkefcar") or sig.startswith("LEF"):
            g.add_node(clause[0],nodetype="var")
            g.add_node(sig,nodetype="clause")
            g.add_edge(clause[0], sig)
            if len(clause) == 1:
                g.add_edge(sig,"B")
            else:
                for i in range(1, len(clause)):
                    g.add_node(clause[i],nodetype="var")
                    g.add_edge(sig,clause[i])
        else:
            raise ValueError(sig + ":not recognized")
    
    for u,v in nx.bfs_edges(g,"T"):
        if "level" not in g.nodes[v]:
            g.nodes[v]["level"] = g.nodes[u]['level']+1
        if v == "B":
            g.nodes[v]["level"] = max(g.nodes[v]["level"], g.nodes[u]['level'] + 1)
            
    return g

        


    
def make_color(active):
    return [nodecolor(node,active) for node in active]
def nodecolor(node,active):
    if active[node] == 1: # Node is active
        return "tab:red"
    elif active[node] == 2: # Node was pruned
        return "tab:orange"
    else:
        return "tab:cyan" # Node is unactive


def active_nodes(active,onlyvars=False,onlyintvars=False):
    if onlyvars and onlyintvars: raise ValueError("Attention fct active_nodes")
    if onlyintvars:
        return set([node for node in active if active[node] and type(node)==int])
    if onlyvars:
        return set([node for node in active if active[node] and (type(node)==int or node=="T" or node=="B")])
    
    return set([node for node in active if active[node]])


def build_subsets(subgraph):
    # On detecte les cycles
    for cycle in nx.simple_cycles(subgraph):
        raise ValueError("cycle")
        
    g = subgraph

    for u in g.nodes:
        g.nodes[u]["groups"] = []
        g.nodes[u]["nb"] = 1
    g.nodes["B"]["groups"] = ["B"]
    for i,node in enumerate(g.successors("B")):
        g.nodes[node]["groups"] = ["B"+str(i+1)]
        
    for u,v in nx.bfs_edges(subgraph,"B"):
        u = v # Looking for a node BFS not edge
        for v in g.successors(u):
            if g.nodes[u]["nodetype"] == "var":
                for group in g.nodes[u]["groups"]:
                    g.nodes[v]["groups"].append(group + str(g.nodes[u]["nb"]))
                    g.nodes[u]["nb"] += 1 
            else:
                for group in g.nodes[u]["groups"]:
                    g.nodes[v]["groups"].append(group)
                    
    
def shuffle_all(lists):
    for _list in lists:
        shuffle(_list)
    shuffle(lists)
def make_labels(g):
    label = {}
    for node in g.nodes:
        if not type(node)==int:
            if node == "T":
                label[node] = "$\\top$"
            elif node == "B":
                label[node] = "$\\bot$"
            else:
                start = node.index("[")
                li = eval(node[start:])
                # li = [el+1 for el in li]
                li = list(map(str,li))
                # li = list(map(str,eval(node[start:])))
                name = node[:start]
                if name == "AL":
                    label[node] = "$\\phi^{atleast}" +  "(" + str(li[0]) + ")$"
                elif name == "AM":
                    label[node] = "$\\phi^{atmost}" +  "(" + ",".join(li) + ")$"
                elif name == "rkefres":
                    label[node] = "$\\phi^{rkef}" + "_{res}" +  "(" + ",".join(li) + ")$"
                elif name == "rkefcar":
                    label[node] = "$\\phi^{rkef}" + "_{car}" +  "(" + ",".join(li) + ")$"
                elif name == "ref" or name == "ref2":
                    label[node] = "$\\phi^{ref}" + "_{car}" +  "(" + ",".join(li) + ")$"
                elif name == "rkefdir":
                    label[node] = "$\\phi^{rkef}" + "_{dir}" +  "(" + ",".join(li) + ")$"
                else:
                    label[node] = "?"

        else:
            x,y,_ = get_ij_from_k(node)
            # x,y = str(max(x,y)+1),str(min(x,y)+1)
            x,y = str(max(x,y)),str(min(x,y))
            label[node] = "$x_{"+str(x)+str(y)+"}$"
    return label

def get_elicitsets(g):
    sets = []
    for clause in g.predecessors("B"):
        sets.append( set(g.predecessors(clause)) )

    return sets 

def get_frontier(g):
    frontier = []
    for clause in g.successors("T"):
        frontier.append(list(g.successors(clause)))
    return frontier
        

def dicogen(gobj):
    """ 
    from SAT Imp Graph
    generate dico where 
        key = an elicit set 
        dico[key] = all the states that are elicited 
    """
    elicitsets =get_elicitsets(gobj.g)
    front = get_frontier(gobj.g)
    dico = {str(el):[] for el in elicitsets} 
    for val in product(*front):
        for el in dico:
            if eval(el).issubset( set(val) ):
                dico[el].append( val )
    return dico 
    
def Ugen(gobj):
    front = get_frontier(gobj.g)
    return set(product(*front))
def set_cover_instance(U,dico):
    """ 
    U is all states, dico from dicogen 
    key = a state 
    supdico[key] = all the states elicited by key 
    """ 
    supdico = {str(el):set() for el in U}
    for el in U:
        for elicit in dico:
            if el in dico[elicit]: 
                for el2 in dico[elicit]:
                    supdico[str(el)].add(el2)
    return supdico 

def is_assign_consistent(varlist):
    matching = {}
    for var in varlist: 
        i,j,_ = get_ij_from_k(var) 
        if i in matching and matching[i] != j: return False 
        if j in matching and matching[j] != i: return False 
        matching[i] = j 
        matching[j] = i 
    return True 

def text_expl(nodes, prefp = None):
    """ 
    Textual explanation for the SAT Imp Graph 
    """

    text = ""
    if type(nodes) == str or type(nodes)==int:
        nodes = [nodes]
    for node in nodes:
        if type(node) == int:
            i,j,_ = get_ij_from_k(node)
            text += f"Assume agent {i} is matched with agent {j}."
        elif node == "B":
            text += "Contradiction."
        elif node.startswith("AM"):
            i,j,k = eval(node[2:])
            text += f"Agent {k} cannot be matched to both agents {i} and {j}."
        elif node.startswith("AL"):
            i = eval(node[2:])[0]
            text += f"Agent {i} should be matched with at least one agent."
        elif node.startswith("rkefdir"):
            i,j,p,q = eval(node[7:]) 
            text += f"Agent {i} envies agent {j} because they prefer {q} over {p} and ranks {q} better than {j} does."
        elif node.startswith("rkefres"):
            if prefp is None: raise ValueError("Please provide pref profile")
            i,j,p = eval(node[7:])
            jprefs = set( [prefp[j][ag] for ag in range( prefp[j].index(p) )] )
            text += f"To avoid envy on agent {i}, agent {j} must have a partner they prefer over {p}" 
            if len(jprefs) > 0:
                text += f", one among: {jprefs}."
            else:
                text += ". However, no other agent satisfies that requirement."
        elif node.startswith("ref2"):
            if prefp is None: raise ValueError("Please provide pref profile")
            li = eval(node[4:])
            if len(li) == 1:
                p = li[0]
                ags = set([ag for ag,prefs in enumerate(prefp) if prefs[0]==p])
                text += f"Agent {p} needs to be matched with an agent that ranks them first, one among: {ags}."
            else:
                p,l,i = li 
                text += f"Either agent {i} should be matched to an agent they rank in their top {l-1}, or agent {p} should be matched to agent that ranks them in their top {l}."
        elif node.startswith("PREF"):
            i = eval(node[4:])[0]
            text += f"Agent {i} should be matched with an agent they prefer over their previous assignment."
        elif node.startswith("haAL"):
            i = eval(node[4:])[0]
            text += f"Agent {i} should be assigned at least one object."
        elif node.startswith("haAM"):
            _,o,i,j = node[4:-1].split("_")
            text += f"Object {o} can't be assigned to both agent {i} and agent {j}"
        elif node.startswith("LEF"):
            val = node[4:-1].split("_")

            is_ha = len(val) == 4 
            if len(val) == 4:
                i,j,_,ob = val 
            if len(val) == 3:
                i,j,p = val
                
            j = int(j)
            if is_ha:
                text += f"To avoid envy on agent {i}, agent {j} should receive an object they prefer over {ob}"
                jprefs = set( [prefp[j][r] for r in range( prefp[j].index(f"{ob}") )] )
            else:
                text += f"To avoid envy on agent {j}, agent {i} should be matched with an agent they prefer over {p}"

                print("prefp i")
                i = int(i)
                jprefs = set( [prefp[i][r] for r in range( int(prefp[i].index(int(p))) )] )         

            if len(jprefs) > 0:
                text += f", one among: {jprefs}."
            else:
                text += ". However, no other agent satisfies that requirement."
        elif node == "T": continue
        else:
            raise ValueError("Unknown node: " + node)
    return text + "\n"
            
            

if __name__ == "__main__":
    pass