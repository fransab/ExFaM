# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 10:43:07 2025

@author: franc
"""
from .sequential_al_graph import Seq
from .roommate_sat import *
from .implications import *
from .explain_mus import *
from .heuristics import *
from .roommate import *
from .tools import *
from .funcs import *
from .cnf import *

import sys
import numpy as np
from tqdm import tqdm
import multiprocessing
from time import sleep 
from copy import deepcopy
from datetime import datetime 
from time import perf_counter as clock
from itertools import combinations, permutations
from random import randint, choice, choices, sample,random, shuffle
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

from pysat.formula import WCNF

k = float("inf")

def depthdir():
    return 4
def breadthdir(n,a):
    """ a is nb of at-least clauses in MUS""" 
    return (n-1) ** a 
def lendir(n,a):
    """a is nb of at-least clauses in MUS""" 
    return 1 + ((n-1)**a)*3


def havesameimp(mus):
    imps = set()
    for clause in mus:
        if isrkef(clause):
            if clause[0] in imps:
                return True 
            else:
                imps.add(clause[0])
    return False

""" show seq act better than imp when >1 at least clause in mus"""
# n,k = 10,2  
# x = []
# y = []
# mini = float("inf")
# err = 0
# for _ in tqdm(range(2000)):
#     p = find_unsat(n,k)
#     F = Formula(n,p,k,"res")
#     # mus = find_minalmus(F)
#     mus = retrieve_mus(F)
#     if len([1 for clause in mus if all([var>0 for var in clause])]) == 1:
#         continue
#     if len(set([clause[0] for clause in mus])) < len(mus): # On ne prend pas mus avec plusieurs fois la mm clause
#         err += 1
#         continue
#     G = SAT_Imp_Graph(mus, F)
#     G.propagate()
#     a = G.log["LENGTH"] 
#     g = Seq_act_g(mus, F)
#     g.init()
#     b = g.log["LENGTH"]
#     x.append(a)
#     y.append(b)
#     # if abs(b-a) > 0 :
#     #     break
    
# plt.plot(x,"-r",label="SAT Imp Graph")
# plt.plot(y,"-b",label="Seq Imp Graph")
# plt.ylim([0,300])
# plt.xlabel("Instance") 
# plt.ylabel("Size of explanation")
# plt.legend()
# plt.show()


""" Show extended use of atmost clauses"""
# n,k = 6,2
# err=0
# x = []
# ag = None 
# bg = None 
# for _ in tqdm(range(1000)):
#     p = find_unsat(n,k)
#     F = Formula(n,p,k,"res")
#     mus = find_minalmus(F)
#     if len(set([clause[0] for clause in mus])) < len(mus): # On ne prend pas mus avec plusieurs fois la mm clause
#         err += 1
#         continue
#     g1 = Seq_act_g(mus, F)
#     g1.init()
#     g2 = Seq_act_g(mus, F)
#     g2.allam = True 
#     g2.init()
#     a = g1.log["LENGTH"]
#     b = g2.log["LENGTH"]
#     if b < a :
#         if ag is None:
#             ag = g1 
#             bg = g2         
#         if g1.log["LENGTH"] < ag.log["LENGTH"]:
#             ag = g1 
#             bg = g2
#         rap = 100*b/a
#         x.append(rap)        


"""
We find that if we sort AL clauses by the ones which variables 
have the most clause-variable successors , and use this order 
in seq act graph, it gives a short explanation 
"""
# n,k = 6,2
# err = 0
# NV = 20000 
# nc = {3:0,4:0,5:0,6:0}
# for _ in tqdm(range(NV)):
#     p = find_unsat(n,k)
    
#     F = Formula(n,p,k,"dir")
#     mus = retrieve_mus(F)
#     nc[ nbalinmus(mus) ] += 1
#     # while havesameimp(mus):
#     #     shuffle(F.cnf)
#     #     mus = retrieve_mus(F)

#     simp = SAT_Imp_Graph(mus, F)
    
#     order = sort_al_bynbsucc(simp)
#     g = Seq_act_g(mus, F, ALorder=order)
#     g.init()
#     h = Seq_act_g(mus, F,ALorder = order[::-1])
#     h.init()
#     if h.log["LENGTH"] < g.log["LENGTH"]:
#         err += 1 
#     else:
#         raise ValueError
# print()
# print("Sorting at-least clauses by nb of variable-nodes that have the most successors")
# print("Percentage of cases where higher nb of vars is better than random")
# print(100*err/NV)


"""
When choosing a MUS that minimizes the sum of lengths of all 
clauses , it usually gives a short explanation in the sat imp 
graph 
"""
def totsum(mus):
    return sum([sum([1 for var in clause if var > 0]) for clause in mus])
# n,k=6,2
# err = 0
# err2 = 0
# NT = 500
# for _ in tqdm(range(NT)):
#     p = find_unsat(n,k)
#     F = Formula(n,p,k,"res")

#     mus = find_mingloblenmus(F)
#     g = SAT_Imp_Graph(mus, F)
#     g.propagate()
    
#     mus2 = find_mingloblenposmus(F)
#     gg = SAT_Imp_Graph(mus2, F)
#     gg.propagate()

#     start = clock()
#     for _ in range(100):

#         shuffle(F.cnf)
#         mu = retrieve_mus(F)
#         h = SAT_Imp_Graph(mu, F)
#         h.propagate()
        
#         # if h.log["LENGTH"] < g.log["LENGTH"]:
#         #     err += 1
        
#         if totsum(mu) < totsum(mus2):
#             raise ValueError
#         if h.log["LENGTH"] < gg.log["LENGTH"]:
#             err2 += 1
#             print("I",end="")
#             if totsum(mus2) == totsum(mu):
#                 print("J")
#             # else:
#             #     raise ValueError

# print("choosing a mus that minimizes the sum of lengths of clauses")
# print(100-100*err/NT)


# for n in range(4,16,2):
#     for k in range(2,n,2):
#         print("n,k=",n,k)
#         for _ in tqdm(range(1000),leave=False):
#             p = find_unsat(n, k)
#             F = Formula(n, p, k, "res")
#             G = reduce_F(F)
#             if solve(F.cnf).status != solve(G.cnf).status:
#                 pass


# while 1:
#     n = 8 
#     k = 2 
#     p = find_unsat(n,k)
#     F = Formula(n, p, k, "res")
#     G = reduce_F(F)
#     musA = retrieve_mus(F)
#     musB = retrieve_mus(G)
#     A = SAT_Imp_Graph(musA, G); A.propagate()
#     B = SAT_Imp_Graph(musB, G); B.propagate()

#     if A.log["LENGTH"] < B.log["LENGTH"] and A.log["LENGTH"] < 30:
#         break


""" 
Manually check why some preferences profile can't have less than x AL clauses
""" 
# n = 6
# k = 2
# p= find_unsat(n,k)
# F = Formula(n,p,k,'dir')
# while find_mini_nb_clauses(F.cnf,prog=False)[0] < 4:
#     p = find_unsat(n,k)
#     F = Formula(n,p,k,'dir')
# mus = retrieve_mus(F)
# while nbalinmus(mus) > 4:
#     mus = retrieve_mus(F)
# sort_cnf(mus)

# al,am,rk = sep_c(F.cnf)
# for a in mus[-1]:
#     for b in mus[-2]:
#         for c in mus[-3]:
#             vv = [a,b,c]
#             v = set([-a,-b,-c])
#             ag = set()
#             print(translate_cnf([[el] for el in vv]),end=" ")
#             for var in v:
#                 i,j,_ = get_ij_from_k(var)
#                 ag.add(i)
#                 ag.add(j)
#             if any([set(clause).issubset(v) for clause in am]) :
#                 print("AM")
#             elif any([set(clause).issubset(v) for clause in rk]) :
#                 print("RK")
#             else:
#                 print("X")
                

"""
Sorting clauses by most variables that lead directly 
to B is beneficial to explanation length 
"""
# n = 10
# k = 2 
# err  = 0
# final = 0
# vals = []
# for _ in tqdm(range(2000)):
#     p = find_unsat(n,k)
#     F = Formula(n,p,k,"res")
#     mus = retrieve_mus(F)
#     if havesameimp(mus): continue
#     final += 1
#     h = SAT_Imp_Graph(mus, F)
#     o = find_order_al_c(h)

#     h = Seq_act_g(mus, F, ALorder=o)
#     h.init()
    
#     good = True 
#     mini =float("inf")
#     for _ in range(5):
#         g = Seq_act_g(mus, F, ALorder=None)
#         g.init() 
#         mini = min(mini, g.log["LENGTH"])
#         if not h.log["LENGTH"] <= g.log["LENGTH"]:
#             good = False 
#             break 
#     if good:
#         err += 1
#         vals.append( 100 *  h.log["LENGTH"] / mini)
# print("Choosing in priority clauses that have the most variables that lead directly to B in Seq Act")
# print(100*err/final)


def length_random_plus(mus,F):
    length = float("inf")
    for _ in range(10):
        s =Seq(mus, F)
        s.init()
        length = min(length, s.log["LENGTH"])
    return length

def length_random(mus,F):
    s = Seq(mus, F)
    s.init()
    length = s.log["LENGTH"]
    return length

def length_maxtoB(mus,F,satimp):
    o = h_minContrad(satimp)
    s = Seq(mus, F,ALorder=o)
    s.init()
    length = s.log["LENGTH"]
    return length 

def length_maxclauselink(mus,F,satimp):
    o = h_maxVarConnectSum(satimp)
    s = Seq(mus, F,ALorder=o)
    s.init()
    length = s.log["LENGTH"]
    return length 

""" 
Check heuristics performance - with multithreading
"""
# def myxp(n,k):
#         F,mus = generate_instance(n, k, "dir",mus=True)
#         mu = nbalinmus(mus)
#         sat = SAT_Imp_Graph(mus, F)
#         a = length_random(mus, F)
#         b = length_random_plus(mus, F)
#         # c = length_maxtoB(mus, F, sat)
#         d  = length_maxclauselink(mus, F, sat)
#         return (mu,a,b,d)
# if __name__ == "__main__":
#     vals = {}
#     for n in [8]:
#         vals[n] = {}
#         for k in range(2,7,2):
#             d = datetime.now()
#             dh,dm,ds = d.hour,d.minute,d.second
#             print(f"started n={n}, k={k} at {dh}:{dm}:{ds}")
#             t1 = clock()
#             tries = []
#             musvals = []
#             vals2 = {"random":[],"randomP":[],"maxtoB":[],"maxclause":[],"I":[]}
#             NUM_RUNS = 500 
#             with ProcessPoolExecutor() as executor:
#                 futures = [executor.submit(myxp,n,k) for _ in range(NUM_RUNS)]
#                 for future in tqdm(as_completed(futures), total=NUM_RUNS):
#                     mu,a,b,d = future.result()
#                     vals2["random"].append(a)
#                     vals2["randomP"].append(b)
#                     # vals2["maxtoB"].append(c)
#                     vals2["maxclause"].append(d)        
#                     musvals.append(mu)
#             vals[n][k] = (vals2,sum(musvals)/len(musvals))



""" 
Make stats on the lengths of CNF and random MUSes for the 3 formulations
""" 

# vals = {}
# for n in reversed(range(6,20,2)):
#     vals[n] = {}
#     kvals = list(range(2,n,2))
#     if len(kvals) > 4 :
#         kvals = list(range(2,n,4))
#     for k in kvals:
#         dic = {"dirF":[],"dirM":[],"resF":[],"resM":[],"carF":[],"carM":[]}
#         print("n k",n,k)
#         a,b,c = [],[],[]
#         for _ in tqdm(range(1000)):
#             p = find_unsat(n,k)
#             Fd = Formula(n,p,k,"dir")
#             md = retrieve_mus(Fd)
#             Fr = Formula(n,p,k,"res")
#             mr = retrieve_mus(Fr)
#             Fc = Formula(n,p,k,"car")
#             mc = retrieve_mus(Fc)
#             ld,lmd = len(Fd.cnf) , len(md)
#             lr,lmr = len(Fr.cnf) , len(mr)
#             lc,lmc = len(Fc.cnf) , len(mc)
#             dic["dirF"].append( ld ) ; dic["dirM"].append( lmd )
#             dic["resF"].append( lr ) ; dic["resM"].append( lmr )
#             dic["carF"].append( lc ) ; dic["carM"].append( lmc )
            
#             # ga = Seq_act_g(md, Fd); ga.init()
#             # gb = Seq_act_g(mr, Fr); gb.init()
#             # gc = Seq_act_g(mc, Fc); gc.init()
#             # a.append(ga.log["LENGTH"])
#             # b.append(gb.log["LENGTH"])
#             # c.append(gc.log["LENGTH"])
            
#         # plt.clf()
#         # plt.plot(a,label = "Direct")
#         # plt.plot(b,label = "restriction")
#         # plt.plot(c,label = "Characterization")
#         # plt.title(f"Considering n = {n}, k = {k}")
#         # plt.legend()
#         # plt.show()
#         vals[n][k] = dic





"""
Run some instances  
"""
# a = []
# b = []
# for _ in tqdm(range(200)):
#     n = 10
#     k = 2 
#     F,mus = generate_instance(n, k, "car",mus=True)

#     if havesameimp(mus):
#         op += 1
#     g = Seq_act_g(mus, F)
#     t1 = clock()
#     g.init()
#     t2 = clock()
#     le = g.log["LENGTH"]
#     a.append(t2-t1)
#     b.append(le)


""" 
Find times where Seq act is better/equal/worse than sat imp 
""" 
# n = 8
# k = 2
# TOT = 100
# nb   = 0
# nbeq = 0
# for _ in tqdm(range(100)):
#     F,mus = generate_instance(n,k,"res",mus=True)
 
#     G = SAT_Imp_Graph(mus, F); G.textual = False; G.propagate()
#     Gs = Seq_act_g(mus, F); Gs.mktxt = False; Gs.init()
#     if Gs.log["LENGTH"] < G.log["LENGTH"]:
#         nb += 1 
#     elif Gs.log["LENGTH"] == G.log["LENGTH"]:
#         nbeq += 1

        
# percbet = 100 * nb / TOT 
# perceq  = 100 * nbeq / TOT 
# ot      = 100 * (TOT-nb-nbeq) / TOT 
# print("Nb of Seq act is better,",percbet)
# print("Nb of Seq act is equal,",perceq)
# print("Nb of Seq act is worse,",ot)



""" 
Check if reducing a CNF by removing clauses that are included by others
will make it better to solve 
"""

# vals = {}
# for n in range(4,13,2):
#     vals[n] = {}
#     for k in range(2,n,2):
#         print(f"started n={n}, k={k}")
#         lengths = []
#         Glengths = []
#         for _ in tqdm(range(500)):
#             F = generate_instance(n,k,"car")
#             G = reduce_F(F)
#             lengths.append(len(F.cnf))
#             Glengths.append(len(G.cnf))
#         vals[n][k] = (lengths,Glengths)

# n = 10
# k = 2
# count = 0
# co = 0
# for _ in tqdm(range(500)):
#     F,mus = generate_instance(n, k, "car",mus=True)
#     Fr = Formula(n,F.p,k,"res")
#     musr = retrieve_mus(Fr)
#     g = Seq_act_g(mus, F); g.init()
#     h = Seq_act_g(musr, Fr); h.init()
#     if g.log["LENGTH"] > h.log["LENGTH"]:
#         count += 1 
#     if g.log["LENGTH"] == h.log["LENGTH"]:
#         co += 1 
# print(count,co,"/500")
    

# k = 2
# for n in range(4,50,2):
#     print("n=",n)
#     for tries in tqdm(range(1000), leave=False):
#         F = generate_instance(n, k, "res")
#         if find_mini_nb_alloc_clauses(F.cnf,prog=False)[0] == 1:
#             break 
#     if tries == 999:
#         print("impossible")
#         break
#     print("done on",tries,"tries")


""" 
Count nb of each type of clause in explanation 
""" 
# n = 4
# k = 1
# F = generate_instance(n, k, "dir")
# alloc,others = sep_alloc_from_cnf(F.cnf)
# for arr in combinations(alloc, 3):
#     newC = list(arr) + others
#     if not solve(newC).status :
#         ccnf = CNF(from_clauses=newC)
#         with OptUx(ccnf.weighted()) as optux:
#             mini = float("inf")
#             vals = set()
#             for mus in optux.enumerate():
#                 if mini == float("inf"):
#                     mini = len(mus)
#                 elif mini < len(mus):
#                     break
#                 nu = str([len(el) for el in sep_c([newC[i-1] for i in mus])])

#                 if nu not in vals:
#                     print(nu)
#                     vals.add(nu)
#                     if len(vals) > 1:
#                         raise ValueError
#     break


# n = 14
# k = 2
# F = generate_instance(n, k, "dir")
# alloc,others = sep_alloc_from_cnf(F.cnf)
# for arr in combinations(alloc, 3):
#     newC = list(arr) + others
#     if not solve(newC).status :
#         ccnf = CNF(from_clauses=newC)
#         with OptUx(ccnf.weighted()) as optux:
#             mini = float("inf")
#             vals = set()
#             for mus in optux.enumerate():
#                 print(len(mus))
#                 break 
#     break


# n =6
# k = 1
# F = generate_instance(n, k, "dir")
# alloc,others = sep_alloc_from_cnf(F.cnf)

# for arr in combinations(alloc, 3):
#     newC = list(arr) + others
    
#     clauses = []
#     if not solve(newC).status :
#         others = [set([-var for var in clause]) for clause in others]
#         prodcount = {}
#         for vals in product(*arr):
#             if len(set(vals)) == 2:
#                 v = str(sorted(set(vals)))
#                 if v not in prodcount:
#                     prodcount[v] = 1
#         break


# n = 8
# k = 8
# for _ in tqdm(range(1000)):
#     F = generate_instance(n, k, "dir")
#     if find_mini_nb_alloc_clauses(F.cnf)[0] > 3:
#         print("stop")
#         break 


# for n in [4,6,8,10,12,14,16,18,20]:
#     for k in range(2,n-1,2):
#         F = generate_instance(n, k, "car")
#         oldlen = []
#         newlen = []
        
#         for _ in tqdm(range(1000))



# vals = load_obj("Fmuscompvals")
# for n in vals:
#     for k in vals[n]:
#         plotF = []
#         plotM = []
#         for key in vals[n][k]:
#             # title = f"With n={n} k={k} for {key}"
#             # plt.clf()
#             # plt.plot(vals[n][k][key])
#             # plt.title(title)
#             # plt.show()
#             if key.endswith("M"):
#                 plotM.append(vals[n][k][key])
#             else:
#                 plotF.append(vals[n][k][key])
#         plt.xticks(range(3),["dir","car","ref"])
#         plt.title(str(n) + " " + str(k) + "for F")
#         plt.boxplot(plotF)
#         plt.show()
        
#         plt.xticks(range(3), ["dir","car","ref"])
#         plt.title(str(n) + " " + str(k) + "for M")
#         plt.boxplot(plotM)
#         plt.show()

# # Sample data
# data = [[7, 8, 9, 10, 11], [1, 2, 5, 6, 7]]

# # Create the boxplot
# plt.boxplot(data)

# # Set x-axis label
# plt.xlabel("Group")

# # Set x-tick labels (optional, for multiple box plots)
# plt.xticks([1, 2], ["Group A", "Group B"])

# # Show the plot
# plt.show()

# n,k = 8,2
# vals = [ [],[],[],[],[],[] ]
# for _ in tqdm(range(300)):
#     F,mus = generate_instance(n, k, "dir",mus=True)
#     g1 = Seq_act_g(mus, F); g1.setH(h_maxClauseHeur1); g1.init()
#     g2 = Seq_act_g(mus, F); g2.setH(h_maxClauseHeur2); g2.init()
#     g3 = Seq_act_g(mus, F); g3.setH(h_maxClauseHeur3); g3.init()
#     g4 = Seq_act_g(mus, F); g4.setH(h_maxClauseHeur4); g4.init()
#     vals[0].append( g1.log["LENGTH"] )
#     vals[1].append( g2.log["LENGTH"] )
#     vals[2].append( g3.log["LENGTH"] )
#     vals[3].append( g4.log["LENGTH"] )
#     vals[4].append( length_random(mus, F) )
#     vals[5].append( length_random_plus(mus, F) )
    
# # v = load_obj()
# v = vals
# for i,el in enumerate(v):
#     plt.plot(el,label="H_"+str(i))
# plt.legend()
# plt.show()
# def p(n):
#     a = n-1
#     b = factorial(n-2)
#     c= b**(n-2)
#     d = factorial(a)**n
#     return (a*b*c)/d
# vals=v
# for i in range(len(vals)):
#     for j in range(len(vals)):
#         if i==j: continue 
#         if all([vals[i][k] >= vals[j][k] for k in range(len(vals[i]))]):
#             print(i,j)


# n ,k= 12,2 
# for _ in tqdm(range(10)):
#     F = generate_instance(n, k, "dir")
#     G = generate_instance(n, k, "res")
#     le = len([1 for clause in F.cnf if not isrkef(clause)])
#     print(le)
#     print(len(F.cnf)-le)
#     print(len(G.cnf)-le)
#     print("================")


# n = 4
# k = 2 
# F = generate_instance(n, k, "dir")
# C = CNF(from_clauses=F.cnf)
# with OptUx(C.weighted()) as optux:
#     best = None
#     for mus in optux.enumerate():
#         cost = optux.cost 
#         if best is None: best = cost 
#         elif cost > best: break 
#         if mus[:3] == [1,2,3]:
#             mus = [F.cnf[i-1] for i in mus]
#             break 
    
# if type(mus[0]) == int: raise ValueError
# al,am,rk = sep_c(mus)
# am = [set(el) for el in am]
# rk = [set(el) for el in rk]
# clauses = {}
# for varli in product(*al):
#     li = set([-el for el in varli])
#     c = None
#     clau = None
#     names = [get_ij_from_k(v) for v in varli]
#     names = [f"X_{i}{j}" for i,j,_ in names]
#     for clause in am:
#         if clause.issubset(li):
#             c = "AM"
#             clau = clause
#             break
#     if c is None:
#         for clause in rk:
#             if clause.issubset(li): 
#                 c = "RK"
#                 clau = clause 
#                 break 
#     if str(clau) not in clauses:
#         clauses[str(clau)]= 0
#     clauses[str(clau)] += 1
#     print(names,":",c)


# n = 4
# k = 2 
# F = generate_instance(n, k, "res")
# if any([len(F.e[el]) > 1 for el in F.e]):
#     print("ok")

################
# STARTED EXPS #
################
""" 
For the car formulation, store len mus, nb al clauses in a mus, and the length of expl 
from sat imp and seq imp graphs 
"""
def myxp(n,k):
    F,mus = generate_instance(n, k, "res",mus=True)

    ga = SAT_Imp_Graph(mus, F)
    ga.propagate()
    gb = Seq(mus, F)
    gb.init()
    return len(mus) , nbalinmus(mus), ga.log["LENGTH"], gb.log["LENGTH"]


# vals = {}
# errs = {}
# for n in range(4,21,4):
#     vals[n] = {}
#     errs[n] = {}
#     kvals = list(range(2,n,2))
#     if len(kvals) > 3:
#         kvals = list(range(2,n,4))
#     for k in kvals:
#         print(f'n={n},k={k}')
#         errs[n][k] = 0
#         vals2 = {"lenmus":[],"nbal":[],"lensatimp":[],"lenseq":[]}
#         for _ in tqdm(range(1000)):
#             try:
#                 a,b,c,d = myxp(n, k)
#                 vals2["lenmus"].append(a)
#                 vals2["nbal"].append(b)
#                 vals2["lensatimp"].append(c)
#                 vals2["lenseq"].append(d)
#             except:
#                 errs[n][k] += 1
#         vals[n][k] = vals2



# for n in range(4,21,4):
#     vals[n] = {}
#     kvals = list(range(2,n,2))
#     if len(kvals) > 3:
#         kvals = list(range(2,n,4))
#     for k in kvals:
#         print(f'fill n={n},k={k}',end=" ")
#         while len(vals[n][k]) < 1000:
#             try:
#                 a,b,c,d = myxp(n, k)
#                 vals[n][k]["lenmus"].append(a)
#                 vals[n][k]["nbal"].append(b)
#                 vals[n][k]["lensatimp"].append(c)
#                 vals[n][k]["lenseq"].append(d)
#             except :
#                 errs[n][k] += 1
#         print(" done")
    
# svv = (vals,errs)
# store_obj(svv,"firstres")
# print("ONE DONE ")

# """ 
# Find the minimum number of alloc clauses in MUSes of diffrent formulations 
# """
# vals = {}
# print("start",datetime.now())
# for n in range(4,21,4):
#     vals[n] = {}
#     kvals = list(range(2,n,2))
#     if len(kvals) > 3:
#         kvals = list(range(2,n,4))
#     for k in kvals:
#         nb = []
#         vals[n][k] = {}
#         for form in ["dir","car","res"]:
#             vals[n][k][form] = []
#         print(f'n={n},k={k}')
#         for _ in tqdm(range(1000)):
#             p = find_unsat(n, k)
#             for form in ["dir","car","res"]:
#                 F = Formula(n, p, k, form)
#                 vals[n][k][form].append( find_mini_nb_alloc_clauses(F, prog=False)[0] )
                

