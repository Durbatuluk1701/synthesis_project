
type grammar = 
  | Int of int
  | Add of grammar * grammar
  | Sub of grammar * grammar
  | Mul of grammar * grammar
  | If of grammar * grammar * grammar
  | Var of string

type 'G environment =
  string -> 'G

(* type 'G semantics = 
  'G -> 'G -> 'G  

type 'G spec =
  'G -> bool

type 'G semGus = 'G * 'G semantics * 'G spec *)

let rec eval (env : int environment) (g : grammar) : int =
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