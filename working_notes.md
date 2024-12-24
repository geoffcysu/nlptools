
```
1a.我吃[NP我做的飯]
1b.我說[CP我做飯]
```

`[VP我吃[NP我做的飯]]  --EPP-->  TP我[VP吃[NP我做的飯]]`
NP(RC:我做的, head:飯)



predicate: 在前面加一個主詞就變句子
做飯->predicate

======

Problem: How to decide the comp of a VP is a NP or CP

```
2a. CP我說[NP我寫的詩]
2b. CP我說[CP我寫的詩[DegP很棒]]
```

P1:To decide if a sentence exists predicate:
1.use parse_VP to test head patterns: V, Aux, Deg
    - because if there exists VP, it wouldn't be NP
2.if the sentence doesn't exist RC (xx的)
    - RC is an NP-exclusive pattern (RC implies adjectives)

But P1 fail to distinguish 2a, 2b.

Resolution:
1. to simply try parsing NP and CP (but the problem is that current procedure will focus on 寫 instad of 很)
    - try to redefine the rule for parsing VP?

x
solved! It's already handled by v_pat (that it excluded)