# store_obj(vals,"second")
# print("TWO DONE ")

""" 
For the res formulation, store len mus, nb al clauses in a mus, and the length of expl 
from sat imp and seq imp graphs 
"""
# vals = {}
# errs = {}
# for n in range(4,19,4):
#     vals[n] = {}
#     errs[n] = {}
#     kvals = list(range(2,n,2))
#     if len(kvals) > 3:
#         kvals = list(range(2,n,4))
#     for k in kvals:
#         print(f'n={n},k={k}')
#         lenmu,nbal,lensatimp,lenseqa = [],[],[],[]
#         vals[n][k] = {}
#         errs[n][k] = 0
#         for _ in tqdm(range(1000)):
#             F,mus = generate_instance(n, k, "res",mus=True)
#             try:
#                 ga = SAT_Imp_Graph(mus, F)
#                 ga.propagate()
#                 gb = Seq_act_g(mus, F)
#                 gb.init()
                
#                 lenmu.append( len(mus) )
#                 nbal.append( nbalinmus(mus) )
#                 lensatimp.append( ga.log["LENGTH"] )
#                 lenseqa.append( gb.log["LENGTH"] )
#             except: 
#                 errs[n][k] += 1
#         vals[n][k]["lenmus"] = lenmu 
#         vals[n][k]["nbal"] = nbal 
#         vals[n][k]["lensatimp"] = lensatimp
#         vals[n][k]["lenseq"] = lenseqa
            
