import sys
from ast import literal_eval

from lark import Lark, ast_utils, Transformer, v_args

import ast_classes


parser = Lark.open('grammar.lark', parser='lalr', start=['body', 'expr'])


@v_args(inline=True)
class ToAst(Transformer):
    def include_stmt(self, file):
        with open(file, encoding='utf-8') as f:
            return ast_compile(f.read())
    
    def IDENT(self, v):
        return str(v)
    
    def INT(self, v):
        return literal_eval(v)
    
    def FLOAT(self, v):
        return literal_eval(v)
    
    def STRING(self, v):
        return literal_eval(v)
    
    def true(self):
        return ast_classes.Bool(True)
    
    def false(self):
        return ast_classes.Bool(False)
    
    def null(self):
        return ast_classes.Null()
    
    # desugaring
    
    def do_while_stmt(self, body, cond):
        return ast_classes.Body([
            body,
            ast_classes.WhileStmt(
                cond,
                body,
            ),
        ])
    
    def for_stmt(self, start, cond, step, body):
        return ast_classes.Body([
            start,
            ast_classes.WhileStmt(
                cond,
                ast_classes.Body([
                    body,
                    step,
                ])
            ),
        ])


transformer = ast_utils.create_transformer(ast_classes, ToAst())


def ast_compile(src):
    pt = parser.parse(src, start='body')
    return transformer.transform(pt)

def ast_compile_expr(src):
    pt = parser.parse(src, start='expr')
    return transformer.transform(pt)


def main(args):
    if len(args) > 1:
        file = args[1]
        with open(file, encoding='utf-8') as f:
            string = f.read()
    else:
        print('Enter code to convert into AST (EOF when done):')
        string = sys.stdin.read()
    print()
    print('Result:')
    print(ast_compile(string))

if __name__ == '__main__':
    main(sys.argv)
