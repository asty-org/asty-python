import os.path

from asty.nodes import (
    BasicLitNode,
    CallExprNode,
    FileNode,
    IdentNode,
    SelectorExprNode,
)
from asty.utils import run_with_container
from asty.visitors import NodeVisitor


class TestVisitor(NodeVisitor):
    def visit_CallExprNode(self, node):
        match node:
            case CallExprNode(
                fun=SelectorExprNode(
                    x=IdentNode(name='fmt'),
                    sel=IdentNode(name='Println'),
                ),
                args=[
                    BasicLitNode(
                        kind='STRING',
                        value=value,
                    ),
                    *_,
                ],
            ):
                print(f"Found: {value}!")
        return super().generic_visit(node)


def main():
    root = os.path.dirname(__file__)
    result = run_with_container(
        {root: "/var/data"},
        ["go2json", "-input", "/var/data/test.go"],
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))

    tree = FileNode.parse_raw(result.stdout)

    visitor = TestVisitor()
    visitor.visit(tree)


if __name__ == "__main__":
    main()