# store_obj(vals,"third")
# print("THREE DONE ")



""" 
Compare Sat Imp from random MUSes for the three formulations 
""" 
# vals = {}
# print("start",datetime.now())
# for n in range(4,21,4):
#     vals[n] = {}
#     kvals = list(range(2,n,2))
#     if len(kvals) > 3:
#         kvals = list(range(2,n,4))
#     for k in kvals:
#         nb = []
#         vals[n][k] = {}
#         for form in ["dir","car","res"]:
#             vals[n][k][form] = {}
#             vals[n][k][form]["lenmus"] = []
#             vals[n][k][form]["nbal"] = []
#             vals[n][k][form]["len"] = []
#         print(f'n={n},k={k}')
#         for _ in tqdm(range(1000)):
#             p = find_unsat(n, k)
#             for form in ["dir","car","res"]:
#                 F = Formula(n, p, k, form)
#                 mus = retrieve_mus(F)
#                 vals[n][k][form]["lenmus"].append(len(mus))
#                 vals[n][k][form]["nbal"].append( nbalinmus(mus) )
                
#                 if form == "dir":
#                     vals[n][k][form]["len"].append( lendir(n, nbalinmus(mus)) )
#                 else:
#                     try:
#                         g = SAT_Imp_Graph(mus, F); g.propagate()
#                         vals[n][k][form]["len"].append( g.log["LENGTH"] )
#                     except:
#                         for form2 in ["dir","car","res"]:
#                             if form2==form: break 
#                             if len(vals[n][k][form]["len"]) <  len(vals[n][k][form2]["len"]):
#                                 for key in vals[n][k][form2]:
#                                     del vals[n][k][form2][key][-1]
#                         break
# store_obj(vals,"fourth")
# print("FOUR DONE ")
                

