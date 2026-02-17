
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 16:12:46 2024

@author: sabatinofr
"""


from .cnf import FormulaSRP
 
from .roommate import rk_ef 
from .roommate import get_rkef_matchings 
from .roommate import get_all_matchings

from .roommate_sat import get_matching
from .roommate_sat import find_all_models 
from .roommate_sat import solve 
from .roommate_sat import retrieve_mus
from .roommate_sat import find_unsat
from .roommate_sat import get_ij_from_k
from .roommate_sat import find_n_unsat
from .roommate_sat import translate_cnf

from .implications import procedure

from .tools import store_obj 

import pickle
import numpy as np
from tqdm import tqdm
from math import factorial
from random import shuffle
from pysat.formula import CNF, WCNF
import matplotlib.pyplot as plt 
from itertools import combinations
from pysat.examples.optux import OptUx
from time import perf_counter as clock
from copy import deepcopy
    


def remove_ag_from_p(p,ag):
    newp = []
    for i,el in enumerate(p):
        if i == ag: continue 
        el = [pref for pref in el if pref != ag]
        el = [pref-1 if pref>ag else pref for pref in el]
        newp.append(tuple(el))
    return tuple(newp)

def remove_ags_from_p(p,agli):
    # remove agents from bigger index to not break order 
    agli.sort(reverse=True) 
    for agent in agli:
        p = remove_ag_from_p(p, agent)
    return p

def generate_instance(n,k,f,mus = False):
    p = find_unsat(n,k)
    F = FormulaSRP(n,p,k,f)
    if mus:
        mus = retrieve_mus(F)
        return F,mus
    else:
        return F 
    

def issuperset(a,b):
    return b.issubset(a)
def reduce_F(F):
    """ 
    Removing redundant clauses from 
    restriction formulation 
    """ 
    G = deepcopy(F)
    G.cnf = [set(clause) for clause in G.cnf]
    G.cnf = [sorted(clause) for clause in G.cnf if not any([issuperset(clause, el) for el in G.cnf if el!=clause])]
    return G


def find_minmax_mus_fast(cnfx,N=10):
    """ find muses with minimal and maximal length on N iterations """
    mini = float("inf")
    maxi = -float("inf")
    for _ in range(N):
        shuffle(cnfx)
        mus = retrieve_mus(cnfx,fast=True)
        mini = min(mini,len(mus))
        maxi = max(maxi,len(mus))
    return mini,maxi


def find_minmax_alloc_mus_fast(cnfx,N=10, prog = False):
    """ find muses with minimal and maximal nb of alloc clauses on N iterations """
    mini = float("inf")
    maxi = -float("inf") 
    if prog: pbar = tqdm(total=N)
    for _ in range(N):
        shuffle(cnfx)
        mus = retrieve_mus(cnfx,fast=True)
        nbal = len([1 for clause in mus if all([var>0 for var in clause])])
        mini = min(mini,nbal)
        maxi = max(maxi,nbal)
        if prog: pbar.update(1)
    if prog: pbar.close()
        
    return mini,maxi


def mus_stats(cnf):
    """ build stats on a mus """
    log = {}
    log["n_clauses"] = len(cnf)
    log["n_agents"]  = 0
    log["n_vars"] = 0
    vars_ = set()
    agents= set()
    for clause in cnf:
        for var in clause:
            vars_.add(abs(var))
            i,j,pos = get_ij_from_k(var)
            agents.add(i)
            agents.add(j)
    log["n_agents"] = len(agents)
    log["n_vars"] = len(vars_)
    return log


def find_best_mus_fast(F,N_TRIES=10,prog=False):
    """ find smallest MUS that has the least nb of AL clauses """
    bestAL = float("inf")
    bestLEN= float("inf")
    bestMUS = None 
    vals = range(N_TRIES)
    if prog: vals = tqdm(vals)
    for _ in vals:
        shuffle(F.cnf)
        mus = retrieve_mus(F.cnf,fast=True)
        nbAL = len([1 for clause in mus if all([var > 0 for var in clause])])
        lemu = len(mus)
        if nbAL < bestAL:
            bestAL = nbAL 
            bestMUS = mus 
        elif nbAL == bestAL and lemu < bestLEN:
            bestLEN = lemu
            bestMUS = mus 
    return bestMUS 

def find_mus_condition(F,fcond, N_TRIES=10,prog=False):
    """ find a mus that satisfies the condition"""
    vals = range(N_TRIES)
    if prog: vals = tqdm(vals)
    for _ in vals:
        shuffle(F.cnf)
        mus = retrieve_mus(F.cnf,fast=True)
        if fcond(mus,F): return mus
    raise ValueError("Couldn't find adequate mus")

def nbcomb(n,k):
    return factorial(n) / (factorial(k) * factorial(n-k)) 
def sep_alloc_from_cnf(cnf):
    """ separate allocation clauses from the others """
    AL = []
    others = []
    for clause in cnf:
        if all([var>0 for var in clause]):
            AL.append(clause)
        else:
            others.append(clause)
    return AL,others
      

def find_mini_nb_alloc_clauses(F, prog = True): 
    """ find CNF still UNSAT with the least nb of alloc clauses """
    unsat_cnf = reduce_F(F).cnf
    alloc,others = sep_alloc_from_cnf(unsat_cnf)
    first_bound = find_minmax_alloc_mus_fast(unsat_cnf,N=2, prog = False)[0]
    save_f = None
    if prog: print("Starting at bound",first_bound)
    first_bound = min(first_bound,6)
    for size in range(first_bound,-1,-1):
        nb = nbcomb(len(alloc),size)
        if prog: pbar = tqdm(total=nb)
        found = False
        for comb in combinations(alloc,size):
            formula = list(comb) + others 
            g = solve(formula)
            if prog: pbar.update(1)
            if g.status == False:
                found = True 
                save_f = formula
                break
        if prog: 
            pbar.close()
        if not found:
            # if size == first_bound: raise ValueError
            # return "Min number is " + str(size+1) 
            return size+1,save_f
def find_miniclauses_iter(n,k,NIT,form="res"):
    for _ in tqdm(range(NIT)):
        p = find_unsat(n,k)
        F = FormulaSRP(n,p,k,form)
        # print( find_mini_nb_alloc_clauses(F.cnf, prog = False) )
        if int(find_mini_nb_alloc_clauses(F.cnf,prog=False)[-1]) > 3:
            print(p)
            raise ValueError
def find_miniclauses_iter2(n,k,NIT,form="res"):
    for _ in tqdm(range(NIT)):
        p = find_unsat(n,k)
        F = FormulaSRP(n,p,k,form)
        if find_mini_nb_alloc_clauses(F.cnf, prog = False)[0] > 1:
            print(p)
            raise ValueError 

def find_mus_opti_nodir(F):
    """ find mus with only 1 alloc clause for res and car ; returns None if none"""
    alloc,others = sep_alloc_from_cnf(F.cnf)
    for calloc in alloc:
        f = [calloc] + others # Only 1 alloc clause
        if not solve(f).status:
            return retrieve_mus(f,fast=False)
                
        
def find_mus_veryfast_nodir(F,max_branch = 1):
    raise NotImplementedError
    alloc,others = sep_alloc_from_cnf(F.cnf)
    for calloc in alloc:
        sat = {var:0 for var in calloc}
        for level in range(1,max_branch+1):
            # nodir because the first literal of the clause must be negative
            mus_others = [clause for clause in others if len(clause) <= level and -clause[0] in sat and not sat[-clause[0]]] 
            # if any([]) ...
        
        if len(mus_others) == len(calloc):
            return True # Returns a reduced CNF and we can find a MUS of it 
    return False 


def find_minimus_dir(F,nbAL=3):
    alloc,others=sep_alloc_from_cnf(F.cnf)
    for comb in combinations(alloc,nbAL):
        f = list(comb)+others 
        if not solve(f).status:
            return retrieve_mus(f)
    return None
    raise ValueError("Didn't find a MUS")
def find_weird_instance(n,k,TOT = 10,nAL=3):
    pbar = tqdm(total = TOT)
    for _ in range(TOT):
        p = find_unsat(n,k)
        F = FormulaSRP(n,p,k,"dir")
        mus = find_minimus_dir(F,nbAL=nAL)
        if mus == None:
            pbar.close()
            return p
        pbar.update(1)
    return None
    

def find_minwmus(F): 
    """ 
    Optux minimise le weight 
    """ 
    wcnf = WCNF()
    W = len(F.cnf) * 10e5
    for clause in F.cnf: 
        if F.e[str(clause)][0].startswith("AL"):
            wcnf.append( clause, weight = W )
        else:
            wcnf.append( clause, weight = 1 )

    with OptUx(wcnf) as optux:
        for mus in optux.enumerate():
            return [F.cnf[i-1] for i in mus]

    return None


def find_minlenmus(F): 
    """ 
    Optux minimise le weight 
    """ 
    wcnf = WCNF()
    # W = len(F.cnf) * 10e5
    for clause in F.cnf: 
        wcnf.append( clause, weight = 1 )

    with OptUx(wcnf) as optux:
        for mus in optux.enumerate():
            return [F.cnf[i-1] for i in mus]

    return None

def find_mingloblenmus(F,findall=False): 
    """ 
    Optux minimise le weight 
    """ 
    wcnf = WCNF()
    # W = len(F.cnf) * 10e5
    for clause in F.cnf: 
        wcnf.append( clause, weight = len(clause) )

    muses = []
    cost = None 
    with OptUx(wcnf) as optux:
        for mus in optux.enumerate():
            if not findall:
                return [F.cnf[i-1] for i in mus]
            if cost is None: cost = optux.cost 
            if optux.cost > cost: break  
            muses.append([F.cnf[i-1] for i in mus])
    return muses

def find_mingloblenposmus(F,findall=False): 
    """ 
    Optux minimise le weight 
    """ 
    wcnf = WCNF()
    # W = len(F.cnf) * 10e5
    for clause in F.cnf: 
        wcnf.append( clause, weight = len([var>0 for var in clause]) )

    muses = []
    cost = None 
    with OptUx(wcnf) as optux:
        for mus in optux.enumerate():
            if not findall:
                return [F.cnf[i-1] for i in mus]
            if cost is None: cost = optux.cost 
            if optux.cost > cost: break  
            muses.append([F.cnf[i-1] for i in mus])
    return muses


def find_minalmus(F, return_nb=False, count_tot=False): 
    """ 
    Optux minimise le weight 
    """ 
    wcnf = WCNF()
    W = len(F.cnf) * 10e5
    nb = 0
    for clause in F.cnf: 
        if F.e[str(clause)][0].startswith("AL"):
            wcnf.append( clause, weight = W )
        else:
            wcnf.append( clause, weight = 1)

    with OptUx(wcnf) as optux:
        for mus in optux.enumerate():
            mus = [F.cnf[i-1] for i in mus]
            if count_tot:
                nbal = len([1 for clause in mus if all([v>0 for v in clause])]) 
                if nbal == 1:
                    nb += 1
                    if nb% 100 == 0:
                        print(nb)
                    continue
                else:
                    return nb 
            if return_nb:
                return len([1 for clause in mus if all([v>0 for v in clause])])
            return mus

    return None

def find_maxalmus(F): 
    """ 
    Optux minimise le weight 
    """ 
    wcnf = WCNF()
    W = len(F.cnf) * 10e5
    nb = 0
    for clause in F.cnf: 
        if isal(clause):
            wcnf.append( clause, weight = -W )
        else:
            wcnf.append( clause, weight = 1)

    with OptUx(wcnf) as optux:
        for mus in optux.enumerate():
            mus = [F.cnf[i-1] for i in mus]
            print(optux.cost)
            for el in mus:
                if isal(el):
                    print(el)
            # return mus

    return None


def nbalinmus(mus):
    return len([1 for clause in mus if isal(clause)])
def isal(clause):
    return all([var>0 for var in clause])
def isam2(clause): # Plus rapide mais on perd l'info entre rkef dir et am 
    return len(clause)==2 and all([var<0 for var in clause])
def isam(clause):
    if len(clause) != 2: return False 
    x,y = translate_cnf([clause])[0]
    a,b,fa = x
    i,j,fb = y 
    return fa==fb==False and len(set([a,b,i,j])) == 3 
def isrkef(clause):
    return not (isal(clause) or isam(clause))



def sep_c(mus):
    """
    separate AL,AM,rkef clauses in a mus 
    """
    atleast = []
    rkef = []
    atmost = []
    for clause in mus:
        if isal(clause):
            atleast.append(clause)
        elif isam(clause):
            atmost.append(clause)
        else:
            rkef.append(clause)
    return atleast, atmost, rkef

def ptotex(p,human=False):
    text = ["\\begin{align*}"]
    for i, line in enumerate(p):
        if human:
            line = [el+1 for el in line]
            i += 1
        line = map(str,line)
        line = "\t" + str(i) + ": \\quad " + " \\succ ".join(line) + " \\\\"
        text.append(line)
    text.append("\\end{align*}")
    for el in text:
        print(el)
 
def mustotex(mus,F,abrege=True,human=True):
    text = ["\\begin{align*}"]
    if not abrege:
        for clause in mus: 
            sig = F.e[str(clause)][0]
            if sig.startswith("AL"):
                up = "atleast"
                down = ""
                vals = "(" + str( list( eval( sig[2:] ) )[0] ) + ")"
            elif sig.startswith("AM"):
                up = "atmost"
                down = ""
                vals = str( tuple( eval( sig[2:] ) ) )
            elif sig.startswith("rkefdir"):
                up = "rkef"
                down = "dir"
                vals = str( tuple( eval( sig[7:] ) ) )
            elif sig.startswith("rkefres"):
                up = "rkef"
                down = "res"
                vals = str( tuple( eval( sig[7:] ) ) )
            form = f"&\\phi^{{{up}}}" 
            if down != "": form += f"_{{{down}}}"
            
            form += vals + " \\\\"
            
            cvars = []
            for var in clause:
                v = ""
                if var < 0:
                    v += "\\neg "
                i,j,_ = get_ij_from_k(var)
                ij = str(i) + str(j)
                v += f"x_{{{ij}}}"
                cvars.append(v) 
    
            text.append("\t" + " \\vee ".join(cvars) + ": " + form)
    else:
        for clause in mus: 
            sig = F.e[str(clause)][0]
            if sig.startswith("AL"):
                tipe = "atleast"
                vals = "(" + str( list( eval( sig[2:] ) )[0] ) + ")"
            elif sig.startswith("AM"):
                tipe = "atmost"
                vals = str( tuple( eval( sig[2:] ) ) )
            elif sig.startswith("rkefdir"):
                tipe="rkefdir"
                vals = str( tuple( eval( sig[7:] ) ) )
            elif sig.startswith("rkefres"):
                tipe="rkefres"
                vals = str( tuple( eval( sig[7:] ) ) )
            elif sig.startswith("ref"):
                tipe="ref"
                vals = str( tuple( eval( sig[3:] ) ) )
            elif sig.startswith("rkefcar"):
                tipe="rkefcar"
                vals = str( tuple( eval( sig[7:] ) ) )
            form = f"&\\{tipe}" 
            vals = eval(vals)
            if type(vals)==int:
                vals = tuple([vals])

            if human:
                vals = str(tuple([el+1 for el in vals]))

            form += vals + " \\\\"
            
            cvars = []
            for var in clause:
                v = ""
                if var < 0:
                    v += "\\neg "
                i,j,_ = get_ij_from_k(var)
                if human:
                    i += 1 
                    j+= 1
                ij = str(i) + str(j)
                v += f"x_{{{ij}}}"
                cvars.append(v) 
    
            text.append("\t" + " \\vee ".join(cvars) + ": " + form)
    text.append("\\end{align*}")
    
    for el in text:
        print(el)


def newptotex(p):
    te = ["\\begin{center}"]
    val = 2*(len(p)-1)
    te.append("\\begin{tabular}{*{"+str(val)+"}{c}}")
    pp  = [[str(i+1) for i in el]for el in p]
    for i,el in enumerate(pp):
        line = "\t" + f"${i+1}$: & " + " & $\\succ$ & ".join(["$"+ag+"$" for ag in el]) 
        if i!= len(p)-1:
            line += " \\\\"
        te.append(line)
    te.append("\\end{tabular}")
    te.append("\\end{center}")
    for el in te:
        print(el)

if __name__ == "__main__":
    pass

