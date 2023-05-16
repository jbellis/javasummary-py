from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from JavaParserBaseListener import JavaParserBaseListener

class JavaSummaryListener(JavaParserBaseListener):
    def __init__(self):
        self.indentation = 0

    def enterPackageDeclaration(self, ctx):
        print(f"# Package {ctx.qualifiedName().getText()}")

    def enterClassDeclaration(self, ctx):
        print(f"{'  ' * self.indentation}Class {ctx.Identifier().getText()}:")
        self.indentation += 1

    def exitClassDeclaration(self, ctx):
        self.indentation -= 1

    def enterFieldDeclaration(self, ctx):
        fieldType = ctx.typeType().getText()
        for varDec in ctx.variableDeclarators().variableDeclarator():
            varName = varDec.variableDeclaratorId().getText()
            if varName not in ['logger']:
                if 'static' in ctx.getText():
                    print(f"{'  ' * self.indentation}Static fields:\n{'  ' * self.indentation}  {fieldType} {varName}")
                else:
                    print(f"{'  ' * self.indentation}Fields:\n{'  ' * self.indentation}  {fieldType} {varName}")

    def enterMethodDeclaration(self, ctx):
        if ctx.Identifier().getText() not in ['toString', 'equals', 'hashCode']:
            returnType = ctx.typeTypeOrVoid().getText()
            methodName = ctx.Identifier().getText()
            params = [child.getText() for child in ctx.formalParameters().formalParameterList().formalParameter()]
            if 'public' in ctx.getText():
                if 'static' in ctx.getText():
                    print(f"{'  ' * self.indentation}Static methods:\n{'  ' * self.indentation}  {returnType} {methodName}({', '.join(params)})")
                else:
                    print(f"{'  ' * self.indentation}Methods:\n{'  ' * self.indentation}  {returnType} {methodName}({', '.join(params)})")

    def enterConstructorDeclaration(self, ctx):
        constructorName = ctx.Identifier().getText()
        params = [child.getText() for child in ctx.formalParameters().formalParameterList().formalParameter()]
        print(f"{'  ' * self.indentation}Methods:\n{'  ' * self.indentation}  {constructorName}({', '.join(params)})")

def main():
    for filename in os.listdir(os.getcwd()):
        if filename.endswith('.java'):
            lexer = JavaLexer(FileStream(filename))
            stream = CommonTokenStream(lexer)
            parser = JavaParser(stream)
            tree = parser.compilationUnit()

            walker = ParseTreeWalker()
            listener = JavaSummaryListener()
            walker.walk(listener, tree)

if __name__ == '__main__':
    main()
