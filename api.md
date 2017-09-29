ink API needs:

json --> story
```python
s = inkpy.Story(file_path)
# or
with open(file_path) as file_content
    s = inkpy.Story(file_content)
```

story --> has next lines
```python
if s.can_continue
```

story --> next lines
```python
txt = s.continue_(max=False)
```
can't call it `continue` because of python's

story --> current lines
```python
txt = s.text
```

story --> choices
```python
chs = s.choices
```

story --| choose from the choices
```python
chs = s.choices
for ch in chs:
    print("%d: %s" % ch.idx, ch.text)
i = int(input("> "))
s.choose(i)
```

story --| move the story cursor
```python
s.goto("knot.stitch")
```

story --> tags (line, knot, story)
```python
s.tags
s.tagsat("path")
s.gtags
```

story --> save/load state
```python
s.save("path/to/file")
#or
s.save(writeable)
###
s.load("path/to/file")
#or
s.load(readable)
###
# if you want to do your own serialization, you have these options:
s.json = deserialized_obj
serializeable_obj = s.json
```

story --> reset the state
```python
s.reset()
```

story --> reset the call stack
```python
s.reset_callstack()
```

story --| get/set variable
``` python
v = s.vars["var"]
s.vars["var"] = v
```
todo: value APIs (for things other than int, str, bool, etc)

story --> visit count of a certain path
``` python
n = s.visit_count("path")
```

story --| add/remove variable listener
``` python
def f(name, new_value):
    dostuff()
s.watch("var",f)
s.unwatch(f)
```

story --| bind/unbind external functions
```python
# in ink file :
# EXTERNAL sqr(x)
def sqr(x): return x*x

s.bindfun("sqr",sqr)
s.unbindfun("sqr")
```

choice --> text
choice --> index
```python
chs = s.choices
for ch in chs:
    print("%d: %s" % ch.idx, ch.text)
```

list values:: (for variables)
nothing --> empty inklist
```python
l = InkList() #empty list
```
inklist --> inklist
```python
lcp = l.copy()
```
origin_name + story --> empty inklist
```python
l = s.inklist(name)
```

list --| add/remove item(s)
```python
l += item(s)
l -= item(s)
```
list --> check if a name is present
```python
"name" in l
```
list --> max,min...
```python
mx, mn = (l.max, l.min)
```
list --> all possible values
```python
l.all
```
list --| binary operations
```python
l1 + l2 # Union
l1 ^ l2 # Intersection
l1 - l2 # Difference
l1 in l2 # Contains
l1 > l2 # Greater than
l1 >= l2 # Greater than or equal to
l1 < l2 # Lesser than
l1 <= l2 # Lesser than or equal to
l1 == l2 # Structural equality
```
list --> hashcode
```python
hash(l)
```
list --> string representation
```python
s = str(l)
###
print(l)
```

divert values (for variables)::
NOT IMPLEMENTED
(gonna wait for Inkle to do it. I don't want to outscope their own engine)
