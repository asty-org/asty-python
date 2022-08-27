import os.path

from asty.nodes import (
    CallExprNode,
    FileNode,
    IdentNode,
    SelectorExprNode,
)
from asty.utils import run_with_container
from asty.visitors import NodeTransformer


class SampleTransformer(NodeTransformer):
    def visit_CallExprNode(self, node):
        match node:
            case CallExprNode(
                fun=IdentNode(name='print'),
                args=args,
            ):
                return CallExprNode.construct(
                    fun=SelectorExprNode.construct(
                        x=IdentNode.construct(name='log'),
                        sel=IdentNode.construct(name='Print'),
                    ),
                    args=args,
                )
        return super().generic_visit(node)


def main():
    root = os.path.dirname(__file__)
    result = run_with_container(
        ["go2json", "-input", "/var/data/sample.go"],
        volumes={root: "/var/data"},
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))

    tree = FileNode.parse_raw(result.stdout)

    transformer = SampleTransformer()
    tree = transformer.visit(tree)

    data = tree.json(
        exclude_unset=True,
        by_alias=True,
    )
    result = run_with_container(
        ["json2go"],
        input=data.encode("utf-8"),
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))

    print(result.stdout.decode("utf-8"))


if __name__ == "__main__":
    main()
