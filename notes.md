It may be possible to just use the runs structure to check if there is a cycle that goes: 

```
(     all inside junction x     ) run (     all inside junction y    )  run (     all inside junction z    )  run (  return to start)
(jx.left or jx.right -> jx.root )  -> (jy.left or jy.right -> jy.root)  ->  (jz.left or jz.right -> jz.root)  ->   jx.left or jx.right
```
this will be visible from the runs structure as an alternating sequence of root -> LR, root -> LR, root -> LR

