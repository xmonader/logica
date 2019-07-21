import copy
import inspect

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
                res.qs[qidx] = q.rewrite_vars(env)
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

    @staticmethod
    def satisfy(kb, q):
        return not AndQ.satisfy(kb, q)

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
            newclause[i] = env.get(el, el)
    return newclause

def runquery(kb, q, mainenv=None):
    main = mainenv or {}
    originalfacts = kb.get('facts', [])
    originalrules = kb.get('rules', [])

    def ask_simple(kb, query, env=None, depth=0):
        
        env = env or {}
        facts = kb.get('facts', [])
        rules = kb.get('rules', [])

        for fact in facts:
            if isinstance(query, AndQ):
                subqueries = query.qs
                for qidx, q in enumerate(subqueries):
                    e = unify(fact, q)
                    if e:
                        yield e
        
    
    def ask(kb, query, env=None, depth=0):
        def dprint(*m):
            print("\t"*depth, *m)

        env = env or {}
        facts = kb.get('facts', [])
        rules = kb.get('rules', [])
        for fact in facts:
            if isinstance(query, AndQ):
                subqueries = query.qs
                for qidx, q in enumerate(subqueries):
                    if isinstance(q, list):
                        if fact == q:
                            yield {}, True
                        extended = unify(fact, q, env)
                        if not extended:
                            yield {}, False
                        if extended:
                            extended = {**env, **extended}
                            rewritten_query = query.rewrite_vars(extended)

                            nextgoal = AndQ(*rewritten_query.qs[qidx+1:])
                            if AndQ.satisfy(kb, rewritten_query):
                                yield extended, True
                            else:
                                optenvs = list(ask_simple(kb, nextgoal))
                                for optenv in optenvs:
                                    for potential_sol, matches in ask(kb, nextgoal, {**optenv, **extended}, depth+1):
                                        yield potential_sol, matches

            if isinstance(query, OrQ):
                subqueries = query.qs
                for qidx, q in enumerate(subqueries):
                    if isinstance(q, list):
                        extended = unify(fact, q, env)
                        if extended:
                            yield extended, True

            if isinstance(query, NotQ):
                resQ = AndQ(*query.qs)
                subqueries = resQ.qs
                for qidx, q in enumerate(subqueries):
                    if isinstance(q, list):
                        res = runquery(kb, AndQ(q))
                        for e,m in res:
                            print("e, m : ", e, m)
                            if m:
                                print("bad env: ", e)
                            else:
                                print(resQ)
                                yield e, True

            
    print("MAIN", " query: {} env: {} ".format(q, mainenv))

    results = list(ask(kb, q, mainenv))
    uniq_results = []
    for r in results:
        if r[1] and r not in uniq_results:
            # env, matches or not.
            uniq_results.append(r)
    return uniq_results


def funinfo(fun):
    def wrapper(*args, **kwargs):
        print("\n\n### {} \n\n".format(fun.__code__.co_name))
        print('```python')
        print(inspect.getsource(fun))
        print('```')
        print('```')
        fun(*args, **kwargs)
        print('```')

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
def test_query_simple0():
    kb = {
        'facts': [ 
            ["man", "ahmed"],
            ["man", "jo"],
            ["man", "prince"],
        ]
    }

    q = AndQ( ["man", "ahmed"] )
    print(runquery(kb, q))

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
            ["father", "emam", "thabet"],
            ["father", "thabet", "ahmed"],
            ["father", "thabet", "omnia"],
        ]
    }
    q = AndQ(["father", "?x", "?y"], ["father", "?y", "?z"])
    print(runquery(kb, q))

@funinfo
def test_query_simple_or1():
    ## HIDDEN VARIABLES..
    kb = {
        'facts': [ 
            ["father", "emam", "thabet"],
            ["mother", "thabet", "zainab"],
        ]
    }
    q = OrQ(["father", "?a", "?b"], ["mother", "?c", "?d"])
    print(runquery(kb, q))

@funinfo
def test_query_simple_or2():

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
            ["eats", "jo", "chocolate"]
        ]
    }

    q = OrQ(["loves", "?name", "python"], ["eats", "?name", "chocolate"])
    print(runquery(kb, q))

@funinfo
def test_query_simple_not1():
    kb = {
        'facts': [ 
            ["father", "a", "b"],
            ["father", "a", "c"],
            ["father", "z", "b"],
            ["father", "z", "y"],
        ]
    }
    q = AndQ(NotQ(["father", "a", "?x"]), ["father", "z", "?x"])
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


    query1 = AndQ(
        ["man", "?name"],
        ["loves", "?name", "python"]
    )
    query2 = AndQ(
        ["man", "?name"],
        ["loves", "?name", "gevent"]
    )

    query3 = AndQ(
        ["woman", "?name"],
    )
    query4 = AndQ(
        ["bird", "?name"],
    )
    query5 = AndQ(
        ["man", "?name"],
    )
    query6 = AndQ(
        ["loves", "?name", "python"]
    )
    query7 = AndQ(
        ["loves", "?name", "gevent"]
    )
    query8 = AndQ(
        ["loves", "?name", "rust"]
    )
    query9 = AndQ(
        ["loves", "?name", "go"]
    )
    query10 = AndQ(
        ["man", "?name"],
        ["cute", "?name"],
        ["loves", "?name", "?lang"],
    )

    query11 = AndQ(
        ["alien", "?name"]
    )
    for q in [query1, query2, query3, query4, query5, query6, query7, query8, query9, query10]:
        print("Query: ", q)
        print(runquery(kb, q))

def main():
    test_unify_simple()
    test_unify_simple_with_env()
    test_unify_complex()
    test_unify_very_complex()
    test_dontunify_simple()
    test_dontunify_complex()
    test_query_simple0()
    test_query_simple()
    test_query_simple2()
    test_query_simple3()
    test_query_simple4()
    test_query_simple5()
    test_query_simple6()
    test_query_simple7()

    test_query_simple_or1()
    test_query_simple_or2()

    test_query_simple_not1()

    test_query_complex()

    # test_simple_rule()
    # test_simple_rule2()


if __name__ == '__main__':
    main()