"""Static analyzer and checker"""


from enum import Enum

from lark.tree import Meta

from bl_ast.base import ASTVisitor
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
            f"column {self.meta.column}:\n" +
            f"{self.msg}\n"
        )

    def get_context(self, text: str | bytes, span: int = 40) -> str | bytes:
        """Returns a pretty string pinpointing the error in the text,
        with span amount of context characters around it.

        Note:
            The parser doesn't hold a copy of the text it has to parse,
            so you have to provide it again
        """
        # stolen from Lark
        pos = self.meta.start_pos
        start = max(pos - span, 0)
        end = pos + span
        if isinstance(text, str):
            before = text[start:pos].rsplit('\n', 1)[-1]
            after = text[pos:end].split('\n', 1)[0]
            return (
                before + after + '\n' + ' ' * len(before.expandtabs()) +
                '^\n'
            )
        text = bytes(text)
        before = text[start:pos].rsplit(b'\n', 1)[-1]
        after = text[pos:end].split(b'\n', 1)[0]
        return (
            (before + after + b'\n' + b' ' * len(before.expandtabs()) +
             b'^\n').decode("ascii", "backslashreplace")
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

    def visit(self, node: nodes._AstNode) -> nodes._AstNode:
        # pylint: disable=too-many-locals
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
            case nodes._Stmt():
                return self.visit_stmt(node)
        return node

    def visit_stmt(self, node: nodes._Stmt) -> nodes._Stmt:
        """Visit a statement node"""
        # pylint: disable=too-many-return-statements
        match node:
            case nodes.Body():
                return self.visit_body(node)
            case nodes.ReturnStmt(meta=meta):
                for i in range(-1, -1 - len(self.modes), -1):
                    match self.modes[i]:
                        case BodyType.MODULE:
                            break
                        case BodyType.FUNCTION:
                            return node
                raise StaticError(
                    "'return' used outside of functions", meta
                )
            case nodes.IfStmt(meta=meta, condition=condition, body=body):
                match self.visit(condition):
                    case nodes.TrueLiteral():
                        return body
                    case nodes.FalseLiteral():
                        return nodes.NopStmt(meta)
                self.modes.append(BodyType.NORMAL)
                node.body = self.visit_body(body)
                self.modes.pop()
            case nodes.IfElseStmt(
                condition=condition, then_body=then_body, else_body=else_body
            ):
                match self.visit(condition):
                    case nodes.TrueLiteral():
                        return then_body
                    case nodes.FalseLiteral():
                        return else_body
                self.modes.append(BodyType.NORMAL)
                node.then_body = self.visit_body(then_body)
                node.else_body = self.visit_stmt(else_body)
                self.modes.pop()
            case nodes.WhileStmt(
                condition=condition, body=body,
                eval_condition_after=eval_condition_after,
            ):
                match self.visit(condition):
                    case nodes.FalseLiteral():
                        if eval_condition_after:
                            return body
                        return nodes.NopStmt(condition.meta)
                self.modes.append(BodyType.LOOP)
                node.body = self.visit_body(body)
                self.modes.pop()
            case nodes.BreakStmt(meta=meta):
                for i in range(-1, -1 - len(self.modes), -1):
                    match self.modes[i]:
                        case BodyType.MODULE | BodyType.FUNCTION:
                            break
                        case BodyType.LOOP:
                            return node
                raise StaticError(
                    "'break' used outside of loops", meta
                )
            case nodes.ContinueStmt(meta=meta):
                for i in range(-1, -1 - len(self.modes), -1):
                    match self.modes[i]:
                        case BodyType.MODULE | BodyType.FUNCTION:
                            break
                        case BodyType.LOOP:
                            return node
                raise StaticError(
                    "'continue' used outside of loops", meta
                )
            case nodes.FunctionStmt(body=body):
                self.modes.append(BodyType.FUNCTION)
                node.body = self.visit_body(body)
                self.modes.pop()
            case nodes.ModuleStmt(body=body) | nodes.ClassStmt(body=body):
                self.modes.append(BodyType.MODULE)
                self.visit(body)
                self.modes.pop()
        return node

    def visit_body(self, node: nodes.Body) -> nodes.Body:
        """Visit a body node"""
        statements = node.statements
        # pylint: disable=consider-using-enumerate
        for i in range(len(statements)):
            stmt = statements[i]
            match stmt:
                case nodes.BreakStmt():
                    if self.modes[-1] == BodyType.LOOP:
                        # Equivalent to statements = statements[:i+1]
                        while len(statements) > i + 1:
                            statements.pop()
                        break
                case nodes.ContinueStmt():
                    if self.modes[-1] == BodyType.LOOP:
                        # Equivalent to statements = statements[:i]
                        # So the continue is deleted as well
                        while len(statements) > i:
                            statements.pop()
                        break
                case nodes.ReturnStmt():
                    if self.modes[-1] == BodyType.FUNCTION:
                        # Equivalent to statements = statements[:i+1]
                        while len(statements) > i + 1:
                            statements.pop()
                        break
            statements[i] = self.visit_stmt(stmt)
        return node
