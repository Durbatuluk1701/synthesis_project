from typing import Mapping, list
import SemgusTypes as SGT
import SMT
from Utils import ImpossibleError, filterNones, list_to_str, trueMap

counter = 0
realizableDecl = SMT.SMTRelDeclaration("realizable", [])
realizableRel = SMT.SMTFormulaHolder("realizable")
query = SMT.CHCQuery(realizableRel)

NTCtxt = Mapping[str, str]
LeafCtxt = Mapping[str, str]
DeclCtxt = Mapping[str, set[SMT.SMTConstructor]]

def genNewAccessor(opName: str) -> str:
  global counter
  counter = counter + 1
  return f"{opName}Ac{counter}"

def synRelName(ntName: str) -> str: return f"{ntName}.Syn"

def synVarName(ntName: str, index: int) -> str: return f"{ntName}.SynVar{index}"

def genNTCtxt(prods : list[SGT.LHSProductionSet]) -> NTCtxt:
  endMap: NTCtxt = {}
  for lhs in prods:
    endMap[lhs.lhs.nt.ntName] = lhs.lhs.nt.ntType
  return endMap

def genLeafCtxt(ntcTxt: NTCtxt, prods : list[SGT.LHSProductionSet]) -> LeafCtxt:
  # NOTE: This was a complicated function, verify equiv
  endMap: LeafCtxt = {}
  for lhs in prods:
    for rhs in lhs.rhsList:
      if (isinstance(rhs, SGT.RHSOp) or isinstance(rhs, SGT.RHSNt)):
        continue
      if (isinstance(rhs, SGT.RHSLeaf)):
        if (endMap[rhs.leafName] is not None):
          endMap[rhs.leafName] = ntcTxt[lhs.lhs.nt.ntName]
  return endMap

def genConstructorFromRHSExp(ntcTxt: NTCtxt, leafcTxt: LeafCtxt, rhsExp: SGT.RHSExp) -> SMT.SMTConstructor:
  if (isinstance(rhsExp, SGT.RHSOp)):
    accessors: list[SMT.SMTAccessor] = []
    for val in rhsExp.args:
      if (isinstance(val, SGT.RHSNt)):
        accessors.append(SMT.SMTAccessor(genNewAccessor(rhsExp.opName), ntcTxt[val.nt.ntName]))
      if (isinstance(val, SGT.RHSLeaf)):
        accessors.append(SMT.SMTAccessor(genNewAccessor(rhsExp.opName), leafcTxt[val.leafName]))
    return SMT.SMTOpConstructor(rhsExp.opName, accessors)
  if (isinstance(rhsExp, SGT.RHSNt)):
    opName = f"single-NT{rhsExp.nt.ntName}"
    accessorName = genNewAccessor(opName)
    return SMT.SMTOpConstructor(accessorName, [SMT.SMTAccessor(accessorName, ntcTxt[rhsExp.nt.ntName])])
  if (isinstance(rhsExp, SGT.RHSLeaf)):
    return SMT.SMTLeafConstructor(rhsExp.leafName)
  raise ImpossibleError("This should never have been reached!")

def genDatatypeDecl(ntcTxt: NTCtxt, leafCtxt: LeafCtxt, prods: list[SGT.LHSProductionSet]) -> SMT.SMTRecDatatypeDeclaration:
  constructorMap: Mapping[str, list[SMT.SMTConstructor]] = {}
  for prod in prods:
    rhsConsts: list[SMT.SMTConstructor] = []
    for rProd in prod.rhsList:
      rhsConsts.append(genConstructorFromRHSExp(ntcTxt, leafCtxt, rProd.rhsExp))
    lhsType = ntcTxt[prod.lhs.nt.ntName]
    if (constructorMap[lhsType] is not None):
      constructorMap[lhsType] = list(set(constructorMap[lhsType]).union(set(rhsConsts)))
    else:
      constructorMap[lhsType] = rhsConsts
  mappedTerms = []
  for (termty, vals) in constructorMap.items():
    mappedTerms.append(SMT.SMTDatatypeDeclaration(termty, vals))
  return SMT.SMTRecDatatypeDeclaration(mappedTerms)

def genSemRelDecls(chc : SGT.SemanticCHC) -> SMT.SMTRelDeclaration:
  return genRelDecl(chc.decl)

