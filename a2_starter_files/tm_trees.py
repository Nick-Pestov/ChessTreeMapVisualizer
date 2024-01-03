"""Assignment 2: Trees for Treemap

=== CSC148 Winter 2023 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: David Liu, Bogdan Simion, Diane Horton, Sophia Huynh, Tom Ginsberg,
Jonathan Calver, Jacqueline Smith, and Misha Schwartz

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 David Liu, Bogdan Simion, Diane Horton, Sophia Huynh,
Jonathan Calver, Jacqueline Smith, and Misha Schwartz

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the TMTree class, and complete implementations
of several subclasses to represent specific types of data.
"""
from __future__ import annotations
import os
import math  # You can remove this math import if you don't end up using it.
from random import randint
from typing import Optional
import webbrowser
import json


# Provided custom error class that you should use where indicated.
class OperationNotSupportedError(Exception):
    """
    Error to indicate that a given operation is not supported.
    """


# used in a DirectoryTree doctest example
DIRECTORYTREE_EXAMPLE_RESULT = """./(47) None
    documents/(24) None
        report.pdf(13) None
        data.xlsx(10) None
    images/(7) None
        vacation/(6) None
            beach.png(5) None
    my_song.mp3(14) None
    empty_dir(1) None""".replace("/", os.path.sep)


########
# Functions
########
def get_worksheet_tree() -> TMTree:
    """
    Return the TMTree that is shown on the worksheet.
    """
    j = TMTree('j', [], 10)
    k = TMTree('k', [], 5)
    e = TMTree('e', [j, k], 5)
    f = TMTree('f', [], 5)
    b = TMTree('b', [e, f], 5)
    g = TMTree('g', [], 4)
    h = TMTree('h', [], 4)
    i = TMTree('i', [], 2)
    c = TMTree('c', [g, h, i], 5)
    d = TMTree('d', [], 10)
    a = TMTree('a', [b, c, d], 5)
    a.update_rectangles((0, 0, 55, 30))
    return a


def path_to_nested_tuple(path: str) -> tuple[str, int | list]:
    """
    Return a nested tuple representing the files and directories rooted at path.

    A file is represented by a tuple consisting of its name and its size.

    A directory is represented by a tuple consisting of its name, and a list
    of tuples representing the files and subdirectories that it contains.

    The size of a file is defined to be 1 + the size of the file as reported by
    the os.path.getsize function.

    Note: depending on your operating system, these file sizes may not be
    *exactly* the same, so this doctest _might_ not pass when run on
    your computer. Please make sure to run the self-tests on MarkUs once they
    are made available to ensure your code is passing the self-tests
    corresponding to this doctest example.
    Reminder: your solution MUST use the provided ordered_listdir helper
              function to ensure consistent ordering and contents of the
              returned list of file and directory names when traversing the
              file system.

    Precondition:
    <path> is a valid path to a FILE or a DIRECTORY.

    >>> path = os.path.join("example-directory", "workshop", "prep")
    >>> rslt = path_to_nested_tuple(path)
    >>> rslt[0]
    'prep'
    >>> rslt[1]
    [('images', [('Cats.pdf', 17)]), ('reading.md', 7)]
    """
    directory = os.path.basename(os.path.normpath(path))
    return _helper_path_to_nested_tuple(directory, path)


def _helper_path_to_nested_tuple(name: str, path: str) -> \
        tuple[str, int | list]:
    """
    Stupid Helper function

    """
    list_file = ordered_listdir(path)
    result = []
    for element in list_file:
        full_path = os.path.join(path, element)
        if os.path.isfile(full_path):
            size = 1 + os.path.getsize(full_path)
            result.append((element, size))
        else:
            result.append(_helper_path_to_nested_tuple(element,
                                                       full_path))
    return name, result


def ordered_listdir(path: str) -> list[str]:
    """
    Return a list of the files and directories of the given <path>.

    Hidden files that start with "." are ignored and
    the returned strings are sorted by filename.

    Precondition:
    <path> is a valid path
    """
    files = (file for file in os.listdir(path) if not file.startswith("."))
    return sorted(files)


def dir_tree_from_nested_tuple(obj: tuple[str, int | list]) -> DirectoryTree:
    """
    Return a DirectoryTree object representing the file system tree structure
    contained in the given nested <obj>.

    Precondition:

    obj represents a valid file system tree structure, with a directory at
    its root. See the path_to_nested_tuple function for details of the format.

    See the DirectoryTree's doctest examples for sample usage.
    """
    return _helper_file_tree(obj)


def _helper_file_tree(silly_object: tuple[str, int | list]) -> \
        FileTree | DirectoryTree:
    """
    Silly function that returns a FileTree or DirectoryTree so that the
    output of the other silly function is satisfied
    """
    if isinstance(silly_object[1], int):
        return FileTree(silly_object[0], [], silly_object[1])
    else:
        lst = []
        for subtree in silly_object[1]:
            lst.append(_helper_file_tree(subtree))

        return DirectoryTree(silly_object[0], lst, 1)


# provided, do not modify this helper function
def url_from_moves(moves: list[str]) -> str:
    """
    Returns a lichess url corresponding to the board position
    specified by the sequence of <moves>.

    Precondition:
    <moves> must be a list of uci formatted strings (e.g. [e2e4, e7e5])

    >>> url_from_moves(['e2e4']).replace('https://lichess.org/analysis/','')
    'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR_b_KQkq_-_0_1'
    """
    import chess
    board = chess.Board()
    for move in moves:
        board.push(chess.Move.from_uci(move))
    url = 'https://lichess.org/analysis/' + board.fen().replace(' ', '_')
    return url


