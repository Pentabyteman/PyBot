import ast
import inspect

# Toggle module level debugging mode.
DEBUG = False

# List of all AST node classes in ast.py.
all_ast_nodes = \
    [name for (name, obj) in inspect.getmembers(ast)
     if inspect.isclass(obj) and issubclass(obj, ast.AST)]

# List of all builtin functions and types (ignoring exception classes).
all_builtins = \
    [name for (name, obj) in inspect.getmembers(__builtins__)
     if inspect.isbuiltin(obj) or (inspect.isclass(obj) and
                                   not issubclass(obj, Exception))]


def classname(obj):
    return obj.__class__.__name__


def is_valid_ast_node(name):
    return name in all_ast_nodes


def is_valid_builtin(name):
    return name in all_builtins


def get_node_lineno(node):
    return node.lineno if hasattr(node, 'lineno') else 0

# Deny evaluation of code if the AST contain any of the following nodes:
unallowed_ast_nodes = [
    #   'Add', 'And',
    #   'AssAttr', 'AssList', 'AssName', 'AssTuple',
    #   'Assert', 'Assign', 'AugAssign',
    # 'Backquote',
    #   'Bitand', 'Bitor', 'Bitxor', 'Break',
    #   'CallFunc', 'Class', 'Compare', 'Const', 'Continue',
    #   'Decorators', 'Dict', 'Discard', 'Div',
    #   'Ellipsis', 'EmptyNode',
    # 'Import',
    #   'Expression', 'FloorDiv',
    #   'For',
    # 'ImportFrom',
    #   'Function',
    #   'GenExpr', 'GenExprFor', 'GenExprIf', 'GenExprInner',
    #   'Getattr', 'Global', 'If',
    #   'Invert',
    #   'Keyword', 'Lambda', 'LeftShift',
    #   'List', 'ListComp', 'ListCompFor', 'ListCompIf', 'Mod',
    #   'Module',
    #   'Mul', 'Name', 'Node', 'Not', 'Or', 'Pass', 'Power',
    #   'Print', 'Printnl',
    # 'Raise',
    #    'Return', 'RightShift', 'Slice', 'Sliceobj',
    #   'Stmt', 'Sub', 'Subscript',
    #   'Tuple', 'UnaryAdd', 'UnarySub',
    #   'While','Yield'
]

# Deny evaluation of code if it tries to access any of the following builtins:
unallowed_builtins = [
    '__import__',
    #   'abs', 'apply', 'basestring', 'bool', 'buffer',
    #   'callable', 'chr', 'classmethod', 'cmp', 'coerce',
    'compile',
    #   'complex',
    'delattr',
    #   'dict',
    'dir',
    #   'divmod', 'enumerate',
    'eval', 'exec',
    #   'filter', 'float', 'frozenset',
    'getattr', 'globals', 'hasattr',
    #    'hash', 'hex', 'id',
    'input',
    #   'int', 'intern', 'isinstance', 'issubclass', 'iter',
    #   'len', 'list',
    'locals',
    #   'long', 'map', 'max', 'min', 'object', 'oct',
    'open',
    #   'ord', 'pow', 'property', 'range',
    #   'reduce',
    #   'repr', 'reversed', 'round', 'set',
    'setattr',
    #   'slice', 'sorted', 'staticmethod',  'str', 'sum', 'super',
    #   'tuple', 'type', 'unichr', 'unicode',
    'vars',
    #    'xrange', 'zip',
]

allowed_imports = [
    'itertools',
    'numpy',
    'scipy',
    'theano',
    'collections',
    'heapq'
]

for ast_name in unallowed_ast_nodes:
    assert(is_valid_ast_node(ast_name))

# for name in unallowed_builtins:
    # assert(is_valid_builtin(name))


def is_unallowed_ast_node(kind):
    return kind in unallowed_ast_nodes


def is_unallowed_builtin(name):
    return name in unallowed_builtins

# In addition to these we deny access to all lowlevel attrs (__xxx__).
unallowed_attr = [
    'im_class', 'im_func', 'im_self',
    'func_code', 'func_defaults', 'func_globals', 'func_name',
    'tb_frame', 'tb_next',
    'f_back', 'f_builtins', 'f_code', 'f_exc_traceback',
    'f_exc_type', 'f_exc_value', 'f_globals', 'f_locals']


def is_unallowed_attr(name):
    return (name[:2] == '__' and name[-2:] == '__') or \
           (name in unallowed_attr)


class SafeEvalError(Exception):
    """
    Base class for all which occur while walking the AST.

    Attributes:
      errmsg = short decription about the nature of the error
      lineno = line offset to where error occured in source code
    """

    def __init__(self, errmsg, lineno):
        self.errmsg, self.lineno = errmsg, lineno

    def __str__(self):
        return "line {} : {}".format(self.lineno, self.errmsg)


class UnallowedNode(SafeEvalError):
    "Expression/statement in AST evaluates to a restricted AST node type."
    pass


class UnallowedImport(SafeEvalError):
    "Unallowed import"
    pass


class UnallowedBuiltin(SafeEvalError):
    "Expression/statement in tried to access a restricted builtin."
    pass


class UnallowedAttr(SafeEvalError):
    "Expression/statement in tried to access a restricted attribute."
    pass


class Visitor(ast.NodeVisitor):

    def __init__(self):
        super(Visitor, self).__init__()
        for node_name in unallowed_ast_nodes:
            if getattr(self, 'visit_' + node_name, None):
                continue
            setattr(self, 'visit_' + node_name, self.fail)

    def generic_visit(self, node):
        super(Visitor, self).generic_visit(node)

    def fail(self, node, *args):
        node_name = type(node).__name__
        print(node_name, "failed")
        lineno = get_node_lineno(node)
        raise UnallowedNode("Unallowed node {}".format(node_name), lineno)

    def visit_Name(self, node, *args):
        "Disallow any attempts to access a restricted builtin/attr."
        lineno = get_node_lineno(node)
        if is_unallowed_builtin(node.id):
            raise UnallowedBuiltin("Unallowed builtin {}".format(node.id),
                                   lineno)
        elif is_unallowed_attr(node.id):
            raise UnallowedAttr("Unallowed attr {}".format(node.id), lineno)

    def visit_Attribute(self, node, *args):
        "Disallow any attempts to access a restricted attribute."
        name = node.attr
        lineno = get_node_lineno(node)
        if is_unallowed_attr(name):
            raise UnallowedAttr("Unallowed attr {}".format(name), lineno)

    def visit_Import(self, node, *args):
        lineno = get_node_lineno(node)
        for alias in node.names:
            if alias.name not in allowed_imports:
                raise UnallowedImport("Unallowed Import {}".format(alias.name),
                                      lineno)

    def visit_ImportFrom(self, node, *args):
        lineno = get_node_lineno(node)
        print("import from", node.module)
        if node.module not in allowed_imports:
            raise UnallowedImport("Unallowed Import {}".format(node.module),
                                  lineno)


def verify(path):
    with open(path, 'r') as f:
        tree = ast.parse(f.read())
        checker = Visitor()
        try:
            checker.visit(tree)
            return True
        except Exception as e:
            print("Error", e)
            return False

if __name__ == '__main__':
    with open('verify_test.py', 'r') as f:
        tree = ast.parse(f.read())
        checker = Visitor()
        checker.visit(tree)
