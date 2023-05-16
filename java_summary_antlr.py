import os
import sys
import traceback

from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from JavaParserListener import JavaParserListener

printed_packages = set()
class JavaSummaryListener(JavaParserListener):
    def __init__(self):
        self.indentation = 0
        self.static_fields = []
        self.fields = []
        self.static_methods = []
        self.methods = []

    def enterPackageDeclaration(self, ctx):
        global printed_packages
        package_name = ctx.qualifiedName().getText()
        if package_name not in printed_packages:
            print(f"# Package {package_name}")
            printed_packages.add(package_name)

    def enterClassDeclaration(self, ctx):
        class_name = ctx.identifier().getText()
        extends_clause = ''
        implements_clause = ''

        if ctx.EXTENDS():
            extends_clause = f' extends {ctx.typeType().getText()}'
        
        if ctx.IMPLEMENTS():
            implements_clause = f' implements {", ".join([type.getText() for type in ctx.typeList().typeType()])}'
            
        print(f"{'  ' * self.indentation}Class {class_name}{extends_clause}{implements_clause}:")
        self.indentation += 1

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
                    lexer = JavaLexer(FileStream(filepath, encoding='utf-8'))
                    stream = CommonTokenStream(lexer)
                    parser = JavaParser(stream)
                    tree = parser.compilationUnit()

                    walker = ParseTreeWalker()
                    listener = JavaSummaryListener()
                    walker.walk(listener, tree)
                except Exception as e:
                    raise Exception(f"Error processing {filepath}: {e}\n{traceback.format_exc()}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a directory to scan as the first command line argument.")
        sys.exit(1)

    directory = sys.argv[1]
    main(directory) 