def moves_to_nested_dict(moves: list[list[str]]) -> dict[tuple[str,
int], dict]:
    """
    Convert <games> into a nested dictionary representing the sequence of moves
    made in the games.

    Each list in <games> corresponds to one game, with the i'th str being the
    i'th move of the game.

    The nested dictionary's keys are tuples containing the string representing
    the move made on that turn and an integer indicating how many games ended
    immediately after this move. See the docstring example below.

    The values of each nested dictionary are themselves nested dictionaries of
    this structure. An empty dictionary is stored as the value for a move that
    will correspond to a leaf

    Note: to keep the docstring short, we use single letters in place
          of real chess moves, as it has no impact on the logic of how this
          code needs to be implemented, since it should work for arbitary
          strings used to denote moves.


    >>> moves_to_nested_dict([[]])  # empty lists are ignored
    {}
    >>> moves_to_nested_dict([])
    {}
    >>> moves_to_nested_dict([['a'], []])
    {('a', 1): {}}
    >>> d = moves_to_nested_dict([["a", "b", "c"],
    ...                           ["a", "b"], ["d", "e"], ["d", "e"]])
    >>> d
    {('a', 0): {('b', 1): {('c', 1): {}}}, ('d', 0): {('e', 2): {}}}
    >>> d = moves_to_nested_dict([
    ...    ["a", "b", "c"], ["a", "b"], ["d", "e", "a"], ["d", "e"]])
    >>> d
    {('a', 0): {('b', 1): {('c', 1): {}}}, ('d', 0): {('e', 1): {('a', 1): {}}}}
    """
    d = {}
    m = moves.copy()
    for game in m:
        _helper_add_dict_recursively(d, game)
    return d


def _helper_add_dict_recursively(d: dict, lst: list[str]) -> None:
    """
    Going to create nested dictionaries with branching points
    """
    if len(lst) == 0:
        return None
    keys = d.keys()
    in_keys = False
    for element in keys:
        if element[0] == lst[0]:
            if len(lst) == 1:
                d[(lst[0], element[1] + 1)] = d.pop(element)
                return None
            else:
                lst.pop(0)
                _helper_add_dict_recursively(d[element], lst)
                return None
    if not in_keys:
        if len(lst) == 1:
            d[(lst[0], 1)] = {}
            lst.pop()
        else:
            key = (lst[0], 0)
            lst.pop(0)
            d[key] = {}
            _helper_add_dict_recursively(d[key], lst)
    return None


########
# TMTree and subclasses
########

