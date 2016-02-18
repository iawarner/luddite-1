# luddite

> *noun* - a member of any of the bands of English workers who destroyed machinery, especially in cotton and woolen mills, that they believed was threatening their jobs 

This python package serves to house python modules for use in bio-informatic repositories. All additions will be added as they are needed. 

#Philosophy

This effort is being made to curb the number of one off tasks that have been started in the lab that have later turned into repetitive one off tasks. 

With that in mind - you should be trying to borrow as much code from stable sources as possible. ( i.e. If it can't be installed through pip or isn't a maintained/stable source please don't make it a dependency.) We don't want anything that's important going the way of [GeoCities](https://en.wikipedia.org/wiki/Yahoo!_GeoCities). 

#Style Guide: 
In general - please just write clean , easily readable code. Stick to the zen of python. 

1. Beautiful is better than ugly.
2. Explicit is better than implicit.
3. Simple is better than complex.
4. Complex is better than complicated.
5. Flat is better than nested.
6. Sparse is better than dense.
7. Readability counts.
8. Special cases aren't special enough to break the rules.
  * __Although practicality beats purity.__
9. Errors should never pass silently.
  * __Unless explicitly silenced.__
10. In the face of ambiguity, refuse the temptation to guess.
11. There should be one-- and preferably only one --obvious way to do it.
  * __Although that way may not be obvious at first unless you're Dutch.__
12. Now is better than never.
  * __Although never is often better than right now.__
13. If the implementation is hard to explain, it's a bad idea.
14. If the implementation is easy to explain, it may be a good idea.
15. NameSpaces are one honking great idea -- let's do more of those!

When in doubt look to the [Google](https://google.github.io/styleguide/pyguide.html) Python style guide.

# Best practices within this package

1. We will use [pydoit](http://pydoit.org/) instead of system calls. 
  * If it's a commonly used program - make a specific package for it so other can use it.
2. We will document as much as possible.
3. We will test.



