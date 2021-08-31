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
        res = list()
        # row
        res.extend([RC(rc.r, i) for i in range(9)])
        # column
        res.extend([RC(i, rc.c) for i in range(9)])
        # box
        box_corner = RC(((rc.r)//3)*3, ((rc.c)//3)*3)
        res.extend([RC(box_corner.r + i, box_corner.c + j) for i in range(3) for j in range(3)])
        return set(res)

class Sudoku:
    def __init__(self):
        # List of possible values for each cell in the board
        self.options = Board()
        # List of values already selected
        self.const = Board()
        # The number of values already selected
        self.counter = 0

        for r in range(9):
            for c in range(9):
                rc = RC(r, c)
                self.options[rc] = [i for i in range(1, 10)]
                self.const[rc] = False

    def set_board(self, board: Board):
        for r in range(9):
            for c in range(9):
                rc = RC(r, c)
                num = board[rc]
                if num != 0:
                    self[rc] = num

    def __setitem__(self, key: RC, value: int):
        # For neighbour_rc in self.options.neighbours_rc(key):
        for neighbour_rc in Board.neighbours(key):
            try:
                self.options[neighbour_rc].remove(value)
            except ValueError:
                pass  # do nothing!

        if not self.const[key]:
            self.counter += 1
        self.const[key] = True
        self.options[key] = [value]

    """Find the cell with the minimum number of options"""
    def shortest(self):
        shortest_rc = None
        shortest_length = 9
        for i in range(9):
            for j in range(9):
                rc = RC(i, j)
                if (not self.const[rc]) and len(self.options[rc]) < shortest_length:
                    shortest_length = len(self.options[rc])
                    shortest_rc = RC(i, j)
        return shortest_rc, self.options[shortest_rc]

    def is_solved(self):
        return self.counter == 81

    def to_board(self):
        res = Board()
        res.board = [[self.options[RC(r, c)][0] for c in range(9)] for r in range(9)]
        return res

class BFS:
    class Node:
        def __init__(self, sudoku, rc):
            self.sudoku = sudoku
            self.rc = rc
            self.current_index = -1

        def optional_values(self):
            return self.sudoku.options[self.rc]

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
            shortest_rc, shortest_options = self.current.shortest()
            if len(shortest_options) == 1:  # The only option
                self.current[shortest_rc] = shortest_options[0]
            elif len(shortest_options) == 0:    # No solution
                if not self.next():
                    return None     # No solution!
            else:
                self.add_node(self.current, shortest_rc)    # Many options, drop level in the search tree
                self.next()

            if self.current.is_solved():
                return self.current.to_board()


"""Example:"""

input = [[3,0,0,0,0,0,0,2,0],
         [0,0,0,0,0,0,9,6,4],
         [2,0,8,0,0,0,0,5,0],
         [1,7,0,0,8,0,0,0,0],
         [0,0,0,2,0,0,0,0,7],
         [0,0,0,0,5,0,4,0,0],
         [0,0,9,0,0,0,0,0,0],
         [0,0,6,0,0,4,0,0,5],
         [0,2,0,9,0,6,0,0,0]]

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