class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    While this is not an abstract class,
    it should be subclassed to fit the needs of the
    specific data being visualized.

    You may NOT add any attributes, public or private, to this class.

    You can freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization. A pygame rectangle is of the form:
        (x, y, width, height) where (x, y) is the upper, left corner of
        the rectangle.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; that is to say, the tree that contains
        this tree as a subtree, or None if this tree is the root.
    _expanded:
        Whether this tree is considered expanded for visualization.

    Note: this class does not support a representation for an empty tree,
    as we are only interested in visualizing non-empty trees.

    === Representation Invariants ===
    - data_size > 0
    - _name is a non-empty string
    - If _subtrees is not empty, then data_size is greater than or equal to the
    sum of the data_size of each subtree.

    - _colour's elements are each in the range 0-255, inclusive

    - if _parent_tree is not None, then self is in _parent_tree._subtrees
    - if _parent_tree is None, this is a root of a tree (no parent)
    - this tree is the _parent_tree for each tree _subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for **every** subtree
      in _subtrees
    - if _subtrees is empty, then _expanded is False

    See method docstrings for sample usage.
    """

    rect: Optional[tuple[int, int, int, int]]
    data_size: int
    _colour: tuple[int, int, int]
    _name: str
    _subtrees: list[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: list[TMTree],
                 data_size: int = 1) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        This tree's data_size attribute is initialized to be
        the sum of the sizes of its <subtrees> + <data_size>.

        Set this tree as the parent for each of its subtrees.

        The tree is initially expanded, unless it has no subtrees.

        The rect attribute is initially None.

        This tree is initially a root (has no parent).

        Preconditions:
        <name> is a non-empty string
        <data_size> >= 0
        if <subtrees> is empty, then <data_size> > 0
        all trees in <subtrees> are roots (they don't have parents)

        >>> t1 = TMTree('B', [], 5)
        >>> t1.rect is None
        True
        >>> t1.data_size
        5
        >>> t2 = TMTree('A', [t1], 1)
        >>> t2.rect is None
        True
        >>> t2.data_size
        6
        """
        self.rect = None

        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        self._colour = (r, g, b)

        self._name = name
        self._subtrees = subtrees
        self._parent_tree = None

        if len(subtrees) <= 0:
            self._expanded = False
        else:
            self._expanded = True

        tree_sizes = 0
        if self._subtrees:
            for subtree in self._subtrees:
                tree_sizes += subtree.data_size
                subtree._parent_tree = self
        self.data_size = data_size + tree_sizes

    def is_displayed_tree_leaf(self) -> bool:
        """
        Return whether this tree is a leaf in the displayed-tree.

        >>> t1 = TMTree('B', [], 5)
        >>> t1.is_displayed_tree_leaf()
        True
        >>> t2 = TMTree('A', [t1], 1)
        >>> t1.is_displayed_tree_leaf()
        True
        >>> t2.is_displayed_tree_leaf()
        False
        """
        if not self._expanded:
            if self._parent_tree is None:
                return True
            return self._parent_tree._expanded
        return self._subtrees == [] and self._parent_tree._expanded

    # Methods for the string representation
    def get_path_string(self) -> str:
        """
        Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name, and the suffic for this tree at the end. See the following
        doctest examples for the format.

        >>> d1 = TMTree('C1', [], 5)
        >>> d2 = TMTree('C2', [d1], 1)
        >>> d3 = TMTree('C', [d2], 1)
        >>> d3.get_path_string()
        'C(7) None'
        >>> d1.get_path_string()
        'C | C2 | C1(5) None'
        """
        path = ''
        curr = self
        lst = []
        while curr._parent_tree is not None:
            lst.append(curr)
            curr = curr._parent_tree
        lst.append(curr)
        for item in reversed(lst):
            if item == lst[0]:
                path += f'{self._name}{self.get_suffix()}'
            else:
                path += f'{item._name}{item.get_separator()}'
        return path.replace("/", os.path.sep)

    # Note: you may encounter an "R0201 (no self use error)" pyTA error related
    # to this method (and PyCharm might show a warning as well), but it should
    # go away once you finish the assignment.
    def get_separator(self) -> str:
        """
        Return the string used to separate names in the string
        representation of a path from the tree root to this tree.

        Override this method in a subclass if the data has a different
        separator string.

        >>> TMTree('root', []).get_separator()
        ' | '
        """
        return ' | '

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.

        The default implementation is to indicate the size and rect,
        but should be overridden in a subclass if the data has a different
        suffix.

        >>> TMTree('root', []).get_suffix()
        '(1) None'
        """
        return f"({self.data_size}) {self.rect}"

    def __str__(self) -> str:
        """
        Return a string representation of the tree rooted at <self>.

        >>> d1 = TMTree('C1', [], 5)
        >>> d2 = TMTree('C2', [d1], 1)
        >>> d3 = TMTree('C', [d2], 1)
        >>> print(d3)
        C | (7) None
            C2 | (6) None
                C1(5) None
        """
        return self._str_helper().rstrip()  # rstrip removes the trailing '\n'

    def _str_helper(self, indent: int = 0) -> str:
        """
        Recursive helper for __str__
        <indent> specifies the indentation level.

        Refer to __str__ for sample usage.
        """
        tab = "    "  # four spaces
        rslt = f"{indent * tab}{self._name}"
        if self._subtrees:
            rslt += self.get_separator()
        rslt += f"({self.data_size}) {self.rect}\n"
        for subtree in self._subtrees:
            rslt += subtree._str_helper(indent + 1)
        return rslt

    def update_rectangles(self, rect: tuple[int, int, int, int]) -> None:
        """
        Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.

        Note: you don't need to consider the self._expanded attribute here,
              as get_rectangles will take care of only returning the rectangles
              that correspond to leaves in the displayed-tree.

        >>> t1 = TMTree('B', [], 5)
        >>> t2 = TMTree('A', [t1], 1)
        >>> t2.update_rectangles((0, 0, 100, 200))
        >>> t2.rect
        (0, 0, 100, 200)
        >>> t1.rect
        (0, 0, 100, 200)
        >>> s1 = TMTree('C1', [], 5)
        >>> s2 = TMTree('C2', [], 15)
        >>> t3 = TMTree('C', [s1, s2], 1)
        >>> t3.update_rectangles((0, 0, 100, 200))
        >>> s1.rect
        (0, 0, 100, 50)
        >>> s2.rect
        (0, 50, 100, 150)
        >>> t3.rect
        (0, 0, 100, 200)
        >>> s4 = TMTree('C1', [], 5)
        >>> s5 = TMTree('C2', [], 15)
        >>> t2 = TMTree('C', [s4, s5], 1)
        >>> t2.update_rectangles((0, 0, 200, 100))
        >>> s4.rect
        (0, 0, 50, 100)
        >>> s5.rect
        (50, 0, 150, 100)
        >>> t2.rect
        (0, 0, 200, 100)
        """
        if len(self._subtrees) != 0:
            self.rect = rect
            x, y, w, h = rect[0], rect[1], rect[2], rect[3]

            ssum = 0
            for subtree in self._subtrees:
                ssum += subtree.data_size

            if w > h:
                for subtree in self._subtrees:
                    subtree_w = int(math.floor((w * subtree.data_size) / ssum))
                    subtree.rect = (x, y, subtree_w, h)
                    x += subtree_w

                last_w = rect[0] + rect[2] - self._subtrees[-1].rect[0]
                self._subtrees[-1].rect = (self._subtrees[-1].rect[0],
                                           self._subtrees[-1].rect[1],
                                           last_w, self._subtrees[-1].rect[3])
            else:
                for subtree in self._subtrees:
                    subtree_h = int(math.floor((h * subtree.data_size) / ssum))
                    subtree.rect = (x, y, w, subtree_h)
                    y += subtree_h

                last_h = rect[1] + rect[3] - self._subtrees[-1].rect[1]
                self._subtrees[-1].rect = (self._subtrees[-1].rect[0],
                                           self._subtrees[-1].rect[1],
                                           self._subtrees[-1].rect[2], last_h)

            for subtree in self._subtrees:
                subtree.update_rectangles(subtree.rect)
        else:
            self.rect = rect

    def get_rectangles(self) -> list[tuple[tuple[int, int, int, int],
    tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.

        >>> t1 = TMTree('B', [], 5)
        >>> t2 = TMTree('A', [t1], 1)
        >>> t2.update_rectangles((0, 0, 100, 200))
        >>> t2.get_rectangles()[0][0]
        (0, 0, 100, 200)
        >>> s1 = TMTree('C1', [], 5)
        >>> s2 = TMTree('C2', [], 15)
        >>> t3 = TMTree('C', [s1, s2], 1)
        >>> t3.update_rectangles((0, 0, 100, 200))
        >>> rectangles = t3.get_rectangles()
        >>> rectangles[0][0]
        (0, 0, 100, 50)
        >>> rectangles[1][0]
        (0, 50, 100, 150)
        """
        lst = []
        tup = tuple()
        if self._subtrees is None:
            if self.is_displayed_tree_leaf():
                tup = tup + (self.rect,)
                tup = tup + (self._colour,)
                lst.append(tup)
        else:
            lst = []
            if self.is_displayed_tree_leaf():
                tup = tup + (self.rect,)
                tup = tup + (self._colour,)
                lst.append(tup)
            for sub in self._subtrees:
                lst.extend(sub.get_rectangles())
        return lst

    def get_tree_at_position(self, pos: tuple[int, int]) -> Optional[TMTree]:
        """
        Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is first encountered when
        traversing the TMTree in the natural order.

        Preconditions:
        update_rectangles has previously been called on the root of the tree
        that self is part of.

        self is part of the displayed-tree.

        >>> t1 = TMTree('B', [], 5)
        >>> t2 = TMTree('A', [t1], 1)
        >>> t2.update_rectangles((0, 0, 100, 200))
        >>> t1.get_tree_at_position((10, 10)) is t1
        True
        >>> t2.get_tree_at_position((10, 10)) is t1
        True
        >>> t2.get_tree_at_position((500, 500)) is None
        True
        >>> s1 = TMTree('C1', [], 5)
        >>> s2 = TMTree('C2', [], 15)
        >>> t3 = TMTree('C', [s1, s2], 1)
        >>> t3.update_rectangles((0, 0, 100, 200))
        >>> t3.get_tree_at_position((0, 0)) is s1
        True
        >>> t3.get_tree_at_position((100, 100)) is s2
        True
        """
        if not self._subtrees:  # self._subtrees == []
            total_wid = self.rect[0] + self.rect[2]
            total_length = self.rect[1] + self.rect[3]
            if self.rect[0] <= pos[0] <= total_wid and \
                    self.rect[1] <= pos[1] <= total_length:
                return self
            return None
        else:
            possible_item_lst = []
            for subtree_1 in self._subtrees:
                possible_item_lst.append(subtree_1.get_tree_at_position(pos))
            for subtree_2 in possible_item_lst:
                if subtree_2 is not None:
                    return subtree_2
            return None

    def expand(self) -> TMTree:
        """
        Set this tree to be expanded, and return its first (leftmost) subtree.

        But if this tree has no subtrees, do nothing (since a leaf can't
        be expanded), and return self.

        Precondition:
        self is part of the displayed-tree

        Note: for simplicity, we directly mutate the _expanded attribute for
        this doctest example.

        >>> s1 = TMTree('C1', [], 5)
        >>> s2 = TMTree('C2', [], 15)
        >>> t3 = TMTree('C', [s1, s2], 1)
        >>> t3._expanded = False
        >>> s1.is_displayed_tree_leaf()
        False
        >>> t3.expand() is s1
        True
        >>> s1.is_displayed_tree_leaf()
        True
        """
        if not self._subtrees:
            return self
        else:
            self._expanded = True
            curr = self
            while curr._parent_tree is not None:
                curr._expanded = True
                curr = curr._parent_tree
            return self._subtrees[0]

    def expand_all(self) -> TMTree:
        """
        Fully expand this TMTree and ALL of its subtrees.

        Return the "last" TMTree. By "last", we mean the rightmost subtree of
        the last TMTree that is expanded when we traverse the TMTree in the
        usual "for subtree in self._subtrees" order.

        If self has no subtrees, return self.

        Precondition:
        self is a part of the displayed-tree

        Note: for simplicity, we directly mutate the _expanded attribute for
        this doctest example.

        >>> d1 = TMTree('C1', [], 5)
        >>> d2 = TMTree('C2', [d1], 1)
        >>> d3 = TMTree('C', [d2], 1)
        >>> d3._expanded = False
        >>> d2._expanded = False
        >>> d1.is_displayed_tree_leaf()
        False
        >>> d2.is_displayed_tree_leaf()
        False
        >>> d3.expand_all() is d1
        True
        >>> d1.is_displayed_tree_leaf()
        True
        >>> d2.is_displayed_tree_leaf()
        False
        """
        if not self._subtrees:
            return self
        else:
            lst = []
            self._expanded = True
            for sub in self._subtrees:
                lst.append(sub.expand_all())
            return lst[-1]

    def collapse(self) -> TMTree:
        """
        Remove self from the displayed-tree and return self's parent.

        If this node is the root of the whole tree, do nothing and return self.

        Hint: removing self from the displayed-tree requires setting its
              parent's _expanded attribute to False, so make sure to fix any
              other _expanded attributes that now violate our RIs.

        Precondition:
        self is a leaf of the displayed-tree


        >>> d1 = TMTree('C1', [], 5)
        >>> d2 = TMTree('C2', [d1], 1)
        >>> d1.is_displayed_tree_leaf()
        True
        >>> d2.is_displayed_tree_leaf()
        False
        >>> d1.collapse() is d2
        True
        >>> d1.is_displayed_tree_leaf()
        False
        >>> d2.is_displayed_tree_leaf()
        True
        """
        if self._parent_tree is None:
            return self
        else:
            self._parent_tree._expanded = False
            subtrees_lst = self._parent_tree._subtrees
            for subtree in subtrees_lst:
                subtree._expanded = False
            return self._parent_tree

    def _get_root(self) -> TMTree:
        """
        Not sure if this exists yet, but we'll be able to get access to the
        biggest bird in the code
        """
        if self._parent_tree is None:  # must write 'is None' or it'll be wrong
            return self
        else:
            return self._parent_tree._get_root()

    def _expanded_false(self) -> None:
        """
        recursive private method used for collapse, that iterates through all
        the children of self, and set's the self._expanded attribute to False
        """
        self._expanded = False
        if self._subtrees:
            for subtree in self._subtrees:
                subtree._expanded_false()
        return None

    def collapse_all(self) -> TMTree:
        """
        Collapse the entire displayed-tree to a single node (the root).
        Return the root of the tree that self is a part of.

        Precondition:
        self is a leaf of the displayed-tree

        >>> d1 = TMTree('C1', [], 5)
        >>> d2 = TMTree('C2', [d1], 1)
        >>> d3 = TMTree('C', [d2], 1)
        >>> d1.is_displayed_tree_leaf()
        True
        >>> d1.collapse_all() is d3
        True
        >>> d1.is_displayed_tree_leaf()
        False
        >>> d2.is_displayed_tree_leaf()
        False
        >>> d3.is_displayed_tree_leaf()
        True
        """
        root = self._get_root()
        root._expanded_false()
        return root

    def move(self, destination: TMTree) -> None:
        """
        Move this tree to be the last subtree of <destination>.

        Note: Be sure to fix any violations of RIs that might result from
        your mutations. For example, be careful not to violate any RIs related
        to the _expanded attribute of any TMTree objects that you modify.

        Importantly, this method must:

        1. Appropriately update the data_size attribute of ALL
        TMTrees whose size changes as a result of this change.

        2. Reapply the treemap algorithm to the root of the tree that self is
        a part of to update the rect attributes to reflect the new tree
        structure. Use the root's current rect attribute as the
        starting rectangle for the treemap algorithm.

        3. Expand self's new parent so that self remains a leaf in the
        displayed-tree (self's new parent will no longer be a leaf in the
        displayed-tree)

        Preconditions:
        both self and destination are leaves in the displayed-tree

        self is not destination (note, this and the above precondition together
        will also mean that neither self nor destination can be the root of
        the tree)

        update_rectangles has previously been called on the root of the tree
        that self is part of.

        Moving self will not result in self's parent having a data size of zero.
        This last condition is to ensure we don't accidentally introduce a data
        size of 0 into our tree structure when self is moved.
        Note: the visualizer will violate this last precondition if you try to
        make such a move, but we of course won't when testing your code.

        >>> s1 = TMTree('C1', [], 5)
        >>> s2 = TMTree('C2', [], 15)
        >>> t3 = TMTree('C', [s1, s2], 1)
        >>> t3.update_rectangles((0, 0, 100, 200))
        >>> s1.is_displayed_tree_leaf()
        True
        >>> s2.is_displayed_tree_leaf()
        True
        >>> s2.move(s1)
        >>> s2.rect
        (0, 0, 100, 200)
        >>> s1.data_size
        20
        >>> t3.data_size
        21
        >>> t3.get_tree_at_position((0, 0)) is s2
        True
        >>> s1.is_displayed_tree_leaf()
        False
        >>> s2.is_displayed_tree_leaf()
        True
        """
        if self._parent_tree is None:
            size = self.data_size
        else:
            size = self.data_size
            a = self._parent_tree
            while a is not None:
                a.data_size -= size
                a = a._parent_tree
            parent = self._parent_tree
            parent._subtrees.remove(self)
            if len(parent._subtrees) == 0:
                parent._expanded = False

        destination._subtrees.append(self)
        self._parent_tree = destination
        destination._expanded = True
        b = self._parent_tree
        while b is not None:
            b.data_size += size
            b = b._parent_tree
        root = self._get_root()
        self.update_rectangles(root.rect)

    def change_size(self, factor: float) -> None:
        """
        Change the value of this tree's data_size attribute by <factor> of
        its current size.

        If the change results in the data_size being less than the sum of its
        subtree data sizes, then the data_size should be set to the sum of its
        subtree data sizes (the smallest possible value allowed).

        If the change results in the data_size being less
        than 1, the data_size should be set to 1.

        Always "round up" the amount to change, so that it's an int, and ensure
        some change is made.

        Example I: if data_size is 5 and <factor> is
        0.01, the new data_size would be 6. Or if <factor> was -0.01 instead,
        the new data_size would be 4.

        Example II: if data_size is 140, then 1% of this is 1.4,
        which is "rounded up" to 2. So its value could increase up to 142,
        or decrease down to 138.

        Importantly, this method must:

        1. Appropriately update the data_size attribute of ALL
        TMTrees whose size changes as a result of this change.

        2. Reapply the treemap algorithm to the root of the tree that self is
        a part of to update the rect attributes to reflect the updated
        data_size attributes. Use the root's current rect attribute as the
        starting rectangle for the treemap algorithm.

        Precondition:
        <factor> != 0

        self is a leaf of the displayed-tree

        update_rectangles has previously been called on the root of the tree
        that self is part of.

        >>> s1 = TMTree('C1', [], 5)
        >>> s2 = TMTree('C2', [], 15)
        >>> t3 = TMTree('C', [s1, s2], 1)
        >>> t3.update_rectangles((0, 0, 100, 200))
        >>> s2.change_size(-2/3)
        >>> s2.data_size
        5
        >>> t3.data_size
        11
        >>> s2.rect
        (0, 100, 100, 100)
        """
        old_size = self.data_size
        if factor < 0:
            change = int(math.floor(self.data_size * factor))
        else:
            change = int(math.ceil(self.data_size * factor))
        new_size = old_size + change

        subtree_sizes = 0
        for subtree in self._subtrees:
            subtree_sizes += subtree.data_size

        if new_size < subtree_sizes or new_size < 1:
            if subtree_sizes >= 1:
                new_size = subtree_sizes
            else:
                new_size = 1

        self.data_size = new_size

        subtree = self
        while subtree._parent_tree is not None:
            subtree._parent_tree.data_size += change
            subtree = subtree._parent_tree

        subtree.update_rectangles(subtree.rect)


