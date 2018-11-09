
def isvar(x):
    if isinstance(x, str):
        return x.startswith("?")
    return False


def unify(xs, ys, env=None):
    # [3 a 5] [y 7 z]  => {y:3 a:7 z:5}
    # 
    env = env or {}
    if len(xs) != len(ys):
        return False
    elif xs == ys == []:
        return env

    # elif len(xs) > 0 and len(ys) > 0:
    e = xs[0]
    f = ys[0]
    # print("UNIFYING X0: {} Y0: {}, ENV: {}".format(xs[0], ys[0],env))

    # print("E {} and F {} and ENV {} ".format(e, f, env))
    if isinstance(e, list) and isinstance(f, list):
        return unify(e, f, env) and unify(xs[1:], ys[1:], env)
    if isvar(e) and e not in env:
        env[e] = f
    elif isvar(f) and f not in env:
        env[f] = e
        
    if isvar(e) and e in env:
        return unify([env[e]], [f], env) and unify(xs[1:], ys[1:], env)
        
    if isvar(f) and f in env:
        return unify([env[f]], [e], env) and unify(xs[1:], ys[1:], env)

    return e == f and unify(xs[1:], ys[1:], env)

def test_unify_simple():
    l1 = [3, '?a', 5]
    l2 = ['?y', 7, '?z']
    print(unify(l1, l2))

def test_unify_simple_with_env():
    l1 = [3, '?a', '?z']
    l2 = ['?y', 7, '?z']
    print(unify(l1, l2, {'?z':16}))

def test_unify_complex():
    l1 = [ [3,5,6], '?x', ['?z', 5]]
    l2 = [ '?j', 11, [24, 5]]
    print(unify(l1, l2))


def test_unify_very_complex():
    l1 = ['?x', [5, '?z'], [0,[[4,5], 19]]]
    l2 = [ 3, [5, 26], [0, ['?k', 19]] ]
    print(unify(l1, l2))

def test_dontunify_complex():
    l1 = [ [3,5,6], '?x', [24, 5]]
    l2 = [ '?j', 11]
    print(unify(l1, l2))

def query_simple(query, facts):
    for f in facts:
        res = unify(query, f)
        if res:
            print(res)
        
def rename_vars(clause, env):
    # print("RENAMING .... ENV: ", env)
    newclause = clause[:]
    for i,el in enumerate(clause):
        # print("   EL {} , ENV {} ".format(el, env))
        if el in env:
            newclause[i] = env[el]
    # print("CLAUSE NOW: ", clause)
    return newclause


def ask(facts, clauses, env=None, depth=0, visited=None, msg=""):
    import copy
    
    env = copy.deepcopy(env) or {}
    visited = visited or {'facts':[], 'clauses':[]}
    # print(" "*depth, "FACTS: ", facts, "CLAUSES: ", clauses)
    # print(" "*depth, "ENV: ", env, " DEPTH:", depth)
    # print("VISITED: ", visited)
    if len(visited['clauses']) == len(clauses):
        # print("SUCCESS")
        return env
    if not clauses:
        # print(" Failed with env {}".format(env))
        return env 


    results = []
    # for fid, fact in enumerate(facts):
    for cid, clause in enumerate(clauses):
        choices = []
        for f in facts:
            if f[0] != clause[0]:
                continue
            res = unify(f, clause, env)
            if res:
                choices.append(res)
                # print("Clause {} can be unified with {} in ways {}".format(clause, f, choices))

        for e in choices:
            rewritten_clauses = []
            for c in clauses:
                rewritten_clauses.append(rename_vars(c, e)) 
            for rcid, rc in enumerate(rewritten_clauses):
                for fid, fact in enumerate(facts):
                    # if fact[0] != rc[0]:
                    #     continue
                    res = unify(fact, clause, e)
                    if res:
                        # print("[+]unified {} and fact {}".format(rc, fact))
                        newvisited=  copy.deepcopy(visited)
                        newvisited['facts'].append(fact)
                        newvisited['clauses'].append(clause)
                        r = ask(facts, rewritten_clauses[rcid+1:], res, rcid, newvisited)
                        print("R: ", r, depth)
                        if depth == len(clauses):
                            results.append(r) 
    return results

def test_query_complex():
    facts = [ 
        ["woman", "nour"],
        ["man", "jo"],
        ["man", "ahmed"],
        ["loves", "ahmed", "python"],
        ["loves", "jo", "gevent"],
    ]
    clauses1 = [
        ["man", "?name"],
        ["loves", "?name", "python"],
    ]

    clauses2 = [
        ["man", "?name"],
        ["loves", "?name", "gevent"],
    ]

    clauses3 = [
        ["woman", "?name"],
    ]
    clauses4 = [
        ["bird", "?name"],
    ]
    clauses5 = [
        ["man", "?name"],
    ]
    for c in [clauses1, clauses2, clauses3, clauses4, clauses5]:
        print("Query: ", c)
        print(ask(facts, c))


def test_simple_facts():
    facts = [ 
        ["man", "ahmed"],
        ["man", "jo"],
        ["man", "prince"],
    ]

    q = ["man", "?name"]
    query_simple(q, facts)




def main():
    # test_unify_simple()
    # test_unify_simple_with_env()
    # # test_unify_complex()
    # # test_unify_very_complex()
    # # test_dontunify_complex()
    # test_simple_facts()
    test_query_complex()

if __name__ == '__main__':
    main()