""" 
Find the minimum size of a MUS  
"""
# vals = {}
# print("start",datetime.now())
# for n in range(4,21,4):
#     vals[n] = {}
#     kvals = list(range(2,n,2))
#     if len(kvals) > 3:
#         kvals = list(range(2,n,4))
#     for k in kvals:
#         nb = []
#         vals[n][k] = []
#         print(f'n={n},k={k}')
#         for _ in tqdm(range(1000)):
#             F = generate_instance(n, k, "car")
#             vals[n][k].append( len(find_mingloblenmus(F)) )
                

# store_obj(vals,"fifth")
# print("DONE ")


# Faire dessin avec tous ce qu'on a trouve 
# resultats, contre exemples, ce qu'on sait/ sait pas / cherche... 
            
            
# a = load_obj("fifth")


""" 
Check max mus 
"""
# i = 0 
# while 1:
#     if i%100 == 0:
#         print(i)
#     F = generate_instance(8,float("inf"),"dir")
#     found = False
#     # for _ in range(20):
#     #     mus = retrieve_mus(F)
#     #     if nbalinmus(mus) <= 4:
#     #         found = True 
#     #         break 
#     if not found:
#         als,o = sep_alloc_from_cnf(F.cnf)
#         # print("check")
#         if not any([not solve(list(comb)+o).status for comb in combinations(als,4)]):
#             print("aah")
#             break
#     i += 1 

