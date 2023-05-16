import os
import sys
import traceback

from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from JavaParserListener import JavaParserListener

class JavaSummaryListener(JavaParserListener):
    def __init__(self):
        self.indentation = 0
        self.static_fields = []
        self.fields = []
        self.static_methods = []
        self.methods = []
        self.printed_packages = set()

    def enterPackageDeclaration(self, ctx):
        package_name = ctx.qualifiedName().getText()
        if package_name not in self.printed_packages:
            print(f"# Package {package_name}")
            self.printed_packages.add(package_name)

    def enterClassDeclaration(self, ctx):
        print(f"{'  ' * self.indentation}Class {ctx.identifier().getText()}:")
        self.indentation += 1
        self.static_fields = []
        self.fields = []
        self.static_methods = []
        self.methods = []

    def exitClassDeclaration(self, ctx):
        if self.static_fields:
            print(f"{'  ' * self.indentation}Static fields:")
            for field in self.static_fields:
                print(f"{'  ' * self.indentation}  {field}")
        if self.fields:
            print(f"{'  ' * self.indentation}Fields:")
            for field in self.fields:
                print(f"{'  ' * self.indentation}  {field}")
        if self.static_methods:
            print(f"{'  ' * self.indentation}Static methods:")
            for method in self.static_methods:
                print(f"{'  ' * self.indentation}  {method}")
        if self.methods:
            print(f"{'  ' * self.indentation}Methods:")
            for method in self.methods:
                print(f"{'  ' * self.indentation}  {method}")
        self.indentation -= 1

    def enterFieldDeclaration(self, ctx):
        fieldType = ctx.typeType().getText()
        for varDec in ctx.variableDeclarators().variableDeclarator():
            varName = varDec.variableDeclaratorId().getText()
            if varName not in ['logger']:
                if 'static' in ctx.getText():
                    self.static_fields.append(f"{fieldType} {varName}")
                else:
                    self.fields.append(f"{fieldType} {varName}")

    def enterMethodDeclaration(self, ctx):
        if ctx.identifier().getText() not in ['toString', 'equals', 'hashCode']:
            returnType = ctx.typeTypeOrVoid().getText()
            methodName = ctx.identifier().getText()
            if ctx.formalParameters().formalParameterList() is not None:
                params = [child.getText() for child in ctx.formalParameters().formalParameterList().formalParameter()]
            else:
                params = []
            if 'public' in ctx.getText():
                if 'static' in ctx.getText():
                    self.static_methods.append(f"{returnType} {methodName}({', '.join(params)})")
                else:
                    self.methods.append(f"{returnType} {methodName}({', '.join(params)})")

    def enterConstructorDeclaration(self, ctx):
        constructorName = ctx.identifier().getText()
        if ctx.formalParameters().formalParameterList() is not None:
            params = [child.getText() for child in ctx.formalParameters().formalParameterList().formalParameter()]
        else:
            params = []
        self.methods.append(f"{constructorName}({', '.join(params)})")


def main(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.java'):
                try:
                    filepath = os.path.join(root, filename)
                    lexer = JavaLexer(FileStream(filepath))
                    stream = CommonTokenStream(lexer)
                    parser = JavaParser(stream)
                    tree = parser.compilationUnit()

                    walker = ParseTreeWalker()
                    listener = JavaSummaryListener()
                    walker.walk(listener, tree)
                except Exception as e:
                    raise Exception(f"Error processing {filepath}: {e}\n{traceback.format_exc()}")                    raise Exception(f"Error processing {filepath}: {e}\n{traceback.format_exc()}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a directory to scan as the first command line argument.")
        sys.exit(1)

    directory = sys.argv[1]
    main(directory) 
