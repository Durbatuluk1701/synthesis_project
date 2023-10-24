# Synthesis Final Project

This project will attempt to apply a semi-"divide-and-conquer" approach to 
proving the unrealizability of a specification.

We will break down a problem to its smallest "sub-grammars" and from their
build to the "minimal realizable" grammar.
Then, it will be dispatched to a state-of-the-art SMT solver (z3)
to actually synthesize a satisfying solution to the specification.

The presumed performance benefits will come from the synthesis
taking place with the "minimal realizable" grammar.


## Build Instructions

1. Make sure you have dune and ocaml (using opam)
2. Run "dune build"
3. Run "dune exec ./\<fileName\>.exe"

## Adding Files
1. Run "dune init executable \<fileName\>"

## General Methodology:

The SemGuS problem has three components:
1. A search space given by a regular tree grammar G
2. Semantics for the grammar G
3. A specification of the desired behavior of the program

Given that we are provided that,
we want to find sub-grammars of G
and attempt to prove unrealizability for the sub-grammars.

