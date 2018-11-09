
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
    for i,el in enumerate(clause):
        # print("   EL {} , ENV {} ".format(el, env))
        if el in env:
            clause[i] = env[el]
    # print("CLAUSE NOW: ", clause)
    return clause


def ask(facts, clauses, env=None, depth=0, visited=None):
    env = env or {}
    visited = visited or {'facts':[], 'clauses':[]}
    # print(" "*depth, "FACTS: ", facts)
    # print(" "*depth, "ENV: ", env, " DEPTH:", depth)
    # print("VISITED: ", visited)
    if len(visited['clauses']) == len(clauses):
        print("SUCCESS")
        return env
    if not clauses:
        print(" Failed with env {}".format(env))
        return env 

    import copy
    results = []

    for fid, fact in enumerate(facts):
        if fact in visited['facts']:
            continue
        for cid, clause in enumerate(clauses):
            if clause in visited['clauses']:
                continue
            # print(depth*"\t", "[+] Fact now is {}, clause is {} and env {}".format(fact, clause, env))
            res = unify(fact, clause, env)
            if not res:
                # print(depth*"\t\t", "   [-] couldn't unify {} with fact {} in env {}".format(clause, fact, env))
                break # try another fact
            else:
                visited['facts'].append(fact)
                visited['clauses'].append(clause)
                rewritten_clauses = []
                for c in clauses:
                    rewritten_clauses.append(rename_vars(clause, res)) 
                # print(depth*"   ", "    [+] unified {} with fact {} and resulting env is {} ".format(clause, fact, res))
                result = ask(facts, rewritten_clauses, res, depth+1, visited)
                # print(result)
                if len(visited['clauses']) == len(clauses):
                    return result 
    return {}

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
    for c in [clauses1, clauses2, clauses3, clauses4]:
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