from abc import (
    ABC,
    abstractmethod,
)
from enum import Enum
from typing import (
    Annotated,
    Literal,
    Optional,
    Iterable,
    Sequence,
    Union,
)

from pydantic import (
    BaseModel,
    Field,
    validator,
)

from .features import analyze_function_bodies


class NodeType(str, Enum):
    POSITION = 'Position'
    COMMENT = 'Comment'
    COMMENT_GROUP = 'CommentGroup'
    FIELD = 'Field'
    FIELD_LIST = 'FieldList'
    BAD_EXPR = 'BadExpr'
    IDENT = 'Ident'
    ELLIPSIS = 'Ellipsis'
    BASIC_LIT = 'BasicLit'
    FUNC_LIT = 'FuncLit'
    COMPOSITE_LIT = 'CompositeLit'
    PAREN_EXPR = 'ParenExpr'
    SELECTOR_EXPR = 'SelectorExpr'
    INDEX_EXPR = 'IndexExpr'
    INDEX_LIST_EXPR = 'IndexListExpr'
    SLICE_EXPR = 'SliceExpr'
    TYPE_ASSERT_EXPR = 'TypeAssertExpr'
    CALL_EXPR = 'CallExpr'
    STAR_EXPR = 'StarExpr'
    UNARY_EXPR = 'UnaryExpr'
    BINARY_EXPR = 'BinaryExpr'
    KEY_VALUE_EXPR = 'KeyValueExpr'
    ARRAY_TYPE = 'ArrayType'
    STRUCT_TYPE = 'StructType'
    FUNC_TYPE = 'FuncType'
    INTERFACE_TYPE = 'InterfaceType'
    MAP_TYPE = 'MapType'
    CHAN_TYPE = 'ChanType'
    BAD_STMT = 'BadStmt'
    DECL_STMT = 'DeclStmt'
    EMPTY_STMT = 'EmptyStmt'
    LABELED_STMT = 'LabeledStmt'
    EXPR_STMT = 'ExprStmt'
    SEND_STMT = 'SendStmt'
    INC_DEC_STMT = 'IncDecStmt'
    ASSIGN_STMT = 'AssignStmt'
    GO_STMT = 'GoStmt'
    DEFER_STMT = 'DeferStmt'
    RETURN_STMT = 'ReturnStmt'
    BRANCH_STMT = 'BranchStmt'
    BLOCK_STMT = 'BlockStmt'
    IF_STMT = 'IfStmt'
    CASE_CLAUSE = 'CaseClause'
    SWITCH_STMT = 'SwitchStmt'
    TYPE_SWITCH_STMT = 'TypeSwitchStmt'
    COMM_CLAUSE = 'CommClause'
    SELECT_STMT = 'SelectStmt'
    FOR_STMT = 'ForStmt'
    RANGE_STMT = 'RangeStmt'
    IMPORT_SPEC = 'ImportSpec'
    VALUE_SPEC = 'ValueSpec'
    TYPE_SPEC = 'TypeSpec'
    BAD_DECL = 'BadDecl'
    GEN_DECL = 'GenDecl'
    FUNC_DECL = 'FuncDecl'
    FILE = 'File'
    PACKAGE = 'Package'
    MATCH_RULE = 'MatchRule'

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

    # noinspection PyUnusedLocal
    def __pretty__(self, fmt, skip_exc):
        return repr(self)


NodeOrSequence = Union['Node', Sequence['Node']]
FieldSequence = Iterable[tuple[str, NodeOrSequence]]


class BaseNode(BaseModel, ABC):
    node_type: NodeType = Field(alias='NodeType')
    ref_id: Optional[int] = Field(alias='RefId')

    @abstractmethod
    def iterate_children(self) -> FieldSequence:
        ...

    @property
    @abstractmethod
    def position(self) -> Optional['PositionNode']:
        ...

    @classmethod
    def construct(cls, _fields_set: Optional[set[str]] = None, **values):
        _fields_set = _fields_set or {'node_type', *values.keys()}
        return super().construct(_fields_set, **values)

    def __repr_args__(self):
        return [
            (k, v)
            for k, v in self.__dict__.items()
            if k in self.__fields_set__ - {'node_type'}
        ]


def iter_field(name: str, node: Optional[NodeOrSequence]):
    if node is not None:
        yield name, node


Node = Annotated[
    Union[
        'PositionNode',
        'CommentNode',
        'CommentGroupNode',
        'FieldNode',
        'FieldListNode',
        'BadExprNode',
        'IdentNode',
        'EllipsisNode',
        'BasicLitNode',
        'FuncLitNode',
        'CompositeLitNode',
        'ParenExprNode',
        'SelectorExprNode',
        'IndexExprNode',
        'IndexListExprNode',
        'SliceExprNode',
        'TypeAssertExprNode',
        'CallExprNode',
        'StarExprNode',
        'UnaryExprNode',
        'BinaryExprNode',
        'KeyValueExprNode',
        'ArrayTypeNode',
        'StructTypeNode',
        'FuncTypeNode',
        'InterfaceTypeNode',
        'MapTypeNode',
        'ChanTypeNode',
        'BadStmtNode',
        'DeclStmtNode',
        'EmptyStmtNode',
        'LabeledStmtNode',
        'ExprStmtNode',
        'SendStmtNode',
        'IncDecStmtNode',
        'AssignStmtNode',
        'GoStmtNode',
        'DeferStmtNode',
        'ReturnStmtNode',
        'BranchStmtNode',
        'BlockStmtNode',
        'IfStmtNode',
        'CaseClauseNode',
        'SwitchStmtNode',
        'TypeSwitchStmtNode',
        'CommClauseNode',
        'SelectStmtNode',
        'ForStmtNode',
        'RangeStmtNode',
        'ImportSpecNode',
        'ValueSpecNode',
        'TypeSpecNode',
        'BadDeclNode',
        'GenDeclNode',
        'FuncDeclNode',
        'FileNode',
        'PackageNode',
        'MatchRuleNode',
    ],
    Field(discriminator="node_type"),
]


