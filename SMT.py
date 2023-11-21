from typing import Sequence
import Utils

class SMT:
  def __init__(self):
    pass
  
class SMTCommand(SMT):
  def __init__(self):
    super().__init__()
    
class Declaration(SMTCommand):
  def __init__(self):
    super().__init__()

class SMTExpr(SMTCommand):
  def __init__(self):
    super().__init__()

class Skip(SMTCommand):
  def __init__(self):
    super().__init__()
  def __str__(self) -> str:
    return ""

class SMTVarDeclaration(Declaration):
  def __init__(self, varName : str, sortName : str):
    super().__init__()
    self.varName = varName
    self.sortName = sortName
  def __str__(self) -> str:
    return f"(declare-var {self.varName} {self.sortName})"

class SMTRelDeclaration(Declaration):
  def __init__(self, relName : str, sortNames: Sequence[str]):
    super().__init__()
    self.relName = relName
    self.sortNames = sortNames
  def __str__(self) -> str:
    return f"(declare-rel {self.relName} (" + Utils.sequence_to_str(" ", self.sortNames) + "))"

class SMTConstructor:
  def __init__(self): 
    pass
  
class SMTAccessor:
  def __init__(self, accessorName : str, argSort : str):
    self.accessorName = accessorName
    self.argSort = argSort
  def __str__(self) -> str:
    return f"({self.accessorName} {self.argSort})"

class SMTOpConstructor(SMTConstructor):
  def __init__(self, name : str, accessors : Sequence[SMTAccessor]):
    super().__init__()
    self.name = name
    self.accessors = accessors
  def __str__(self) -> str:
    return f"({self.name} " + Utils.sequence_to_str(" ", self.accessors) + ")"
    
class SMTLeafConstructor(SMTConstructor):
  def __init__(self, name : str):
    super().__init__()
    self.name = name
  def __str__(self) -> str:
    return self.name

class SMTDatatypeDeclaration(Declaration):
  def __init__(self, typeName : str, constructors : Sequence[SMTConstructor]):
    super().__init__()
    self.typeName = typeName
    self.constructors = constructors
  def __str__(self) -> str:
    return f"({self.typeName} " + Utils.sequence_to_str(" ", self.constructors) + ")"

class SMTRecDatatypeDeclaration(Declaration):
  def __init__(self, types : Sequence[SMTDatatypeDeclaration]):
    super().__init__()
    self.types = types
  def __str__(self) -> str:
    return f"(declare-datatypes () (" + Utils.sequence_to_str("\n", self.types) + "))"

class SMTFormulaHolder(SMTExpr):
  def __init__(self, formula : str):
    super().__init__()
    self.formula = formula
  def __str__(self) -> str:
    return self.formula

class CHCRule(SMTCommand):
  def __init__(self, premise : SMTFormulaHolder, conclusion : SMTFormulaHolder):
    super().__init__()
    self.premise = premise
    self.conclusion = conclusion
  def __str__(self) -> str:
    return f"(rule (=> {str(self.premise)} {str(self.conclusion)}))"

class CHCQuery(SMTCommand):
  def __init__(self, query : SMTFormulaHolder):
    super().__init__()
    self.query = query
  def __str__(self) -> str:
    return f"(query {str(self.query)})"