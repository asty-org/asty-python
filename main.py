from devtools import pprint

from asty.nodes import (
    BasicLitNode,
    CallExprNode,
    FileNode,
    IdentNode,
    MatchRuleNode,
    SelectorExprNode,
)
from asty.visitors import (
    Matcher,
    NodeTransformer,
)


class TestNodeTransformer(NodeTransformer):
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


pattern = MatchRuleNode.construct(
    name='call',
    rules=[
        CallExprNode.construct(
            fun=IdentNode.construct(name='print'),
            args=[
                MatchRuleNode.construct(
                    name='constant',
                    rules=[
                        BasicLitNode.construct(
                            kind='STRING',
                        ),
                    ]
                )
            ],
        ),
    ],
)


if __name__ == '__main__':
    filename = "/Users/evgenus/tfc/asty/output.json"
    tree = FileNode.parse_file(filename)

    # transformer = TestNodeTransformer()
    # tree = transformer.visit(tree)

    # from devtools import pprint
    # pprint(tree)

    matcher = Matcher(pattern)
    matcher.match(tree)
    pprint(matcher)

    # output = "/Users/evgenus/tfc/asty/output-processed.json"
    # data = tree.json(
    #     exclude_unset=True,
    #     by_alias=True,
    #     indent=2,
    # )
    # with open(output, 'w') as stream:
    #     stream.write(data)
