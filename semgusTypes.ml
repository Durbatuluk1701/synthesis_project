open Set

type sort = string

let list_to_str (sep : string) list =
  String.concat sep (List.map (fun x -> x#toString) list)

class virtual semgusElement =
  object(self)
    method purifyName (name : string): string = 
      if (String.starts_with ~prefix:"0" name)
      then "purified" ^ name
      else name
    method virtual toString : string
  end


class nonTerminal (ntName : string) (ntType : sort) =
  object(self)
    inherit semgusElement
    method purify: nonTerminal =
      new nonTerminal (self#purifyName ntName) (self#purifyName ntType)
    method toString =
      "(nonterminal " ^ ntName ^ " " ^ ntType ^ ")"
  end

class lhs (nt : nonTerminal) =
  object
    inherit semgusElement
    method purify: lhs =
      new lhs nt#purify
    method toString =
      "(" ^ nt#toString ^ ")"
  end

class virtual rhsExp = 
  object(self)
    inherit semgusElement
    method virtual purify : rhsExp
  end
  
class rhs (rhsExp : rhsExp) =
  object
    inherit semgusElement
    method purify : rhs =
      new rhs (rhsExp#purify)
    method toString =
      "(" ^ rhsExp#toString ^ ")"
  end

class lhsProductionSet (lhs : lhs) (rhsList : rhs list) =
  object
    inherit semgusElement
    method purify: lhsProductionSet =
      new lhsProductionSet (lhs#purify) (List.map (fun x -> x#purify) rhsList)
    method toString =
      "(" ^ lhs#toString ^ "\n" ^ (list_to_str "\n" rhsList) ^ ")"
  end

class synthFun (name : string) (termType : sort) (grm : lhsProductionSet list) =
  object(self)
    inherit semgusElement
    method purify: synthFun =
      new synthFun (self#purifyName name) (self#purifyName termType) (List.map (fun x -> x#purify) grm)
    method toString =
      "(synth-term " ^ name ^ " " ^ termType ^ "\n(" ^ 
        (list_to_str "\n" grm) ^ 
        ")\n)\n"
  end

class virtual rhsAtom =
  object(self)
    inherit rhsExp
    method virtual purify : rhsAtom
  end
  

class rhsOp (opName : string) (args : rhsAtom list) =
  object(self)
    inherit rhsExp
    method purify : rhsOp =
      new rhsOp (self#purifyName opName) (List.map (fun x -> x#purify) args)
    method toString =
      "(" ^ opName ^ " " ^ 
      (list_to_str " " args) ^ ")"
  end

class rhsNT (nt : nonTerminal) =
  object(self)
    inherit rhsAtom
    method purify : rhsNT =
      new rhsNT nt#purify
    method toString =
      nt#toString
  end

class rhsLeaf (leafName : string) = 
  object(self)
    inherit rhsAtom
    method purify : rhsLeaf =
      new rhsLeaf (self#purifyName leafName)
    method toString =
      leafName
  end

class smtFormula (formula : string) =
  object(self)
    inherit semgusElement
    (* NOTE: This is sort of a hack to return SELF! *)
    method purify : smtFormula = new smtFormula formula
    method toString =
      formula
  end

class sortDecl (sortName : sort) =
  object(self)
    inherit semgusElement
    method purify: sortDecl =
      new sortDecl (self#purifyName sortName)
    method toString: string =
      "(declare-sort : " ^ sortName ^ ")"
  end

class varDecl (varName : string) (sortName : sort) =
  object(self)
    inherit semgusElement
    method purify: varDecl =
      new varDecl (self#purifyName varName) (self#purifyName sortName)
    method toString =
      "(declare-var " ^ varName ^ " " ^ sortName ^ ")"
  end

class relDecl (relName : string) (args : sort list) =
  object(self)
    inherit semgusElement
    method purify: relDecl =
      new relDecl (self#purifyName relName) (List.map (self#purifyName) args)
    method toString =
      "(declare-rel " ^ relName ^ " " ^ (String.concat " " args) ^ ")"
    method getName = relName
    method getArgs = args
  end

class ntDecl (ntName : string) (ntType : sort) (ntRel : relDecl) =
  object(self)
    inherit semgusElement
    method purify: ntDecl =
      new ntDecl (self#purifyName ntName) (self#purifyName ntType) (ntRel#purify)
    method toString =
      "(declare-nt " ^ ntName ^ " " ^ ntType ^ " " ^ 
      "(" ^ ntRel#getName ^ 
      " (" ^ (String.concat " " ntRel#getArgs) ^ "))" ^ ")"
  end

class semanticCHC (decl : relDecl) (vars : Set.Make(smtVariable)) (head : smtFormula) (tail : smtFormula) =
  object
    inherit semgusElement
    method purify : semanticCHC =
      new semanticCHC decl#purify (List.map (fun x -> x#purify) vars) head#purify tail#purify
    method toString =
      "(rule (" ^ head#toString ^ ") (" ^ tail#toString ^ "))"
  end

class smtVariable (name : string) (tp : sort) =
  object(self)
    inherit semgusElement
    method purify : smtVariable =
      new smtVariable (self#purifyName name) tp
    method toString =
      ""
  end

class smtConstraint (formula : smtFormula) =
  object(self)
    inherit semgusElement
    method purify : smtConstraint =
      new smtConstraint (formula#purify)
    method toString =
      "(constraint " ^ formula#toString ^ ")"
  end

class semgusFile (commands : semgusElement list) = 
  object(self)
    method purify : semgusFile = 
      new semgusFile (List.map (fun (x : semgusElement) -> x#purify) commands)
    method toString : string =
      String.concat "\n" (List.map (fun x -> x#toString) commands)
  end