class PositionNode(BaseNode):
    node_type: Literal[NodeType.POSITION] = Field(alias='NodeType', default=NodeType.POSITION)
    filename: Optional[str] = Field(alias='Filename', default=None)
    offset: Optional[int] = Field(alias='Offset', default=None)
    line: Optional[int] = Field(alias='Line', default=None)
    column: Optional[int] = Field(alias='Column', default=None)

    @property
    def short_location(self):
        if self.filename is None or self.offset is None:
            return None
        return f"{self.filename}:{self.offset}"

    @property
    def full_location(self):
        if self.short_location is None or self.column is None:
            return None
        return f"{self.short_location}:{self.offset}"

    @property
    def position(self):
        return self

    def iterate_children(self) -> FieldSequence:
        yield from ()


class CommentNode(BaseNode):
    node_type: Literal[NodeType.COMMENT] = Field(alias='NodeType', default=NodeType.COMMENT)
    slash: Optional[PositionNode] = Field(alias='Slash', default=None)
    text: Optional[str] = Field(alias='Text', default=None)

    def iterate_children(self):
        yield from iter_field('slash', self.slash)

    @property
    def position(self):
        return self.slash


class CommentGroupNode(BaseNode):
    node_type: Literal[NodeType.COMMENT_GROUP] = Field(alias='NodeType', default=NodeType.COMMENT_GROUP)
    comment_list: Optional[list[Node]] = Field(alias='List')

    def iterate_children(self):
        yield from iter_field('comment_list', self.comment_list)

    @property
    def position(self):
        if self.comment_list:
            return self.comment_list[0].position


