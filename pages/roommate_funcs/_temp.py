# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 14:22:10 2024

@author: sabatinofr
"""
if not __name__ == "__main__":
    from sequential_al_graph import *
    from roommate_sat import *
    from implications import *
    from explain_mus import *
    from heuristics import *
    from roommate import *
    from tools import *
    from funcs import *
    from tests import *
    from cnf import *

import sys
import numpy as np
from tqdm import tqdm
import multiprocessing
from time import sleep 
from copy import deepcopy
from datetime import datetime 
from time import perf_counter as clock
from itertools import combinations, permutations
from random import randint, choice, sample,random

from pysat.formula import WCNF


k = float("inf")
# n = 8
# formulation = "res"

def randseq(sat,F):
    s = Seq(sat, F)
    s.start() 
    return s.log["LENGTH"]
def best_n_randseq(sat,F,n=100):
    best = float("inf")
    logs = []
    for _ in range(10):
        s = Seq(sat, F)
        s.start() 
        best = min(best, s.log["LENGTH"])
        logs.append(s.log["LENGTH"])
    
    return best 


""" 
Generate instances of the Sequential activation graph 
""" 
def findnbmus(F):  
    cn = CNF()
    for clause in F.cnf:
        cn.append(clause)
    with OptUx(cn.weighted(), unsorted=True) as optux:
        val = 0
        for mus in optux.enumerate():
            val += 1 
            if val > 9999:
                break
        return val
    
""" 
Check if a heuristic is better than random or random+
"""
# va,vb,vc = 0,0,0
# invalid = 0
# maxi = 0
# for _ in tqdm(range(100)):
#     F=generate_instance(n, k, formulation)
#     mus = find_best_mus_fast(F)

#     sat = SAT_Imp_Graph(mus, F) 
#     s = Seq(sat, F)
#     s.setH(h_maxClauseLinkOnMinVar)
#     s.start() 
#     a = randseq(sat, F)
#     b = best_n_randseq(sat, F)
#     c = s.log["LENGTH"]
#     if c < a:
#         va += 1 
#     if c < b:
#         vb += 1 
#     if c == a or c ==b:
#         vc += 1
    

""" 
examples from the paper
"""
# n=4
# formulation="dir"
# p = ((3,2,4),(3,1,4),(4,2,1),(1,2,3))
# p = tuple([tuple([i-1 for i in el]) for el in p])
# F = Formula(n,p,k,formulation)
# mus = [[1,3,5],[2,3,6],[4,5,6],[-1,-6],[-3,-5],[-5,-6],[-2,-5],[-3,-6],[-2,-4],[-3,-4]]
# sort_cnf(mus)
            

"""
possible heuristics in <heuristics.py> file
h_maxClauses
h_maxClausesOnMinVar
h_minNew
h_bestAssignedRank
h_miniTopRank
h_matchedTopRank
h_clauseSize
h_bestChar 
"""

"""
k is set to inf 
Try heuristics for direct formulation  or characterization 
For direct use n=6/8 else takes time...or iterate seq act less

use param formulation="car" for generating CNF in characterization formulation 
use param formulation="dir" for generating CNF in direct formulation 
"""

""" 
This code generates 100 instances of unsat instances roommate matching problems , with a MUS
generates 100 random sequential activation and keeps all the different lengths 
Generates seq act with an heuristic and ranks its length among the random one  
    1 / x: heuristic got the best (shortest) length among x different ones 
