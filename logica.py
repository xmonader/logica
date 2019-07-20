DEPTH_LIMIT = 100
def isvar(x):
    if isinstance(x, str):
        return x.startswith("?")
    return False

def unify(xs, ys, env=None):
    # [3 a 5] [y 7 z]  => {y:3 a:7 z:5}
    # 
    # print("unifying xs {} and ys {} ".format(xs, ys))
    env = env or {}
    if len(xs) != len(ys):
        return {}
    elif xs == ys == []:
        return env
    
    lhead = xs[0]
    rhead = ys[0]
    # print("UNIFYING X0: {} Y0: {}, ENV: {}".format(xs[0], ys[0],env))

    # print("E {} and F {} and ENV {} ".format(e, f, env))
    if isinstance(lhead, list) and isinstance(rhead, list):
        return unify(lhead, rhead, env) and unify(xs[1:], ys[1:], env)
    if isvar(lhead) and lhead not in env:
        env[lhead] = rhead
    elif isvar(rhead) and rhead not in env:
        env[rhead] = lhead
        
    if isvar(lhead) and lhead in env:
        return unify([env[lhead]], [rhead], env) and unify(xs[1:], ys[1:], env)
        
    if isvar(rhead) and rhead in env:
        return unify([env[rhead]], [lhead], env) and unify(xs[1:], ys[1:], env)

    return lhead == rhead and unify(xs[1:], ys[1:], env)

def rename_vars(clause, env):
    # print("renaming {} in env {}".format(clause, env))
    newclause = clause[:]
    for i,el in enumerate(clause):
        if el in env:
            newclause[i] = env[el]
    return newclause

def query(kb, queries, mainenv=None):
    main = mainenv or {}
    originalfacts = kb.get('facts', [])
    originalrules = kb.get('rules', [])

    """
        kb = {
        'facts': [
            ["woman", "nour"],
            ["woman", "katia"],
            ["man", "jo"],
            ["man", "ahmed"],
            ["cute", "ahmed"],
            ["loves", "nour", "python"],
            ["loves", "ahmed", "python"],
            ["loves", "jo", "gevent"],
            ["loves", "katia", "gevent"],
            ["loves", "andrew", "rust"],
            ["man", "andrew"],
            ["man", "khaled"],
            ["loves", "khaled", "rust"],
            ["loves", "ahmed", "haskell"],
            ["man", "azmy"],
            ["loves", "azmy", "go"],
        ],
        'rules': [
            
            [ ['mortal', '?x'], ['man', '?x'] ],
            [ ['mortal, '?x'],  ['woman', '?x']]
        ]

    }

    qs: man jo

        search results = []
        for f in facts:
            if f[0] == q[0]:
                res = unify(f, q)
                search results add res
                # should we early quit if no variables at all?

    qs: man ?x
        search results = []
        for f in facts:
            if f[0] == q[0]:
                res = unify(f, q)
                search results add res
    
    qs: man ?x, loves python

        for q in qs:
            qenvchoices = {}   => {['man', ?x'] : (x? jo or ?x ahmed) }
            for f in facts:
                if f[0] == q[0]:
                    res = unify(f, q)
                    qenvchoices.append(res)
            
            for choice in qenvchoicess:
                solve the rest of qs with X is Jo, ahmed
    """
    def satisfy(kb, resolved):
        facts = kb.get('facts', [])
        rules = kb.get('rules', [])
        return all(el in facts for el in resolved)


    def ask(kb, queries, env=None, depth=0, originalqueries_len=0, unified=0):
        env = env or {}
        # print(depth*"\t\t", "  in ask => env: {} depth {} queries_len {}".format(env, depth, originalqueries_len))
        # if depth == DEPTH_LIMIT or depth + 1 == originalqueries_len or not queries:
        if not queries:
            # print("\t\t"*depth, " returning now ", env, depth, originalqueries_len)
            yield env
    
        facts = kb.get('facts', [])
        rules = kb.get('rules', [])
        # query -> choices { ['man', '?x'] : [{'?x':'ahmed'}, {'?x':'jo'} }
        for fact in facts:
            for cidx, clause in enumerate(queries):
                e = unify(fact, clause, env)
                if e:
                    renamed_clauses = [rename_vars(q, e) for q in queries]
                    for potential_solution in ask(kb, renamed_clauses[cidx+1:], e):
                        # print(" potentil solution: ", potential_solution)
                        if satisfy(kb, renamed_clauses):
                            yield potential_solution
        subgoals = []
        for rule in rules:
            rule_head = rule[0]
            rule_conditions = rule[1:]

            for cidx, clause in enumerate(queries):
                if clause[0] == rule_head[0]:
                    subgoalenv = query(kb, rule_conditions, env)
                    if subgoalenv:
                        print(subgoalenv)
                    # if subgoalenv:
        # print(subgoals)

    print("MAIN", " queries: {} env: {} ".format(queries, mainenv))

    results = list(ask(kb, queries, mainenv, 0, len(queries)))
    uniq_results = []
    for r in results:
        if r not in uniq_results:
            uniq_results.append(r)
    return uniq_results

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

