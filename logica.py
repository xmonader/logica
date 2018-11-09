
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


def rename_vars(clause, env):
    # print("RENAMING .... ENV: ", env)
    newclause = clause[:]
    for i,el in enumerate(clause):
        # print("   EL {} , ENV {} ".format(el, env))
        if el in env:
            newclause[i] = env[el]
    # print("CLAUSE NOW: ", clause)
    return newclause


def query(facts, clauses, env=None):
    results = []
    def ask(facts, clauses, env=None, depth=0, originalclauseslen=-1):
        import copy
        
        if originalclauseslen == -1:
            originalclauseslen = len(clauses)

        # for fid, fact in enumerate(facts):
        clausesinfo = {}
        for cid, clause in enumerate(clauses):
            choices = []
            for f in facts:
                if f[0] != clause[0]:
                    continue
                newenv = copy.deepcopy(env)
                res = unify(f, clause, newenv)
                if res:
                    choices.append(res)
                    # print("Clause {} can be unified with {} in ways {}".format(clause, f, choices))
            clausesinfo[cid] = {'choices': choices, 'clause':clause}
        # print(clausesinfo)
        for fid, fact in enumerate(facts):
            for clauseid, clauseinfo in clausesinfo.items():
                choices = clauseinfo['choices']
                clause = clauseinfo['clause']
                for e in choices:
                    rewritten_clause = rename_vars(clause, e)
                    res = unify(fact, rewritten_clause, e)
                    if not res:
                        continue
                        # print("[-] couldn't unify {} with {} in env {}".format(fact, rewritten_clause, e))
                    else:
                        # print("     "*depth, "[+] unified {} with {} in env {}".format(fact, rewritten_clause, res))
                        res = ask(facts[fid+1:], clauses[clauseid+1:], res, depth+1, originalclauseslen)
                        if depth + 1 == originalclauseslen:
                            # print("SUCCESS!!!")
                            # print(res)
                            results.append(res)
                            # return res
        return env
    ask(facts, clauses, env, 0, -1)
    return results



def test_query_simple():
    facts = [ 
        ["man", "ahmed"],
        ["man", "jo"],
        ["man", "prince"],
    ]

    clauses = [["man", "?name"],]
    print(query(facts, clauses))



def test_query_complex():
    facts = [ 
        ["woman", "nour"],
        ["man", "jo"],
        ["man", "ahmed"],
        ["loves", "nour", "python"],
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
    clauses6 = [
        ["loves", "?name", "python"]
    ]
    for c in [clauses1, clauses2, clauses3, clauses4, clauses5, clauses6]:
        print("Query: ", c)
        print(query(facts, c))




def main():
    test_unify_simple()
    test_unify_simple_with_env()
    test_unify_complex()
    test_unify_very_complex()
    test_dontunify_complex()
    test_query_simple()
    test_query_complex()

if __name__ == '__main__':
    main()