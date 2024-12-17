"""baba-lang function type"""


from dataclasses import dataclass
from typing import Optional, Protocol, TYPE_CHECKING

from lark.tree import Meta

from bl_ast.nodes import FormArgs, Body

from .base import Value, NULL
from .env import Env

if TYPE_CHECKING:
    from .main import ASTInterpreter


@dataclass(frozen=True)
class BLFunction(Value):
    form_args: FormArgs
    body: Body

    def call(self, args, interpreter, meta):
        # Create an environment (call frame)
        parent = interpreter.locals
        env = Env(parent=parent)
        # Populate it with arguments
        form_args = self.form_args.args
        for farg, arg in zip(form_args, args):
            env.new_var(farg, arg)
        # Run the body
        interpreter.locals = env
        interpreter.visit_stmt(self.body)
        # Clean it up
        interpreter.locals = parent
        return NULL