# p = ((1, 4, 5, 3, 2, 6, 7), (0, 2, 4, 3, 6, 5, 7), (1, 3, 6, 4, 5, 0, 7), (6, 4, 5, 0, 2, 7, 1), (6, 0, 1, 5, 7, 2, 3), (6, 0, 2, 3, 1, 4, 7), (3, 5, 2, 4, 0, 1, 7), (6, 4, 3, 5, 2, 1, 0))
# F = Formula(8, p, float("inf"), "dir")
# a,b = sep_alloc_from_cnf(F.cnf) 
# for clauses in combinations(a,5):
#     print( solve(list(clauses)+b).status )
    # print([F.e[str(clause)] for clause in clauses])
    # for comb in product(*clauses):
    #     vals = set([-e for e in comb])
    #     po = "X"
    #     for clause in b:
    #         if set(clause).issubset(vals):
    #             po = "O"
    #             break 
    #     if po == "X":
    #         print([get_ij_from_k(el) for el in set(comb)])
    # print("=========") 



# for _ in tqdm(range(100)):
#     p = find_unsat(n, k)
#     F = Formula(n,p,k,"dir")
#     val = nbalinmus( find_minalmus(F) ) 
#     if val > 3:
#         break




# n=6
# ps = []
# for _ in tqdm(range(3000)):
#     p = find_unsat(n, k)
#     F = Formula(n, p, k, "dir")
#     if nbalinmus( find_minalmus(F) ) > 3:
#         break

