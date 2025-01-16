"""AST parser"""

import ast
from pathlib import Path

from lark import Lark, ast_utils, v_args, Token
from lark.visitors import Transformer, Discard, _DiscardType
from lark.tree import Meta

from . import nodes


grammar_path = Path(__file__).parent.parent / "grammar.lark"
common_opts = {
    "grammar_filename": grammar_path,
    "parser": "earley",
    "propagate_positions": True,
}
body_parser = Lark.open(start="body", **common_opts)
expr_parser = Lark.open(start="expr", **common_opts)


class Extras(Transformer):
    """Transformer for transforming syntactic sugars and tokens"""

    # pylint: disable=invalid-name
    # pylint: disable=missing-function-docstring
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments

    @v_args(inline=True, meta=True)
    def do_while_stmt(
        self, meta: Meta, body: nodes.Body, cond: nodes._Expr
    ) -> nodes.WhileStmt:
        return nodes.WhileStmt(meta, cond, body, eval_cond_after_body=True)

    @v_args(inline=True, meta=True)
    def for_stmt(
        self, meta: Meta,
        initializer: nodes._Expr | None,
        condition: nodes._Expr | None,
        updater: nodes._Expr | None,
        body: nodes.Body,
    ) -> nodes.Body:
        """C-style for statement desugar

        Rough expansion result:

        for (<initializer>; <condition>; <updater>) { ... }

        ==>

        <initializer>
        while <condition> {
            ...
            <updater>
        }
        """
        statements = []
        loop_body_statements: list[nodes._Stmt] = [body]
        if initializer is not None:
            statements.append(initializer)
        if updater is not None:
            loop_body_statements.append(updater)
        if condition is None:
            condition = nodes.TrueLiteral(meta)
        loop_body = nodes.Body(meta, loop_body_statements)
        loop = nodes.WhileStmt(meta, condition, loop_body)
        statements.append(loop)
        return nodes.Body(meta, statements)

    @v_args(inline=True, meta=True)
    def module_var_stmt(
        self, meta: Meta, name: Token, value: nodes._Expr
    ) -> nodes.Assign:
        return nodes.Assign(meta, nodes.VarPattern(meta, name), value)

    def nop_stmt(self, children: list) -> _DiscardType:
        return Discard

    @v_args(inline=True, meta=True)
    def short_fn_literal(
        self, meta: Meta, form_args: nodes.FormArgs, expr: nodes._Expr
    ) -> nodes.FunctionLiteral:
        body = nodes.Body(meta, [nodes.ReturnStmt(meta, expr)])
        return nodes.FunctionLiteral(meta, form_args, body)

    def INT(self, lexeme: str) -> int:
        return int(lexeme)

    def FLOAT(self, lexeme: str) -> float:
        return float(lexeme)

    def STRING(self, lexeme: str) -> str:
        return ast.literal_eval(lexeme)


_to_ast = ast_utils.create_transformer(nodes, Extras())


def parse_to_ast(src: str, parser: Lark = body_parser) -> nodes._AstNode:
    """Parse baba-lang source code to AST"""
    return _to_ast.transform(parser.parse(src))


def parse_expr_to_ast(src: str) -> nodes._Expr:
    """Parse baba-lang expression to AST"""
    return _to_ast.transform(expr_parser.parse(src))
