import argparse
import os
import sys
import traceback
from collections import defaultdict

from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from JavaParserListener import JavaParserListener

printed_packages = set()
class JavaSummaryListener(JavaParserListener):
    def __init__(self, methods_only=False):
        self.indentation = 0
        self.static_fields = []
        self.fields = []
        self.static_methods = []
        self.methods = []
        self.methods_only = methods_only
        self.ignore_class = defaultdict(bool)
        self.file_description = ""  # New variable to store the class description

    def enterPackageDeclaration(self, ctx):
        global printed_packages
        package_name = ctx.qualifiedName().getText()
        if package_name not in printed_packages:
            self.file_description += f"# Package {package_name}\n"  # Append to the string instead of printing
            printed_packages.add(package_name)

    def enterClassDeclaration(self, ctx):
        self.ignore_class[self.indentation] = False
        class_name = ctx.identifier().getText()
        extends_clause = ''
        implements_clause = ''

        if ctx.EXTENDS():
            extended = ctx.typeType().getText()
            if 'Exception' in extended or 'Error' in extended:
                self.ignore_class[self.indentation] = True
                return
            extends_clause = f' extends {extended}'

        if ctx.IMPLEMENTS():
            istring = ', '.join(I.getText() for I in ctx.typeList())
            implements_clause = f' implements {istring}'

        self.file_description += f"{'  ' * self.indentation}Class {class_name}{extends_clause}{implements_clause}:\n"
        self.indentation += 1

    def exitClassDeclaration(self, ctx):
        if not self.ignore_class[self.indentation]:
            if not self.methods_only:
                if self.static_fields:
                    self.file_description += f"{'  ' * self.indentation}Static fields:\n"
                    for field in self.static_fields:
                        self.file_description += f"{'  ' * self.indentation}  {field}\n"
            if self.static_methods:
                self.file_description += f"{'  ' * self.indentation}Static methods:\n"
                for method in self.static_methods:
                    self.file_description += f"{'  ' * self.indentation}  {method}\n"
            if not self.methods_only:
                if self.fields:
                    self.file_description += f"{'  ' * self.indentation}Fields:\n"
                    for field in self.fields:
                        self.file_description += f"{'  ' * self.indentation}  {field}\n"
            if self.methods:
                self.file_description += f"{'  ' * self.indentation}Methods:\n"
                for method in self.methods:
                    self.file_description += f"{'  ' * self.indentation}  {method}\n"
        self.indentation -= 1

    def enterFieldDeclaration(self, ctx):
        if self.ignore_class[self.indentation]:
            return
        fieldType = ctx.typeType().getText()
        for varDec in ctx.variableDeclarators().variableDeclarator():
            varName = varDec.variableDeclaratorId().getText()
            if varName not in ['logger']:
                if 'static' in ctx.getText():
                    self.static_fields.append(f"{fieldType} {varName}")
                else:
                    self.fields.append(f"{fieldType} {varName}")

    def enterMethodDeclaration(self, ctx):
        if self.ignore_class[self.indentation]:
            return
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
        if self.ignore_class[self.indentation]:
            return
        constructorName = ctx.identifier().getText()
        if ctx.formalParameters().formalParameterList() is not None:
            params = [child.getText() for child in ctx.formalParameters().formalParameterList().formalParameter()]
        else:
            params = []
        self.methods.append(f"{constructorName}({', '.join(params)})")


def main(directory, methods_only):
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
                    listener = JavaSummaryListener(methods_only=methods_only)
                    walker.walk(listener, tree)

                    print(listener.file_description)  # Print the class description here
                except Exception as e:
                    raise Exception(f"Error processing {filepath}: {e}\n{traceback.format_exc()}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some java files.')
    parser.add_argument('directory', type=str, help='A directory to scan')
    parser.add_argument('--methods-only', action='store_true', help='Omit fields from the output')

    args = parser.parse_args()

    main(args.directory, args.methods_only)
