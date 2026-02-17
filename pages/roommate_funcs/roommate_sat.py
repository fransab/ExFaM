"""
Created on Tue Feb 13 15:29:15 2024

@author: sabatinofr
"""
from pysat.formula import CNF
from pysat.solvers import Glucose3, Minisat22

from pysat.examples.musx import MUSX
from pysat.examples.optux import OptUx

from .roommate import generate_preferences

from .cnf import FormulaSRP

import numpy as np
from tqdm import tqdm

from random import shuffle

def get_all_matchings(F):
    mods = find_all_models(F.cnf)
    return [get_matching(m) for m in mods]

def get_ij_from_k(k,human=False):
    """ 
    Retrieve X_(i,j) from X_k with symmetry 
    """
    pos = k > 0
    k = abs(k)
    i = 1
    while k > i*(i+1) / 2:
        i += 1
    j = int( k - (i-1)*i / 2 - 1)
    if human:
        return (i+1,j+1,pos)
    return (i,j,pos)
    

def get_k_from_ij(i,j,val=True):
    """ 
    Retrieve X_k from X_(i,j) with symmetry
    """
    i,j = max(i,j) , min(i,j)
    if not val:
        return -int(i*(i-1)/2 + j + 1)
    return int(i*(i-1)/2 + j + 1)


def find_all_models(cnf):
    """ 
    Given a cnf, returns all models that satisfy it 
    """ 
    models = []
    while 1:
        g = Glucose3()
        for el in cnf:
            g.add_clause(el)
        for model in models:
            g.add_clause([-lit for lit in model]) # Forbid all the models already found
        found_sol = g.solve()
        if not found_sol: break # All the models have been found
        models.append(g.get_model())
    return models

def co(i):
    return 1
def retrieve_mus(obj, fast = True, shuff=True):
    """ 
    Retrieve a set of clauses that is a MUS 
    """
    if type(obj) == list:
        clauses = obj
    else:
        clauses = obj.cnf
        
    if shuff: 
        shuffle(clauses)


    cnf = CNF(from_clauses=clauses)
    # g = Glucose3()
    # for clause in cnfx:
    #     g.add_clause(clause)
    # solved = g.solve()
    
    # if solved:
    #     return -1

    mus = None

    if fast:
        wncf = cnf.weighted()
        musx = MUSX(cnf.weighted(), verbosity=0)
        mus = musx.compute()
    else:
        with OptUx(cnf.weighted()) as optux:
            for mus in optux.enumerate():
                mus = mus
                break
        
    mus = [clauses[i-1] for i in mus] # Retrieve actual clauses instead of indices

    return mus


def find_sat(n,k):    
    """ 
    Find a SAT instance P of the roommate pb with n agents 
    """
    i = 0
    solved = False 
    while not solved:
        P = generate_preferences(n)
        cnf = FormulaSRP(n, P, k, "car").cnf
        g = Glucose3()
        for clause in cnf:
            g.add_clause(clause)
        solved = g.solve()
        i += 1 
    # print("Iterations needed to find SAT P:",i)
    return P 


def find_unsat(n,k):   
    """ 
    Find an UNSAT instance P of the roommate pb with n agents 
    """
    i = 0
    solved = True
    while solved:
        P = generate_preferences(n)
        cnf = FormulaSRP(n, P, k, "car").cnf
        g = Glucose3()
        for clause in cnf:
            g.add_clause(clause)
        solved = g.solve()
        i += 1 
    # print("Iterations needed to find UNSAT P:",i)
    return P 

def find_n_unsat(n,k, N_FIND,prog=False):
    if n < 4 or n == 4 and N_FIND > 480: raise ValueError("Try bigger numbers")
    Ps = set()
    if prog: pbar = tqdm(total = N_FIND)
    while len(Ps) < N_FIND:
        P = find_unsat(n, k)
        if P not in Ps:
            Ps.add(P)
            if prog: pbar.update(1)
    if prog: pbar.close()
    return Ps

def get_matching(model):
    """ 
    Retrieve a matching from the model of a CNF with symmetry and ensure it is valid
    """
    matching = {}

    for var in model:
        a,b,positive = get_ij_from_k(var)
        # a,b = val[abs(var)]
        if positive:
            if a in matching and matching[a] != b: raise ValueError("Matching inconsistant1") 
            else:                                  matching[a] = b 
            if b in matching and matching[b] != a: raise ValueError("Matching inconsistant2") 
            else:                                  matching[b] = a 
        else:
            if a in matching and matching[a] == b: raise ValueError("Matching inconsistant3") 
            if b in matching and matching[b] == a: raise ValueError("Matching inconsistant4") 
    
    return matching
            
def cnf3_to_latex(cnf):
    """ 
    translate cnf to latex 
    """
    clauses = []
    for clause in cnf:
        new = []
        for var in clause:
            i,j,pos = get_ij_from_k(var)
            if not pos:
                new.append("\\neg " + "X_{"+str(i)+str(j)+"}")
            else:
                new.append("X_{"+str(i)+str(j)+"}")
        new = " \\vee ".join(new)
        clauses.append(new)
    return " \\wedge ".join(clauses)

def translate_cnf(cnf,n = None, human = False):
    # Use return instead of print to check variable explorer
    return [[get_ij_from_k(val, human = human) for val in clause] for clause in cnf]

def antitranslate_cnf(cnf,n = None):
    return [[get_k_from_ij(i,j,val) for i,j,val in clause] for clause in cnf]

def solve(obj):
    """ 
    Return the solver object that solves the given CNF 
    """
    if type(obj) == FormulaSRP:
        cnf = obj.cnf 
    else:
        cnf = obj
    g = Glucose3() 
    for el in cnf:
        g.add_clause(el)
    g.solve()
    return g

def make_list_unique(liste):
    new = []
    for sublist in liste:
        if sublist not in new:
            new.append(sublist)
    return new 

def sort_cnf(cnf):
    for clause in cnf:
        clause.sort()
    cnf.sort()

            
def is_mus(mus):
    g = solve(mus)
    if g.status:
        print("Satisfiable")
        return False 
    for i in range(len(mus)):
        musi = mus[:]
        del musi[i]
        g = solve(musi)
        if not g.solve:
            print("A subformula is UNSAT")
            return False 
    return True

def make_cnf_mini(cnfx):
    sort_cnf(cnfx)
    return make_list_unique(cnfx)

