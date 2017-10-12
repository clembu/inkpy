# inkpy
A python port of inkle's ink engine
**THIS PROJECT IS ABANDONNED**

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

To tell you the truth, this was really an exercise to understand how to actually program with python,
beyond simple tutorial scripts or small projects.

Turns out you can't.

It's not made for that. Python is made for small modules, or packages of small modules, not libraries.
If one needs a complex virtual machine in a python environment, one would go write a C extension or something.

I am now putting an end to inkpy.
It doesn't work, there's `TypeError`s everywhere. It's okay, I don't care, I don't want nor have the time to fix it.

I'll just leave the code here for future reference, and if I ever want to go back to it someday.