""" 
example for mus 4 AL 
"""

# n=6    
# p= ((4, 3, 1, 2, 5), (4, 2, 3, 5, 0), (4, 0, 3, 5, 1), (2, 4, 1, 0, 5), (2, 1, 3, 0, 5), (4, 0, 2, 3, 1))
# F = Formula(n,p,k,"dir")
# mus =[[1, 2, 4, 7, 11], [1, 3, 5, 8, 12], [4, 5, 6, 10, 14], [11, 12, 13, 14, 15], [-14, -11], [-12, -1], [-14, -4], [-15, -8], [-11, -4], [-13, -6], [-11, -5], [-11, -6], [-11, -10], [-14, -1], [-12, -2], [-14, -2], [-15, -1], [-13, -5], [-13, -4], [-13, -10], [-15, -3], [-12, -4], [-15, -5], [-12, -7], [-14, -7]]
# a,b = sep_alloc_from_cnf(F.cnf)
# for al in combinations(a,3):
#     print(  solve(list(al)+b).status )
#     print([F.e[str(acc)] for acc in al])
#     for vals in product(*al):
#         vals = set([-el for el in vals])
#         clau = False
#         for clause in b:
#             clause = set(clause)
#             if clause.issubset(vals):
#                 clau = True 
#                 break 
#         if not clau:
#             print([get_ij_from_k(v) for v in vals])
#             break




