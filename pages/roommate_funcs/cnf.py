# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 15:28:54 2024

@author: sabatinofr
"""
import numpy as np 

from .roommate import rank

from .tools import cnf3_vars
from .tools import ordered



class FormulaSRP:
    def __init__(self,n,p,k,f,g=None):
        self.n = n 
        self.p = p
        self.k = k
        self.g = g
        self.f = f
        self.x = cnf3_vars(n)
        self.e = {}
        self.agents = list(range(n))
        if f=="dir": make_matching(self); make_rkef_dir(self)
        elif f=="res": make_matching(self); make_rkef_res(self)
        elif f=="car": make_atmost(self); make_car2(self)
        elif f=="lef": make_matching(self); make_lef(self)
        # elif f=="car2": make_atmost(self); make_car(self)
        else: raise ValueError(f"Choose a valid formula: {f} not in list")
        self.cnf = [eval(el) for el in self.e.keys()]
        # Reduce option 
        self.cnf = [set(clause) for clause in self.cnf]
        self.cnf = [sorted(clause) for clause in self.cnf if not any([issuperset(clause, el) for el in self.cnf if el!=clause])]
    
    def add_clause(self,clause,name=False):
        clause.sort()
        if str(clause) in self.e:
            if name: self.e[str(clause)].append(name)
        else:
            if name: self.e[str(clause)] = [name]
            self.cnf.append(clause)
            self.cnf.sort()
    
    def name(self,clause):
        return self.e[str(clause)][0]
    
    def add_pref(self, i,o):
        make_pref(self,i,o)
def issuperset(a,b):
    return b.issubset(a)

def make_atleast(fobj):
    agents = fobj.agents
    e = fobj.e 
    x = fobj.x
    # Each agent should be matched at least once
    for i in agents:
        clause = []
        for j in agents:
            if i > j:
                clause.append( x[i,j] )
            elif i < j: 
                clause.append( x[j,i] )
                
        eclause = str(sorted(list(map(int,clause))))
        xclause = "AL" + str(list([i]))
        if eclause in e:
            e[eclause].append(xclause)
        else:
            e[eclause] = [xclause]
def make_atmost(fobj):
    agents = fobj.agents
    e = fobj.e 
    x = fobj.x
    # Each agent should be matched at most once
    for i in agents:
        for j in agents:
            if j >= i: break
            for p in agents:
                if p == i or p == j: continue 
                if p < i and p < j:
                    clause = [-x[i,p], -x[j,p]] 
                elif p < i and p > j:
                    clause = [-x[i,p], -x[p,j]]
                elif p > i and p < j:
                    clause = [-x[p,i], -x[j,p]]
                elif p > i and p > j:
                    clause = [-x[p,i], -x[p,j]]

                eclause = str(sorted(list(map(int,clause))))
                xclause = "AM" + str([i,j,p])
                if eclause in e:
                    e[eclause].append(xclause)
                else:
                    e[eclause] = [xclause]
def make_matching(fobj):
    make_atleast(fobj)
    make_atmost(fobj)
    
                
def make_rkef_dir(fobj):
    agents = fobj.agents 
    P = fobj.p 
    e = fobj.e 
    k = fobj.k
    x = fobj.x
    for i in agents:
        for j in agents:
            if j == i: continue # An agent can't be envious of themself
            for p in agents:
                if p == i: continue # i cannot be matched to themself
                if p == j: continue # we have q != i and p==j => q==i
                for q in agents:
                    if q == j: continue # j cannot be matched to themself
                    if q == i: continue # r_i(q) not defined if q == i 
                    if q == p: continue # i and j can't be matched to the same agent
                    if rank(P,i,p) > rank(P,i,q) and rank(P,j,q) > min(k,rank(P,i,q)):
                        clause = [-ordered(x,i,p) , -ordered(x,j,q)]
    
                        eclause = str(sorted(list(map(int,clause))))
                        xclause = "rkefdir" + str([i,j,p,q])
                        if eclause in e:
                            e[eclause].append(xclause)
                        else:
                            e[eclause] = [xclause]

def make_rkef_res(fobj):
    agents = fobj.agents 
    P = fobj.p 
    e = fobj.e 
    k = fobj.k
    x = fobj.x
    for i in agents:
        for j in agents:
            if i == j: continue 
            for p in agents: 
                if p == i or p == j: continue
                if rank(P,i,p) > rank(P,j,p) or rank(P, i, p) > k:
                    clause = [-ordered(x,i,p)]
                    for l in agents:
                        if l == j: continue 
                        if rank(P,j,l) < rank(P,j,p):
                            clause.append(ordered(x, j, l))
    
                    eclause = str(sorted(list(map(int,clause))))
                    xclause = "rkefres" + str([i,j,p])
                    if eclause in e:
                        e[eclause].append(xclause)
                    else:
                        e[eclause] = [xclause]

def prefers(P,i,o1,o2):
    """ 
    return True if agent o1 >_i o2
    """
    return rank(P, i, o1) < rank(P, i, o2) 

def make_lef(fobj):
    agents = fobj.agents 
    P = fobj.p 
    e = fobj.e 
    k = fobj.k
    x = fobj.x
    g = fobj.g
    from .roommate_sat import get_ij_from_k
    for i in agents:
        for j in g[i]:
            for p in agents:
                if p == i: continue
                if p == j:continue
                clause = [ordered(x,i,pp) for pp in agents if pp != p and pp!=i and prefers(P, i, pp, p) ] # and prefers(P, i, o, op)
                clause = [-ordered(x,j,p)] + clause 
                eclause = str(sorted(list(map(int,clause))))
                print(f"clause agent {i} sees agent {j} for agent {p} ")
                echeck = eval(eclause)
                print(echeck)
                print([get_ij_from_k(k) for k in echeck])

                xclause = f"LEF[{i}_{j}_{p}]"
                if eclause in e:
                    e[eclause].append(xclause)
                else:
                    e[eclause] = [xclause]

    def add_pref(self,i,o):
        clause = make_pref(self,i,o)
        return clause 
def make_pref(F,i,o):
    agents = F.agents
    x = F.x 
    e = F.e 
    P = F.p
    clause = [ordered(x,i,k) for k in agents if k!= i and prefers(P,i,k,o)] 
    
    eclause = str(sorted(list(map(int,clause))))
    xclause = f"PREF[{i}]"

    if eclause in e:
        e[eclause].append(xclause)
    else:
        e[eclause] = [xclause]

    F.cnf = [sorted(eval(el)) for el in F.e.keys()]
    clause = eval(eclause)
    
    return clause


def make_car(fobj):
    agents = fobj.agents
    P = fobj.p 
    e = fobj.e
    k = fobj.k
    x = fobj.x
    
    # rk-EF constraint
    for i in agents:
        for j in agents:
            if i==j: continue
            for p in agents:
                if p==i: continue
                if p==j: continue 
                if not rank(P, i, p) > k: continue 
                clause = [- ordered(x, i, p)]
                for q in agents:
                    if q==j: continue 
                    if not rank(P, j, q) < rank(P, j, p): continue
                    clause.append( ordered(x, j, q) )

                eclause = str(sorted(list(map(int,clause))))
                xclause = "rkefcar" + str([i,j,p])
                if eclause in e:
                    e[eclause].append(xclause)
                else:
                    e[eclause] = [xclause]

    # r-EF constraint
    for i in agents:
        for p in agents:
            if p==i: continue 
            rip = rank(P, i, p)
            clause = [ordered(x, i, p)]
            for t in agents:
                if t==i: continue 
                if t==p: continue 
                if not rank(P,i,t) < rip: continue
                clause.append(ordered(x, i, t))
            for q in agents:
                if q==p: continue 
                if q==i: continue
                if not rank(P,q,p) <= rip: continue 
                clause.append(ordered(x,p,q))

            eclause = str(sorted(list(map(int,clause))))
            xclause = "ref" + str([i,p])
            if eclause in e:
                e[eclause].append(xclause)
            else:
                e[eclause] = [xclause]
            
def make_car2(fobj):
    agents = fobj.agents
    P = fobj.p 
    e = fobj.e
    k = fobj.k
    x = fobj.x

    for p in agents:
        clause = []
        pli = []
        for i in agents:
            if p==i: continue 
            if rank(P, i, p) == 1:
                clause.append( ordered(x,i,p) )

        if clause != []: 
            eclause = str(sorted(list(map(int,clause))))
            xclause = "ref2" + str([p])
            if eclause in e:
                e[eclause].append(xclause)
            else:
                e[eclause] = [xclause]
        else:
            for l in range(2,len(agents)):
                for i in agents:
                    if i==p: continue 
                    if rank(P, i, p) != l:
                        continue 

                    clause = []
                    for q in agents:
                        if q==i: 
                            continue 
                        if rank(P, i, q) > l:
                            continue 
                        clause.append( ordered(x,i,q) )

                    for j in agents:
                        if j==p: 
                            continue 
                        if rank(P, j, p) > l:
                            continue 
                        
                        if not ordered(x, j, p) in clause:
                            clause.append( ordered(x,j,p) )
                        
                    eclause = str(sorted(list(map(int,clause))))
                    xclause = "ref2" + str([p,l,i])
                    if eclause in e:
                        e[eclause].append(xclause)
                    else:
                        e[eclause] = [xclause]