def test_dontunify_simple():
    l1 = [ 4, '?j']
    l2 = [ '?j', 7]
    print(unify(l1, l2))

def test_query_simple():
    kb = {
        'facts': [ 
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
        ]
    }

    queries = [["man", "?name"],]
    print(query(kb, queries))

def test_query_simple2():
    kb = {
        'facts': [ 
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
            ["loves", "ahmed", "python"],
        ]
    }
    queries = [["man", "?name"], ["loves", "?name", "python"]]
    print(query(kb, queries))


def test_query_simple3():
    kb = {
        'facts': [ 
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
            ["loves", "ahmed", "python"],
            ["loves", "jo", "gevent"]
        ]
    }
    queries = [["man", "?name"], ["loves", "?name", "python"]]
    print(query(kb, queries))
    queries = [["man", "?name"], ["loves", "?name", "gevent"]]
    print(query(kb, queries))


def test_query_simple4():
    kb = {
        'facts': [ 
            ["woman", "nour"],
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
            ["loves", "ahmed", "python"],
            ["loves", "ahmed", "nour" ],
            ["loves", "jo", "gevent"],
            ["loves", "jo", "python"],
        ]
    }
    queries = [["man", "?name"], ["loves", "?name", "python"], ["loves", "?name", "nour"]]
    print(query(kb, queries))



def test_query_simple5():
    kb = {
        'facts': [ 
            ["woman", "nour"],
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
            ["loves", "ahmed", "python"],
            ["loves", "ahmed", "nour" ],
            ["loves", "jo", "gevent"],
            ["loves", "jo", "python"],
        ]
    }
    # queries = [["man", "?name"], ["loves", "?name", "python"], ["loves", "?name", "?girl"], ["woman", "?girl"]]
    # print(query(kb, queries))
    queries = [["man", "?name"], ["loves", "?name", "?girl"], ["woman", "?girl"]]
    print(query(kb, queries))

def test_simple_rule():
    kb = {
        'facts': [ 
            ["woman", "nour"],
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
            ["loves", "ahmed", "python"],
            ["loves", "ahmed", "nour" ],
            ["loves", "jo", "gevent"],
            ["loves", "jo", "python"],
        ],
        'rules':
            [
                [ ["mortal", "?x"], ["man", "?x"]],
                [ ["mortal", "?x"], ["woman", "?x"]],
            ]
    }
    queries = [ ["mortal", "ahmed"] ]
    print(query(kb, queries))


def test_simple_rule2():
    kb = {
        'facts': [ 
            ["woman", "nour"],
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
            ["loves", "ahmed", "python"],
            ["loves", "ahmed", "nour" ],
            ["loves", "jo", "gevent"],
            ["loves", "jo", "python"],
        ],
        'rules':
            [
                [ ["mortal", "?x"], ["man", "?x"]],
                [ ["mortal", "?x"], ["woman", "?x"]],
            ]
    }
    queries = [ ["mortal", "?x"], ["loves", "?x", "gevent"] ]
    print(query(kb, queries))


def test_query_complex():
    kb = {
        'facts': [
            ["woman", "nour"],
            ["woman", "katia"],
            ["man", "jo"],
            ["man", "ahmed"],
            ["cute", "ahmed"],
            ["loves", "nour", "python"],
            ["loves", "ahmed", "python"],
            ["loves", "jo", "gevent"],
            ["loves", "katia", "gevent"],
            ["loves", "andrew", "rust"],
            ["man", "andrew"],
            ["man", "khaled"],
            ["loves", "khaled", "rust"],
            ["loves", "ahmed", "haskell"],
            ["man", "azmy"],
            ["loves", "azmy", "go"],
        ],
    } 


    query1 = [
        ["man", "?name"],
        ["loves", "?name", "python"],
    ]
    query2 = [
        ["man", "?name"],
        ["loves", "?name", "gevent"],
    ]
    query3 = [
        ["woman", "?name"],
    ]
    query4 = [
        ["bird", "?name"],
    ]
    query5 = [
        ["man", "?name"],
    ]
    query6 = [
        ["loves", "?name", "python"]
    ]
    query7 = [
        ["loves", "?name", "gevent"]
    ]
    query8 = [
        ["loves", "?name", "rust"]
    ]
    query9 = [
        ["loves", "?name", "go"]
    ]
    query10 = [
        ["man", "?name"],
        ["cute", "?name"],
        ["loves", "?name", "?lang"],
    ]

    query11 = [
        ["alien", "?name"]
    ]
    for q in [query1, query2, query3, query4, query5, query6, query7, query8, query9, query10]:
        print("Query: ", q)
        print(query(kb, q))

def main():
    test_unify_simple()
    test_unify_simple_with_env()
    test_unify_complex()
    test_unify_very_complex()
    test_dontunify_simple()
    test_dontunify_complex()
    test_query_simple()
    test_query_simple2()
    test_query_simple3()
    test_query_simple4()
    test_query_simple5()
    test_query_complex()
    test_simple_rule()
    test_simple_rule2()


if __name__ == '__main__':
    main()