# n=6
# F = generate_instance(n, k, "res")
# for _ in tqdm(range(1000)):
#     mus1 = retrieve_mus(F)
#     while nbalinmus(mus1) != 1:
#         mus1 = retrieve_mus(F)
#     sort_cnf(mus1)
#     mus2 = retrieve_mus(F)
#     sort_cnf(mus2)
#     while nbalinmus(mus2) != 1 or mus2==mus1:
#         mus2 = retrieve_mus(F)
#         sort_cnf(mus2)
#     a = SAT_Imp_Graph(mus1, F)
#     b = SAT_Imp_Graph(mus2, F)
#     a.propagate()
#     b.propagate()
#     if a.log["LENGTH"] != b.log["LENGTH"]:
#         break
""" 
Instance with 3AL in MUS 
"""  
# n,k = 6,2 
# pr = ((2, 1, 3, 4, 5), (0, 2, 5, 4, 3), (4, 3, 1, 5, 0), (1, 0, 5, 4, 2), (5, 0, 2, 1, 3), (3, 0, 4, 2, 1))
# Fr = Formula(n,pr,k,"dir")
# ar,br = sep_alloc_from_cnf(Fr.cnf)
# br = [set(el) for el in br]

# for clauses in combinations(ar,3):
#     print([ar.index(clause) for clause in clauses])
#     for comb in product(*clauses):
#         vals = set([-e for e in comb])
#         po = "X"
#         for clause in br:
#             if clause.issubset(vals):
#                 po = "O"
#                 break 
#         if po == "X":
#             print([get_ij_from_k(el) for el in set(comb)])
#     print("=========")
    
# agents = set(range(n))
# allli = []
# for agli in combinations(agents,3):
#     agli = set(agli)
#     print("trying",agli)
#     foundit = False 
#     for agent in agents:
#         agnew = deepcopy(agli)
#         agnew.add(agent)
#         if len(agnew) != 4: continue 
        
#         remov = [ag for ag in agents if ag not in agnew ]
#         newp = remove_ags_from_p(pr, remov)
#         F = Formula(4, newp, k, "dir") 
#         if not solve(F.cnf).status :
#             foundit = True 
#             break 
#     if not foundit:
#         raise ValueError


""" 
Check iteratively the smallest possible MUS 
""" 
# n,k = 12,2 
# nbi = 0
# while 1:
#     F = generate_instance(n, k, "dir")
#     mini = float("inf")
#     while 1:
#         le = nbalinmus(  retrieve_mus(F) )
#         if le < mini:
#             mini = le 
#             print(mini)
#         if mini <= n/2+1:
#             nbi += 1
#             break 
#     print("done")
    

""" 
Check the 3 bound 
""" 
# n,k = 6,2 
# while 1:
#     F = generate_instance(n, k, "dir")
#     a,b = sep_alloc_from_cnf(F.cnf)
#     for comb in tqdm(combinations(a,3), total=nbcomb(n,3),leave=False):
#         new = list(comb) + b 
#         F.cnf = new
#         if not solve(new).status:
#             val = nbalinmus( find_minalmus(F) )
#             print(val)
#             if val == 3:
#                 break


    
    
    

# aa,ab,pa,musa = None,None ,None,None
# ba,bb,pb,musb = None,None,None,None
# n,k = 6,2
# for _ in tqdm(range(100)):
#     F,mus = generate_instance(n, k, "car",mus=True)
#     a = SAT_Imp_Graph(mus, F); a.propagate()
#     b = Seq_act_g(mus, F); b.init()
#     lena,lenb = a.log["LENGTH"], b.log["LENGTH"]
#     if min(lena,lenb) < 20:
#         if lena < lenb:
#             aa = a 
#             ab = b 
#             pa = F.p 
#             musa = mus
#         if lena > lenb:
#             ba = a 
#             bb = b
#             pb = F.p 
#             musb = mus
#     if len(mus) == 3:
#         break
    # if not None in [aa,ba]:
    #     break
    
"""
Proof of n clauses for a mus of restriction formulation
"""
# for _ in tqdm(range(1000)):
#     n,k = 6,7
#     p = generate_preferences(n)
#     p = [list(el) for el in p]
    
#     if p[1][0] != 0:
#         idx = p[1].index(0)
#         p[1][0], p[1][idx] = p[1][idx],p[1][0]
    
#     if p[2][0] != 1:
#         idx = p[2].index(1)
#         p[2][0], p[2][idx] = p[2][idx],p[2][0]
#     modif = False
#     for i,el in enumerate(p):
#         if i!= 1 and p[i][0] == 0:
#             idx = -1  
#             while idx == -1: 
#                 idx = randint(1,n-2)
#                 if p[i][idx] == 0 or p[i][idx] == 1:
#                     idx = -1
#             p[i][0], p[i][idx] = p[i][idx], p[i][0]

#         if i!= 2 and p[i][0] == 1:
#             idx = -1  
#             while idx == -1: 
#                 idx = randint(1,n-2)
#                 if p[i][idx] == 0 or p[i][idx] == 1:
#                     idx = -1
#             p[i][0], p[i][idx] = p[i][idx], p[i][0]