def genSemVarDecls(chc : SGT.SemanticCHC) -> set[SMT.SMTVarDeclaration]:
  acc: set[SMT.SMTVarDeclaration] = set()
  for var in chc.vars:
    acc.add(SMT.SMTVarDeclaration(var.name, var.tp))
  return acc
    
def translateCHC(chc : SGT.SemanticCHC) -> SMT.CHCRule:
  return SMT.CHCRule(SMT.SMTFormulaHolder(chc.head.formula), SMT.SMTFormulaHolder(chc.tail.formula))

def getVarDecl(varDecl: SGT.VarDecl) -> SMT.SMTVarDeclaration: return SMT.SMTVarDeclaration(varDecl.varName, varDecl.sortName)
def genRelDecl(relDecl: SGT.RelDecl) -> SMT.SMTRelDeclaration: return SMT.SMTRelDeclaration(relDecl.relName, relDecl.args)

def genSpecificationCHC(constraints : list[SGT.SmtConstraint]) -> SMT.CHCRule:
  constFormulas: list[str] = []
  for val in constraints:
    constFormulas.append(val.formula.formula)
  formulaStr = list_to_str(" ", constFormulas)
  premiseStr = formulaStr if (len(constFormulas) == 1) else f"(and {formulaStr})"
  return SMT.CHCRule(SMT.SMTFormulaHolder(premiseStr), realizableRel)

def translateLHSProductionSet(l : list[SGT.LHSProductionSet]) -> tuple[NTCtxt, LeafCtxt, SMT.SMTRecDatatypeDeclaration]:
  ntCtxt = genNTCtxt(l)
  leafCtxt = genLeafCtxt(ntCtxt, l)
  datatypeDecl = genDatatypeDecl(ntCtxt, leafCtxt, l)
  return (ntCtxt, leafCtxt, datatypeDecl)

def genSyntaxDecls(l: list[SGT.LHSProductionSet]) -> set[SMT.SMTRelDeclaration]:
  return set(map(lambda l: SMT.SMTRelDeclaration(synRelName(l.lhs.nt.ntName), [l.lhs.nt.ntType]), l))

def genSyntaxRules(l : list[SGT.LHSProductionSet]) -> tuple[list[SMT.CHCRule], set[SMT.SMTVarDeclaration]]:
  allCHCRules: list[SMT.CHCRule] = []
  allVarDecs: set[SMT.SMTVarDeclaration] = set()
  
  for lhs in l:
    headVar = synVarName(lhs.lhs.nt.ntName, 0)
    headVarDecl = SMT.SMTVarDeclaration(headVar, lhs.lhs.nt.ntType)
    headRel = synRelName(lhs.lhs.nt.ntName)
    head = SMT.SMTFormulaHolder(f"({headRel} {headVar})")
    premisesDecls: list[tuple[SMT.SMTFormulaHolder, set[SMT.SMTVarDeclaration]]] = []
    for rhs in lhs.rhsList:
      if (isinstance(rhs, SGT.RHSOp)):
        rhsTermStringVals: list[str] = []
        rhsPremisesVals: list[SMT.SMTFormulaHolder] = []
        rhsVarDecls: set[SMT.SMTVarDeclaration] = set()
        for i in range(len(rhs.args)):
          arg = rhs.args[i]
          if (isinstance(arg, SGT.RHSNt)):
            rhsTermStringVals.append(synVarName(arg.nt.ntName, i+1))
            rhsPremisesVals.append(SMT.SMTFormulaHolder(f"({synRelName(arg.nt.ntName)} {synVarName(arg.nt.ntName, i + 1)})"))
            rhsVarDecls.add(SMT.SMTVarDeclaration(synVarName(arg.nt.ntName, i + 1), arg.nt.ntType))

          if (isinstance(arg, SGT.RHSLeaf)):
            rhsTermStringVals.append(arg.leafName)
            rhsPremisesVals.append(SMT.SMTFormulaHolder("true"))

          else:
            raise ImpossibleError("Error, only types shouldve been RHSNt and RHSLeaf")
        rhsTermString = list_to_str(" ", rhsTermStringVals)
        rhsPremiseString = list_to_str(" ", rhsPremisesVals)
        eqString = f"(= {headVar} ({rhs.opName} {rhsTermString}))"
        premisesDecls.append((SMT.SMTFormulaHolder(f"(and {eqString} {rhsPremiseString})"), rhsVarDecls))
      if (isinstance(rhs, SGT.RHSNt)):
        rhsVar = synVarName(rhs.nt.ntName, 1)
        rhsRel = synRelName(rhs.nt.ntName)
        premisesDecls.append(
          (SMT.SMTFormulaHolder(f"add ((= {rhsVar} {headVar}) ({rhsRel} {rhsVar}))"), set([SMT.SMTVarDeclaration(rhsVar, rhs.nt.ntType)]))
          )
        continue
      if (isinstance(rhs, SGT.RHSLeaf)):
        premisesDecls.append(
          (SMT.SMTFormulaHolder(f"(= {headVar} {rhs.leafName})"),
           set())
        )
        continue
    premises: list[SMT.CHCRule] = []
    decls: set[SMT.SMTVarDeclaration] = set()
    for (fh, vd) in premisesDecls:
      premises.append(SMT.CHCRule(fh, head))
      decls.union(vd)
    decls.add(headVarDecl)

    allCHCRules.extend(premises)
    allVarDecs.union(decls)
  return (allCHCRules, allVarDecs)


