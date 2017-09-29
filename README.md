# inkpy
A python port of inkle's ink engine

The idea is that pythonnet relies on Mono and DotNet and stuff, and they say on [their website](http://pythonnet.github.io/) that
```
Unit testing shows that PythonNet will run under Mono, though the Mono runtime is less supported so there still may be problems.
```
so it's kinda unreliable.

So here I go, diving into porting inkle's stuff to python.
Main goal was that it works exactly the same, with the exact same API.

Turns out that's not *Pythonic*. I mean, Ink is a C# library with its load of overloads, `out` parameters, generic lists...
So the exercise now it's to **make it a pythonic API**

---
