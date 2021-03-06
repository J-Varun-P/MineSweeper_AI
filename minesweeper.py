import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells
        #raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        #raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        #raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        #raise NotImplementedError


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)
        self.mark_safe(cell)

        for y in self.safes:
            for x in self.knowledge:
                x.mark_safe(y)

        neighbor_cells = set()
        for i in range(-1,2):
            for j in range(-1,2):
                if cell[0]+i >= 0 and cell[0]+i < self.height:
                    if cell[1]+j >= 0 and cell[1]+j < self.width:
                        if (i+cell[0],j+cell[1]) != cell:
                            neighbor_cells.add((i+cell[0],j+cell[1]))
        sentence = Sentence(neighbor_cells, count)
        self.knowledge.append(sentence)

        check = 1
        while(check == 1):
            check = 0
            for i in range(len(self.knowledge)-1):
                for j in range(i+1,len(self.knowledge)):
                    x = self.knowledge[i]
                    y = self.knowledge[j]
                    if len(x.cells) != 0 and len(y.cells) != 0:
                        if x.cells.issubset(y.cells):
                            check = 1
                            y.cells = y.cells - x.cells
                            y.count = y.count - x.count
                        if y.cells.issubset(x.cells):
                            check = 1
                            x.cells = x.cells - y.cells
                            x.count = x.count - y.count


        check = 1
        while(check == 1):
            check = 0
            for i in self.knowledge:
                if i.count == 0:
                    if len(i.cells) != 0:
                        check = 1
                        temp = []
                        for j in i.cells:
                            temp.append(j)
                        for j in temp:
                            self.mark_safe(j)
                if i.count == len(i.cells):
                    if len(i.cells) != 0:
                        check = 1
                        temp = []
                        for j in i.cells:
                            temp.append(j)
                        for j in temp:
                            self.mark_mine(j)

        for i in self.knowledge:
            for j in self.safes:
                if j in i.cells:
                    i.mark_safe(j)
            for j in self.mines:
                if j in i.cells:
                    i.mark_mine(j)


        #raise NotImplementedError

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for i in self.safes:
            if i not in self.moves_made:
                return i
        return None
        #raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.moves_made) == 56:
            return None
        while True:
            i = random.randint(0,7)
            j = random.randint(0,7)
            if (i,j) not in self.moves_made:
                if (i,j) not in self.mines:
                    return (i,j)
        #raise NotImplementedError
