# logica
playing around with declarative programming techniques unifications and chaining


## Examples

- Every example assumes that you imported `unify, query from logica`
- Every example is a function followed by the result when it's called.

```python

def test_unify_simple():
    l1 = [3, '?a', 5]
    l2 = ['?y', 7, '?z']
    print(unify(l1, l2))
```
```bash

{'?y': 3, '?a': 7, '?z': 5}
```

```python
def test_unify_simple_with_env():
    l1 = [3, '?a', '?z']
    l2 = ['?y', 7, '?z']
    print(unify(l1, l2, {'?z':16}))
```

```bash
{'?z': 16, '?y': 3, '?a': 7}
```
```python
def test_unify_complex():
    l1 = [ [3,5,6], '?x', ['?z', 5]]
    l2 = [ '?j', 11, [24, 5]]
    print(unify(l1, l2))
```
```bash
{'?j': [3, 5, 6], '?x': 11, '?z': 24}
```
```python
def test_unify_very_complex():
    l1 = ['?x', [5, '?z'], [0,[[4,5], 19]]]
    l2 = [ 3, [5, 26], [0, ['?k', 19]] ]
    print(unify(l1, l2))
```

```bash
{'?x': 3, '?z': 26, '?k': [4, 5]}

```

```python
def test_dontunify_complex():
    l1 = [ [3,5,6], '?x', [24, 5]]
    l2 = [ '?j', 11]
    print(unify(l1, l2))
```

```bash
False

```


```python
def test_query_simple():
    facts = [ 
        ["man", "ahmed"],
        ["man", "jo"],
        ["man", "prince"],
    ]

    clauses = [["man", "?name"],]
    print(query(facts, clauses))
``` 

```bash
[{'?name': 'ahmed'}, {'?name': 'jo'}, {'?name': 'prince'}]
```

```python
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
``` 

```bash

Query:  [['man', '?name'], ['loves', '?name', 'python']]
[{'?name': 'ahmed'}]
Query:  [['man', '?name'], ['loves', '?name', 'gevent']]
[{'?name': 'jo'}]
Query:  [['woman', '?name']]
[{'?name': 'nour'}]
Query:  [['bird', '?name']]
[]
Query:  [['man', '?name']]
[{'?name': 'jo'}, {'?name': 'ahmed'}]
Query:  [['loves', '?name', 'python']]
[{'?name': 'nour'}, {'?name': 'ahmed'}]

