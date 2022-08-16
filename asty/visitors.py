from collections import deque
from typing import (
    Sequence,
)
from asty.nodes import (
    Node,
)


def iter_fields(node: Node):
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
            elif isinstance(old_value, Node):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
