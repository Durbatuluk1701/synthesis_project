from SemgusTypes import *;

def semgus2SMT(semgusFile: SemgusFile): list[SMTCommand] = {
  val univGrm = utils.filterNones(semgusFile.commands.map{case l: LHSProductionSet => Some(l); case _ => None})
  val constraints = utils.filterNones(semgusFile.commands.map{case c: Constraint => Some(c); case _ => None})
  val synthFuns = utils.filterNones(semgusFile.commands.map{case s: SynthFun => Some(s); case _ => None})
  val chcEvents = utils.filterNones(semgusFile.commands.map{case c: SemanticCHC => Some(c); case _ => None})
  val rest = semgusFile.commands.filter{
    case _: Constraint => false; case _: SynthFun => false; case _: LHSProductionSet => false; case _ => true}

  val (nctxt, lctxt, datatypeDecls) = translateLHSProductionSet(univGrm)
  val semanticRules = chcEvents.map{translateCHC}
  val semanticVarDecls = chcEvents.foldLeft(Set(): Set[SMTVarDeclaration]){
    case (acc, event) => acc.union(genSemVarDecls(event))}.toList
  val semanticDecls = chcEvents.foldLeft(Set(): Set[SMTRelDeclaration]){
    case (acc, event) => acc + genSemRelDecls(event)}.toList

  val (syntaxVarDecls, syntaxRelDecls, syntaxRules) =
    synthFuns.foldLeft((Set(): Set[SMTVarDeclaration], Set(): Set[SMTRelDeclaration], Nil: List[CHCRule])){
      case ((varacc, relacc, ruleacc), s) => val (varset, relset, rulelist) = translateSynthFun(s)
      (varacc.union(varset), relacc.union(relset), ruleacc:::rulelist)
  }

  val specCHC = genSpecificationCHC(constraints)
  datatypeDecls::semanticVarDecls:::syntaxVarDecls.toList:::semanticDecls:::(realizableDecl::Nil):::
    syntaxRelDecls.toList:::syntaxRules:::semanticRules:::(specCHC::query::Nil)
}
}

