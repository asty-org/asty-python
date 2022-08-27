import os.path
from asty.nodes import (
    BasicLitNode,
    FileNode,
    IdentNode,
    MatchRuleNode,
)
from asty.utils import run_with_container
from asty.visitors import Matcher


def main():
    root = os.path.dirname(__file__)
    with open(os.path.join(root, 'pattern.json'), 'r') as stream:
        data = stream.read()

    pattern = MatchRuleNode.parse_raw(data)

    result = run_with_container(
        ["go2json", "-positions", "-input", "/var/data/test.go"],
        volumes={root: "/var/data"},
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))

    tree = FileNode.parse_raw(result.stdout)

    matcher = Matcher(pattern)
    match = matcher.match(tree)

    for result in match:
        for calls in result['call']:
            for fun in calls['fun']:
                assert isinstance(fun.node, IdentNode)
                pos = fun.node.name_pos
                print(fun.node.name, f'{pos.filename}:{pos.line}:{pos.column}')
            for args in calls['args']:
                for const in args['constant']:
                    assert isinstance(const.node, BasicLitNode)
                    pos = const.node.value_pos
                    print('\t', const.node.value, f'{pos.filename}:{pos.line}:{pos.column}')


if __name__ == "__main__":
    main()
