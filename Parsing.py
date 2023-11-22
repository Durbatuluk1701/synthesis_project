from typing import list
from SemgusTypes import LHSProductionSet, NTDecl, RelDecl, SortDecl, SynthFun, VarDecl
from Utils import ImpossibleError, list_to_str, trueMap


class SExpr:
  def __init__(self):
    pass
  def __str__(self) -> str:
    raise ImpossibleError("Should never construct just SExpr")
  def removeAnnotations(self) -> 'SExpr':
    return self

class SExprLeaf(SExpr):
  def __init__(self):
    super().__init__()
    pass

class SExprInt(SExprLeaf):
  def __init__(self, v : int):
    super().__init__()
    self.v = v
  def __str__(self) -> str:
    return str(self.v)
  
class SExprBool(SExprLeaf):
  def __init__(self, v : bool):
    super().__init__()
    self.v = v
  def __str__(self) -> str:
    return str(self.v)

class SExprString(SExprLeaf):
  def __init__(self, s : str):
    super().__init__()
    self.s = s
  def __str__(self) -> str:
    return f"\"{self.s}\""

class SExprBV(SExprLeaf):
  def __init__(self, v : int):
    super().__init__()
    self.v = v
  def __str__(self) -> str:
    # NOTE: Is this right?!
    return f"#x{self.v}%08x"

class SExprName(SExprLeaf):
  def __init__(self, s : str):
    super().__init__()
    self.s = s
  def __str__(self) -> str:
    return self.s

class SExprList(SExpr):
  def __init__(self, slist: list[SExpr]):
    super().__init__()
    self.slist = slist
  def __str__(self) -> str:
    listStr = list_to_str(" ", self.slist)
    return f"({listStr})"
  def removeAnnotations(self) -> SExpr:
    if (isinstance(self.slist[0], SExprName) and self.slist[0].s == "!"):
      return self.slist[1].removeAnnotations()
    return SExprList(trueMap(lambda x: x.removeAnnotations(), self.slist))

class Token:
  def __init__(self) -> None:
    pass
    self.isEmpty = False
  def __str__(self) -> str:
    raise ImpossibleError("Should never call pure token str method")

class LParen(Token):
  def __init__(self) -> None:
    super().__init__()
  def __str__(self) -> str:
    return "("
 
class RParen(Token):
  def __init__(self) -> None:
    super().__init__()
  def __str__(self) -> str:
    return ")"

class Whitespace(Token):
  def __init__(self) -> None:
    super().__init__()
  def __str__(self) -> str:
    return " "

class Newline(Token):
  def __init__(self) -> None:
    super().__init__()
  def __str__(self) -> str:
    return "\n"

class Quote(Token):
  def __init__(self) -> None:
    super().__init__()
  def __str__(self) -> str:
    return "\""

class SemiColon(Token):
  def __init__(self) -> None:
    super().__init__()
  def __str__(self) -> str:
    return ";"

class StrToken(Token):
  def __init__(self, s : str) -> None:
    super().__init__()
    self.s = s
    self.isEmpty = True if len(s) == 0 else False
  def __str__(self) -> str:
    return self.s

# TODO: This class can definitely be optimized
class Lexer:
  def __init__(self) -> None:
    pass
  def recursiveTokenize(self, input: list[str], currentStr : str, tokenList: list[Token]) -> list[Token]:
    if len(input) > 0:
      first = input[0]
      rest = input[1:]
      if (first == "("):
        tokenList.append(StrToken(currentStr))
        tokenList.append(LParen())
        return self.recursiveTokenize(rest, "", tokenList)
      if (first == ")"):
        tokenList.append(StrToken(currentStr))
        tokenList.append(RParen())
        return self.recursiveTokenize(rest, "", tokenList)
      if (first == " " or first == "\t"):
        tokenList.append(StrToken(currentStr))
        tokenList.append(Whitespace())
        return self.recursiveTokenize(rest, "", tokenList)
      if (first == "\n" or first == "\r"):
        tokenList.append(StrToken(currentStr))
        tokenList.append(Newline())
        return self.recursiveTokenize(rest, "", tokenList)
      if (first == ";"):
        tokenList.append(StrToken(currentStr))
        tokenList.append(SemiColon())
        return self.recursiveTokenize(rest, "", tokenList)
      else:
        return self.recursiveTokenize(rest, currentStr + first, tokenList)
    return tokenList
  def tokenize(self, input: list[str]) -> list[Token]:
    tokenList = self.recursiveTokenize(input, "", [])
    retList = []
    for t in tokenList:
      if not t.isEmpty:
        retList.append(t)
    return retList

class ParseResult:
  def __init__(self, res : SExpr, rem : list[Token]) -> None:
    self.res = res
    self.rem = rem

class ParseError(Exception):
    def __init__(self, message="Error encountered during parsing"):
        self.message = message
        super().__init__(self.message)

