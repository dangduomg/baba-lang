import sys
from ast import literal_eval

from lark import Lark, ast_utils, Transformer, v_args

import ast_classes


parser = Lark.open('grammar.lark', parser='lalr')


@v_args(inline=True)
class ToAst(Transformer):
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


transformer = ast_utils.create_transformer(ast_classes, ToAst())


def ast_compile(src):
    pt = parser.parse(src)
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
