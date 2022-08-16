from asty.nodes import (
    CallExprNode,
    FileNode,
    IdentNode,
    SelectorExprNode,
)
from asty.visitors import (
    NodeTransformer,
)


class TestNodeTransformer(NodeTransformer):
    def visit_CallExprNode(self, node):
        match node:
            case CallExprNode(
                fun=IdentNode(name='print'),
                args=args,
            ):
                return CallExprNode.from_values(
                    fun=SelectorExprNode.from_values(
                        x=IdentNode.from_values(name='log'),
                        sel=IdentNode.from_values(name='Print'),
                    ),
                    args=args,
                )
        return super().generic_visit(node)


if __name__ == '__main__':
    filename = "/Users/evgenus/tfc/asty/output.json"
    tree = FileNode.parse_file(filename)

    transformer = TestNodeTransformer()
    tree = transformer.visit(tree)

    output = "/Users/evgenus/tfc/asty/output-processed.json"
    data = tree.json(
        exclude_unset=True,
        by_alias=True,
        indent=2,
    )
    with open(output, 'w') as stream:
        stream.write(data)
