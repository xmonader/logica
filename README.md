# logica
playing around with declarative programming techniques unifications and chaining


## Examples

- Every example assumes that you imported `unify, query from logica`
- Every example is a function followed by the result when it's called.



### test_unify_simple 


```python
@funinfo
def test_unify_simple():
    l1 = [3, '?a', 5]
    l2 = ['?y', 7, '?z']
    print(unify(l1, l2))

```
```
{'?y': 3, '?a': 7, '?z': 5}
```


### test_unify_simple_with_env 


```python
@funinfo
def test_unify_simple_with_env():
    l1 = [3, '?a', '?z']
    l2 = ['?y', 7, '?z']
    print(unify(l1, l2, {'?z':16}))

```
```
{'?z': 16, '?y': 3, '?a': 7}
```


### test_unify_complex 


```python
@funinfo
def test_unify_complex():
    l1 = [ [3,5,6], '?x', ['?z', 5]]
    l2 = [ '?j', 11, [24, 5]]
    print(unify(l1, l2))

```
```
{'?j': [3, 5, 6], '?x': 11, '?z': 24}
```


### test_unify_very_complex 


```python
@funinfo
def test_unify_very_complex():
    l1 = ['?x', [5, '?z'], [0,[[4,5], 19]]]
    l2 = [ 3, [5, 26], [0, ['?k', 19]] ]
    print(unify(l1, l2))

```
```
{'?x': 3, '?z': 26, '?k': [4, 5]}
```


### test_dontunify_simple 


```python
@funinfo
def test_dontunify_simple():
    l1 = [ 4, '?j']
    l2 = [ '?j', 7]
    print(unify(l1, l2))

```
```
False
```


### test_dontunify_complex 


```python
@funinfo
def test_dontunify_complex():
    l1 = [ [3,5,6], '?x', [24, 5]]
    l2 = [ '?j', 11]
    print(unify(l1, l2))

```
```
{}
```


### test_query_simple0 


```python
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

```
```
MAIN  query: AndQ([['man', 'ahmed']]) env: None 
[({}, True)]
```


### test_query_simple 


```python
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

```
```
MAIN  query: AndQ([['man', '?x']]) env: None 
[({'?x': 'ahmed'}, True), ({'?x': 'jo'}, True), ({'?x': 'prince'}, True)]
```


### test_query_simple2 


```python
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

```
```
MAIN  query: AndQ([['man', '?name'], ['loves', '?name', 'python']]) env: None 
[({'?name': 'ahmed'}, True)]
```


### test_query_simple3 


```python
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

```
```
MAIN  query: AndQ([['man', '?name'], ['loves', '?name', 'python']]) env: None 
[({'?name': 'ahmed'}, True)]
MAIN  query: AndQ([['man', '?name'], ['loves', '?name', 'gevent']]) env: None 
[({'?name': 'jo'}, True)]
```


### test_query_simple4 


```python
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

```
```
MAIN  query: AndQ([['man', '?name'], ['loves', '?name', 'python'], ['loves', '?name', 'nour']]) env: None 
[({'?name': 'ahmed'}, True)]
```


### test_query_simple5 


```python
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

```
```
MAIN  query: AndQ([['man', '?name'], ['woman', '?girl'], ['loves', '?name', '?girl']]) env: None 
[({'?name': 'ahmed', '?girl': 'nour'}, True)]
MAIN  query: AndQ([['man', '?name'], ['loves', '?name', '?girl'], ['woman', '?girl']]) env: None 
[({'?girl': 'nour', '?name': 'ahmed'}, True)]
```


### test_query_simple6 


```python
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

```
```
MAIN  query: AndQ([['father', '?x', '?y'], ['father', '?y', '?z']]) env: None 
[({'?z': 'monad', '?x': 'monoid', '?y': 'functor'}, True)]
```


### test_query_simple7 


```python
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

```
```
MAIN  query: AndQ([['father', '?x', '?y'], ['father', '?y', '?z']]) env: None 
[({'?z': 'ahmed', '?x': 'emam', '?y': 'thabet'}, True), ({'?z': 'omnia', '?x': 'emam', '?y': 'thabet'}, True)]
```


### test_query_simple_or1 


```python
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

```
```
MAIN  query: OrQ([['father', '?a', '?b'], ['mother', '?c', '?d']]) env: None 
[({'?a': 'emam', '?b': 'thabet'}, True), ({'?c': 'thabet', '?d': 'zainab'}, True)]
```


### test_query_simple_or2 


```python
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

```
```
MAIN  query: OrQ([['loves', '?name', 'python'], ['eats', '?name', 'chocolate']]) env: None 
[({'?name': 'ahmed'}, True), ({'?name': 'jo'}, True)]
```


### test_query_simple_not1 


```python
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

```
```
MAIN  query: AndQ([<__main__.NotQ object at 0x7f804880dd10>, ['father', 'z', '?x']]) env: None 
[({'?x': 'y'}, True)]
```


### test_query_complex 


```python
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

```
```
Query:  AndQ([['man', '?name'], ['loves', '?name', 'python']])
MAIN  query: AndQ([['man', '?name'], ['loves', '?name', 'python']]) env: None 
[({'?name': 'ahmed'}, True)]
Query:  AndQ([['man', '?name'], ['loves', '?name', 'gevent']])
MAIN  query: AndQ([['man', '?name'], ['loves', '?name', 'gevent']]) env: None 
[({'?name': 'jo'}, True)]
Query:  AndQ([['woman', '?name']])
MAIN  query: AndQ([['woman', '?name']]) env: None 
[({'?name': 'nour'}, True), ({'?name': 'katia'}, True)]
Query:  AndQ([['bird', '?name']])
MAIN  query: AndQ([['bird', '?name']]) env: None 
[]
Query:  AndQ([['man', '?name']])
MAIN  query: AndQ([['man', '?name']]) env: None 
[({'?name': 'jo'}, True), ({'?name': 'ahmed'}, True), ({'?name': 'andrew'}, True), ({'?name': 'khaled'}, True), ({'?name': 'azmy'}, True)]
Query:  AndQ([['loves', '?name', 'python']])
MAIN  query: AndQ([['loves', '?name', 'python']]) env: None 
[({'?name': 'nour'}, True), ({'?name': 'ahmed'}, True)]
Query:  AndQ([['loves', '?name', 'gevent']])
MAIN  query: AndQ([['loves', '?name', 'gevent']]) env: None 
[({'?name': 'jo'}, True), ({'?name': 'katia'}, True)]
Query:  AndQ([['loves', '?name', 'rust']])
MAIN  query: AndQ([['loves', '?name', 'rust']]) env: None 
[({'?name': 'andrew'}, True), ({'?name': 'khaled'}, True)]
Query:  AndQ([['loves', '?name', 'go']])
MAIN  query: AndQ([['loves', '?name', 'go']]) env: None 
[({'?name': 'azmy'}, True)]
Query:  AndQ([['man', '?name'], ['cute', '?name'], ['loves', '?name', '?lang']])
MAIN  query: AndQ([['man', '?name'], ['cute', '?name'], ['loves', '?name', '?lang']]) env: None 
[({}, True), ({'?lang': 'python', '?name': 'ahmed'}, True), ({'?lang': 'haskell', '?name': 'ahmed'}, True)]
```
