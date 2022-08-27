from collections import (
    deque,
)
from typing import (
    Iterable,
    Optional,
    Sequence,
)

from asty.nodes import (
    BaseNode,
    MatchRuleNode,
    Node,
)


def iter_fields(node: BaseNode):
    if node is not None:
        yield from node.iterate_children()


def iter_child_nodes(node):
    for name, field in iter_fields(node):
        if isinstance(field, Sequence):
            for item in field:
                yield item
        else:
            yield field


def walk(node):
    todo = deque([node])
    while todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


class NodeVisitor:
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    self.visit(item)
            else:
                self.visit(value)


class NodeTransformer(NodeVisitor):
    def generic_visit(self, node):
        for field, old_value in iter_fields(node):
            if isinstance(old_value, Sequence):
                new_values = []
                for value in old_value:
                    value = self.visit(value)
                    if value is None:
                        continue
                    if isinstance(value, Sequence):
                        new_values.extend(value)
                        continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, BaseNode):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node


class MatchingResult:
    def __init__(self, pattern: BaseNode, node: BaseNode, context: str = None):
        self.pattern = pattern
        self.node = node
        self.context = context
        self.matches: list['MatchingResult'] = []

    def __getitem__(self, key: str):
        for match in self.matches:
            if match.context == key:
                yield match

    def attach(self, *sub_match: 'MatchingResult'):
        self.matches.extend(sub_match)
        return self

    def __pretty__(self, fmt, **_kwargs):
        from devtools import sformat

        yield sformat('MatchingResult', sformat.bold) + '('
        yield 1
        yield 'context='
        yield sformat(repr(self.context), sformat.green)
        yield ','
        yield 0
        yield 'pattern='
        yield sformat(repr(self.pattern.node_type), sformat.blue, sformat.italic)
        yield ','
        yield 0
        yield 'node='
        yield sformat(repr(self.node.node_type), sformat.yellow, sformat.italic)
        yield ','
        yield 0
        if self.matches:
            yield 'matchers='
            yield fmt(self.matches)
            yield ','
            yield 0
        yield -1
        yield ')'


Result = Iterable[MatchingResult]


class Matcher:
    def __init__(self, pattern: BaseNode, context: Optional[str] = None):
        self.pattern = pattern
        self.context = context

    def make_matcher(self, pattern: BaseNode, context: str) -> 'Matcher':
        return Matcher(pattern, context)

    def make_result(self, node: BaseNode) -> MatchingResult:
        return MatchingResult(self.pattern, node, self.context)

    def match(self, node: BaseNode) -> Result:
        method = 'match_' + self.pattern.__class__.__name__
        matcher = getattr(self, method, self.generic_match)
        return list(matcher(node))

    def _single_match(self, node: BaseNode) -> Result:
        assert isinstance(self.pattern, MatchRuleNode)
        # TODO: add operator usage
        for rule in self.pattern.rules:
            sub_matcher = self.make_matcher(rule, self.pattern.name)
            if sub_match := sub_matcher.match(node):
                yield self.make_result(node).attach(*sub_match)

    def _search_match(self, tree: BaseNode) -> Result:
        for node in walk(tree):
            yield from self._single_match(node)

    def match_MatchRuleNode(self, node: BaseNode) -> Result:
        assert isinstance(self.pattern, MatchRuleNode)
        if self.pattern.exact:
            yield from self._single_match(node)
        else:
            yield from self._search_match(node)

    def generic_match(self, node: BaseNode) -> Result:
        complex_fields: dict[str, Node] = {
            name: value
            for name, value in iter_fields(self.pattern)
        }

        for name in self.pattern.__fields_set__:
            if name in complex_fields:
                continue
            pattern_value = getattr(self.pattern, name)
            node_value = getattr(node, name, None)
            if pattern_value != node_value:
                return

        sub_matches: list[MatchingResult] = []

        for name, pattern_value in complex_fields.items():
            items = pattern_value if isinstance(pattern_value, Sequence) else [pattern_value]
            for item in items:
                sub_matcher = self.make_matcher(item, name)
                node_value = getattr(node, name, None)
                if node_value is None:
                    continue

                sub_match = []
                if isinstance(node_value, Sequence):
                    for node_item in node_value:
                        sub_match.extend(sub_matcher.match(node_item))
                if isinstance(node_value, BaseNode):
                    sub_match.extend(sub_matcher.match(node_value))

                if not sub_match:
                    return

                sub_matches.extend(sub_match)

        yield self.make_result(node).attach(*sub_matches)
