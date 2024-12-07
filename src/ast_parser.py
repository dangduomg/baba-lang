"""AST parser"""


import ast
from typing import Optional

from lark import Lark, Transformer, ast_utils, v_args
from lark.tree import Meta

import ast_classes


common_opts = {'grammar_filename': 'grammar.lark', 'parser': 'lalr', 'propagate_positions': True}
body_parser = Lark.open(start='body', **common_opts)
expr_parser = Lark.open(start='expr', **common_opts)


class Extras(Transformer):
    """Transformer for transforming syntactic sugars and tokens"""

    #pylint: disable=invalid-name
    #pylint: disable=missing-function-docstring
    #pylint: disable=unused-argument
    #pylint: disable=too-many-arguments

    @v_args(inline=True, meta=True)
    def do_while_stmt(self, meta: Meta, body: ast_classes.Body, cond: ast_classes._Expr
                      ) -> ast_classes.WhileStmt:
        return ast_classes.WhileStmt(meta, cond, body, eval_condition_after=True)

    @v_args(inline=True, meta=True)
    def for_stmt(self,
        meta: Meta,
        initializer: Optional[ast_classes._Expr],
        condition: Optional[ast_classes._Expr],
        updater: Optional[ast_classes._Expr],
        body: ast_classes.Body,
    ) -> ast_classes.Body:
        statements = []
        loop_body_statements: list[ast_classes._Stmt] = [body]
        if initializer is not None:
            statements.append(initializer)
        if updater is not None:
            loop_body_statements.append(updater)
        if condition is None:
            condition = ast_classes.Literal(meta, True)
        loop_body = ast_classes.Body(meta, loop_body_statements)
        loop = ast_classes.WhileStmt(meta, condition, loop_body)
        statements.append(loop)
        return ast_classes.Body(meta, statements)

    def INT(self, lexeme: str) -> int:
        return int(lexeme)

    def FLOAT(self, lexeme: str) -> float:
        return float(lexeme)

    def STRING(self, lexeme: str) -> str:
        return ast.literal_eval(lexeme)

    def TRUE(self, lexeme: str) -> bool:
        return True

    def FALSE(self, lexeme: str) -> bool:
        return False

    def NULL(self, lexeme: str) -> None:
        return None


_to_ast = ast_utils.create_transformer(ast_classes, Extras())


def parse_to_ast(src: str, parser: Lark = body_parser) -> ast_utils.Ast:
    """Parse baba-lang source code to AST"""
    return _to_ast.transform(parser.parse(src))
