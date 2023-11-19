from typing import TypeVar

T = TypeVar('T')

def list_to_str (sep : str, l : list[T]) -> str:
  retStr: str = ""
  for i in range(len(l)):
    retStr += l[i].tostr
    if (i == len(l)):
      retStr += sep
  return retStr

class SemgusElement:
  def __init__(self):
    pass
  def purifyName(self, name : str) -> str:
    if (name[0] == "0"):
      return f"purified{name}"
    else:
      return name
  def purify():
    raise NotImplementedError

def purifyMap(l : list[SemgusElement]) -> list[SemgusElement]:
  acc = []
  for val in l:
    acc += val.purify()
  return acc

class NonTerminal(SemgusElement):
  def __init__(self, ntName : str, ntType : str):
    super().__init__()
    self.ntName = ntName
    self.ntType = ntType
    self.tostr = f"(nonterminal {ntName} {ntType})"
  def purify(self):
    return NonTerminal(self.purifyName(self.ntName), self.purifyName(self.ntType))

class LHS(SemgusElement):
  def __init__(self, nt : NonTerminal):
    super().__init__()
    self.nt = nt
    self.tostr = "({self.nt.tostr})"
  def purify(self):
    return LHS(self.nt.purify())

class RHS(SemgusElement):
  def __init__(self, rhsExp : SemgusElement):
    super().__init__()
    self.rhsExp = rhsExp
    self.tostr = "({rhsExp.tostr})"
  def purify(self):
    return RHS(self.rhsExp.purify())
    
class LHSProductionSet(SemgusElement):
  def __init__(self, lhs : LHS, rhsList : list[RHS]):
    super().__init__()
    self.lhs = lhs
    self.rhsList = rhsList
    self.tostr = f"({lhs.tostr}\n" + list_to_str('\n', rhsList) + ")"
  def purify(self):
    return LHSProductionSet(self.lhs.purify(), map(lambda x: x.purify(), self.rhsList))

class SynthFun(SemgusElement):
  def __init__(self, name : str, termType : str, grm : list[LHSProductionSet]):
    super().__init__()
    self.name = name
    self.termType = termType
    self.grm = grm
    self.tostr = f"(synth-term {name} {termType}\n(" + (list_to_str('\n', grm)) + ")\n)\n"
  def purify(self):
    return SynthFun(self.purifyName(self.name), self.purifyName(self.termType), purifyMap(self.grm))

class RHSOp(SemgusElement):
  def __init__(self, opName : str, args : list[SemgusElement]):
    super().__init__()
    self.opName = opName
    self.args = args
    self.tostr = f"({opName} " + list_to_str("\n", args) + ")"
  def purify(self):
    return RHSOp(self.purifyName(self.opName), purifyMap(self.args))

class RHSNt(SemgusElement):
  def __init__(self, nt : NonTerminal):
    super().__init__()
    self.nt = nt
    self.tostr = nt.tostr
  def purify(self):
    return RHSNt(self.nt.purify())

class RHSLeaf(SemgusElement):
  def __init__(self, leafName : str):
    super().__init__()
    self.leafName = leafName
    self.tostr = leafName
  def purify(self):
    return RHSLeaf(self.purifyName(self.leafName))

class SMTFormula(SemgusElement):
  def __init__(self, formula : str):
    super().__init__()
    self.formula = formula
    self.tostr = formula
  def purify(self):
    return SMTFormula(self.formula)

class SortDecl(SemgusElement):
  def __init__(self, sortName : str):
    super().__init__()
    self.sortName = sortName
    self.tostr = f"(declare-sort : {sortName})"
  def purify(self):
    return SortDecl(self.purifyName(self.sortName))

class VarDecl(SemgusElement):
  def __init__(self, varName : str, sortName : str):
    super().__init__()
    self.varName = varName
    self.sortName = sortName
    self.tostr = f"(declare-var {varName} {sortName})"
  def purify(self):
    return VarDecl(self.purifyName(self.varName), self.purifyName(self.sortName))
  
class RelDecl(SemgusElement):
  def __init__(self, relName: str, args: list[str]):
    super().__init__()
    self.relName = relName
    self.args = args
    self.tostr = f"(declare-rel {relName} " +  list_to_str(" ", args) + ")"
  def purify(self):
    return RelDecl(self.purifyName(self.relName, map(self.purifyName, self.args)))

class NTDecl(SemgusElement):
  def __init__(self, ntName : str, ntType: str, ntRel : RelDecl):
    super().__init__()
    self.ntName = ntName
    self.ntType = ntType
    self.ntRel = ntRel
    self.tostr = f"(declare-nt {ntName} {ntType} ({ntRel.relName} (" + list_to_str(" ", ntRel.args) + ")))"
  def purify(self):
    return NTDecl(self.purifyName(self.ntName), self.purifyName(self.ntType, self.ntRel.purify()))

class SMTVariable(SemgusElement):
  def __init__(self, name : str, tp : str):
    super().__init__()
    self.name = name
    self.tp = tp
    self.tostr = ""
  def purify(self):
    return SMTVariable(self.purifyName(self.name), self.tp)
    
class SemanticCHC(SemgusElement):
  def __init__(self, decl : RelDecl, vars : set[SMTVariable], head : SMTFormula, tail : SMTFormula):
    super().__init__()
    self.decl = decl
    self.vars = vars
    self.head = head
    self.tail = tail
    self.tostr = f"(rule ({head.tostr}) ({tail.tostr}))"
  def purify(self):
    return SemanticCHC(self.decl.purify(), purifyMap(self.vars), self.head.purify(), self.tail.purify())


class SmtConstraint(SemgusElement):
  def __init__(self, formula : SMTFormula):
    super().__init__()
    self.formula = formula
    self.tostr = f"(constraint {formula.tostr})"
  def purify(self):
    return SmtConstraint(self.formula.purify())

class SemgusFile:
  def __init__(self, commands : list[SemgusElement]):
    self.commands: list[SemgusElement] = commands
    self.tostr: str = list_to_str("\n", commands)
  def purify(self):
    return SemgusFile(map(lambda x: x.purify(), self.commands))