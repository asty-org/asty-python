from collections import (
    defaultdict,
    deque,
)
from functools import wraps
from typing import (
    Sequence,
)
from asty.nodes import (
    BaseNode,
    MatchRuleNode,
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


class Matcher:
    sub_matchers: dict[str, list['Matcher']]

    def __init__(self, pattern: BaseNode):
        self.pattern = pattern
        self.sub_matchers = defaultdict(list)

    def make_matcher(self, context: str, pattern: BaseNode) -> 'Matcher':
        matcher = Matcher(pattern)

        def decorator(func):
            @wraps(func)
            def wrapper(node):
                result = func(node)
                if result:
                    self.sub_matchers[context].append(matcher)
                return result
            return wrapper

        matcher.match = decorator(matcher.match)

        return matcher

    def match(self, node: BaseNode):
        method = 'match_' + self.pattern.__class__.__name__
        matcher = getattr(self, method, self.generic_match)
        return matcher(node)

    def single_match(self, node: BaseNode):
        assert isinstance(self.pattern, MatchRuleNode)
        for rule in self.pattern.rules:
            sub_matcher = self.make_matcher(self.pattern.name, rule)
            if sub_matcher.match(node):
                return True
        return False

    def search_match(self, tree: BaseNode):
        search_matches = [
            self.single_match(node)
            for node in walk(tree)
        ]
        return any(search_matches)

    def match_MatchRuleNode(self, node: BaseNode):
        assert isinstance(self.pattern, MatchRuleNode)
        if self.pattern.exact:
            return self.single_match(node)
        else:
            return self.search_match(node)

    def field_match(self, node, name):
        value = getattr(node, name, None)
        if value is None:
            return False
        elif isinstance(value, Sequence):
            items_matches = [self.match(item) for item in value]
            return any(items_matches)
        else:
            return self.match(value)

    def generic_match(self, node):
        complex_fields = {
            name: value
            for name, value in iter_fields(self.pattern)
        }

        for name in self.pattern.__fields_set__:
            if name in complex_fields:
                continue
            pattern_value = getattr(self.pattern, name)
            node_value = getattr(node, name, None)
            if pattern_value != node_value:
                return False

        for name, value in complex_fields.items():
            if isinstance(value, Sequence):
                for item in value:
                    sub_matcher = self.make_matcher(name, item)
                    if not sub_matcher.field_match(node, name):
                        return False
            else:
                sub_matcher = self.make_matcher(name, value)
                if not sub_matcher.field_match(node, name):
                    return False

        return True

    def __pretty__(self, fmt, **kwargs):
        yield 'Matcher('
        yield 1
        yield 'type='
        yield fmt(self.pattern.node_type)
        yield ','
        yield 0
        if self.sub_matchers:
            yield 'matchers='
            yield fmt(dict(self.sub_matchers))
            yield ','
            yield 0
        # for name, value in self.sub_matchers.items():
        #     for item in value:
        #         yield name
        #         yield '='
        #         yield fmt(item)
        #         yield ','
        #         yield 0
        yield -1
        yield ')'
