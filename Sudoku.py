import copy

def copyOf(some_object):
    return copy.deepcopy(some_object)

class RC:
    """Represent index by row and column"""
    def __init__(self, r, c):
        self.r = r
        self.c = c

    def __str__(self):
        return "RC({0},{1})".format(self.r, self.c)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, RC):
            return False
        return self.r == other.r and self.c == other.c

    def __hash__(self):
        return self.r + 10 * self.c

class Board:
    def __init__(self):
        self.board = [[None for c in range(9)] for r in range(9)]

    def __getitem__(self, index):
        if isinstance(index, RC):
            return self.board[index.r][index.c]
        elif isinstance(index, int):
            return self.board[index]

    def __setitem__(self, key: RC, value):
        self.board[key.r][key.c] = value

    @staticmethod
    def neighbours(rc: RC):
        res = set([RC(rc.r, i) for i in range(9)])     # row
        res.update([RC(i, rc.c) for i in range(9)])     # column
        res.update(Board.box_within(rc))    # box
        res.remove(rc)
        return res

    @staticmethod
    def row_within(rc: RC):
        return [RC(rc.r, i) for i in range(9)]

    @staticmethod
    def column_within(rc: RC):
        return [RC(i, rc.c) for i in range(9)]

    @staticmethod
    def box_within(rc: RC):
        rc_box_num = RC(rc.r // 3, rc.c // 3)
        box_corner = RC(3 * rc_box_num.r, rc_box_num.c * 3)
        return [RC(box_corner.r + i, box_corner.c + j) for i in range(3) for j in range(3)]

class NumsForPosition():
    def __init__(self):
        super().__init__()
        self.board = Board()
        self.possible = True
        self.implication = dict()
        for r in range(9):
            for c in range(9):
                rc = RC(r, c)
                self.board[rc] = [i for i in range(1, 10)]

    def positions_for_num_in_unit(self, num: int, unit):
        return [rc for rc in unit if num in self.board[rc]]

    def __setitem__(self, key: RC, value: int):
        if value not in self.board[key]:
            self.possible = False
            return

        # Remove value from neighbours
        for neighbour_rc in Board.neighbours(key):
            self.remove_val(neighbour_rc, value)

        # Remove other values from key
        for other_val in self.board[key]:
            if other_val != value:
                self.remove_val(key, other_val)

        # Remove value from key
        self.board[key] = []
        del self.implication[key]

    def remove_val(self, rc: RC, value: int):
        if value not in self.board[rc]:
            return
        self.board[rc].remove(value)

        if len(self.board[rc]) == 0:
            self.possible = False
            return
        if len(self.board[rc]) == 1:
            self.implication[rc] = self.board[rc][0]

        for unit in [Board.row_within(rc), Board.column_within(rc), Board.box_within(rc)]:
            unit_options = self.positions_for_num_in_unit(value, unit)
            if len(unit_options) == 0:
                self.possible = False
                return
            if len(unit_options) == 1:
                self.implication[unit_options[0]] = value

    """Find the cell with the minimum number of options"""
    def shortest(self):
        shortest_rc = None
        shortest_length = 9
        for i in range(9):
            for j in range(9):
                rc = RC(i, j)
                if len(self.board[rc]) < shortest_length and len(self.board[rc]) >= 2:
                    shortest_length = len(self.board[rc])
                    shortest_rc = RC(i, j)
        return shortest_rc, self.board[shortest_rc]

class Sudoku:
    def __init__(self):
        # List of possible values for each cell in the board
        self.options = NumsForPosition()
        # List of values already selected
        self.result = Board()
        # The number of values already selected
        self.counter = 0

    def set_board(self, board: Board):
        for r in range(9):
            for c in range(9):
                rc = RC(r, c)
                num = board[rc]
                if num != 0:
                    self[rc] = num

    def __setitem__(self, key: RC, value: int):
        self.options[key] = value
        self.result[key] = value
        self.counter += 1

    def possible(self):
        return self.options.possible

    def has_next(self):
        return len(self.options.implication) > 0

    def set_next(self):
        next_step = next((x, self.options.implication[x]) for x in self.options.implication)
        self[next_step[0]] = next_step[1]

    def is_solved(self):
        return self.counter == 81


class BFS:
    class Node:
        def __init__(self, sudoku, rc):
            self.sudoku = sudoku
            self.rc = rc
            self.current_index = -1

        def optional_values(self):
            return self.sudoku.options.board[self.rc]

        def current_val(self):
            return self.optional_values()[self.current_index]

        def overflow(self):
            return self.current_index >= len(self.optional_values())

    def __init__(self):
        self.stack = list()
        self.current = None

    def last(self):
        return self.stack[-1]

    """Next option in DFS tree"""
    def next(self):
        while len(self.stack) > 0:
            self.last().current_index += 1
            if self.last().overflow():
                self.stack.pop(-1)
            else:
                self.current = copyOf(self.last().sudoku)
                self.current[self.last().rc] = self.last().current_val()
                return True
        return False

    def add_node(self, options, rc):
        self.stack.append(self.Node(copyOf(options), rc))

    def search(self, sudoku):
        self.current = copyOf(sudoku)
        while True:
            if self.current.possible():
                if self.current.has_next():  # The only option
                    self.current.set_next()
                else:
                    shortest_rc, shortest_options = self.current.options.shortest()
                    self.add_node(self.current, shortest_rc)  # Many options, drop level in the search tree
                    self.next()
            else:
                if not self.next():
                    return None     # No solution!

            if self.current.is_solved():
                return self.current.result


"""Example:"""

input = [[3,4,0,0,0,1,0,0,0],
         [0,2,0,0,0,9,0,0,0],
         [0,0,0,5,0,0,0,7,0],
         [0,0,0,0,0,3,1,0,7],
         [6,8,0,0,0,0,3,0,2],
         [0,0,0,0,0,0,0,6,0],
         [0,0,8,0,7,4,0,1,0],
         [0,0,0,0,0,0,0,0,0],
         [0,0,9,0,0,0,6,8,5]]

values_board = Board()
values_board.board = input
sdk = Sudoku()
sdk.set_board(values_board)

bfs = BFS()
solution = bfs.search(sdk)

if solution is None:
    print('No solution!')
else:
    for r in solution.board:
        print(r)
