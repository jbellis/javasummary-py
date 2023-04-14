import re
import sys
import javalang

def full_typename(type_node):
    if isinstance(type_node, javalang.tree.ReferenceType):
        type_parts = [type_node.name]
        while type_node.sub_type:
            type_node = type_node.sub_type
            type_parts.append(type_node.name)
        return '.'.join(type_parts)
    return type_node.name

def elide_method_references(java_code):
    pattern = r'(\w+\[\]::\w+)|(\w+::\w+)'
    return re.sub(pattern, '1', java_code)

def process_class(class_node, indent=0):
    # Class signature
    generic_info = ''
    if class_node.type_parameters:
        generic_info = '<' + ', '.join([tp.name for tp in class_node.type_parameters]) + '>'
    result = '  ' * indent + f'Class {class_node.name}{generic_info}:\n'

    # Process fields
    for field in class_node.fields:
        for field_declarator in field.declarators:
            if field_declarator.name in {'logger'}:
                continue
            field_type = full_typename(field.type)
            result += '  ' * indent + f'  {field_type} {field_declarator.name}\n'

    # Process constructors
    for constructor in class_node.constructors:
        if 'public' in constructor.modifiers:
            result += '  ' * indent + f'  public {class_node.name}('
            result += ', '.join([f'{param.type.name} {param.name}' for param in constructor.parameters])
            result += ')\n'

    # Process methods
    for method in class_node.methods:
        if 'public' in method.modifiers:
            rt = method.return_type.name if method.return_type else 'void'
            result += '  ' * indent + f'  public {rt} {method.name}('
            result += ', '.join([f'{param.type.name} {param.name}' for param in method.parameters])
            result += ')\n'

    # Process inner classes
    for nested_class in class_node.body:
        if isinstance(nested_class, javalang.tree.ClassDeclaration):
            result += process_class(nested_class, indent + 1)

    return result

def summarize_java_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Parse Java source code
    tree = javalang.parse.parse(elide_method_references(content))

    # Process classes
    summary = ''
    for class_node in tree.types:
        if isinstance(class_node, javalang.tree.ClassDeclaration):
            summary += process_class(class_node)

    return summary

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python java_summary.py <path_to_java_file>')
        sys.exit(1)

    java_file_path = sys.argv[1]
    summary = summarize_java_file(java_file_path)
    print(summary)