class Parser:
  def __init__(self) -> None:
    pass
  def parseNewComment(self, tokens: list[Token]) -> list[Token]:
    if (isinstance(tokens[0], Newline)):
      return tokens[1:]
    return self.parseNewComment(tokens[1:])
  
  def parseNewString(self, tokens : list[Token], builtStr: str) -> ParseResult:
    head = tokens[0]
    tail = tokens[1:]
    if (isinstance(head, Quote)):
      return ParseResult(SExprString(builtStr), tail)
    if (isinstance(head, Newline)):
      raise ParseError("Newlines should not be found in string literals")
    return self.parseNewString(tail, builtStr + str(head))

  def parseNewSExpr(self, tokens: list[Token], sexprs : list[SExpr]) -> ParseResult:
    head = tokens[0]
    tail = tokens[1:]
    if (isinstance(head, LParen)):
      p = self.parseNewSExpr(tail, [])
      sexprs.append(p.res)
      return self.parseNewSExpr(p.rem, sexprs)
    if (isinstance(head, RParen)):
      return ParseResult(SExprList(sexprs), tail)
    if (isinstance(head, Whitespace) or isinstance(head, Newline)):
      return self.parseNewSExpr(tail, sexprs)
    if (isinstance(head, Quote)):
      p = self.parseNewString(tail, "")
      sexprs.append(p.res)
      return self.parseNewSExpr(p.rem, sexprs)
    if (isinstance(head, SemiColon)):
      return self.parseNewSExpr(self.parseNewComment(tail), sexprs)
    if (isinstance(head, StrToken)):
      s = head.s
      t: SExpr | None = None
      if (s.isdigit()):
        t = SExprInt(int(s))
      elif (s == "true"):
        t = SExprBool(True)
      elif (s == "false"):
        t = SExprBool(False)
      elif (s[0:2] == "#x"):
        t = SExprBV(int(s[2:],16))
      else:
        t = SExprName(s)
      sexprs.append(t)
      return self.parseNewSExpr(tail, sexprs)
    raise ImpossibleError("this shouldn't be hit unless an unconstructable token type is used")

  def parse(self, tokens : list[Token]) -> SExpr:
    tokens.append(RParen())
    return self.parseNewSExpr(tokens, []).res

class TranslatorError(Exception):
    def __init__(self, message="Error encountered during translation"):
        self.message = message
        super().__init__(self.message)

class Translator:
  def __init__(self) -> None:
    pass

  def parseNewSortDecl(self) -> SortDecl:
    raise NotImplementedError

  def parseNewVarDecl(self, varNameArgs : SExpr, sortNameArg : SExpr) -> list[VarDecl]:
    varNames: list[str] = []
    sortName: str | None = None
    if (isinstance(varNameArgs, SExprName)):
      varNames = [varNameArgs.s]
    elif (isinstance(varNameArgs, SExprList)):
      for val in varNameArgs.slist:
        if (isinstance(val, SExprName)):
          varNames.append(val.s)
        else:
          raise TranslatorError("Malformed var names in declare-var")
    else:
      raise TranslatorError("Predefined names are not allowed as variable names")
    if (isinstance(sortNameArg, SExprName)):
      sortName = sortNameArg.s
    else:
      raise TranslatorError("Malformed sort name in declare-var")
    retList = []
    for var in varNames:
      retList.append(VarDecl(var, sortName))
    return retList

  def parseNewRelDecl(self, args: list[SExpr]) -> RelDecl:
    relName: str | None = None
    if (isinstance(args[0], SExprName)):
      relName = args[0].s
    else:
      raise TranslatorError("Malformed relation name in declare-rel")
    argSorts = []
    if (isinstance(args[1], SExprList)):
      for val in args[1].slist:
        if (isinstance(val, SExprName)):
          argSorts.append(val.s)
        else:
          raise TranslatorError("Malformed sort argument in declare-rel")
    else:
      raise TranslatorError("malformed sort block in declare-rel")
    return RelDecl(relName, argSorts)

  def praseNewNTDecl(self, ntNameArg: SExpr, ntTypeArg: SExpr, ntRelArg: SExpr) -> NTDecl:
    ntName: str | None = None
    if (isinstance(ntNameArg, SExprName)):
      ntName = ntNameArg.s
    else:
      raise TranslatorError("Malformed nonterminal name in declare-nt")
    ntType: str | None = None
    if (isinstance(ntTypeArg, SExprName)):
      ntType = ntTypeArg.s
    else:
      raise TranslatorError("Malformed term-type name in declare-nt")
    ntRel = None
    if (isinstance(ntRelArg, SExprList)):
      ntRel = self.parseNewRelDecl(ntRelArg.slist)
    else:
      raise TranslatorError("Malformed relation declareation in declare-nt")
    return NTDecl(ntName, ntType, ntRel)

  def parseSExprCommand(self, s : SExpr) -> list[SemgusEvent]:

  def parseNewSynthBlock(self, termNameArg: SExpr, termTypeArg : SExpr, grmBlockArg : SExpr) -> SynthFun:
    name : str | None = None
    if (isinstance(termNameArg, SExprName)):
      name = termNameArg.s
    else:
      raise TranslatorError("Malformed synth-term name in synth-term")
    termTp : str | None = None
    if (isinstance(termTypeArg, SExprName)):
      termTp = termTypeArg.s
    else:
      raise TranslatorError("Malformed synth-term term-type in synth-term")
    cmds = None
    if (isinstance(grmBlockArg, SExprList)):
      cmds = trueMap(self.parseSExprCommand, grmBlockArg.slist)
    else:
      raise TranslatorError("Grammar block malformed in synth-term")
    nts = filter(lambda x: isinstance(x, NTDecl), cmds)
    vars = filter(lambda x: isinstance(x, VarDecl), cmds) 
    prodSets = filter(lambda x: isinstance(x, LHSProductionSet), cmds)