#     F = Formula(n,p,k,"res")
#     if solve(F.cnf).status:
#         print()
#         for el in p:
#             print(el)
#         break


"""
Test
""" 
def find_mus(F): 
    """ 
    Optux minimise le weight 
    """ 
    wcnf = WCNF()
    cnf = CNF()
    W = len(F.cnf) * 10e5
    nb = 0
    for clause in F.cnf: 
        cnf.append(clause)

        wcnf.append( clause, weight = -W )

    maxi = -float("inf")
    with OptUx(wcnf, unsorted=False) as optux:
        for mus in optux.enumerate():
            mus = [F.cnf[i-1] for i in mus]
            if nbalinmus(mus) == F.n:
                print(mus)
                print(F.p)
                raise ValueError
            print(len(mus))
        print("======")


            # return [F.cnf[i-1] for i in mus]

    return maxi

# n = 6
# for _ in tqdm(range(100)):
#     F = generate_instance(n, k, "res")
#     le = find_mus(F)
#     break

""" 
n=6 res mus with $n$ at least clauses 
""" 
# p=((3, 4, 1, 2, 5), (5, 3, 2, 0, 4), (3, 5, 1, 0, 4), (5, 0, 4, 1, 2), (5, 1, 0, 2, 3), (3, 2, 0, 4, 1))
# mus= [[1, 2, 4, 7, 11], [1, 3, 5, 8, 12], [2, 3, 6, 9, 13], [4, 5, 6, 10, 14], [7, 8, 9, 10, 15], [11, 12, 13, 14, 15], [-8, -7], [-4, -2], [-8, -1], [-7, -1], [-15, -14], [-14, -4], [-15, -9], [-2, 5, 12], [-11], [-5], [-3, 14], [-9, 4], [-13], [-3, 15], [-6, 14], [-10], [-12, 15]]
    



# val = r""" 
# 0: \quad 5 \succ 1 \succ 4 \succ 2 \succ 3 \\
# 1: \quad 5 \succ 4 \succ 3 \succ 0 \succ 2 \\
# 2: \quad 0 \succ 3 \succ 1 \succ 5 \succ 4 \\
# 3: \quad 5 \succ 4 \succ 0 \succ 2 \succ 1 \\
# 4: \quad 5 \succ 1 \succ 0 \succ 2 \succ 3 \\
# 5: \quad 1 \succ 3 \succ 0 \succ 2 \succ 4 \\
# """

def convertp(s):
    s = s.split("\n")
    assert s[0] == " " and s[-1] == ""
    del s[0]; del s[-1]
    p = []
    for el in s:
        el = el.split(" ")
        del el[0]; del el[0]
        if el[-1] == "\\\\": del el[-1] 
        agval = []
        for ag in el:
            if ag == "\\succ": continue 
            elif ag.isnumeric():
                agval.append(int(ag))
            else:
                raise ValueError("Unrecognized:",ag) 
        p.append( tuple(agval) )
    return tuple(p)

def convertcnf(s):
    s = s.split("\n")
    assert s[0] == " " and s[-1] == ""
    del s[0]; del s[-1]
    cnf = []
    for el in s:
        clause = []
        el = el.split(" ")
        if el[-1] == "\\\\": del el[-1]
        for i, val in enumerate(el):
            if val=="\\neg" or val=="\\vee": continue
            elif val.startswith("&\\"): break
            elif val.startswith("x_{"):
                if val.endswith(":"):
                    val = val[3:-2]
                else:
                    val = val[3:-1]
                posi = True
                if len(val) != 2: raise ValueError("can't determine agent (could be xxy or xyy): " +str(val))
                if el[i-1]=="\\neg": posi = False 
                valu = get_k_from_ij(int(val[0]), int(val[1]))
                if not posi: valu = -valu 
                clause.append(valu)
            else:
                raise ValueError(val,"unknown")
        cnf.append(clause)
    return cnf


def generate_names(n):
    """
    Return a dict i:name for agent <i> and gives them a name
    """
    v = n // 2
    fnames = ["Fleur","Ana","Lou","Alba","Inès","Clara"]
    mnames = ["Dao","Tom","Louis","Alex","Pierre","Paul"]
    # chosen = sample(fnames,k=v) + sample(mnames, k=v)
    # shuffle(chosen)
    chosen = fnames[:v] + mnames[:v]
    print("names1", fnames[:v])
    print("names2", mnames[:v])
    return chosen

def make_namelist(n):
    """  
    Return dict to know what name correpsond to every label for agents
    """
    names = generate_names(n)
    return {f"Agent {i}":name for i,name in enumerate(names)} | {f"agent {i}":name for i,name in enumerate(names)} | {str(i):name for i,name in enumerate(names)}

def no_better_partner(p,m,agent):
    G = FormulaSRP(len(p), p, float("inf"),"res")
    clause = []

    for j in G.p[agent]:
        if j == m[agent]:
            break 
        clause.append( ordered(G.x, agent, j) )
    if clause == []:
        return [f"Agent {agent} already has their favorite partner"]
    clause = list(map(int,clause))
    # G.add_clause(clause, f"Agent {agent} must have a partner they prefer over {m[agent]}")
    G.add_clause(clause, f"PREF[{agent}]")
    if solve(G).status == True:
        return [f"There exists a fair matching where agent {agent} has a better partner, sorry!"]
    else:
        mus = retrieve_mus(G)
        Simp = SAT_Imp_Graph(mus, G)
        S = Seq(Simp,G)
        S.start()
        return S.text

if __name__=="__main__":
    find_unsat(n, k)