######################
# subclasses of TMTree
######################

class FileTree(TMTree):
    """
    A tree representation of a file in a file system, for use with our
    treemap visualizer.

    Importantly, this class and DirectoryTree do not fully function as a
    representation of a file system. For example, when "moving" files and
    directories, one is still restricted to only moving leaves of the
    displayed-tree.

    The _name attribute stores the *name* of the file, not its full
    path.

    See the class docstring for DirectoryTree for detailed doctest examples
    demonstrating the expected behaviour.

    Important: Since you are free to implement these subclasses, we will only
         create instances of them through calls to
         dir_tree_from_nested_tuple, so please make sure to implement
         that function correctly.
    """
    # Hint: you should only have to write a fairly small amount of code here.
    def __init__(self, name: str, subtrees: list[TMTree], datasize: int) -> \
            None:
        super().__init__(name, subtrees, datasize)

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.

        The default implementation is to indicate the size and rect,
        but should be overridden in a subclass if the data has a different
        suffix.

        >>> TMTree('root', []).get_suffix()
        '(1) None'
        """
        return " (file)"

    def get_separator(self) -> str:
        """
        Return the string used to separate names in the string
        representation of a path from the tree root to this tree.

        Override this method in a subclass if the data has a different
        separator string.
        """
        return os.path.sep

    def move(self, destination: TMTree) -> None:
        """
            Move this tree to be the last subtree of <destination>.

            Note: Be sure to fix any violations of RIs that might result from
            your mutations. For example, be careful not to violate any RIs
            related to the _expanded attribute of any TMTree objects that you
            modify.

            Importantly, this method must:

            1. Appropriately update the data_size attribute of ALL
            TMTrees whose size changes as a result of this change.

            2. Reapply the treemap algorithm to the root of the tree that self
            is a part of to update the rect attributes to reflect the new tree
            structure. Use the root's current rect attribute as the
            starting rectangle for the treemap algorithm.

            3. Expand self's new parent so that self remains a leaf in the
            displayed-tree (self's new parent will no longer be a leaf in the
            displayed-tree)

            Preconditions:
            both self and destination are leaves in the displayed-tree

            self is not destination (note, this and the above precondition
            together will also mean that neither self nor destination can be the
            root of the tree)

            update_rectangles has previously been called on the root of the tree
            that self is part of.

            Moving self will not result in self's parent having a data size of
            zero. This last condition is to ensure we don't accidentally
            introduce a data size of 0 into our tree structure when self is
            moved.
            Note: the visualizer will violate this last precondition if you try
            to make such a move, but we of course won't when testing your code.

            >>> s1 = TMTree('C1', [], 5)
            >>> s2 = TMTree('C2', [], 15)
            >>> t3 = TMTree('C', [s1, s2], 1)
            >>> t3.update_rectangles((0, 0, 100, 200))
            >>> s1.is_displayed_tree_leaf()
            True
            >>> s2.is_displayed_tree_leaf()
            True
            >>> s2.move(s1)
            >>> s2.rect
            (0, 0, 100, 200)
            >>> s1.data_size
            20
            >>> t3.data_size
            21
            >>> t3.get_tree_at_position((0, 0)) is s2
            True
            >>> s1.is_displayed_tree_leaf()
            False
            >>> s2.is_displayed_tree_leaf()
            True
            """
        if isinstance(destination, FileTree):
            raise OperationNotSupportedError
        else:
            TMTree.move(self, destination)


class DirectoryTree(TMTree):
    """A tree representation of a directory in a file system for use with
    our treemap visualizer.

    The _name attribute stores the *name* of the directory, not its full
    path.


    A tree representation of a file in a file system, for use with our
    treemap visualizer.

    Importantly, this class and DirectoryTree do not fully function as a
    representation of a file system. For example, when "moving" files and
    directories, one is still restricted to only moving leaves of the
    displayed-tree.

    The _name attribute stores the *name* of the file, not its full
    path.

    Important: Since you are free to implement these subclasses, we will only
         create instances of them through calls to
         dir_tree_from_nested_tuple, so please make sure to implement
         that function correctly.

    See the doctest demonstrating the expected behaviour, and refer to the
    handout to ensure that your classes provide the required functionality.


    >>> my_dir = dir_tree_from_nested_tuple((
    ...     (".", [
    ...         ("documents", [("report.pdf", 13), ("data.xlsx", 10)]),
    ...         ("images", [("vacation", [("beach.png", 5)])]),
    ...         ("my_song.mp3", 14),
    ...         ("empty_dir", [])
    ...     ])
    ... ))
    >>> my_dir.data_size
    47
    >>> len(my_dir._subtrees)
    4
    >>> documents = my_dir._subtrees[0]
    >>> isinstance(documents, DirectoryTree)
    True
    >>> isinstance(documents, TMTree)
    True
    >>> images = my_dir._subtrees[1]
    >>> empty_dir = my_dir._subtrees[3]
    >>> report_file = documents._subtrees[0]
    >>> data_file = documents._subtrees[1]
    >>> isinstance(data_file, FileTree)
    True
    >>> isinstance(data_file, TMTree)
    True
    >>> documents.data_size
    24
    >>> images.data_size
    7
    >>> str(my_dir) == DIRECTORYTREE_EXAMPLE_RESULT
    True
    >>> path_string = documents.get_path_string()
    >>> path_string == './documents (directory)'.replace("/", os.path.sep)
    True
    >>> path_string = data_file.get_path_string()
    >>> path_string == './documents/data.xlsx (file)'.replace("/", os.path.sep)
    True
    >>> my_dir.update_rectangles((0, 0, 200, 400))  # call update before move.
    >>> try:
    ...     data_file.move(report_file)  # can't because report is not a dir
    ...     raised_error = False
    ... except OperationNotSupportedError:
    ...     raised_error = True
    >>> raised_error
    True
    >>> path_string = data_file.get_path_string()
    >>> path_string == './documents/data.xlsx (file)'.replace("/", os.path.sep)
    True
    >>> data_file.move(empty_dir)  # can move; empty_dir is a leaf and directory
    >>> path_string = data_file.get_path_string()
    >>> path_string == './empty_dir/data.xlsx (file)'.replace("/", os.path.sep)
    True
    """
    def __init__(self, name: str, subtrees: list[TMTree], datasize: int) -> \
            None:
        super().__init__(name, subtrees, datasize)

    def change_size(self, factor: float) -> None:
        raise OperationNotSupportedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.

        The default implementation is to indicate the size and rect,
        but should be overridden in a subclass if the data has a different
        suffix.

        >>> TMTree('root', []).get_suffix()
        '(1) None'
        """
        return " (directory)"

    def get_separator(self) -> str:
        """
        Return the string used to separate names in the string
        representation of a path from the tree root to this tree.

        Override this method in a subclass if the data has a different
        separator string.
        """
        return os.path.sep

    def move(self, destination: TMTree) -> None:
        """
            Move this tree to be the last subtree of <destination>.

            Note: Be sure to fix any violations of RIs that might result from
            your mutations. For example, be careful not to violate any RIs
            related to the _expanded attribute of any TMTree objects that you
            modify.

            Importantly, this method must:

            1. Appropriately update the data_size attribute of ALL
            TMTrees whose size changes as a result of this change.

            2. Reapply the treemap algorithm to the root of the tree that self
            is a part of to update the rect attributes to reflect the new tree
            structure. Use the root's current rect attribute as the
            starting rectangle for the treemap algorithm.

            3. Expand self's new parent so that self remains a leaf in the
            displayed-tree (self's new parent will no longer be a leaf in the
            displayed-tree)

            Preconditions:
            both self and destination are leaves in the displayed-tree

            self is not destination (note, this and the above precondition
            together will also mean that neither self nor destination can be the
            root of the tree)

            update_rectangles has previously been called on the root of the tree
            that self is part of.

            Moving self will not result in self's parent having a data size of
            zero.
            This last condition is to ensure we don't accidentally introduce a
            data size of 0 into our tree structure when self is moved.
            Note: the visualizer will violate this last precondition if you try
            to make such a move, but we of course won't when testing your code.

            >>> s1 = TMTree('C1', [], 5)
            >>> s2 = TMTree('C2', [], 15)
            >>> t3 = TMTree('C', [s1, s2], 1)
            >>> t3.update_rectangles((0, 0, 100, 200))
            >>> s1.is_displayed_tree_leaf()
            True
            >>> s2.is_displayed_tree_leaf()
            True
            >>> s2.move(s1)
            >>> s2.rect
            (0, 0, 100, 200)
            >>> s1.data_size
            20
            >>> t3.data_size
            21
            >>> t3.get_tree_at_position((0, 0)) is s2
            True
            >>> s1.is_displayed_tree_leaf()
            False
            >>> s2.is_displayed_tree_leaf()
            True
            """
        if isinstance(destination, FileTree):
            raise OperationNotSupportedError
        else:
            TMTree.move(self, destination)