class FieldNode(BaseNode):
    node_type: Literal[NodeType.FIELD] = Field(alias='NodeType', default=NodeType.FIELD)
    doc: Optional[CommentGroupNode] = Field(alias='Doc', default=None)
    names: Optional[list['IdentNode']] = Field(alias='Names')
    type: Optional[Node] = Field(alias='Type', default=None)
    tag: Optional['BasicLitNode'] = Field(alias='Tag', default=None)
    comment: Optional[CommentGroupNode] = Field(alias='Comment', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('doc', self.doc)
        yield from iter_field('names', self.names)
        yield from iter_field('type', self.type)
        yield from iter_field('tag', self.tag)
        yield from iter_field('comment', self.comment)

    @property
    def position(self):
        if self.names:
            return self.names[0].position


class FieldListNode(BaseNode):
    node_type: Literal[NodeType.FIELD_LIST] = Field(alias='NodeType', default=NodeType.FIELD_LIST)
    opening: Optional[PositionNode] = Field(alias='Opening', default=None)
    field_list: Optional[list[Node]] = Field(alias='List')
    closing: Optional[PositionNode] = Field(alias='Closing', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('opening', self.opening)
        yield from iter_field('field_list', self.field_list)
        yield from iter_field('closing', self.closing)

    @property
    def position(self):
        return self.opening


class BadExprNode(BaseNode):
    node_type: Literal[NodeType.BAD_EXPR] = Field(alias='NodeType', default=NodeType.BAD_EXPR)
    from_pos: Optional[PositionNode] = Field(alias='From', default=None)
    to_pos: Optional[PositionNode] = Field(alias='To', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('from_pos', self.from_pos)
        yield from iter_field('to_pos', self.to_pos)

    @property
    def position(self):
        return self.from_pos


class IdentNode(BaseNode):
    node_type: Literal[NodeType.IDENT] = Field(alias='NodeType', default=NodeType.IDENT)
    name_pos: Optional[PositionNode] = Field(alias='NamePos', default=None)
    name: Optional[str] = Field(alias='Name', default=None)
    # obj: Optional[Object] = Field(alias='Obj', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('name_pos', self.name_pos)

    @property
    def position(self):
        return self.name_pos


class EllipsisNode(BaseNode):
    node_type: Literal[NodeType.ELLIPSIS] = Field(alias='NodeType', default=NodeType.ELLIPSIS)
    ellipsis: Optional[PositionNode] = Field(alias='Ellipsis', default=None)
    elt: Optional[Node] = Field(alias='Elt', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('ellipsis', self.ellipsis)
        yield from iter_field('elt', self.elt)

    @property
    def position(self):
        return self.ellipsis


class BasicLitNode(BaseNode):
    node_type: Literal[NodeType.BASIC_LIT] = Field(alias='NodeType', default=NodeType.BASIC_LIT)
    value_pos: Optional[PositionNode] = Field(alias='ValuePos', default=None)
    kind: Optional[str] = Field(alias='Kind', default=None)
    value: Optional[str] = Field(alias='Value', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('value_pos', self.value_pos)

    @property
    def position(self):
        return self.value_pos


class FuncLitNode(BaseNode):
    node_type: Literal[NodeType.FUNC_LIT] = Field(alias='NodeType', default=NodeType.FUNC_LIT)
    type: Optional['FuncTypeNode'] = Field(alias='Type', default=None)
    body: Optional['BlockStmtNode'] = Field(alias='Body', default=None)

    @validator("body", pre=True)
    def validate_body(cls, value):
        if not analyze_function_bodies.get():
            return None
        return value

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('type', self.type)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        if self.type:
            return self.type.position


class CompositeLitNode(BaseNode):
    node_type: Literal[NodeType.COMPOSITE_LIT] = Field(alias='NodeType', default=NodeType.COMPOSITE_LIT)
    type: Optional[Node] = Field(alias='Type', default=None)
    lbrace: Optional[PositionNode] = Field(alias='Lbrace', default=None)
    elts: Optional[list[Node]] = Field(alias='Elts')
    rbrace: Optional[PositionNode] = Field(alias='Rbrace', default=None)
    incomplete: Optional[bool] = Field(alias='Incomplete', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('type', self.type)
        yield from iter_field('lbrace', self.lbrace)
        yield from iter_field('elts', self.elts)
        yield from iter_field('rbrace', self.rbrace)

    @property
    def position(self):
        if self.type:
            return self.type.position


class ParenExprNode(BaseNode):
    node_type: Literal[NodeType.PAREN_EXPR] = Field(alias='NodeType', default=NodeType.PAREN_EXPR)
    lparen: Optional[PositionNode] = Field(alias='Lparen', default=None)
    x: Optional[Node] = Field(alias='X', default=None)
    rparen: Optional[PositionNode] = Field(alias='Rparen', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('lparen', self.lparen)
        yield from iter_field('x', self.x)
        yield from iter_field('rparen', self.rparen)

    @property
    def position(self):
        return self.lparen


class SelectorExprNode(BaseNode):
    node_type: Literal[NodeType.SELECTOR_EXPR] = Field(alias='NodeType', default=NodeType.SELECTOR_EXPR)
    x: Optional[Node] = Field(alias='X', default=None)
    sel: Optional[IdentNode] = Field(alias='Sel', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('x', self.x)
        yield from iter_field('sel', self.sel)

    @property
    def position(self):
        if self.x:
            return self.x.position


class IndexExprNode(BaseNode):
    node_type: Literal[NodeType.INDEX_EXPR] = Field(alias='NodeType', default=NodeType.INDEX_EXPR)
    x: Optional[Node] = Field(alias='X', default=None)
    lbrack: Optional[PositionNode] = Field(alias='Lbrack', default=None)
    index: Optional[Node] = Field(alias='Index', default=None)
    rbrack: Optional[PositionNode] = Field(alias='Rbrack', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('x', self.x)
        yield from iter_field('lbrack', self.lbrack)
        yield from iter_field('index', self.index)
        yield from iter_field('rbrack', self.rbrack)

    @property
    def position(self):
        if self.x:
            return self.x.position


class IndexListExprNode(BaseNode):
    node_type: Literal[NodeType.INDEX_LIST_EXPR] = Field(alias='NodeType', default=NodeType.INDEX_LIST_EXPR)
    x: Optional[Node] = Field(alias='X', default=None)
    lbrack: Optional[PositionNode] = Field(alias='Lbrack', default=None)
    indices: Optional[list[Node]] = Field(alias='Indices')
    rbrack: Optional[PositionNode] = Field(alias='Rbrack', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('x', self.x)
        yield from iter_field('lbrack', self.lbrack)
        yield from iter_field('indices', self.indices)
        yield from iter_field('rbrack', self.rbrack)

    @property
    def position(self):
        if self.x:
            return self.x.position


class SliceExprNode(BaseNode):
    node_type: Literal[NodeType.SLICE_EXPR] = Field(alias='NodeType', default=NodeType.SLICE_EXPR)
    x: Optional[Node] = Field(alias='X', default=None)
    lbrack: Optional[PositionNode] = Field(alias='Lbrack', default=None)
    low: Optional[Node] = Field(alias='Low', default=None)
    high: Optional[Node] = Field(alias='High', default=None)
    max: Optional[Node] = Field(alias='Max', default=None)
    slice3: Optional[bool] = Field(alias='Slice3', default=None)
    rbrack: Optional[PositionNode] = Field(alias='Rbrack', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('x', self.x)
        yield from iter_field('lbrack', self.lbrack)
        yield from iter_field('low', self.low)
        yield from iter_field('high', self.high)
        yield from iter_field('max', self.max)
        yield from iter_field('rbrack', self.rbrack)

    @property
    def position(self):
        if self.x:
            return self.x.position


class TypeAssertExprNode(BaseNode):
    node_type: Literal[NodeType.TYPE_ASSERT_EXPR] = Field(alias='NodeType', default=NodeType.TYPE_ASSERT_EXPR)
    x: Optional[Node] = Field(alias='X', default=None)
    lparen: Optional[PositionNode] = Field(alias='Lparen', default=None)
    type: Optional[Node] = Field(alias='Type', default=None)
    rparen: Optional[PositionNode] = Field(alias='Rparen', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('x', self.x)
        yield from iter_field('lparen', self.lparen)
        yield from iter_field('type', self.type)
        yield from iter_field('rparen', self.rparen)

    @property
    def position(self):
        if self.x:
            return self.x.position


class CallExprNode(BaseNode):
    node_type: Literal[NodeType.CALL_EXPR] = Field(alias='NodeType', default=NodeType.CALL_EXPR)
    fun: Optional[Node] = Field(alias='Fun', default=None)
    lparen: Optional[PositionNode] = Field(alias='Lparen', default=None)
    args: Optional[list[Node]] = Field(alias='Args')
    ellipsis: Optional[PositionNode] = Field(alias='Ellipsis', default=None)
    rparen: Optional[PositionNode] = Field(alias='Rparen', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('fun', self.fun)
        yield from iter_field('lparen', self.lparen)
        yield from iter_field('args', self.args)
        yield from iter_field('ellipsis', self.ellipsis)
        yield from iter_field('rparen', self.rparen)

    @property
    def position(self):
        if self.fun:
            return self.fun.position


class StarExprNode(BaseNode):
    node_type: Literal[NodeType.STAR_EXPR] = Field(alias='NodeType', default=NodeType.STAR_EXPR)
    star: Optional[PositionNode] = Field(alias='Star', default=None)
    x: Optional[Node] = Field(alias='X', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('star', self.star)
        yield from iter_field('x', self.x)

    @property
    def position(self):
        return self.star


class UnaryExprNode(BaseNode):
    node_type: Literal[NodeType.UNARY_EXPR] = Field(alias='NodeType', default=NodeType.UNARY_EXPR)
    op_pos: Optional[PositionNode] = Field(alias='OpPos', default=None)
    op: Optional[str] = Field(alias='Op', default=None)
    x: Optional[Node] = Field(alias='X', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('op_pos', self.op_pos)
        yield from iter_field('x', self.x)

    @property
    def position(self):
        return self.op_pos


class BinaryExprNode(BaseNode):
    node_type: Literal[NodeType.BINARY_EXPR] = Field(alias='NodeType', default=NodeType.BINARY_EXPR)
    x: Optional[Node] = Field(alias='X', default=None)
    op_pos: Optional[PositionNode] = Field(alias='OpPos', default=None)
    op: Optional[str] = Field(alias='Op', default=None)
    y: Optional[Node] = Field(alias='Y', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('x', self.x)
        yield from iter_field('op_pos', self.op_pos)
        yield from iter_field('y', self.y)

    @property
    def position(self):
        if self.x:
            return self.x.position


class KeyValueExprNode(BaseNode):
    node_type: Literal[NodeType.KEY_VALUE_EXPR] = Field(alias='NodeType', default=NodeType.KEY_VALUE_EXPR)
    key: Optional[Node] = Field(alias='Key', default=None)
    colon: Optional[PositionNode] = Field(alias='Colon', default=None)
    value: Optional[Node] = Field(alias='Value', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('key', self.key)
        yield from iter_field('colon', self.colon)
        yield from iter_field('value', self.value)

    @property
    def position(self):
        if self.key:
            return self.key.position


class ArrayTypeNode(BaseNode):
    node_type: Literal[NodeType.ARRAY_TYPE] = Field(alias='NodeType', default=NodeType.ARRAY_TYPE)
    lbrack: Optional[PositionNode] = Field(alias='Lbrack', default=None)
    len: Optional[Node] = Field(alias='Len', default=None)
    elt: Optional[Node] = Field(alias='Elt', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('lbrack', self.lbrack)
        yield from iter_field('len', self.len)
        yield from iter_field('elt', self.elt)

    @property
    def position(self):
        return self.lbrack


class StructTypeNode(BaseNode):
    node_type: Literal[NodeType.STRUCT_TYPE] = Field(alias='NodeType', default=NodeType.STRUCT_TYPE)
    struct: Optional[PositionNode] = Field(alias='Struct', default=None)
    fields: Optional[FieldListNode] = Field(alias='Fields', default=None)
    incomplete: Optional[bool] = Field(alias='Incomplete', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('struct', self.struct)
        yield from iter_field('fields', self.fields)

    @property
    def position(self):
        return self.struct


class FuncTypeNode(BaseNode):
    node_type: Literal[NodeType.FUNC_TYPE] = Field(alias='NodeType', default=NodeType.FUNC_TYPE)
    func: Optional[PositionNode] = Field(alias='Func', default=None)
    type_params: Optional[FieldListNode] = Field(alias='TypeParams', default=None)
    params: Optional[FieldListNode] = Field(alias='Params', default=None)
    results: Optional[FieldListNode] = Field(alias='Results', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('func', self.func)
        yield from iter_field('type_params', self.type_params)
        yield from iter_field('params', self.params)
        yield from iter_field('results', self.results)

    @property
    def position(self):
        return self.func


class InterfaceTypeNode(BaseNode):
    node_type: Literal[NodeType.INTERFACE_TYPE] = Field(alias='NodeType', default=NodeType.INTERFACE_TYPE)
    interface: Optional[PositionNode] = Field(alias='Interface', default=None)
    methods: Optional[FieldListNode] = Field(alias='Methods', default=None)
    incomplete: Optional[bool] = Field(alias='Incomplete', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('interface', self.interface)
        yield from iter_field('methods', self.methods)

    @property
    def position(self):
        return self.interface


class MapTypeNode(BaseNode):
    node_type: Literal[NodeType.MAP_TYPE] = Field(alias='NodeType', default=NodeType.MAP_TYPE)
    map: Optional[PositionNode] = Field(alias='Map', default=None)
    key: Optional[Node] = Field(alias='Key', default=None)
    value: Optional[Node] = Field(alias='Value', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('map', self.map)
        yield from iter_field('key', self.key)
        yield from iter_field('value', self.value)

    @property
    def position(self):
        return self.map


class ChanTypeNode(BaseNode):
    node_type: Literal[NodeType.CHAN_TYPE] = Field(alias='NodeType', default=NodeType.CHAN_TYPE)
    begin: Optional[PositionNode] = Field(alias='Begin', default=None)
    arrow: Optional[PositionNode] = Field(alias='Arrow', default=None)
    dir: Optional[str] = Field(alias='Dir', default=None)
    value: Optional[Node] = Field(alias='Value', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('begin', self.begin)
        yield from iter_field('arrow', self.arrow)
        yield from iter_field('value', self.value)

    @property
    def position(self):
        return self.begin


class BadStmtNode(BaseNode):
    node_type: Literal[NodeType.BAD_STMT] = Field(alias='NodeType', default=NodeType.BAD_STMT)
    from_pos: Optional[PositionNode] = Field(alias='From', default=None)
    to_pos: Optional[PositionNode] = Field(alias='To', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('from_pos', self.from_pos)
        yield from iter_field('to_pos', self.to_pos)

    @property
    def position(self):
        return self.from_pos


class DeclStmtNode(BaseNode):
    node_type: Literal[NodeType.DECL_STMT] = Field(alias='NodeType', default=NodeType.DECL_STMT)
    decl: Optional[Node] = Field(alias='Decl', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('decl', self.decl)

    @property
    def position(self):
        if self.decl:
            return self.decl.position


class EmptyStmtNode(BaseNode):
    node_type: Literal[NodeType.EMPTY_STMT] = Field(alias='NodeType', default=NodeType.EMPTY_STMT)
    semicolon: Optional[PositionNode] = Field(alias='Semicolon', default=None)
    implicit: Optional[bool] = Field(alias='Implicit', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('semicolon', self.semicolon)

    @property
    def position(self):
        return self.semicolon


class LabeledStmtNode(BaseNode):
    node_type: Literal[NodeType.LABELED_STMT] = Field(alias='NodeType', default=NodeType.LABELED_STMT)
    label: Optional[IdentNode] = Field(alias='Label', default=None)
    colon: Optional[PositionNode] = Field(alias='Colon', default=None)
    stmt: Optional[Node] = Field(alias='Stmt', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('label', self.label)
        yield from iter_field('colon', self.colon)
        yield from iter_field('stmt', self.stmt)

    @property
    def position(self):
        if self.label:
            return self.label.position


class ExprStmtNode(BaseNode):
    node_type: Literal[NodeType.EXPR_STMT] = Field(alias='NodeType', default=NodeType.EXPR_STMT)
    x: Optional[Node] = Field(alias='X', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('x', self.x)

    @property
    def position(self):
        if self.x:
            return self.x.position


class SendStmtNode(BaseNode):
    node_type: Literal[NodeType.SEND_STMT] = Field(alias='NodeType', default=NodeType.SEND_STMT)
    chan: Optional[Node] = Field(alias='Chan', default=None)
    arrow: Optional[PositionNode] = Field(alias='Arrow', default=None)
    value: Optional[Node] = Field(alias='Value', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('chan', self.chan)
        yield from iter_field('arrow', self.arrow)
        yield from iter_field('value', self.value)

    @property
    def position(self):
        if self.chan:
            return self.chan.position


class IncDecStmtNode(BaseNode):
    node_type: Literal[NodeType.INC_DEC_STMT] = Field(alias='NodeType', default=NodeType.INC_DEC_STMT)
    x: Optional[Node] = Field(alias='X', default=None)
    tok_pos: Optional[PositionNode] = Field(alias='TokPos', default=None)
    tok: Optional[str] = Field(alias='Tok', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('x', self.x)
        yield from iter_field('tok_pos', self.tok_pos)

    @property
    def position(self):
        if self.x:
            return self.x.position


class AssignStmtNode(BaseNode):
    node_type: Literal[NodeType.ASSIGN_STMT] = Field(alias='NodeType', default=NodeType.ASSIGN_STMT)
    lhs: Optional[list[Node]] = Field(alias='Lhs')
    tok_pos: Optional[PositionNode] = Field(alias='TokPos', default=None)
    tok: Optional[str] = Field(alias='Tok', default=None)
    rhs: Optional[list[Node]] = Field(alias='Rhs')

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('lhs', self.lhs)
        yield from iter_field('tok_pos', self.tok_pos)
        yield from iter_field('rhs', self.rhs)

    @property
    def position(self):
        if self.lhs:
            return self.lhs[0].position


class GoStmtNode(BaseNode):
    node_type: Literal[NodeType.GO_STMT] = Field(alias='NodeType', default=NodeType.GO_STMT)
    go: Optional[PositionNode] = Field(alias='Go', default=None)
    call: Optional[CallExprNode] = Field(alias='Call', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('go', self.go)
        yield from iter_field('call', self.call)

    @property
    def position(self):
        return self.go


class DeferStmtNode(BaseNode):
    node_type: Literal[NodeType.DEFER_STMT] = Field(alias='NodeType', default=NodeType.DEFER_STMT)
    defer: Optional[PositionNode] = Field(alias='Defer', default=None)
    call: Optional[CallExprNode] = Field(alias='Call', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('defer', self.defer)
        yield from iter_field('call', self.call)

    @property
    def position(self):
        return self.defer


class ReturnStmtNode(BaseNode):
    node_type: Literal[NodeType.RETURN_STMT] = Field(alias='NodeType', default=NodeType.RETURN_STMT)
    return_pos: Optional[PositionNode] = Field(alias='Return', default=None)
    results: Optional[list[Node]] = Field(alias='Results')

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('return_pos', self.return_pos)
        yield from iter_field('results', self.results)

    @property
    def position(self):
        return self.return_pos


class BranchStmtNode(BaseNode):
    node_type: Literal[NodeType.BRANCH_STMT] = Field(alias='NodeType', default=NodeType.BRANCH_STMT)
    tok_pos: Optional[PositionNode] = Field(alias='TokPos', default=None)
    tok: Optional[str] = Field(alias='Tok', default=None)
    label: Optional[IdentNode] = Field(alias='Label', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('tok_pos', self.tok_pos)
        yield from iter_field('label', self.label)

    @property
    def position(self):
        return self.tok_pos


class BlockStmtNode(BaseNode):
    node_type: Literal[NodeType.BLOCK_STMT] = Field(alias='NodeType', default=NodeType.BLOCK_STMT)
    lbrace: Optional[PositionNode] = Field(alias='Lbrace', default=None)
    stmt_list: Optional[list[Node]] = Field(alias='List')
    rbrace: Optional[PositionNode] = Field(alias='Rbrace', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('lbrace', self.lbrace)
        yield from iter_field('stmt_list', self.stmt_list)
        yield from iter_field('rbrace', self.rbrace)

    @property
    def position(self):
        return self.lbrace


class IfStmtNode(BaseNode):
    node_type: Literal[NodeType.IF_STMT] = Field(alias='NodeType', default=NodeType.IF_STMT)
    if_pos: Optional[PositionNode] = Field(alias='If', default=None)
    init: Optional[Node] = Field(alias='Init', default=None)
    cond: Optional[Node] = Field(alias='Cond', default=None)
    body: Optional[BlockStmtNode] = Field(alias='Body', default=None)
    else_pos: Optional[Node] = Field(alias='Else', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('if_pos', self.if_pos)
        yield from iter_field('init', self.init)
        yield from iter_field('cond', self.cond)
        yield from iter_field('body', self.body)
        yield from iter_field('else_pos', self.else_pos)

    @property
    def position(self):
        return self.if_pos


class CaseClauseNode(BaseNode):
    node_type: Literal[NodeType.CASE_CLAUSE] = Field(alias='NodeType', default=NodeType.CASE_CLAUSE)
    case_pos: Optional[PositionNode] = Field(alias='Case', default=None)
    expr_list: Optional[list[Node]] = Field(alias='List')
    colon: Optional[PositionNode] = Field(alias='Colon', default=None)
    body: Optional[list[Node]] = Field(alias='Body')

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('case_pos', self.case_pos)
        yield from iter_field('expr_list', self.expr_list)
        yield from iter_field('colon', self.colon)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        return self.case_pos


class SwitchStmtNode(BaseNode):
    node_type: Literal[NodeType.SWITCH_STMT] = Field(alias='NodeType', default=NodeType.SWITCH_STMT)
    switch: Optional[PositionNode] = Field(alias='Switch', default=None)
    init: Optional[Node] = Field(alias='Init', default=None)
    tag: Optional[Node] = Field(alias='Tag', default=None)
    body: Optional[BlockStmtNode] = Field(alias='Body', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('switch', self.switch)
        yield from iter_field('init', self.init)
        yield from iter_field('tag', self.tag)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        return self.switch


class TypeSwitchStmtNode(BaseNode):
    node_type: Literal[NodeType.TYPE_SWITCH_STMT] = Field(alias='NodeType', default=NodeType.TYPE_SWITCH_STMT)
    switch: Optional[PositionNode] = Field(alias='Switch', default=None)
    init: Optional[Node] = Field(alias='Init', default=None)
    assign: Optional[Node] = Field(alias='Assign', default=None)
    body: Optional[BlockStmtNode] = Field(alias='Body', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('switch', self.switch)
        yield from iter_field('init', self.init)
        yield from iter_field('assign', self.assign)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        return self.switch


class CommClauseNode(BaseNode):
    node_type: Literal[NodeType.COMM_CLAUSE] = Field(alias='NodeType', default=NodeType.COMM_CLAUSE)
    case_pos: Optional[PositionNode] = Field(alias='Case', default=None)
    comm: Optional[Node] = Field(alias='Comm', default=None)
    colon: Optional[PositionNode] = Field(alias='Colon', default=None)
    body: Optional[list[Node]] = Field(alias='Body')

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('case_pos', self.case_pos)
        yield from iter_field('comm', self.comm)
        yield from iter_field('colon', self.colon)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        return self.case_pos


class SelectStmtNode(BaseNode):
    node_type: Literal[NodeType.SELECT_STMT] = Field(alias='NodeType', default=NodeType.SELECT_STMT)
    select: Optional[PositionNode] = Field(alias='Select', default=None)
    body: Optional[BlockStmtNode] = Field(alias='Body', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('select', self.select)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        return self.select


class ForStmtNode(BaseNode):
    node_type: Literal[NodeType.FOR_STMT] = Field(alias='NodeType', default=NodeType.FOR_STMT)
    for_pos: Optional[PositionNode] = Field(alias='For', default=None)
    init: Optional[Node] = Field(alias='Init', default=None)
    cond: Optional[Node] = Field(alias='Cond', default=None)
    post: Optional[Node] = Field(alias='Post', default=None)
    body: Optional[BlockStmtNode] = Field(alias='Body', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('for_pos', self.for_pos)
        yield from iter_field('init', self.init)
        yield from iter_field('cond', self.cond)
        yield from iter_field('post', self.post)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        return self.for_pos


class RangeStmtNode(BaseNode):
    node_type: Literal[NodeType.RANGE_STMT] = Field(alias='NodeType', default=NodeType.RANGE_STMT)
    for_pos: Optional[PositionNode] = Field(alias='For', default=None)
    key: Optional[Node] = Field(alias='Key', default=None)
    value: Optional[Node] = Field(alias='Value', default=None)
    tok_pos: Optional[PositionNode] = Field(alias='TokPos', default=None)
    tok: Optional[str] = Field(alias='Tok', default=None)
    x: Optional[Node] = Field(alias='X', default=None)
    body: Optional[BlockStmtNode] = Field(alias='Body', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('for_pos', self.for_pos)
        yield from iter_field('key', self.key)
        yield from iter_field('value', self.value)
        yield from iter_field('tok_pos', self.tok_pos)
        yield from iter_field('x', self.x)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        return self.for_pos


class ImportSpecNode(BaseNode):
    node_type: Literal[NodeType.IMPORT_SPEC] = Field(alias='NodeType', default=NodeType.IMPORT_SPEC)
    doc: Optional[CommentGroupNode] = Field(alias='Doc', default=None)
    name: Optional[IdentNode] = Field(alias='Name', default=None)
    path: Optional[BasicLitNode] = Field(alias='Path', default=None)
    comment: Optional[CommentGroupNode] = Field(alias='Comment', default=None)
    end_pos: Optional[PositionNode] = Field(alias='EndPos', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('doc', self.doc)
        yield from iter_field('name', self.name)
        yield from iter_field('path', self.path)
        yield from iter_field('comment', self.comment)
        yield from iter_field('end_pos', self.end_pos)

    @property
    def position(self):
        if self.name:
            return self.name.position
        if self.path:
            return self.path.position


class ValueSpecNode(BaseNode):
    node_type: Literal[NodeType.VALUE_SPEC] = Field(alias='NodeType', default=NodeType.VALUE_SPEC)
    doc: Optional[CommentGroupNode] = Field(alias='Doc', default=None)
    names: Optional[list[IdentNode]] = Field(alias='Names')
    type: Optional[Node] = Field(alias='Type', default=None)
    values: Optional[list[Node]] = Field(alias='Values')
    comment: Optional[CommentGroupNode] = Field(alias='Comment', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('doc', self.doc)
        yield from iter_field('names', self.names)
        yield from iter_field('type', self.type)
        yield from iter_field('values', self.values)
        yield from iter_field('comment', self.comment)

    @property
    def position(self):
        if self.names:
            return self.names[0].position


class TypeSpecNode(BaseNode):
    node_type: Literal[NodeType.TYPE_SPEC] = Field(alias='NodeType', default=NodeType.TYPE_SPEC)
    doc: Optional[CommentGroupNode] = Field(alias='Doc', default=None)
    name: Optional[IdentNode] = Field(alias='Name', default=None)
    type_params: Optional[FieldListNode] = Field(alias='TypeParams', default=None)
    assign: Optional[PositionNode] = Field(alias='Assign', default=None)
    type: Optional[Node] = Field(alias='Type', default=None)
    comment: Optional[CommentGroupNode] = Field(alias='Comment', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('doc', self.doc)
        yield from iter_field('name', self.name)
        yield from iter_field('type_params', self.type_params)
        yield from iter_field('assign', self.assign)
        yield from iter_field('type', self.type)
        yield from iter_field('comment', self.comment)

    @property
    def position(self):
        if self.name:
            return self.name.position


class BadDeclNode(BaseNode):
    node_type: Literal[NodeType.BAD_DECL] = Field(alias='NodeType', default=NodeType.BAD_DECL)
    from_pos: Optional[PositionNode] = Field(alias='From', default=None)
    to_pos: Optional[PositionNode] = Field(alias='To', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('from_pos', self.from_pos)
        yield from iter_field('to_pos', self.to_pos)

    @property
    def position(self):
        return self.from_pos


class GenDeclNode(BaseNode):
    node_type: Literal[NodeType.GEN_DECL] = Field(alias='NodeType', default=NodeType.GEN_DECL)
    doc: Optional[CommentGroupNode] = Field(alias='Doc', default=None)
    tok_pos: Optional[PositionNode] = Field(alias='TokPos', default=None)
    tok: Optional[str] = Field(alias='Tok', default=None)
    lparen: Optional[PositionNode] = Field(alias='Lparen', default=None)
    specs: Optional[list[Node]] = Field(alias='Specs')
    rparen: Optional[PositionNode] = Field(alias='Rparen', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('doc', self.doc)
        yield from iter_field('tok_pos', self.tok_pos)
        yield from iter_field('lparen', self.lparen)
        yield from iter_field('specs', self.specs)
        yield from iter_field('rparen', self.rparen)

    @property
    def position(self):
        return self.tok_pos


class FuncDeclNode(BaseNode):
    node_type: Literal[NodeType.FUNC_DECL] = Field(alias='NodeType', default=NodeType.FUNC_DECL)
    doc: Optional[CommentGroupNode] = Field(alias='Doc', default=None)
    recv: Optional[FieldListNode] = Field(alias='Recv', default=None)
    name: Optional[IdentNode] = Field(alias='Name', default=None)
    type: Optional[FuncTypeNode] = Field(alias='Type', default=None)
    body: Optional[BlockStmtNode] = Field(alias='Body', default=None)

    @validator("body", pre=True)
    def validate_body(cls, value):
        if not analyze_function_bodies.get():
            return None
        return value

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('doc', self.doc)
        yield from iter_field('recv', self.recv)
        yield from iter_field('name', self.name)
        yield from iter_field('type', self.type)
        yield from iter_field('body', self.body)

    @property
    def position(self):
        if self.recv:
            return self.recv.position


class LineInfo(BaseModel):
    offset: int = Field(alias='Offset')
    filename: str = Field(alias='Filename')
    line: int = Field(alias='Line')
    column: int = Field(alias='Column')


class File(BaseModel):
    name: str = Field(alias='Name')
    base: int = Field(alias='Base')
    size: int = Field(alias='Size')
    lines: Optional[list[int]] = Field(alias='Lines', default=None)
    infos: Optional[list[int]] = Field(alias='Infos', default=None)


class FileSet(BaseModel):
    base: int = Field(alias='Base')
    files: list[File] = Field(alias='Files')


class FileNode(BaseNode):
    node_type: Literal[NodeType.FILE] = Field(alias='NodeType', default=NodeType.FILE)
    doc: Optional[CommentGroupNode] = Field(alias='Doc', default=None)
    package: Optional[PositionNode] = Field(alias='Package', default=None)
    name: Optional[IdentNode] = Field(alias='Name', default=None)
    decls: Optional[list[Node]] = Field(alias='Decls')
    imports: Optional[list[ImportSpecNode]] = Field(alias='Imports', default=None)
    unresolved: Optional[list[IdentNode]] = Field(alias='Unresolved', default=None)
    comments: Optional[list[CommentGroupNode]] = Field(alias='Comments', default=None)
    file_set: Optional[FileSet] = Field(alias='FileSet', default=None)
    # scope: Optional[Scope] = Field(alias='Scope', default=None)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('doc', self.doc)
        yield from iter_field('package', self.package)
        yield from iter_field('name', self.name)
        yield from iter_field('decls', self.decls)
        yield from iter_field('imports', self.imports)
        yield from iter_field('unresolved', self.unresolved)
        yield from iter_field('comments', self.comments)

    @property
    def position(self):
        return self.package


class PackageNode(BaseNode):
    node_type: Literal[NodeType.PACKAGE] = Field(alias='NodeType', default=NodeType.PACKAGE)
    name: Optional[str] = Field(alias='Name', default=None)
    # scope: Optional[Scope] = Field(alias='Scope', default=None)
    # imports: Optional[map[str]Object] = Field(alias='Imports')
    files: Optional[dict[str, FileNode]] = Field(alias='Files')

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('files', self.files)

    @property
    def position(self):
        return None


class MatchOperatorType(str, Enum):
    ANY_OF = 'anyOf'
    ALL_OF = 'allOf'
    ONE_OF = 'oneOf'
    NOT = 'not'


class MatchRuleNode(BaseNode):
    node_type: Literal[NodeType.MATCH_RULE] = Field(alias='NodeType', default=NodeType.MATCH_RULE)
    name: str = Field(alias='Name')
    rules: list[Node] = Field(alias='Rules', default_factory=list)
    exact: bool = Field(alias='Exact', default=False)
    operator: MatchOperatorType = Field(alias='Operator', default=MatchOperatorType.ANY_OF)

    def iterate_children(self) -> FieldSequence:
        yield from iter_field('rules', self.rules)

    @property
    def position(self):
        return None


BaseNode.update_forward_refs()
PositionNode.update_forward_refs()
CommentNode.update_forward_refs()
CommentGroupNode.update_forward_refs()
FieldNode.update_forward_refs()
FieldListNode.update_forward_refs()
BadExprNode.update_forward_refs()
IdentNode.update_forward_refs()
EllipsisNode.update_forward_refs()
BasicLitNode.update_forward_refs()
FuncLitNode.update_forward_refs()
CompositeLitNode.update_forward_refs()
ParenExprNode.update_forward_refs()
SelectorExprNode.update_forward_refs()
IndexExprNode.update_forward_refs()
IndexListExprNode.update_forward_refs()
SliceExprNode.update_forward_refs()
TypeAssertExprNode.update_forward_refs()
CallExprNode.update_forward_refs()
StarExprNode.update_forward_refs()
UnaryExprNode.update_forward_refs()
BinaryExprNode.update_forward_refs()
KeyValueExprNode.update_forward_refs()
ArrayTypeNode.update_forward_refs()
StructTypeNode.update_forward_refs()
FuncTypeNode.update_forward_refs()
InterfaceTypeNode.update_forward_refs()
MapTypeNode.update_forward_refs()
ChanTypeNode.update_forward_refs()
BadStmtNode.update_forward_refs()
DeclStmtNode.update_forward_refs()
EmptyStmtNode.update_forward_refs()
LabeledStmtNode.update_forward_refs()
ExprStmtNode.update_forward_refs()
SendStmtNode.update_forward_refs()
IncDecStmtNode.update_forward_refs()
AssignStmtNode.update_forward_refs()
GoStmtNode.update_forward_refs()
DeferStmtNode.update_forward_refs()
ReturnStmtNode.update_forward_refs()
BranchStmtNode.update_forward_refs()
BlockStmtNode.update_forward_refs()
IfStmtNode.update_forward_refs()
CaseClauseNode.update_forward_refs()
SwitchStmtNode.update_forward_refs()
TypeSwitchStmtNode.update_forward_refs()
CommClauseNode.update_forward_refs()
SelectStmtNode.update_forward_refs()
ForStmtNode.update_forward_refs()
RangeStmtNode.update_forward_refs()
ImportSpecNode.update_forward_refs()
ValueSpecNode.update_forward_refs()
TypeSpecNode.update_forward_refs()
BadDeclNode.update_forward_refs()
GenDeclNode.update_forward_refs()
FuncDeclNode.update_forward_refs()
FileNode.update_forward_refs()
PackageNode.update_forward_refs()
