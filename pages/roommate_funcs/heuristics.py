# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 15:12:01 2025

@author: sabatinofr
"""

from random import choice
from .roommate_sat import get_ij_from_k
from .roommate import rank


def h_maxVarConnectSum(satimp,debug = False):
    """ 
    count nb of clauses an AL clause is linked to through its variables 
    """
    g = satimp.g
    vals = {}
    for clause in g.successors("T"):
        vals[clause] = sum([len(g[var]) for var in g.successors(clause)])
    
    if debug:
        return vals
    return [k for k, v in sorted(vals.items(), key=lambda item: item[1],reverse=True)]


def h_maxVarConnectMin(satimp,debug = False):
    """ 
    Choose allocation clause that has the most links to other clauses through its successor variable-nodes,
    consider only variable that has the minimum number of links
    """
    g = satimp.g
    vals = {}
    for clause in g.successors("T"):
        vals[clause] = min([len(g[var]) for var in g.successors(clause)])
    
    if debug:
        return vals
    return [k for k, v in sorted(vals.items(), key=lambda item: item[1],reverse=True)]


def h_minContrad(active,actvbl, seq):
    """ 
    Choose the clause that seems the most relevant to explain a step 
    """ 
    satimp = seq.satimp
    len_clauses = {el:0 for el in filter(lambda x: x in actvbl and seq.nodetype(x)=="clause", satimp.g.nodes)}
    endC = seq.endclauses 
    for clause in len_clauses:
        for var in satimp.g.successors(clause):
            if var < 0: continue 
            best = float("inf")
            for endc in endC:
                val = len([x for x in satimp.g.predecessors(endc) if not -x in active.union([var])])
                best = min(best, val)
            len_clauses[clause] += val
    return sorted(len_clauses.keys(), key = lambda x: len_clauses[x])



        
    
def h_maxRankEnvy(active, activatbl, seq):
    """ 
    among the clauses $\atleast(i)$ for an agent $i$ who ranks better an agent $j$ already assigned in the current partial assignment than what does the current partner of $j$, choose the one where $i$ ranks $j$ with the best rank?
    """
    P = seq.satimp.p
    if len(active) == 0:
        return choice(activatbl)
    o = {}
    for obj in active:
        if type(obj) != int:
            continue 
        i,j,_ = get_ij_from_k(obj)
        o[i] = j 
        o[j] = i
    score = {}
    for clause in activatbl:
        score[clause] = 0
        for var in seq.satimp.g[clause]:
            i,k,_ = get_ij_from_k(var)
            try:
                if any([True for l in o if i!=o[l] and i!= l and rank(P,i,o[l]) < min(rank(P, l, o[l]), rank(P, i, l))]):
                    score[clause] += 1
            except:
                print(i,k)
                print(o)
                print(activatbl)
                a=1/0
    return sorted(score.keys(), key = lambda x: score[x], reverse=True)
            

def h_minClause(satimp):
    """ 
    Sort clauses by increasing clause size (nb of successors in the SAT Imp Graph)
    """
    return sorted(filter(lambda x: satimp.g.nodes[x]["nodetype"]=="clause", satimp.g.nodes), key = lambda x: len(satimp.g[x]))
         

def h_maxMatched(active, activatbl, seq):
    """
    choosing in priority clauses $characttop(i)$ involving an agent $i$ already assigned in the current partial assignment?
    """
    if len(active) == 0:
        return choice(activatbl) 
    o = {}
    for obj in active:
        if type(obj) != int:
            continue 
        i,j,_ = get_ij_from_k(obj)
        o[i] = j 
        o[j] = i
        
    score = {}

    for clause in activatbl:
        if type(clause) == int or clause in {"T","B"}: continue 
        score[clause] = 0
        for var in seq.satimp.g[clause]:
            i,j,_ =  get_ij_from_k(var)
            if i in o  or j in o:
                score[clause] += 1
    return sorted(score.keys(), key = lambda x: score[x], reverse=True)
        