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
        if self.count==len(self.cells):
            return self.cells
        return set()
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count==0:
            return self.cells
        return set()
        raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count=self.count-1
        else:
            return None


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            return None




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
        neighbours=set()
        i=cell[0]
        j=cell[1]
        for m in range(i-1,i+2):
            for n in range(j-1,j+2):
                if (m==i and n==j) or (m<0) or (n<0) or (m>=self.height) or (n>=self.width) :
                    continue
                else:
                    if (m,n) in self.mines:
                        count=count-1
                    elif (m,n) not in self.safes:
                        neighbours.add((m,n))
        if neighbours:
            new_sentence=Sentence(neighbours,count)    
            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence)
        
        possible_inference=True
        while possible_inference:
            possible_inference=False
            for i,sentence in enumerate(self.knowledge.copy()):

                if cell in sentence.cells:
                    sentence.cells.remove(cell)
                    possible_inference=True

                if not sentence.cells:
                    self.knowledge.remove(sentence)
                                    

                for block in sentence.known_mines().copy():
                    self.mark_mine(block)
                    possible_inference=True
                for block in sentence.known_safes().copy():
                    self.mark_safe(block)
                    possible_inference=True



            infered_sentences=[]
            for i,sentence in enumerate(self.knowledge):
                for following in self.knowledge[i+1:]:
                    if following.cells < sentence.cells:
                        new_cells=sentence.cells-following.cells
                        new_count=sentence.count-following.count
                        if new_cells:
                            infered_sentences.append(Sentence(new_cells,new_count))

                    if sentence.cells < following.cells:
                        new_cells=following.cells-sentence.cells
                        new_count=following.count-sentence.count
                        if new_cells:
                            infered_sentences.append(Sentence(new_cells,new_count))

            for s in infered_sentences:
                if s not in self.knowledge:
                    possible_inference=True
                    self.knowledge.append(s)            
                        

        


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for sentence in self.knowledge:
            print(sentence)
        print("\n")
        if self.safes:
            for m in self.safes:
                if m not in self.moves_made:
                    return m
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        while True:
            (i,j)=random.randint(0,self.height-1),random.randint(0,self.width-1)
            if (i,j) in self.moves_made or  (i,j) in self.mines:
                (i,j)=random.randint(0,self.height-1),random.randint(0,self.width-1)
            if (i,j) not in self.moves_made and (i,j) not in self.mines:
                return (i,j)

        raise NotImplementedError