class ChessTree(TMTree):
    """
    A chess tree representing sequences of moves in a collection of chess games
    """
    # === Private Attributes ===
    # _white_to_play: True iff it is white's turn to make the next move.

    _white_to_play: bool

    def __init__(self, move_dict: dict[tuple[str, int], dict],
                 last_move: str = "-",
                 white_to_play: bool = True,
                 num_games_ended: int = 0) -> None:
        """
        Initialize this ChessTree given the nested <move_dict>. See the
        moves_to_nested_dict function for the exact format of <move_dict>.

        <last_move> represents the move that was last played. The root of the
        tree has a last move of '-' (default parameter value).

        <white_to_play> indicates where it is white's turn (True) or black's
        turn (False).

        <num_games_ended> indicates how many games ended after the sequence of
        moves corresponding to this ChessTree. Note, this quantity is zero by
        default and, when creating subtrees, should be set based on the int
        from the tuple-keys of <move_dict>.

        Preconditions:
        <move_dict> contains a valid representation of a ChessTree.
        <last_move> is a non-empty string.
        <num_games_ended> > 0 if the resulting ChessTree will be a leaf,
        since at least one game must have ended for it to be a leaf.

        >>> ct = ChessTree({('e2e4', 0) : {('e7e5', 1) : {}}})
        >>> ct.is_displayed_tree_leaf()
        False
        >>> ct.data_size
        1
        >>> ct.rect is None
        True
        >>> print(ct)
        - | (1) None
            e2e4 | (1) None
                e7e5(1) None
        """
        self._white_to_play = white_to_play

        lst = []

        for line in move_dict.keys():
            if not self._white_to_play:
                lst.append(ChessTree(move_dict[line], line[0], True, line[1]))
            else:
                lst.append(ChessTree(move_dict[line], line[0], False, line[1]))

        TMTree.__init__(self, last_move, lst, num_games_ended)

    def get_suffix(self) -> str:
        """
        Return ' (white to play)' if white is next to move,
        ' (black to play)' if black is next to move
        and ' (end)' if this ChessTree has no subtrees.

        >>> ct = ChessTree({('e2e4', 0) : {('e7e5', 1) : {}}})
        >>> ct.get_suffix()
        ' (white to play)'
        >>> last_node = ct.expand_all()
        >>> last_node.get_suffix()
        ' (end)'
        >>> second_last_node = last_node.collapse()
        >>> second_last_node.get_suffix()
        ' (black to play)'
        """
        if not self._subtrees:
            return ' (end)'
        if self._white_to_play:
            return ' (white to play)'
        else:
            return ' (black to play)'

    def open_page(self) -> None:
        """
        Provided code.
        Open a web browser to a lichess url corresponding
        to the board state of this tree.

        Example usage will open a webpage, so it is commented out
        to avoid the webpage popping up if you like to run all doctests as
        you write your code.

        # >>> ct = ChessTree({('e2e4', 1): {}})
        # >>> ct.open_page()  # will open an analysis board with no moves made
        """
        path = self.get_path_string()
        path = path.split(self.get_separator())[1:]
        if not path:
            moves = []
        else:
            path[-1] = path[-1].split(" ")[0]
            moves = path
        print(f'Opening game after moves: {"-".join(moves)}')
        webbrowser.open(url_from_moves(moves))


