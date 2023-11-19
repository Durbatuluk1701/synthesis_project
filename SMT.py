import Utils;

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
    self.toString: str = ""

class SMTVarDeclaration(Declaration):
  def __init__(self, varName : str, sortName : str):
    super().__init__()
    self.varName = varName
    self.sortName = sortName
    self.toString = f"(declare-var {varName} {sortName})"

class SMTRelDeclaration(Declaration):
  def __init__(self, relName : str, sortNames: list[str]):
    super().__init__()
    self.relName = relName
    self.sortNames = sortNames
    self.toString = f"(declare-rel {relName} (" + Utils.list_to_str(" ", sortNames) + "))"

class SMTConstructor:
  def __init__(self): 
    pass
  
class SMTAccessor:
  def __init__(self, accessorName : str, argSort : str):
    self.accessorName = accessorName
    self.argSort = argSort
    self.toString = f"({accessorName} {argSort})"
    pass

class SMTOpConstructor(SMTConstructor):
  def __init__(self, name : str, accessors : list[SMTAccessor]):
    super().__init__()
    self.name = name
    self.accessors = accessors
    self.toString = f"({name} " + Utils.list_to_str(" ", accessors) + ")"
    
class SMTLeafConstructor(SMTConstructor):
  def __init__(self, name : str):
    super().__init__()
    self.name = name
    self.toString = name

class SMTDatatypeDeclaration(Declaration):
  def __init__(self, typeName : str, constructors : list[SMTConstructor]):
    super().__init__()
    self.typeName = typeName
    self.constructors = constructors
    self.toString = f"({typeName} " + Utils.list_to_str(" ", constructors) + ")"

class SMTRecDatatypeDeclaration(Declaration):
  def __init__(self, types : list[SMTDatatypeDeclaration]):
    super().__init__()
    self.types = types
    self.toString = f"(declare-datatypes () (" + Utils.list_to_str("\n", types) + "))"

class SMTFormulaHolder(SMTExpr):
  def __init__(self, formula : str):
    super().__init__()
    self.formula = formula
    self.toString = formula

class CHCRule(SMTCommand):
  def __init__(self, premise : SMTFormulaHolder, conclusion : SMTFormulaHolder):
    super().__init__()
    self.premise = premise
    self.conclusion = conclusion
    self.toString = f"(rule (=> {premise.toString} {conclusion.toString}))"

class CHCQuery(SMTCommand):
  def __init__(self, query : SMTFormulaHolder):
    super().__init__()
    self.query = query
    self.toString = f"(query {query.toString})"