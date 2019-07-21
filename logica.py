import copy

DEPTH_LIMIT = 100
def isvar(x):
    if isinstance(x, str):
        return x.startswith("?")
    return False

class Q:
    def __init__(self, *qs):
        self.qs = list(qs)

    __str__ = lambda self: "({})".format(self.qs)
    
    def consumed(self):

        subqconsumed = all(q.consumed() for q in self.qs if isinstance(q, Q))
        sublconsumed = all(l == [] for l in self.qs if isinstance(l, list))
        
        if subqconsumed and sublconsumed:
            return True
        return False

    def rewrite_vars(self, env):
        res = copy.deepcopy(self)
        for qidx, q in enumerate(res.qs):
            if isinstance(q, list):
                res.qs[qidx] = rename_vars(q, env)
            else:
                res.qs[qdix] = q.rewrite_vars(env)
        return res

class AndQ(Q):
    __str__ = lambda self: "AndQ({})".format(self.qs)

    @staticmethod
    def satisfy(kb, query):
        facts = kb.get('facts', [])
        # print("satisfy: facts {} query {} ".format(kb, query) )
        for el in query.qs:
            if isinstance(el, list):
                if el not in facts:
                    return False
            elif isinstance(el, Q):
                if not el.__class__.satisfy(kb, el):
                    return False
        return True


class OrQ(Q):
    __str__ = lambda self: "OrQ({})".format(self.qs)

class NotQ(Q):
    __str__ = lambda self: "NotQ({})".format(self.qs)


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

def runquery(kb, q, mainenv=None):
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

    def ask(kb, query, env=None, depth=0):
        def dprint(*m):
            print("\t\t\t\t"*depth, m)

        env = env or {}
        # if query.consumed():
        #     yield env
        # if not len(query.qs):
        #     yield env
    
        facts = kb.get('facts', [])
        rules = kb.get('rules', [])
        # query -> choices { ['man', '?x'] : [{'?x':'ahmed'}, {'?x':'jo'} }
        for fact in facts:
            # print("fact :" , fact)
            # print("Query: ", query)
            if isinstance(query, AndQ):
                subqueries = query.qs
                # dprint("subqueries: ", subqueries)
                if subqueries == [[]]:
                    yield env
                # need to be anded together.
                for qidx, q in enumerate(subqueries):
                    # if isinstance(q, Q):
                    #     q = Q
                    if isinstance(q, list):
                        extended = unify(fact, q, env)
                        if extended:
                            # dprint("Q {} F {}".format(q, fact))
                            rewritten_query = query.rewrite_vars(extended)
                            # dprint("Query : {}".format(query))
                            # dprint("Suery : {}".format(rewritten_query))

                            nextgoal = AndQ(*rewritten_query.qs[qidx+1:])
                            if AndQ.satisfy(kb, rewritten_query):
                                yield extended
                            
                            # dprint("extended: {}, nextgoal {} ".format(extended, nextgoal))
                            # import ipdb; ipdb.set_trace()
                            
                            for potential_sol in ask(kb, nextgoal, extended, depth+1):
                                # dprint("potential: ", potential_sol)
                                # if AndQ.satisfy(kb, rewritten_query):
                                    # print("satisfied..")
                                yield potential_sol



    print("MAIN", " query: {} env: {} ".format(q, mainenv))

    results = list(ask(kb, q, mainenv))
    uniq_results = []
    for r in results:
        if r not in uniq_results:
            uniq_results.append(r)
    return uniq_results


def funinfo(fun):
    def wrapper(*args, **kwargs):
        print("\n\n======={}=======\n\n".format(fun.__code__.co_name))
        fun(*args, **kwargs)
    return wrapper

@funinfo
def test_unify_simple():
    l1 = [3, '?a', 5]
    l2 = ['?y', 7, '?z']
    print(unify(l1, l2))

@funinfo
def test_unify_simple_with_env():
    l1 = [3, '?a', '?z']
    l2 = ['?y', 7, '?z']
    print(unify(l1, l2, {'?z':16}))

@funinfo
def test_unify_complex():
    l1 = [ [3,5,6], '?x', ['?z', 5]]
    l2 = [ '?j', 11, [24, 5]]
    print(unify(l1, l2))

@funinfo
def test_unify_very_complex():
    l1 = ['?x', [5, '?z'], [0,[[4,5], 19]]]
    l2 = [ 3, [5, 26], [0, ['?k', 19]] ]
    print(unify(l1, l2))

@funinfo
def test_dontunify_complex():
    l1 = [ [3,5,6], '?x', [24, 5]]
    l2 = [ '?j', 11]
    print(unify(l1, l2))

@funinfo
def test_dontunify_simple():
    l1 = [ 4, '?j']
    l2 = [ '?j', 7]
    print(unify(l1, l2))

@funinfo
def test_query_simple():
    kb = {
        'facts': [ 
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
        ]
    }

    q = AndQ( ["man", "?x"] )
    print(runquery(kb, q))

@funinfo
def test_query_simple2():
    kb = {
        'facts': [ 
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
            ["loves", "ahmed", "python"],
        ]
    }
    q = AndQ(["man", "?name"], ["loves", "?name", "python"])
    print(runquery(kb, q))


@funinfo
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
    q = AndQ(["man", "?name"], ["loves", "?name", "python"])
    print(runquery(kb, q))
    q = AndQ(["man", "?name"], ["loves", "?name", "gevent"])
    print(runquery(kb, q))


@funinfo
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
    q = AndQ( ["man", "?name"], ["loves", "?name", "python"], ["loves", "?name", "nour"])
    print(runquery(kb, q))



@funinfo
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

    q = AndQ(["man", "?name"], ["woman", "?girl"], ["loves", "?name", "?girl"])
    print(runquery(kb, q))

    # BROKEN AGAIN..
    q = AndQ(["man", "?name"], ["loves", "?name", "?girl"], ["woman", "?girl"]) 
    print(runquery(kb, q))


@funinfo
def test_query_simple6():
    ## HIDDEN VARIABLES..
    kb = {
        'facts': [ 
            ["father", "functor", "monad"],
            ["father", "monoid", "functor"],
        ]
    }
    q = AndQ(["father", "?x", "?y"], ["father", "?y", "?z"])
    print(runquery(kb, q))

@funinfo
def test_query_simple7():
    ## HIDDEN VARIABLES..
    kb = {
        'facts': [ 
            ["father", "functor", "notmonad"],
            ["father", "functor", "monad"],
            ["father", "monoid", "functor"],
        ]
    }
    q = AndQ(["father", "?x", "?y"], ["father", "?y", "?z"])
    print(runquery(kb, q))

@funinfo
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
    print(runquery(kb, queries))


@funinfo
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
    print(runquery(kb, queries))


@funinfo
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
        print(runquery(kb, q))

def main():
    # test_unify_simple()
    # test_unify_simple_with_env()
    # test_unify_complex()
    # test_unify_very_complex()
    # test_dontunify_simple()
    # test_dontunify_complex()
    # test_query_simple()
    # test_query_simple2()
    # test_query_simple3()
    # test_query_simple4()
    # test_query_simple5()
    # test_query_simple6()
    test_query_simple7()

    # test_query_complex()
    # test_simple_rule()
    # test_simple_rule2()


if __name__ == '__main__':
    main()