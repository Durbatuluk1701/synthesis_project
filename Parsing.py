from typing import Sequence
from Utils import ImpossibleError, sequence_to_str, trueMap


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
  def __init__(self, slist: Sequence[SExpr]):
    super().__init__()
    self.slist = slist
  def __str__(self) -> str:
    listStr = sequence_to_str(" ", self.slist)
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


