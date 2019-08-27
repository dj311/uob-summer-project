## Interpreting Progol Output

Progol outputs lines like:
```
f=393,p=400,n=0,h=0
```
when searching. But what do they mean? We trauled through the Progol source code to provide you with this valuable information:

```
/* r_search 
  A*-like algorithm based on pseudo-compression
  T is background knowledge.
  C = h<-B is most specific i-bounded clause in mode language s.t. T/\C |= e.
  Search space is C' = h<-B' where B' subset of B. Open list is sorted
  in descending order on heuristic function
  
        g = (c+n)-p             [neg. pseudo-compression]
          = (c+negcover(C'))-poscover(C')       [(c+n)-p]
  
        where cardinality c = |B'|
        
  Let bestclosed = <g0,p0,c0>
  Let Open = <<g1,p1,c1>,..<gn,pn,cn>>. Search terminates when
  n0=0 and p0>pi for 2<=i<=p. Proof that search returns consistent clause
  with maximum positive coverage is immediate from the fact that
  p1>pi and p decreases monotonically along any path in the search.
  When there is more than one clause with this coverage, the one with
  maximum compression will be returned.
  
  Search pruned for
        a) Children of node i with ni=0
        b) Children of node with pi<ci  [there can be no eventual compression]
        c) Any node i with gi<g0 when n0=0
        d) Any node with ci>=Clause-length limit

  Lower-bound distance to goal h can be introduced by tabulating
        the "distance", minimal number of atoms from
        each atom to an atom which computes the output variables
        in the bottom clause. This number is minimised over a given clause
        to give h, the number of required atoms to compute output variables.
        When no outputs in the head then distance is zero for
        all atoms in bottom. Atoms not on path to output
        variables are given a large non-negative distance value.
  
  Actual state record used is the following integer array
  
        f - g+h = ((c+n)-p)+h
        p - positive coverage (n calcuated as f+p-(c+h))
        c - the clause length
        h - min. no atoms to output
        a/u - encoded binding of chosen atom
        par - parent state
  
 */
```
