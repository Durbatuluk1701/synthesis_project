from typing import Any 
import Utils;

class SemgusElement:
  def __init__(self):
    pass
  def purifyName(self, name : str) -> str:
    if (name[0] == "0"):
      return f"purified{name}"
    else:
      return name
  def purify(self) -> 'SemgusElement':
    raise NotImplementedError

def purifyMap(l : list[Any]) -> list[Any]:
  acc = []
  for val in l:
    acc.append(val.purify())
  return acc

class SemgusEvent(SemgusElement):
  def __init__(self):
    super().__init__()
  def purify(self) -> 'SemgusEvent':
    raise NotImplementedError

class NonTerminal(SemgusElement):
  def __init__(self, ntName : str, ntType : str):
    super().__init__()
    self.ntName = ntName
    self.ntType = ntType
  def __str__(self) -> str:
    return f"(nonterminal {str(self.ntName)} {str(self.ntType)})"
  def purify(self):
    return NonTerminal(self.purifyName(self.ntName), self.purifyName(self.ntType))

class LHS(SemgusElement):
  def __init__(self, nt : NonTerminal):
    super().__init__()
    self.nt = nt
  def __str__(self) -> str:
    return f"({str(self.nt)})"
  def purify(self):
    return LHS(self.nt.purify())

class RHSExp(SemgusElement):
  def __init__(self):
    super().__init__()
  def purify(self) -> 'RHSExp':
    raise NotImplementedError

class RHSAtom(RHSExp):
  def __init__(self):
    super().__init__()

class RHS(RHSExp):
  def __init__(self, rhsExp : RHSExp):
    super().__init__()
    self.rhsExp = rhsExp
  def __str__(self) -> str:
    return f"({str(self.rhsExp)})"
  def purify(self):
    return RHS(self.rhsExp.purify())

class LHSProductionSet(SemgusEvent):
  def __init__(self, lhs : LHS, rhsList : list[RHS]):
    super().__init__()
    self.lhs = lhs
    self.rhsList = rhsList
  def __str__(self) -> str:
    return f"({str(self.lhs)}\n" + Utils.list_to_str('\n', self.rhsList) + ")"
  def purify(self):
    return LHSProductionSet(self.lhs.purify(), Utils.trueMap(lambda x: x.purify(), self.rhsList))

class SynthFun(SemgusElement):
  def __init__(self, name : str, termType : str, grm : list[LHSProductionSet]):
    super().__init__()
    self.name = name
    self.termType = termType
    self.grm = grm
  def __str__(self) -> str:
    return f"(synth-term {str(self.name)} {str(self.termType)}\n(" + (Utils.list_to_str('\n', self.grm)) + ")\n)\n"
  def purify(self):
    return SynthFun(self.purifyName(self.name), self.purifyName(self.termType), purifyMap(self.grm))

class RHSOp(RHSExp):
  def __init__(self, opName : str, args : list[RHSAtom]):
    super().__init__()
    self.opName = opName
    self.args = args
  def __str__(self) -> str:
    return f"({self.opName} " + Utils.list_to_str("\n", self.args) + ")"
  def purify(self):
    return RHSOp(self.purifyName(self.opName), purifyMap(self.args))

class RHSNt(RHSAtom):
  def __init__(self, nt : NonTerminal):
    super().__init__()
    self.nt = nt
  def __str__(self) -> str:
    return str(self.nt)
  def purify(self):
    return RHSNt(self.nt.purify())

class RHSLeaf(RHSAtom):
  def __init__(self, leafName : str):
    super().__init__()
    self.leafName = leafName
  def __str__(self) -> str:
    return self.leafName
  def purify(self):
    return RHSLeaf(self.purifyName(self.leafName))

class SMTFormula(SemgusElement):
  def __init__(self, formula : str):
    super().__init__()
    self.formula = formula
  def __str__(self) -> str:
    return self.formula
  def purify(self):
    return SMTFormula(self.formula)

class Decl(SemgusEvent):
  def __init__(self):
    super().__init__()

class SortDecl(Decl):
  def __init__(self, sortName : str):
    super().__init__()
    self.sortName = sortName
  def __str__(self) -> str:
    return f"(declare-sort : {self.sortName})"
  def purify(self):
    return SortDecl(self.purifyName(self.sortName))

class VarDecl(Decl):
  def __init__(self, varName : str, sortName : str):
    super().__init__()
    self.varName = varName
    self.sortName = sortName
  def __str__(self) -> str:
    return f"(declare-var {self.varName} {self.sortName})"
  def purify(self):
    return VarDecl(self.purifyName(self.varName), self.purifyName(self.sortName))
  
class RelDecl(Decl):
  def __init__(self, relName: str, args: list[str]):
    super().__init__()
    self.relName = relName
    self.args = args
  def __str__(self) -> str:
    return f"(declare-rel {self.relName} " +  Utils.list_to_str(" ", self.args) + ")"
  def purify(self):
    return RelDecl(self.purifyName(self.relName), Utils.trueMap(self.purifyName, self.args))

class NTDecl(Decl):
  def __init__(self, ntName : str, ntType: str, ntRel : RelDecl):
    super().__init__()
    self.ntName = ntName
    self.ntType = ntType
    self.ntRel = ntRel
  def __str__(self) -> str:
    return f"(declare-nt {self.ntName} {self.ntType} ({self.ntRel.relName} (" + Utils.list_to_str(" ", self.ntRel.args) + ")))"
  def purify(self):
    return NTDecl(self.purifyName(self.ntName), self.purifyName(self.ntType), self.ntRel.purify())

class SMTVariable(SemgusElement):
  def __init__(self, name : str, tp : str):
    super().__init__()
    self.name = name
    self.tp = tp
  def __str__(self) -> str:
    return ""
  def purify(self):
    return SMTVariable(self.purifyName(self.name), self.tp)
    
class SemanticCHC(SemgusEvent):
  def __init__(self, decl : RelDecl, vars : set[SMTVariable], head : SMTFormula, tail : SMTFormula):
    super().__init__()
    self.decl = decl
    self.vars = vars
    self.head = head
    self.tail = tail
  def __str__(self) -> str:
    return f"(rule ({str(self.head)}) ({str(self.tail)}))"
  def purify(self):
    return SemanticCHC(self.decl.purify(), set(purifyMap(list(self.vars))), self.head.purify(), self.tail.purify())

class SmtConstraint(SemgusEvent):
  def __init__(self, formula : SMTFormula):
    super().__init__()
    self.formula = formula
  def __str__(self) -> str:
    return f"(constraint {str(self.formula)})"
  def purify(self):
    return SmtConstraint(self.formula.purify())

class SemgusFile:
  def __init__(self, commands : list[SemgusElement]):
    self.commands = commands
  def __str__(self) -> str:
    return Utils.list_to_str("\n", self.commands)
  def purify(self):
    return SemgusFile(Utils.trueMap(lambda x: x.purify(), self.commands))