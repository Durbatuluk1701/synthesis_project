
type grammar = 
  | Int of int
  | Add of grammar * grammar
  | Sub of grammar * grammar
  | Mul of grammar * grammar
  | If of grammar * grammar * grammar
  | Var of string

type 'G environment =
  string -> 'G

type ('G, 'V) semantics = 
  'G -> 'V  

type ('G,'V) spec =
  'G -> 'V

type ('G,'V) semGus = 'G * ('G,'V) semantics * ('G,'V) spec

type smt_clause = bool

(* We want to be able to take a grammar 'G, 
   its semantics, and a specification.

   Further, we actually want the specification for the problem
   to be IO examples ( a list of them ) and the true spec
   is just used for verification purposes by an Oracle/SAT/SMT solver
*)

(* The semantics of a function will be 
   a mapping from Constructor to inversions of the
   Constructor
*)

let rec eval (env : int environment) : (grammar, int) semantics =
  fun g ->
    match g with
    | Int i -> i
    | Add (g1, g2) -> eval env g1 + eval env g2
    | Sub (g1, g2) -> eval env g1 - eval env g2
    | Mul (g1, g2) -> eval env g1 * eval env g2
    | If (c, t, e) -> if (eval env c > 0) then eval env t else eval env e
    | Var s -> env s


let test : grammar = If ((Sub ((Var "x"), (Int 11))), (Add ((Var "x"), (Int 11))), (Sub ((Mul ((Var "x"), (Int 11))), (Int 100))))

let () =
  Printf.printf "Enter an integer: ";
  let input_int = read_int () in 
  let res : int = eval (fun str -> if (str = "x") then input_int else 0) test in
  Printf.printf "Result: %d\n" res