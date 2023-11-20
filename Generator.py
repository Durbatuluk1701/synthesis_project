import SemgusTypes as SGT
from SMT import SMTCommand
from Utils import filterNones, trueMap



def semgus2SMT(semgusFile: SGT.SemgusFile) -> list[SMTCommand]:
  univGrm = filterNones(trueMap(lambda x: x if isinstance(x, SGT.LHSProductionSet) else None, semgusFile.commands))

  constraints = filterNones(trueMap(lambda x: x if isinstance(SGT.SmtConstraint) else None, semgusFile.commands))

  synthFuns = filterNones(trueMap(lambda x: x if isinstance(SGT.SynthFun) else None, semgusFile.commands))
  
  chcEvents = filterNones(trueMap(lambda x: x if isinstance(SGT.SemanticCHC) else None, semgusFile.commands))
  
  # NOTE: Possible double encoding of chc events here?
  rest = filterNones(trueMap(lambda x: None if (isinstance(SGT.SmtConstraint) or isinstance(SGT.SynthFun) or isinstance(SGT.LHSProductionSet)) else x, semgusFile.commands))
  
  test

  (nctxt, lctxt, datatypeDecls) = translateLHSProductionSet(univGrm)
  semanticRules = chcEvents.map{translateCHC}
  semanticVarDecls = chcEvents.foldLeft(Set(): Set[SMTVarDeclaration]){
    case (acc, event) => acc.union(genSemVarDecls(event))}.toList
  semanticDecls = chcEvents.foldLeft(Set(): Set[SMTRelDeclaration]){
    case (acc, event) => acc + genSemRelDecls(event)}.toList

  (syntaxVarDecls, syntaxRelDecls, syntaxRules) =
    synthFuns.foldLeft((Set(): Set[SMTVarDeclaration], Set(): Set[SMTRelDeclaration], Nil: List[CHCRule])){
      case ((varacc, relacc, ruleacc), s) => val (varset, relset, rulelist) = translateSynthFun(s)
      (varacc.union(varset), relacc.union(relset), ruleacc:::rulelist)
  }

  specCHC = genSpecificationCHC(constraints)
  datatypeDecls::semanticVarDecls:::syntaxVarDecls.toList:::semanticDecls:::(realizableDecl::Nil):::
    syntaxRelDecls.toList:::syntaxRules:::semanticRules:::(specCHC::query::Nil)

