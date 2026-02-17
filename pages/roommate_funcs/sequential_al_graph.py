# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 14:22:10 2024

@author: sabatinofr
"""
from .explain_mus import text_expl 
from .explain_mus import make_color

from time import sleep
import networkx as nx 
from random import choice 

class Seq:
    def __init__(self, satimp, F):
        self.mus = satimp.mus # list of clauses
        self.g = nx.DiGraph()
        self.p = F.p
        self.names = {F.e[str(clause)][0]:clause for clause in self.mus} # names[cname] = clause
        
        self.endclauses = set([clause for clause in satimp.g.predecessors("B")]) # list of  names
        
        self.log = {"LENGTH":-1,"LENDFS":-1}
        
        self.satimp = satimp
        
        # satimp.draw()
        
        self.logs = []
       
        self.H = None
        self.order = None
        
        self.text = []
        
    def setH(self,h):
        self.H = h
        if h in {h_maxVarConnectSum, h_maxVarConnectMin, h_minClause}:
            self.order = h(self.satimp)
        
        
    def start(self):
        self.sequential(set(), set("T"))
        
    def nodetype(self,node): #used for debugging
        if node not in self.satimp.g:
            raise ValueError("node " + str(node) + " is not in the graph")
        return self.satimp.g.nodes[node]["nodetype"]
    
    def nodechoice(self, active_nodes, activatable_nodes):
        bot_clauses = tuple(filter(lambda x: x in self.endclauses, activatable_nodes))
        if bot_clauses:
            return choice(bot_clauses)
        var_nodes = tuple(filter(lambda x: self.nodetype(x)=="var", activatable_nodes))
        if var_nodes:
            return choice(var_nodes)
        
        prefs = [node for node in activatable_nodes if node.startswith("PREF")]
        if prefs != []: # If we're doing local expl for an agent we want to put this clause first 
            return prefs[0]
        
        if self.H is not None:
            if self.order is not None:
                order = tuple(filter(lambda x: x in activatable_nodes, self.order))
                if len(order) == 0:
                    return choice(tuple(activatable_nodes))

                return order[0]
            else:
                order = self.H(active_nodes, activatable_nodes, self)
                if len(order) == 0:
                    return choice(tuple(activatable_nodes))
                return order[0]
        return choice(tuple(activatable_nodes))
    
    def draw(self,curactive):
        color = {}
        for node in self.satimp.g.nodes:
            if node in curactive:
                color[node] = 1 
            else:
                color[node] = 0 
        colr = make_color(color)
        self.satimp.draw(fancy_labels=1,coloring=colr)
        sleep(0.2)

    def sequential(self, active, activatable):
        self.logs.append( (active,activatable) )

        g = self.satimp.g
        self.log["LENGTH"] += 1
        
        # self.draw(active)
        
        if "B" in activatable:
            # self.draw(active.union("B"))
            self.text.append("Contradiction")
            # print("Contradiction")
            return 

        # vrs = tuple([el for el in activatable if g.nodes[el]["nodetype"]=="var"])
        # if vrs:
        #     x = choice(vrs)
        # else:
        x = self.nodechoice(active, activatable)
        activatable.remove(x)
        self.text.append(text_expl(x,prefp=self.p))

        
        # if not x in self.xcounts:
        #     self.xcounts[x] = 0 
        # self.xcounts[x] += 1 
        # if self.xcounts[x] > 3:
        #     raise ValueError
        
        if self.nodetype(x)=="clause":
            for y in g.successors(x):
                if not y in active:
                    self.sequential(active.union([x]),activatable.union([y])) 
        
        else:
            newactive = active.union([x])
            nextc = [clause for clause in g.successors(x) if not clause in active and all([pred in newactive for pred in g.predecessors(clause)])]
            # endok = [clause for clause in nextc if clause in self.end]
            endok = [] # Clauses that lead to contradiction
            if endok:
                self.sequential(newactive, activatable.union([choice(endok)]))
            else:
                self.sequential(newactive, activatable.union(nextc))
        