if __name__ == '__main__':
    run_pyta = True  # set this to True to run pyTA!
    if run_pyta:
        import python_ta

        python_ta.check_all(config={
            'allowed-import-modules': [
                'python_ta', 'typing', 'math', 'random', 'os', '__future__',
                'webbrowser', 'json', 'chess'
            ],
            'disable': ['C0302',  # disable max module length
                        'C0415'  # disable import-outside-toplevel for chess
                        ],
            'allowed-io': ['ChessTree.open_page']
        })

    # this should run after you finish Task 1
    print("Very small TMTree example")
    s1 = TMTree('C1', [], 5)
    s2 = TMTree('C2', [], 15)
    t3 = TMTree('C', [s1, s2], 1)
    # after you finish task 2, the rectangles should be updated properly
    # and no longer be all None
    t3.update_rectangles((0, 0, 100, 200))
    print(t3)

    print("\n\nWorksheet TMTree example")
    worksheet_tree = get_worksheet_tree()
    print(worksheet_tree)

    print('=' * 80)
    # this should run after you finish Task 1
    nested_tuple = path_to_nested_tuple("example-directory")
    tree = dir_tree_from_nested_tuple(nested_tuple)
    # after you finish task 2, the rectangles should be updated properly
    # and no longer be all None
    tree.update_rectangles((0, 0, 100, 200))
    print(tree)

    print('=' * 80)

    # this should run after you finish Task 6
    with open('wgm_10.json', 'r') as game_file:
        GAME_LIST = json.load(game_file)
    games = moves_to_nested_dict(GAME_LIST)
    tree = ChessTree(games)
    # this tree will be quite large, so rather than printing the whole thing,
    # we can expand_all and print the path of the "last" tree as a simple check.
    print(tree.expand_all().get_path_string())