"""
# n = 10 # Nb of agents
# heuristic = h_bestChar
# formulation = "car"
# if formulation == "dir" and n>6:
#     print("Maybe reduce nb agents else it takes time")
# for _ in range(100):
    
#     F,mus = generate_instance(n, k, f=formulation,mus=True) 
#     vals = set() # Store lengths of Sequential Activation for random tries
#     satimp = SAT_Imp_Graph(mus, F)
#     for _ in range(100): # iterate seq act 100 times
#         s = Seq(satimp, F)
#         s.start() 
#         vals.add( s.log["LENGTH"] )
#     if len(vals)>10: # If there exists enough different instances of the Seq Act Graph 
#         s = Seq(satimp, F)
#         s.setH(heuristic) # Use an heuristic 
#         s.start()
#         v = s.log["LENGTH"]
#         clas = len(set(filter(lambda x: x<v,vals))) # Nb of random activations that were better than with the heuristic
#         print(clas+1,"/",len(vals)) # Show the rank of the seq act with heuristic compared with random tries
#         # if clas/len(vals) < 0.5:
#         #     satimp.draw()


""" 
try heuristics for restriction formulation 
use precalculated instances because don't find often muses with more than 1 
possible activation sequence 
In total, 61 preferences profiles and 342 muses with n=12
"""
# instances,_ = load_obj("resinst")
# n=12
# heuristic = h_bestAssignedRank
# for p,muses in instances:
#     F = Formula(n,p,k,"res")
#     for mus in muses:
#         satimp = SAT_Imp_Graph(mus, F)
#         vals = set()
#         for _ in range(100):
#             s = Seq(satimp, F)
#             s.start() 
#             vals.add( s.log["LENGTH"] )

#         s = Seq(satimp, F)
#         s.setH(heuristic)
#         s.start()
#         v = s.log["LENGTH"]
#         clas = len(set(filter(lambda x: x<v,vals)))
#         print(clas+1,"/",len(vals))
        
def formate(dico):
    for el in dico:
        # if not el.startswith("h_"): continue
        if  el.startswith("h_"):
            pel = el[2:]
        else:
            pel = el
        print(str(pel)+" &",end = " ")
        print(str(round(np.mean(dico[el]),1)) + " &",end=" ")
        print(str(round(np.var(dico[el]),1)) + " \\\\")
"""
heuristic list 
---- 
h_maxMatched
h_maxRankEnvy
h_maxVarConnectMin
h_maxVarConnectSum
h_minClause
h_minContrad
""" 
# heuristics = ["h_maxMatched","h_maxRankEnvy","h_maxVarConnectMin","h_maxVarConnectSum","h_minClause","h_minContrad"]
# n = 12
# formulation = "res" 
# exp = {}

# for _ in tqdm(range(1000)):
#     F = generate_instance(n, k, formulation)
#     mus1 = retrieve_mus(F)
#     mus2 = None 
#     mus3 = None
#     G = deepcopy(F)
#     _,G.cnf = find_mini_nb_alloc_clauses(F,prog=False)
#     if formulation == "dir":
#         mus2= retrieve_mus(G)
#     if formulation == "res"  or formulation == "car":
#         mus2 = find_minalmus(G)
#         mus3 = find_mingloblenposmus(F)
#     muses = [mus1,mus2]

#     if not mus3 is None: muses.append(mus3)

#     if exp == {}:
#         exp = {f"mus{i}":{} for i  in range(1,len(muses)+1)}
#         for mus in exp:
#             exp[mus] = {h:[] for h in heuristics}
#             exp[mus]["rand"] = []
#             exp[mus]["10rand"] = []
#             exp[mus]["value"] = []
#             exp[mus]["satimp"] = []
    
#     for i,mus in enumerate(exp):
#         curmus = muses[i]
#         if mus=="mus1":
#             exp[mus]["value"].append( (len(curmus),nbalinmus(curmus)) )
#         if mus=="mus2":
#             exp[mus]["value"].append( nbalinmus(curmus) )
#         if mus=="mus3":
#             exp[mus]["value"].append( sum([len([1 for v in c if v>0]) for c in curmus]) )
    
    
#     for i,mus in enumerate(muses):
#         satimp = SAT_Imp_Graph(mus, F)
#         ide = 'mus'+str(i+1)
#         s = Seq(satimp, F)
#         s.start()
#         exp[ide]["rand"].append( randseq(satimp, F))
#         exp[ide]["10rand"].append( best_n_randseq(satimp,F,n=10) )
#         for heur in heuristics:
#             s = Seq(satimp,F)
#             s.setH(eval(heur))
#             s.start()
#             exp[ide][str(heur)].append( s.log["LENGTH"] )
        
#         satimp.propagate()
#         exp[ide]["satimp"].append( satimp.log["LENGTH"] )

# store_obj(exp,"expres12")



# exp = load_obj("expcar")
# lines = []
# prints = {}
# for mus in exp:
#     print(mus)
#     for heur in  exp[mus]:
#         print(heur, np.mean(exp[mus][heur]) )
#         if heur not in prints:
#             prints[heur] = [] 
# print()
# for mus in exp:
#     for heur in exp[mus]:
#         prints[heur].append( np.mean(exp[mus][heur]) )

# for heur in prints:
#     prints[heur] = list(map(str, prints[heur]))
#     lines.append(heur + " & " + prints[heur][0] + " & "  +prints[heur][1] + " & " + prints[heur][2] + " \\\\")
#     print(lines[-1])






""" 
others 
"""
# n=10
# F,mus = generate_instance(n, k, "car", mus=True)
# sat = SAT_Imp_Graph(mus, F)
# s = Seq(sat, F)
# s.start() 

# print( randseq(sat, F) )
# print( best_n_randseq(sat, F, n=10000) )




import matplotlib.pyplot as plt
import numpy as np

from matplotlib import colors
from matplotlib.ticker import PercentFormatter

import matplotlib.pyplot as plt

# Use LaTeX for rendering
plt.rcParams['text.usetex'] = True

# Define the linear orders
# orders = [
#     r"$1 > 2 > 3 > 4$",
#     r"$1 > 2 > \overset{\square}{3} > 4$",
#     r"$1 > 2 > 3 > 4$",
#     r"$1 > 2 > 3 > 4$"
# ]
orders = [r"$2 > 3 > \frac{2}{3}$"]
# Create figure
fig, ax = plt.subplots(figsize=(4, 3))
ax.axis('off')

# Plot each line, vertically spaced
for i, line in enumerate(orders):
    ax.text(0.5, 1 - i * 0.25, line, fontsize=18, ha='center', va='top')

# plt.tight_layout()
plt.show()