def translateSynthFun(s : SGT.SynthFun) -> tuple[set[SMT.SMTVarDeclaration], set[SMT.SMTRelDeclaration], list[SMT.CHCRule]]:
  (syntaxRules, syntaxVarDecls) = genSyntaxRules(s.grm)
  syntaxRelDecls = genSyntaxDecls(s.grm)
  funDecl = SMT.SMTVarDeclaration(s.name, s.termType)
  syntaxVarDecls.add(funDecl)
  return (syntaxVarDecls, syntaxRelDecls, syntaxRules)


def semgus2SMT(semgusFile: SGT.SemgusFile) -> list[SMT.SMTCommand]:
  univGrm = filterNones(trueMap(lambda x: x if isinstance(x, SGT.LHSProductionSet) else None, semgusFile.commands))

  constraints = filterNones(trueMap(lambda x: x if isinstance(x, SGT.SmtConstraint) else None, semgusFile.commands))

  synthFuns = filterNones(trueMap(lambda x: x if isinstance(x, SGT.SynthFun) else None, semgusFile.commands))
  
  chcEvents = filterNones(trueMap(lambda x: x if isinstance(x, SGT.SemanticCHC) else None, semgusFile.commands))
  
  # NOTE: Possible double encoding of chc events here?
  rest = filterNones(trueMap(lambda x: None if (isinstance(x, SGT.SmtConstraint) or isinstance(x, SGT.SynthFun) or isinstance(x, SGT.LHSProductionSet)) else x, semgusFile.commands))
  
  (nctxt, lctxt, datatypeDecls) = translateLHSProductionSet(univGrm)
  
  semanticRules = trueMap(translateCHC, chcEvents)

  semanticVarDeclsSet: set[SMT.SMTVarDeclaration] = set()
  semanticDeclsSet: set[SMT.SMTRelDeclaration] = set()
  for ev in chcEvents:
    semanticVarDeclsSet.union(genSemVarDecls(ev))
    semanticDeclsSet.add(genSemRelDecls(ev))
  semanticVarDecls: list[SMT.SMTVarDeclaration] = list(semanticVarDeclsSet)
  semanticDecls: list[SMT.SMTRelDeclaration] = list(semanticDeclsSet)

  syntaxVarDecls: set[SMT.SMTVarDeclaration] = set()
  syntaxRelDecls: set[SMT.SMTRelDeclaration] = set()
  syntaxRules: list[SMT.CHCRule] = []
  for fn in synthFuns:
    (varset, relset, rulelist) = translateSynthFun(fn)
    syntaxVarDecls.union(varset)
    syntaxRelDecls.union(relset)
    syntaxRules.extend(rulelist)
    
  specCHC = genSpecificationCHC(constraints)

  returnlist: list[SMT.SMTCommand] = []
  returnlist.append(datatypeDecls)
  returnlist.extend(semanticVarDecls)
  returnlist.extend(list(syntaxVarDecls))
  returnlist.extend(semanticDecls)
  returnlist.append(realizableDecl)
  returnlist.extend(list(syntaxRelDecls))
  returnlist.extend(syntaxRules)
  returnlist.extend(semanticRules)
  returnlist.append(specCHC)
  returnlist.append(query)

  return returnlist

