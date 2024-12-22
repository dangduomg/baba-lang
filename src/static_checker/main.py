"""Static analyzer and checker"""


from enum import Enum

from lark.tree import Meta

from bl_ast.base import _AstNode, ASTVisitor
from bl_ast import nodes


class StaticError(ValueError):
    """Static error: program failed the static check"""

    msg: str
    meta: Meta

    def __init__(self, msg, meta, *args, **kwargs):
        super().__init__(msg, meta, *args, **kwargs)
        self.msg = msg
        self.meta = meta

    def __str__(self) -> str:
        return (
            f"Static check failed at line {self.meta.line}, " +
            f"column {self.meta.column}: {self.msg}"
        )


class BodyType(Enum):
    """Context of the Body node"""
    NORMAL = 0
    LOOP = 1
    FUNCTION = 2
    MODULE = 3


class StaticChecker(ASTVisitor):
    """Static checker class"""

    # pylint: disable=too-few-public-methods

    modes: list[BodyType]

    def __init__(self):
        self.modes = [BodyType.MODULE]

    def visit(self, node: _AstNode) -> None:
        # pylint: disable=protected-access
        match node:
            case (
                nodes.Exprs(expressions=expressions)
                | nodes.List(elems=expressions)
            ):
                for expr in expressions:
                    self.visit(expr)
            case (
                nodes.Assign(right=right) | nodes.Inplace(right=right)
                | nodes.Prefix(operand=right) | nodes.Dot(accessee=right)
            ):
                self.visit(right)
            case (
                nodes.And(left=left, right=right)
                | nodes.Or(left=left, right=right)
                | nodes.BinaryOp(left=left, right=right)
                | nodes.Subscript(subscriptee=left, index=right)
            ):
                self.visit(left)
                self.visit(right)
            case nodes.Call(callee=callee, args=args):
                self.visit(callee)
                for arg in args.args:
                    self.visit(arg)
            case nodes.Dict(pairs=pairs):
                for pair in pairs:
                    self.visit(pair.key)
                    self.visit(pair.value)
            case nodes.FunctionLiteral(body=body):
                self.modes.append(BodyType.FUNCTION)
                self.visit(body)
                self.modes.pop()
            case nodes.Body(statements=statements):
                for stmt in statements:
                    self.visit(stmt)
            case nodes.ReturnStmt(meta=meta):
                for i in range(-1, -1 - len(self.modes), -1):
                    match self.modes[i]:
                        case BodyType.MODULE:
                            break
                        case BodyType.FUNCTION:
                            return
                raise StaticError(
                    "'return' used outside of functions", meta
                )
            case nodes.IfStmt(body=body):
                self.modes.append(BodyType.NORMAL)
                self.visit(body)
                self.modes.pop()
            case nodes.IfElseStmt(then_body=then_body, else_body=else_body):
                self.modes.append(BodyType.NORMAL)
                self.visit(then_body)
                self.visit(else_body)
                self.modes.pop()
            case nodes.WhileStmt(body=body):
                self.modes.append(BodyType.LOOP)
                self.visit(body)
                self.modes.pop()
            case nodes.BreakStmt(meta=meta):
                for i in range(-1, -1 - len(self.modes), -1):
                    match self.modes[i]:
                        case BodyType.MODULE | BodyType.FUNCTION:
                            break
                        case BodyType.LOOP:
                            return
                raise StaticError(
                    "'break' used outside of loops", meta
                )
            case nodes.ContinueStmt(meta=meta):
                for i in range(-1, -1 - len(self.modes), -1):
                    match self.modes[i]:
                        case BodyType.MODULE | BodyType.FUNCTION:
                            break
                        case BodyType.LOOP:
                            return
                raise StaticError(
                    "'continue' used outside of loops", meta
                )
            case nodes.FunctionStmt(body=body):
                self.modes.append(BodyType.FUNCTION)
                self.visit(body)
                self.modes.pop()
            case nodes.ModuleStmt(body=body):
                self.modes.append(BodyType.MODULE)
                self.visit(body)
                self.modes.pop()
