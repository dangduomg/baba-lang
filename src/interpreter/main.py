"""AST interpreter"""


from pathlib import Path
from dataclasses import dataclass
from typing import cast

from lark import Token
from lark.tree import Meta
from lark.exceptions import UnexpectedInput

from bl_ast import nodes, parse_to_ast
from bl_ast.base import ASTVisitor

from static_checker import StaticChecker, StaticError

from . import built_ins
from .bl_types import pywrapper, exits, essentials, iterator, colls, numbers
from .bl_types.essentials import (
    Result, ExpressionResult, Success, BLError, Value,
    PythonFunction, Call, NotImplementedException, Env, Return,
    cast_to_instance,
)


@dataclass(frozen=True)
class Script:
    """baba-lang script instance"""
    path: str | None
    meta: Meta | None


class ASTInterpreter(ASTVisitor):
    """AST interpreter"""

    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements

    globals: Env
    locals: Env | None = None

    traceback: list[Call | Script]
    path: str | None

    def __init__(self, path=None):
        self.traceback = [Script(path, None)]
        self.path = path

        self.globals = Env(self)
        # Populate some builtins
        self.globals.new_var("print", PythonFunction(built_ins.print_))
        self.globals.new_var("printf", PythonFunction(built_ins.printf))
        self.globals.new_var("input", PythonFunction(built_ins.input_))
        self.globals.new_var("to_int", PythonFunction(built_ins.to_int))
        self.globals.new_var("to_float", PythonFunction(built_ins.to_float))
        self.globals.new_var("dump", PythonFunction(built_ins.dump))
        self.globals.new_var("to_string", PythonFunction(built_ins.to_string))
        self.globals.new_var("to_bool", PythonFunction(built_ins.to_bool))
        self.globals.new_var("exit", PythonFunction(built_ins.exit_))
        self.globals.new_var("py_function", PythonFunction(
            pywrapper.py_function
        ))
        self.globals.new_var("py_method", PythonFunction(
            pywrapper.py_method
        ))
        self.globals.new_var("py_constant", PythonFunction(
            pywrapper.py_constant
        ))
        self.globals.new_var("Object", essentials.ObjectClass)
        self.globals.new_var("Item", iterator.ItemClass)
        self.globals.new_var("Exception", essentials.ExceptionClass)
        self.globals.new_var(
            "NotImplementedException", essentials.NotImplementedException
        )
        self.globals.new_var(
            "AttrNotFoundException", essentials.AttrNotFoundException
        )
        self.globals.new_var(
            "VarNotFoundException", essentials.VarNotFoundException
        )
        self.globals.new_var(
            "IncorrectTypeException", essentials.IncorrectTypeException
        )
        self.globals.new_var(
            "OutOfRangeException", colls.OutOfRangeException
        )
        self.globals.new_var(
            "KeyNotFoundException", colls.KeyNotFoundException
        )
        self.globals.new_var(
            "ModuleVarNotFoundException", colls.ModuleVarNotFoundException
        )

    def run_src(self, src: str) -> Result:
        """Run baba-lang source code as a string"""
        ast_ = parse_to_ast(src)
        ast_ = StaticChecker().visit(ast_)
        return self.visit(ast_)

    def visit(self, node: nodes._AstNode) -> Result:
        # pylint: disable=protected-access
        match node:
            case nodes._Expr():
                return self.visit_expr(node)
            case nodes._Stmt():
                return self.visit_stmt(node)
        return BLError(cast_to_instance(
            NotImplementedException.new([], self, node.meta)
        ), node.meta, self.path)

    def visit_stmt(self, node: nodes._Stmt) -> Result:
        """Visit a statement node"""
        match node:
            case nodes.NopStmt():
                return Success()
            case nodes.Body(statements=statements):
                res = Success()
                for stmt in statements:
                    res = self.visit(stmt)
                    if isinstance(res, exits.Exit):
                        return res
                return res
            case nodes.IfStmt(meta=meta, condition=condition, body=body):
                cond = self.visit_expr(condition)
                if isinstance(cond, BLError):
                    return cond
                cond = cond.to_bool(self, meta)
                match cond:
                    case BLError():
                        return cond
                    case essentials.Bool(True):
                        return self.visit_stmt(body)
                    case essentials.Bool(False):
                        return Success()
            case nodes.IfElseStmt(
                meta=meta, condition=condition,
                then_body=then_body, else_body=else_body
            ):
                cond = self.visit_expr(condition)
                if isinstance(cond, BLError):
                    return cond
                cond = cond.to_bool(self, meta)
                match cond:
                    case BLError():
                        return cond
                    case essentials.Bool(True):
                        return self.visit_stmt(then_body)
                    case essentials.Bool(False):
                        return self.visit_stmt(else_body)
            case nodes.WhileStmt(
                meta=meta, condition=condition, body=body,
                eval_cond_after_body=eval_cond_after_body,
            ):
                eval_condition = not eval_cond_after_body
                while True:
                    if eval_condition:
                        cond = self.visit_expr(condition)
                        if isinstance(cond, BLError):
                            return cond
                        cond = cond.to_bool(self, meta)
                        match cond:
                            case BLError():
                                return cond
                            case essentials.Bool(False):
                                return Success()
                    res = self.visit_stmt(body)
                    if isinstance(res, exits.Continue):
                        pass
                    elif isinstance(res, exits.Exit):
                        return res
                    if eval_cond_after_body:
                        eval_condition = True
            case nodes.ForEachStmt(
                meta=meta, ident=ident, iterable=iterable, body=body
            ):
                iterable = self.visit_expr(iterable)
                if isinstance(iterable, BLError):
                    return iterable
                iterator_ = iterable.to_iter(self, meta)
                if isinstance(iterator_, BLError):
                    return iterator_
                while True:
                    match el := iterator_.next(self, meta):
                        case BLError():
                            return el
                        case iterator.Item(vars={"value": value}):
                            self.assign(
                                meta, nodes.VarPattern(meta, ident), value
                            )
                            res = self.visit_stmt(body)
                            if isinstance(res, exits.Continue):
                                pass
                            elif isinstance(res, exits.Exit):
                                return res
                        case essentials.Null():
                            return Success()
            case nodes.BreakStmt():
                return exits.Break()
            case nodes.ContinueStmt():
                return exits.Continue()
            case nodes.ReturnStmt(value=value):
                res = None if value is None else self.visit_expr(value)
                if isinstance(res, BLError):
                    return res
                if isinstance(res, Value):
                    return Return(res)
            case nodes.ThrowStmt(meta=meta, value=value):
                res = self.visit_expr(value)
                if isinstance(res, BLError):
                    return res
                if not isinstance(res, essentials.Instance):
                    return BLError(cast_to_instance(
                        NotImplementedException.new([essentials.String(
                            "You can only throw instances"
                        )], self, meta)
                    ), meta, self.path)
                return BLError(res, meta, self.path)
            case nodes.TryStmt(meta=meta, body=body, catch=catch):
                res = self.visit_stmt(body)
                if not isinstance(res, BLError):
                    return Success()
                match catch:
                    case nodes.CatchClause(ident=ident):
                        if ident is not None:
                            self.assign(
                                meta, nodes.VarPattern(meta, ident), res.value
                            )
                        return self.visit_stmt(catch.body)
            case nodes.FunctionStmt(name=name, form_args=form_args, body=body):
                env = None if self.locals is None else self.locals.copy()
                self.globals.new_var(name, essentials.BLFunction(
                    str(name), form_args, body, env
                ))
                return Success()
            case nodes.ModuleStmt(name=name, entries=entries):
                # Create new environment
                self.globals = Env(self, parent=self.globals)
                # Evaluate the body
                for entry in entries.entries:
                    match res := self.visit(entry):
                        case BLError():
                            return res
                vars_ = {
                    str(name): var.value
                    for name, var in self.globals.vars.items()
                }
                # Clean up
                if self.globals.parent is not None:
                    self.globals = self.globals.parent
                self.globals.new_var(name, colls.Module(name, vars_))
                return Success()
            case nodes.ClassStmt():
                return self.visit_class(node)
            case nodes.IncludeStmt():
                return self.visit_include(node)
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [essentials.String("Statement type not supported")], self,
                node.meta
            )
        ), node.meta, self.path)

    def visit_class(self, node: nodes.ClassStmt) -> Result:
        """Visit a class statement node"""
        meta = node.meta
        name = node.name
        super_ = node.super
        entries = node.entries
        # Create new environment
        self.globals = Env(self, parent=self.globals)
        # Evaluate the body
        for entry in entries.entries:
            match res := self.visit(entry):
                case BLError():
                    return res
        vars_ = {
            str(name): var.value
            for name, var in self.globals.vars.items()
        }
        # Clean up
        if self.globals.parent is not None:
            self.globals = self.globals.parent
        # Create the class
        if super_ is None:
            superclass_res = essentials.ObjectClass
        else:
            superclass_res = self._get_var(super_, meta)
            match superclass_res:
                case essentials.Class():
                    pass
                case BLError():
                    return superclass_res
                case _:
                    return BLError(cast_to_instance(
                        essentials.IncorrectTypeException.new([], self, meta)
                    ), meta, self.path)
        self.globals.new_var(name, essentials.Class(
            essentials.String(name), superclass_res, vars_
        ))
        return Success()

    def visit_include(self, node: nodes.IncludeStmt) -> Result:
        """Visit an include statement node"""
        if self.path is None:
            old_path = None
        else:
            old_path = Path(self.path).resolve()
        new_path = self._find_src(node, old_path)
        if new_path is None:
            return BLError(cast_to_instance(
                InvalidIncludeException.new([essentials.String(
                    f"Source file '{node.path}' not found"
                )], self, node.meta)
            ), node.meta, self.path)
        try:
            with new_path.open(encoding="utf-8") as f:
                src = f.read()
        except FileNotFoundError:
            return BLError(cast_to_instance(
                InvalidIncludeException.new([essentials.String(
                    f"Source file '{new_path}' can't be accessed"
                )], self, node.meta)
            ), node.meta, self.path)
        self.path = str(new_path)
        self.traceback.append(Script(str(new_path), node.meta))
        try:
            res = self.run_src(src)
        except (UnexpectedInput, StaticError):
            return BLError(cast_to_instance(
                InvalidIncludeException.new([essentials.String(
                    f"Source file {new_path} has a compile-time error. " +
                    "Check it."
                )], self, node.meta)
            ), node.meta, self.path)
        match res:
            case BLError():
                return res
        self.traceback.pop()
        self.path = None if old_path is None else str(old_path)
        return res

    def _find_src(
        self, node: nodes.IncludeStmt, old_path: Path | None
    ) -> Path | None:
        if old_path is not None:
            if (new_path := old_path.parent / node.path).is_file():
                return new_path
        project_root = Path(__file__).parent.parent.parent
        if (new_path := project_root / node.path).is_file():
            return new_path
        return None

    def visit_expr(self, node: nodes._Expr) -> ExpressionResult:
        """Visit an expression node"""
        match node:
            case nodes.Exprs(expressions=expressions):
                final_res = essentials.NULL
                for expr in expressions:
                    res = self.visit_expr(expr)
                    if isinstance(res, BLError):
                        return res
                    if isinstance(res, Value):
                        final_res = res
                return final_res
            case nodes.Assign(meta=meta, pattern=pattern, right=right):
                rhs_result = self.visit_expr(right)
                if isinstance(rhs_result, BLError):
                    return rhs_result
                if isinstance(rhs_result, Value):
                    return self.assign(meta, pattern, rhs_result)
            case nodes.Inplace(meta=meta, pattern=pattern, op=op, right=right):
                rhs_result = self.visit_expr(right)
                if isinstance(rhs_result, BLError):
                    return rhs_result
                if isinstance(rhs_result, Value):
                    return self.inplace(meta, pattern, op, rhs_result)
            case nodes.LogicalOp(left=left_node, op=op, right=right):
                left = self.visit_expr(left_node)
                if isinstance(left, BLError):
                    return left
                left_bool = left.to_bool(self, left_node.meta)
                if isinstance(left_bool, BLError):
                    return left_bool
                if (
                    op == "&&" and not left_bool.value
                    or op == "||" and left_bool.value
                ):
                    return left
                return self.visit_expr(right)
            case nodes.BinaryOp(meta=meta, left=left, op=op, right=right):
                left = self.visit_expr(left)
                if isinstance(left, BLError):
                    return left
                right = self.visit_expr(right)
                if isinstance(right, BLError):
                    return right
                return left.binary_op(op, right, self, meta)
            case nodes.Subscript(
                meta=meta, subscriptee=subscriptee, index=index
            ):
                subscriptee = self.visit_expr(subscriptee)
                if isinstance(subscriptee, BLError):
                    return subscriptee
                index = self.visit_expr(index)
                if isinstance(index, BLError):
                    return index
                return subscriptee.get_item(index, self, meta)
            case nodes.Call(meta=meta, callee=callee, args=args_in_ast):
                # Visit all args, stop if one is an error
                args = []
                for arg in args_in_ast.args:
                    arg_visited = self.visit_expr(arg)
                    if not isinstance(arg_visited, Value):
                        return arg_visited
                    args.append(arg_visited)
                callee = self.visit_expr(callee)
                if isinstance(callee, BLError):
                    return callee
                return callee.call(args, self, meta)
            case nodes.New(meta=meta, class_name=name, args=args_):
                # Visit all args, stop if one is an error
                args = []
                if args_ is not None:
                    for arg in args_.args:
                        arg_visited = self.visit_expr(arg)
                        if not isinstance(arg_visited, Value):
                            return arg_visited
                        args.append(arg_visited)
                match class_ := self._get_var(name, meta):
                    case essentials.Class():
                        return class_.new(args, self, meta)
                    case BLError():
                        return class_
            case nodes.Prefix(meta=meta, op=op, operand=operand):
                operand = self.visit_expr(operand)
                if isinstance(operand, BLError):
                    return operand
                return operand.unary_op(op, self, meta)
            case nodes.Dot(meta=meta, accessee=accessee, attr_name=attr):
                accessee = self.visit_expr(accessee)
                if isinstance(accessee, BLError):
                    return accessee
                return accessee.get_attr(attr, self, meta)
            case nodes.Var(meta=meta, name=name):
                return self._get_var(name, meta)
            case nodes.String(value=value):
                return essentials.String(value)
            case nodes.Int(value=value):
                return numbers.Int(value)
            case nodes.Float(value=value):
                return numbers.Float(value)
            case nodes.TrueLiteral():
                return essentials.TRUE
            case nodes.FalseLiteral():
                return essentials.FALSE
            case nodes.NullLiteral():
                return essentials.NULL
            case nodes.List(elems=elems_in_ast):
                elems = []
                for e in elems_in_ast:
                    e_visited = self.visit_expr(e)
                    if not isinstance(e_visited, Value):
                        return e_visited
                    elems.append(e_visited)
                return colls.BLList(elems)
            case nodes.Dict(pairs=pairs):
                content = {}
                for pair in pairs:
                    k_visited = self.visit(pair.key)
                    v_visited = self.visit(pair.value)
                    content[k_visited] = v_visited
                return colls.BLDict(content)
            case nodes.FunctionLiteral(form_args=form_args, body=body):
                env = None if self.locals is None else self.locals.copy()
                return essentials.BLFunction(
                    "<anonymous>", form_args, body, env
                )
        return BLError(cast_to_instance(
            NotImplementedException.new([], self, node.meta)
        ), node.meta, self.path)

    def assign(
        self, meta: Meta, pattern: nodes._Pattern, value: Value
    ) -> ExpressionResult:
        """Visit an assignment node"""
        match pattern:
            case nodes.VarPattern(name=name):
                self._new_var(name, value)
                return value
            case nodes.SubscriptPattern(
                subscriptee=subscriptee, index=index
            ):
                subscriptee = self.visit_expr(subscriptee)
                if isinstance(subscriptee, BLError):
                    return subscriptee
                index = self.visit_expr(index)
                if isinstance(index, BLError):
                    return index
                return subscriptee.set_item(index, value, self, meta)
            case nodes.DotPattern(
                accessee=accessee, attr_name=attr
            ):
                accessee = self.visit_expr(accessee)
                if isinstance(accessee, BLError):
                    return accessee
                return accessee.set_attr(attr, value, self, meta)
        return BLError(cast_to_instance(
            NotImplementedException.new([], self, meta)
        ), meta, self.path)

    def inplace(
        self, meta: Meta, pattern: nodes._Pattern, op: Token, right: Value
    ) -> ExpressionResult:
        """Visit an in-place assignment node"""
        # to solve the unbound problem
        accessee = cast(Value, essentials.ObjectClass.new([], self, meta))
        if isinstance(pattern, nodes.VarPattern):
            old_value_get_result = self._get_var(pattern.name, meta)
        elif isinstance(pattern, nodes.DotPattern):
            accessee = self.visit_expr(pattern.accessee)
            if isinstance(accessee, BLError):
                return accessee
            old_value_get_result = accessee.get_attr(
                pattern.attr_name, self, meta
            )
        elif isinstance(pattern, nodes.SubscriptPattern):
            accessee = self.visit_expr(pattern.subscriptee)
            if isinstance(accessee, BLError):
                return accessee
            index = self.visit_expr(pattern.index)
            if isinstance(index, BLError):
                return index
            old_value_get_result = accessee.get_item(index, self, meta)
        else:
            return BLError(cast_to_instance(
                NotImplementedException.new([], self, meta)
            ), meta, self.path)
        if isinstance(old_value_get_result, BLError):
            return old_value_get_result
        new_result = old_value_get_result.binary_op(
            op[:-1], right, self, meta
        )
        match new_result:
            case BLError():
                return new_result
            case Value():
                pass
            case _:
                return BLError(cast_to_instance(
                    NotImplementedException.new([], self, meta)
                ), meta, self.path)
        if isinstance(pattern, nodes.VarPattern):
            self._set_var(pattern.name, new_result, meta)
        if isinstance(pattern, nodes.DotPattern):
            accessee.set_attr(pattern.attr_name, new_result, self, meta)
        return new_result

    def _get_var(self, name: str, meta: Meta) -> ExpressionResult:
        """Get a variable either from locals or globals"""
        if self.locals is not None:
            res = self.locals.get_var(name, meta)
            if isinstance(res, Value):
                return res
        return self.globals.get_var(name, meta)

    def _set_var(self, name: str, value: Value, meta: Meta) -> BLError | None:
        """Set a variable either in locals or globals"""
        if self.locals is not None:
            res = self.locals.set_var(name, value, meta)
            match res:
                case BLError(value=value):
                    if value.class_ == essentials.VarNotFoundException:
                        return self.globals.set_var(name, value, meta)
                    return res
        return self.globals.set_var(name, value, meta)

    def _new_var(self, name: str, value: Value) -> None:
        """Assign a new variable either in locals or globals"""
        if self.locals is not None:
            self.locals.new_var(name, value)
            return
        self.globals.new_var(name, value)


# Interpreter errors
InvalidIncludeException = essentials.Class(
    essentials.String("InvalidIncludeException"), essentials.ExceptionClass
)
IncludeSyntaxErrException = essentials.Class(
    essentials.String("IncludeSyntaxErrException"), essentials.ExceptionClass
)
IncludeRuntimeErrException = essentials.Class(
    essentials.String("IncludeRuntimeErrException"), essentials.ExceptionClass
)
