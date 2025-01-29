"""AST interpreter"""


from pathlib import Path
from dataclasses import dataclass

from lark import Token
from lark.tree import Meta
from lark.exceptions import UnexpectedInput

from bl_ast import nodes, parse_to_ast
from bl_ast.base import ASTVisitor

from static_checker import StaticChecker, StaticError

from . import built_ins, bl_types
from .bl_types import (
    pywrapper, Result, ExpressionResult, Success, BLError, Value,
    PythonFunction, Call, NotImplementedException, exits, Env, Return,
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
        self.globals.new_var("Object", bl_types.ObjectClass)
        self.globals.new_var("Exception", bl_types.ExceptionClass)

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
                for stmt in statements:
                    if isinstance(res := self.visit(stmt), exits.Exit):
                        return res
                return Success()
            case nodes.IfStmt(meta=meta, condition=condition, body=body):
                cond = self.visit_expr(condition).to_bool(self, meta)
                match cond:
                    case BLError():
                        return cond
                    case bl_types.Bool(True):
                        return self.visit_stmt(body)
                    case bl_types.Bool(False):
                        return Success()
            case nodes.IfElseStmt(
                meta=meta, condition=condition,
                then_body=then_body, else_body=else_body
            ):
                cond = self.visit_expr(condition).to_bool(self, meta)
                match cond:
                    case BLError():
                        return cond
                    case bl_types.Bool(True):
                        return self.visit_stmt(then_body)
                    case bl_types.Bool(False):
                        return self.visit_stmt(else_body)
            case nodes.WhileStmt(
                meta=meta, condition=condition, body=body,
                eval_cond_after_body=eval_cond_after_body,
            ):
                eval_condition = not eval_cond_after_body
                while True:
                    if eval_condition:
                        cond = self.visit_expr(condition).to_bool(self, meta)
                        match cond:
                            case BLError():
                                return cond
                            case bl_types.Bool(False):
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
                iterator = self.visit_expr(iterable).to_iter(self, meta)
                while (el := iterator.next(self, meta)) is not bl_types.NULL:
                    match el:
                        case BLError():
                            return el
                        case bl_types.Item(vars={"value": value}):
                            self.assign(
                                meta, nodes.VarPattern(meta, ident), el
                            )
                            res = self.visit_stmt(body)
                            if isinstance(res, exits.Continue):
                                pass
                            elif isinstance(res, exits.Exit):
                                return res
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
                if not isinstance(res, bl_types.Instance):
                    return BLError(cast_to_instance(
                        NotImplementedException.new(
                            [bl_types.String("You can only throw instances")],
                            self, meta,
                        )
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
                self.globals.new_var(
                    name, bl_types.BLFunction(str(name), form_args, body, env)
                )
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
                self.globals.new_var(name, bl_types.Module(name, vars_))
                return Success()
            case nodes.ClassStmt():
                return self.visit_class(node)
            case nodes.IncludeStmt():
                return self.visit_include(node)
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [bl_types.String("Statement type not supported")], self,
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
            superclass_res = bl_types.ObjectClass
        else:
            superclass_res = self._get_var(super_, meta)
            match superclass_res:
                case bl_types.Class():
                    pass
                case BLError():
                    return superclass_res
                case _:
                    return BLError(cast_to_instance(
                        bl_types.IncorrectTypeException.new([], self, meta)
                    ), meta, self.path)
        self.globals.new_var(
            name, bl_types.Class(bl_types.String(name), superclass_res, vars_)
        )
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
                InvalidIncludeException.new([bl_types.String(
                    f"Source file '{node.path}' not found"
                )], self, node.meta)
            ), node.meta, self.path)
        try:
            with new_path.open(encoding="utf-8") as f:
                src = f.read()
        except FileNotFoundError:
            return BLError(cast_to_instance(
                InvalidIncludeException.new([bl_types.String(
                    f"Source file '{new_path}' can't be accessed"
                )], self, node.meta)
            ), node.meta, self.path)
        self.path = str(new_path)
        self.traceback.append(Script(str(new_path), node.meta))
        try:
            res = self.run_src(src)
        except (UnexpectedInput, StaticError):
            return BLError(cast_to_instance(
                InvalidIncludeException.new([bl_types.String(
                    f"Source file {new_path} has a compile-time error. " +
                    "Check it."
                )], self, node.meta)
            ), node.meta, self.path)
        match res:
            case BLError():
                return res
        self.traceback.pop()
        self.path = str(old_path)
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

    def visit_expr(self, node: nodes._Expr) -> ExpressionResult:
        """Visit an expression node"""
        match node:
            case nodes.Exprs(expressions=expressions):
                final_res = bl_types.NULL
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
            case nodes.LogicalOp(left=left, op=op, right=right):
                not_left_res = (
                    self.visit_expr(left).logical_not(self, left.meta)
                )
                if isinstance(not_left_res, BLError):
                    return not_left_res
                if isinstance(not_left_res, bl_types.Bool):
                    left_value = not not_left_res.value
                    if (
                        op == "&&" and left_value
                        or op == "||" and not left_value
                    ):
                        return not_left_res.logical_not(self, left.meta)
                    return self.visit_expr(right)
            case nodes.BinaryOp(meta=meta, left=left, op=op, right=right):
                return self.visit_expr(left).binary_op(
                    op, self.visit_expr(right), self, meta
                )
            case nodes.Subscript(
                meta=meta, subscriptee=subscriptee, index=index
            ):
                return self.visit_expr(subscriptee).get_item(
                    self.visit_expr(index), self, meta
                )
            case nodes.Call(meta=meta, callee=callee, args=args_in_ast):
                # Visit all args, stop if one is an error
                args = []
                for arg in args_in_ast.args:
                    arg_visited = self.visit_expr(arg)
                    if not isinstance(arg_visited, Value):
                        return arg_visited
                    args.append(arg_visited)
                callee = self.visit_expr(callee)
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
                    case bl_types.Class():
                        return class_.new(args, self, meta)
                    case BLError():
                        return class_
            case nodes.Prefix(meta=meta, op=op, operand=operand):
                return self.visit_expr(operand).unary_op(op, self, meta)
            case nodes.Dot(meta=meta, accessee=accessee, attr_name=attr):
                return self.visit_expr(accessee).get_attr(attr, self, meta)
            case nodes.Var(meta=meta, name=name):
                return self._get_var(name, meta)
            case nodes.String(value=value):
                return bl_types.String(value)
            case nodes.Int(value=value):
                return bl_types.Int(value)
            case nodes.Float(value=value):
                return bl_types.Float(value)
            case nodes.TrueLiteral():
                return bl_types.BOOLS[True]
            case nodes.FalseLiteral():
                return bl_types.BOOLS[False]
            case nodes.NullLiteral():
                return bl_types.NULL
            case nodes.List(elems=elems_in_ast):
                elems = []
                for e in elems_in_ast:
                    e_visited = self.visit_expr(e)
                    if not isinstance(e_visited, Value):
                        return e_visited
                    elems.append(e_visited)
                return bl_types.BLList(elems)
            case nodes.Dict(pairs=pairs):
                content = {}
                for pair in pairs:
                    k_visited = self.visit(pair.key)
                    v_visited = self.visit(pair.value)
                    content[k_visited] = v_visited
                return bl_types.BLDict(content)
            case nodes.FunctionLiteral(form_args=form_args, body=body):
                env = None if self.locals is None else self.locals.copy()
                return bl_types.BLFunction("<anonymous>", form_args, body, env)
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
                index = self.visit_expr(index)
                return subscriptee.set_item(index, value, self, meta)
            case nodes.DotPattern(
                accessee=accessee_, attr_name=attr
            ):
                accessee = self.visit_expr(accessee_)
                return accessee.set_attr(attr, value, self, meta)
        return BLError(cast_to_instance(
            NotImplementedException.new([], self, meta)
        ), meta, self.path)

    def inplace(
        self, meta: Meta, pattern: nodes._Pattern, op: Token, right: Value
    ) -> ExpressionResult:
        """Visit an in-place assignment node"""
        # to solve the unbound problem
        accessee = bl_types.ObjectClass.new([], self, meta)
        if isinstance(pattern, nodes.VarPattern):
            old_value_get_result = self._get_var(pattern.name, meta)
        elif isinstance(pattern, nodes.DotPattern):
            accessee = self.visit_expr(pattern.accessee)
            old_value_get_result = accessee.get_attr(
                pattern.attr_name, self, meta
            )
        elif isinstance(pattern, nodes.SubscriptPattern):
            accessee = self.visit_expr(pattern.subscriptee)
            old_value_get_result = accessee.get_item(
                self.visit_expr(pattern.index), self, meta
            )
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
                    if value.class_ == bl_types.VarNotFoundException:
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
InvalidIncludeException = bl_types.Class(
    bl_types.String("InvalidIncludeException"), bl_types.ExceptionClass
)
IncludeSyntaxErrException = bl_types.Class(
    bl_types.String("IncludeSyntaxErrException"), bl_types.ExceptionClass
)
IncludeRuntimeErrException = bl_types.Class(
    bl_types.String("IncludeRuntimeErrException"), bl_types.ExceptionClass
)
