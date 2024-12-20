"""AST node and visitor base class"""


from typing import Any
from abc import ABC, abstractmethod

from lark.ast_utils import Ast, WithMeta


#pylint: disable=too-few-public-methods
#pylint: disable=unnecessary-ellipsis


class _AstNode(Ast, WithMeta):
    """AST node base class"""


class ASTVisitor(ABC):
    """AST visitor interface"""

    @abstractmethod
    def visit(self, node: _AstNode) -> Any:
        """Visit a node

Uses pattern matching to determine type of visited node and dispatch based on that"""
        ...
