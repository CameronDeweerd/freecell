from graphics import *
import random
import time

test = False # change this to true to turn off the shuffling and make an easy win possible

width_window = 1000
height_window = 750
win = GraphWin("Freecell", width_window, height_window)

# list of the dimensions
border = 20
width_cell=70
height_cell=40

x_space_cell=int(((width_window - 2*border)/8 - width_cell)/2)
y_space_cell=5

class card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.width = width_cell
        self.height = height_cell
        self.drawing = ""
        self.drawntext = ""

class location:
    def __init__(self, column, row):
        self.column = column
        self.row = row
        self.card = ""
        self.drawing =""

#format is: board_slot[row][column]
board_slot = [[location(i,j) for i in range(8)] for j in range(18)]
free_slot = [location(i,"F") for i in range(4)] # column number should be 0 to 3
goal_slot = [location(i,"G") for i in range(4,8)] # column number should be 4 to 7

#random.seed(a=None, version=2)
random.seed()

def main():

    new_game()
    win=create_window()
    board()
    draw_board()

    while(True):
        click = win.getMouse() # Pause to view result
        check_clicked(click)

    win.close()    # Close window when done

#emptys the board, freecells, and goalcells
def new_game():

    card_values = [" 1", " 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9", "10", "11", "12", "13"]
    card_suits = ["H", "C", "D", "S"]

    # Delete cards in goal/free cells
    for i in range(4):
        free_slot[i].card=""
        goal_slot[i].card = card(" 0", card_suits[i])

    # Delete all previous cards from board slots
    for i in range(len(board_slot)):
        for j in range(len(board_slot[0])):
            board_slot[i][j].card=""

    # Create a deck and randomize the cards positions
    deck = []
    for value in reversed(card_values):
        for suit in card_suits:
            deck.append(card(value,suit))
    if not test:
        random.shuffle(deck)

    #put cards into array -> 8 columns wide, 7 or 6 cards per column
    for i in range(len(deck)):
        board_slot[i//8][i % 8].card = deck[i]

#Find an open spot for the card and move if its legal
def move_card_logic(clicked_location):

    clicked_card = clicked_location.card

    ###exit if empty slot is selected
    if clicked_location.card == "":
        return

    ###only continue if the card is in an ordered stack
    if not isordered(clicked_location):
        return

    ###count freecells/empty space and ensure enough space to move
    if isinstance(clicked_location.row, int):   #don't check when it's a freecell that was clicked on
        bottom_most_slot = find_empty_location(board_slot[0][clicked_location.column])
        if (bottom_most_slot.row - clicked_location.row) > largest_move():
            return


    moved=False
    ###Check if can go in goal pile
    #get value on card pile and compare to current card
    for j in range(4):
        if int(clicked_location.card.value) == int(goal_slot[j].card.value) + 1 and clicked_location.card.suit == goal_slot[j].card.suit:
            move_drawing(goal_slot[j], clicked_location.card)
            if not goal_slot[j].card.drawing == "":
                goal_slot[j].card.drawing.undraw()
                goal_slot[j].card.drawntext.undraw()
            goal_slot[j].card = clicked_location.card
            clicked_location.card = ""
            moved = True
            break

    if not moved:
        ###Check if can go on a card in another column
        #find bottom card of column
        for j in range(8):
            bottom_most_slot = find_empty_location(board_slot[0][j])
            bottom_most_slot = int(bottom_most_slot.row)

            #get value on card pile and compare to current card
            if bottom_most_slot == 0:
                stackable = True
            else:
                stackable = compare_card(board_slot[bottom_most_slot-1][j].card, clicked_location.card)

            #move stack to first empty spot
            if stackable:
                move_drawing(board_slot[bottom_most_slot][j], clicked_location.card)
                '''TODO make the whole stack move'''
                board_slot[bottom_most_slot][j].card = clicked_location.card
                clicked_location.card = ""
                moved=True
                break


    if not moved:
        ###Check if there is room in the free cells'''
        for j in range(4):
            if free_slot[j].card == "":
                move_drawing(free_slot[j], clicked_location.card)
                free_slot[j].card = clicked_location.card
                clicked_location.card = ""
                moved = True
                break
            
    check_victory()
    board()
    return

#outputs the first empty location in column
def find_empty_location(location):

    if location.card =="":
        return location
    else:
        location = find_empty_location(transpose(location,1,0))
        return location

# compares two cards on the board and returns true if the clicked card can stack.
def compare_card(upper_card, lower_card):

    #compare values
    if (int(upper_card.value) == int(lower_card.value) + 1):

        #compare suits
        if (lower_card.suit == "H" or lower_card.suit == "D") and (upper_card.suit == "C" or upper_card.suit == "S"):
            return True
        elif (lower_card.suit == "C" or lower_card.suit == "S") and (upper_card.suit == "H" or upper_card.suit == "D"):
            return True
        else:
            return False
    else:
        return False

#helper function to look up/down/left/right
def transpose(location, down, right):
    return board_slot[location.row+down][location.column+right]

# looks down the column and finds out if the card/column is moveable'''
def isordered(clicked_location):

    #freecells are ordered by default
    if clicked_location.row =="F":
        return True

    below = transpose(clicked_location,1,0)
    if below.card =="":
        return True
    elif compare_card(clicked_location.card, below.card):
        return isordered(below)
    else:
        return False

# calculate the largest stack that can be moved at once
def largest_move():

    '''TODO allow for moving multiple cards
    free = 0
    empty = 0
    for j in range(8):
        if board_slot[0][j].card == "":
            empty += 1

    for j in range(4):
        if free_slot[j].card == "":
            free += 1

    return (free + 1) * (2**empty)
    '''
    return 1

# TODO end game screen when victory achieved
def check_victory():

    #check if all kings; else display victory
    for i in range(4):
        if not int(goal_slot[i].card.value) == 13:
            return
        
    print("YOU WIN!")
    win.close()

#make the window and the backgrounds of the free/goal cells
def create_window():

    win.setBackground("green")

    # initilize  the locations
    cell=[Rectangle(Point(0,0), Point(0,0))] * 4
    cell_Card=[Rectangle(Point(0,0), Point(0,0))] * 4
    goal=[Rectangle(Point(0,0), Point(0,0))] * 4
    goal_Card=[Rectangle(Point(0,0), Point(0,0))] * 4


    # draw the Freecells
    for i in range(4):
        x1 = border + (2*x_space_cell + width_cell) * i
        x2 = border + (2*x_space_cell + width_cell) * (i+1)
        y1 = border
        y2 = border + (2*y_space_cell + height_cell)
        cell[i] = Rectangle(Point(x1,y1), Point(x2, y2))
        cell[i].draw(win).setFill('orange')


    # draw the Goalcells
    for i in range(4):
        x1 = width_window - (border + (2*x_space_cell + width_cell) * i)
        x2 = width_window - (border + (2*x_space_cell + width_cell) * (i+1))
        y1 = border
        y2 = border + (2*y_space_cell + height_cell)
        goal[i] = Rectangle(Point(x1,y1), Point(x2, y2))
        goal[i].draw(win).setFill('blue')

    '''
    # draw the Freecell Cards
    for i in range(4):
        x1 = border + x_space_cell + (2*x_space_cell + width_cell) * i
        x2 = border + x_space_cell + (2*x_space_cell + width_cell) * i + width_cell
        y1 = border + y_space_cell
        y2 = border + y_space_cell + height_cell
        cell_Card[i] = Rectangle(Point(x1,y1), Point(x2, y2))
        cell_Card[i].draw(win).setFill('white')

    # draw the goalcells
    for i in range(4):
        x1 = width_window - (border + x_space_cell + (2*x_space_cell + width_cell) * i)
        x2 = width_window - (border + x_space_cell + (2*x_space_cell + width_cell) * i + width_cell)
        y1 = border + y_space_cell
        y2 = border + y_space_cell + height_cell
        goal_Card[i] = Rectangle(Point(x1,y1), Point(x2, y2))
        goal_Card[i].draw(win).setFill('white')
    '''

    return win

# returns true if a point is within a given polygon
def inPoly(pt1, poly):

    points = poly.getPoints()
    nvert = len(points) #the number of vertices in the polygon

    #get x and y of pt1
    x = pt1.getX()
    y = pt1.getY()

    # I don't know why this works
    # See the link I provided for details
    result = False
    for i in range(nvert):

        # note: points[-1] will give you the last element
        # convenient!
        j = i - 1

        #get x and y of vertex at index i
        vix = points[i].getX()
        viy = points[i].getY()

        #get x and y of vertex at index j
        vjx = points[j].getX()
        vjy = points[j].getY()

        if (viy > y) != (vjy > y) and (x < (vjx - vix) * (y - viy) / (vjy - viy) + vix):
            result = not result

    return result

###move rectangle + text
def move_drawing(location, card):

    #get cordinates of the card
    points = card.drawing.getPoints()
    x=points[0].getX()
    y=points[0].getY()

    #dimensions
    width_cell=card.width
    height_cell=card.height

    column = location.column
    if not isinstance(location.row, int):
        row = 0
    else:
        row = location.row + 1

    x1 = border + x_space_cell + (2*x_space_cell + width_cell) * column
    y1 = border + y_space_cell + (2*y_space_cell + height_cell) * row

    dx = x1 - x
    dy = y1 - y
    card.drawing.move(dx, dy)
    print("moving "+ str(dx) + " , " + str(dy))
    card.drawntext.move(dx, dy)

#draw all the initial cards
def draw_location(location):

    ###Draw nothing if no card there
    if location.card == "":
        return

    #dimensions
    width_cell=location.card.width
    height_cell=location.card.height

    column = location.column
    if not isinstance(location.row, int):
        row = 0
    else:
        row = location.row + 1

    x1 = border + x_space_cell + (2*x_space_cell + width_cell) * column
    x2 = border + x_space_cell + (2*x_space_cell + width_cell) * column + width_cell
    y1 = border + y_space_cell + (2*y_space_cell + height_cell) * row
    y2 = border + y_space_cell + (2*y_space_cell + height_cell) * row + height_cell

    #drawn_card = Rectangle(Point(x1,y1), Point(x2, y2))
    drawn_card = Polygon(Point(x1,y1), Point(x1,y2), Point(x2,y2), Point(x2,y1))
    drawn_card.draw(win).setFill('white')

    card_values = [" A", " 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9", "10", " J", " Q", " K"]

    card_text = card_values[int(location.card.value)-1] + location.card.suit
    drawn_text = Text(Point((x1+x2)/2, (y1+y2)/2), card_text)
    if location.card.suit == "H" or location.card.suit == "D":
        drawn_text.setTextColor("red")
    drawn_text.draw(win)

    return drawn_card, drawn_text

#Draw initial board
def draw_board():
    '''
    for j in range(4):
        if not free_slot[j].card == "":
            free_slot[j].card.drawing, free_slot[j].card.drawntext = draw_location(free_slot[j])

    for j in range(4):
        if not goal_slot[j].card == "":
            goal_slot[j].card.drawing, goal_slot[j].card.drawntext = draw_location(goal_slot[j])
    '''

    for i in range(8):
        for j in range(8):
            if not board_slot[i][j].card == "":
                board_slot[i][j].card.drawing, board_slot[i][j].card.drawntext = draw_location(board_slot[i][j])

#Cycle through all locations and see if they were clicked
def check_clicked(click):
    for j in range(4):
        if not free_slot[j].card == "":
            if inPoly(click, free_slot[j].card.drawing):
                move_card_logic(free_slot[j])
                return

    for i in range(18):
        for j in range(8):
            if not board_slot[i][j].card == "":
                if inPoly(click, board_slot[i][j].card.drawing):
                    move_card_logic(board_slot[i][j])
                    return


#######################
###TESTING FUNCTIONS###
def column_test(j):
    for i in range(8):
        move_card_logic(board_slot[7-i][j])

def f(j):
    move_card_logic(free_slot[j-1])

def m(j):
    for i in range(10):
        move_card_logic(board_slot[i][j-1])

def board():

    for j in range(4):
        if not (free_slot[j].card == ""):
            print(free_slot[j].card.value + free_slot[j].card.suit, end = '   ')
        else:
            print("   ", end = '   ')


    for j in range(4):
        if not (goal_slot[j].card.value == " 0"):
            print(goal_slot[j].card.value + goal_slot[j].card.suit, end = '   ')
        else:
            print("   ", end = '   ')

    print("")
    print("")

    for i in range(10):
        for j in range(8):
            if not (board_slot[i][j].card == ""):
                print(board_slot[i][j].card.value + board_slot[i][j].card.suit, end = '   ')
            else:
                print("   ", end = '   ')
        print("")

###TESTING FUNCTIONS###
#######################

main()