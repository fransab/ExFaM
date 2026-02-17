# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 09:48:01 2024

@author: sabatinofr
"""
import networkx as nx
import matplotlib.pyplot as plt 



def forced_ass(env,clause):
    """ 
    Given variables with known value in <env> and a <clause>, returns:
        - None if <clause> is satisfiable under <env> OR no bottleneck
        - 'UNSAT' if <clause> is unsatisfiable under <env>
        - <var> if under <env>, the only way to make <clause> SAT is to set <var> to a specific value
    """
    unsat_vals = set()
    for val in clause:
        for el in env:
            if val == el: return None # Clause is SAT
            if val==-el:
                unsat_vals.add(val) # Literal <val> is unsatisfied
                
    if len(set(clause)) == len(unsat_vals):
        return "UNSAT" # All vars in clause are unsatisfied
    
    diff = [el for el in clause if el not in unsat_vals]
    if len(diff) == 1: return diff[0] # Only this can make the clause SAT
    return None # Impossible to find a 'bottleneck literal'


def prove_step_unsat(lit, mus, n, assumed):
    """
    Given a starting literal <lit>, a MUS <mus> and <n>: nb of agents, 
    try to find an explanation why <lit> makes the CNF unsat. 
    use a set <assumed> of variables which variable is already proven
    Returns
        - steps, used_clauses if an explanation is found 
            steps: logical explanation of why <lit> is UNSAT 
            used_clauses: IDs of clauses used for the explanation 
        - False,False if no explanation is found
    """
    env = set([lit])
    env.update(assumed)
    retry = True
    nb_tries = 1
    steps = [("Assume",lit)]
    used_clauses = set()
    while retry:
        retry = False
        for i,clause in enumerate(mus): # Check if a clause is UNSAT
            new_val = forced_ass(env, clause) 
            if new_val == "UNSAT":
                steps.append(("Clause",i+1,"is unsatisfiable"))
                used_clauses.add(i+1)
                return steps,used_clauses
        for i,clause in enumerate(mus):
            new_val = forced_ass(env, clause) # Check if we can find a 'bottleneck'
            if new_val != None:
                env.add(new_val)
                retry = True
                steps.append(("clause",i+1,"implies",new_val))
                used_clauses.add(i+1)
                break
            
        if nb_tries == 1000:
            print("Reached limit")
            break
        
        nb_tries += 1
    return False,False


def try_clause(clause_id,mus, n):
    """ 
    With a given clause id, a mus, and n: nb of agents, returns
        - expl_var if an explanation is found for the MUS, starting with the <clause_id>-th clause. 
        - False else
    """
    expl_var = []
    used_clauses = set()
    temp_env = set() # Variables proven to have this value
    for var in mus[clause_id]:
        s1, c1 = prove_step_unsat(var, mus, n, temp_env)
        if not s1: 
            return False 
        expl_var.append(s1)
        used_clauses.update(c1)
        temp_env.add(-var)
    if len(used_clauses) == len(mus)-1: #-1 because 1 clause is used as a starting point
        expl_var.append("Previous steps showed clause " + str(clause_id+1) + " can never be satisfied")
        return expl_var

    return False


def procedure(mus, n):
    """ 
    With <mus> a MUS, n: nb of agents, returns
        - explanation: the explanation of the MUS if it is found 
        - -1 else
    """
    # TODO
    # - Faire explication en graphe car juste implication pas suffisant 
    # 2 noeuds par literal (positif et negatif) et faire aretes implications 
    # Pour clause atleast faire chaque subset de taille n-1 implique la derniere variable
    # Rajouter phrase expl quand on utilise une variable qui decoule d'une etape precedente
    for i in range(len(mus)): # Iterate over all the clause
        explanation = try_clause(i, mus, n) # Check if starting with the i-th clause finds an explanation
        
        if explanation:
            print("Found an explanation")
            return explanation 
    print("No explanation could be found")
    return -1


def build_graph_from_exp(e,mus,n,sym=True):
    """ 
    Given an explanation e (for now only with the first step), a mus an n: nb agents
    returns
        the nx Graph corresponding to the explanation 
    """
    g = nx.DiGraph()
    level = {}
    node_spacing = 2
    for step in e:
        env = [step[0][1]]
        level[env[0]] = 0
        for i in range(1,len(step)-1):
            _,clause_nb,_,newvar = step[i] # clause_id = clause_nb-1

            used_vars = [var for var in env if -var in mus[clause_nb-1]]
            print(used_vars)
            for v in used_vars:
                g.add_edge(v, newvar, clause=f"$[{clause_nb}]$")
            env.append(newvar)
            level[newvar] = max([level[var] for var in used_vars]) + node_spacing
        
        unsat_c_nb = step[-1][1]
        last = str(unsat_c_nb)+ "_UNSAT"
        level[last] = 0
        for lit in mus[unsat_c_nb-1]:
            print(lit,print(last))
            g.add_edge(-lit, last, clause=f"$[{unsat_c_nb}]$")
            if level[-lit] > level[last]-node_spacing:
                level[last] = level[-lit]+node_spacing
        # break
    for node in g.nodes():
        g.add_node(node, subset=level[node])
    return g


def show_xgraph(e,mus, n,save="graph.png"):
    """ 
    Saves the graph representation of an explanation in an image
    """ 
    plt.clf()
    plt.figure().set_figwidth(15)
    g = build_graph_from_exp(e, mus, n)
    pos = nx.multipartite_layout(g)
    node_labels = {node:literal_to_tex(node, n) for node in g.nodes()} #add 'if not type(node) == str instead of changing tex conversion
    edge_labels = {(u,v):g[u][v]["clause"] for (u,v) in g.edges()}
    # nx.draw_networkx(g,pos=pos,nodelist=[], with_labels=False)
    nx.draw_networkx_labels(g,pos=pos,labels=node_labels)
    nx.draw_networkx_edges(g, pos=pos,node_size = 100, min_source_margin=10,min_target_margin=10)
    nx.draw_networkx_edge_labels(g,pos=pos, edge_labels=edge_labels )
    plt.title("Step 1")
    plt.savefig('graph.png',dpi=400)
    plt.close("all")