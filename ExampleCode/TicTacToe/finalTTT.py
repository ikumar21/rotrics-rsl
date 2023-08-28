from pydexarm import Dexarm
import math 
from random import randint
# FEEDRATE = 8000

'''windows'''
Xdexarm = Dexarm(port="COM6")
Odexarm = Dexarm(port="COM4")
Edexarm = Dexarm(port="COM3")
'''mac & linux'''

#### RUN ONCE
# input values (test for now)
global relax, press, lift

x0 = 0  #origin (x0,y0)
y0 = 300
L = 150  #side length of tic-tac-toe board

relax = [0,190,0]       #arm position to keep out of way of other arms
press = -35             #z-value to press marker into board
lift = -20              #z-value to lift marker slightly above board

pressE = -50
liftE = 150

# calculations
global pc, R, win, win0, XtoO, poss

AB = [[[x0-L/6]*2, [y0+L/2,y0-L/2]], [[x0-L/2,x0+L/2], [y0-L/6]*2]]  #AB[A/B][x/y][i] - A & B lines

pc = [[x0-L/3, x0, x0+L/3]*3, [y0+L/3]*3 + [y0]*3 + [y0-L/3]*3]  #pc[x/y][s] - square center points (xc,yc)

win = [[[x0-L/3]*2,[y0+L/2,y0-L/2]], [[x0]*2,[y0+L/2,y0-L/2]], [[x0+L/3]*2,[y0+L/2,y0-L/2]],
       [[x0-L/2,x0+L/2],[y0+L/3]*2], [[x0-L/2,x0+L/2],[y0]*2], [[x0-L/2,x0+L/2],[y0-L/3]*2],
       [[x0-L/2,x0+L/2],[y0+L/2,y0-L/2]], [[x0-L/2,x0+L/2],[y0-L/2,y0+L/2]]]  #win[w][x/y][i] - win lines (all 8 possible)

winO = [[[-win[0][0][0],-win[0][0][1]],win[0][1]], win[1], [[-win[2][0][0],-win[2][0][1]],win[2][1]],
        [win[3][0],[y0-L/3]*2], win[4], [win[5][0],[y0+L/3]*2],
        win[6], win[7]]  #winO[w][x/y][i] - win lines, converted for O input

XtoO = [*range(8,-1,-1)]  #XtoO[sX] - convert X square to O

poss = [[0,3,6],[1,4,7],[2,5,8], [0,1,2],[3,4,5],[6,7,8], [0,4,8],[2,4,6]]  #poss[w][i] - board element combos for wins

R = L/12  #radius of "O"s

gameType = 0

# functions
def lineDraw(dexarm,p1,p2):
    dexarm.move_to(p1[0], p1[1], lift)
    dexarm.move_to(None, None, press)
    dexarm.move_to(p2[0], p2[1], press)
    dexarm.move_to(None, None, lift)

def XDraw(dexarm,loc):
    # center points of square
    xc = pc[0][loc]
    yc = pc[1][loc]
        
    # draw first X line
    dexarm.move_to(xc-L/12, yc+L/12, lift)
    dexarm.move_to(None, None, press)
    dexarm.move_to(xc+L/12, yc-L/12, press)
    dexarm.move_to(None, None, lift)
    
    # draw second X line
    dexarm.move_to(xc+L/12, yc+L/12, lift)
    dexarm.move_to(None, None, press)
    dexarm.move_to(xc-L/12, yc-L/12, press)
    dexarm.move_to(None, None, lift)

def ODraw(dexarm,loc):
    # center points of square (converted to O orientation)
    xc = pc[0][XtoO[loc]]
    yc = pc[1][XtoO[loc]]

    # move to circle border
    dexarm.move_to(xc+R, yc, None)
    dexarm.move_to(None, None, press)

    # draw circumference
    theta = 0
    while(theta <= 2*math.pi):
        dexarm.move_to(R*math.cos(theta) + xc, R*math.sin(theta) + yc, press);
        theta = theta + math.pi/128;
    
    dexarm.move_to(None, None, lift)

def winDraw(Xdexarm,Odexarm,loc,wins):
    # check if X or O won
    if wins[0] == "X":
        # draw last mark
        XDraw(Xdexarm,loc)

        # draw win line
        Xdexarm.move_to(win[wins[1]][0][0], win[wins[1]][1][0], lift)
        Xdexarm.move_to(None, None, press)
        Xdexarm.move_to(win[wins[1]][0][1], win[wins[1]][1][1], press)
        Xdexarm.move_to(None, None, lift)
        Xdexarm.move_to(relax[0], relax[1], relax[2])
    else:
        # draw last mark
        ODraw(Odexarm,loc)
        
        # draw win line (using win lines relative to O arm)
        Odexarm.move_to(winO[wins[1]][0][0], winO[wins[1]][1][0], lift)
        Odexarm.move_to(None, None, press)
        Odexarm.move_to(winO[wins[1]][0][1], winO[wins[1]][1][1], press)
        Odexarm.move_to(None, None, lift)
        Odexarm.move_to(relax[0], relax[1], relax[2])

def winCheck(XorO):
    # check for 2 X's or 2 O's in row/col/diag
    if XorO == "X":
        sum = 2
    else:
        sum = 8
    
    # check each possibility
    info = None
    
    for t in range(8):
        if board[poss[t][0]] + board[poss[t][1]] + board[poss[t][2]] == sum:
            # check which position is empty
            if board[poss[t][0]] == 0:
                info = [poss[t][0],t]  #empty location and win type
                break
            elif board[poss[t][1]] == 0:
                info = [poss[t][1],t]
                break
            else:
                info = [poss[t][2],t]
                break
    
    return info

def erase(dexarm,liftE,pressE):
    dexarm.move_to(0,300,liftE)

    # draw 3 row win lines
    #dexarm.move_to(win[3][0][1], win[3][1][1], pressE)
    dexarm.move_to(x0+L/2, y0+L/2, pressE)
    dexarm.move_to(x0-L/2, y0+L/2, pressE)

    dexarm.move_to(win[4][0][0], win[4][1][0], pressE)
    dexarm.move_to(win[4][0][1], win[4][1][1], pressE)

    dexarm.move_to(win[5][0][0], win[5][1][0], pressE)
    dexarm.move_to(win[5][0][1], win[5][1][1], pressE)
    
    # move to center
    dexarm.move_to(x0,y0,pressE)

    dexarm.move_to(0,300,liftE)

# setup
Edexarm.go_home()
Edexarm._send_cmd("G92.1\r\n")
Edexarm.move_to(0,300,liftE)

Xdexarm.go_home()
Xdexarm._send_cmd("G92.1\r\n")
Xdexarm.move_to(relax[0], relax[1], relax[2])

Odexarm.go_home()
Odexarm._send_cmd("G92.1\r\n")
Odexarm.move_to(relax[0], relax[1], relax[2])

while True:
    #### FULL GAME (once per game)
    # reset board vector
    board = [0]*9  #record board moves, 1 is X, 4 is O

    # board lines
    #  vertical lines
    lineDraw(Xdexarm, [AB[0][0][0], AB[0][1][0]], [AB[0][0][1], AB[0][1][1]])
    lineDraw(Odexarm, [AB[0][0][0], AB[0][1][0]], [AB[0][0][1], AB[0][1][1]])

    #  horizontal
    lineDraw(Xdexarm, [AB[1][0][0], AB[1][1][0]], [AB[1][0][1], AB[1][1][1]])
    lineDraw(Odexarm, [AB[1][0][0], AB[1][1][0]], [AB[1][0][1], AB[1][1][1]])

    Xdexarm.move_to(relax[0], relax[1], relax[2])
    Odexarm.move_to(relax[0], relax[1], relax[2])

    # iterate for maximum 9 possible moves (i = 0:4)
    for i in range(5):
        
        #### X move
        loc = None  #location to draw
        wins = None  #who wins, and win number
        
        #  check for winning move
        check = winCheck("X")
        if check != None:
            loc = check[0]  #assign location
            board[loc] = 1
            wins = ["X",check[1]]  #set as a win, and which type of win
            break           #exit current game
        
        #  check for blocking win
        check = winCheck("O")
        if check != None:
            loc = check[0]  #assign location
        
        #  select random empty space
        if loc == None:  #check if location already selected
            loc = randint(0,8)
            while board[loc] != 0:
                loc = randint(0,8)
        
        #   update board with move
        board[loc] = 1
        
        #  draw X
        XDraw(Xdexarm,loc)
        Xdexarm.move_to(relax[0], relax[1], relax[2])

        #  check if board full
        if sum(board) == 21:  #only = 21 when 5 X's & 4 O's (X always starts in tic-tac-toe)
            break
        
        print(i);print(board[0:3]);print(board[3:6]);print(board[6:9]) # display matrix
        
        #### O move
        loc = None  #location to draw
        wins = None  #who wins, and win number
        
        #  check for winning move
        check = winCheck("O")
        if check != None:
            loc = check[0]  #assign location
            board[loc] = 4
            wins = ["O",check[1]]  #set as a win, and which type of win
            break           #exit current game
        
        #  check for blocking win
        check = winCheck("X")
        if check != None:
            loc = check[0]  #assign location
        
        #  select random empty space
        if loc == None:  #check if location already selected
            loc = randint(0,8)
            while board[loc] != 0:
                loc = randint(0,8)
        
        #  set & draw O
        #   update board with move
        board[loc] = 4
        ODraw(Odexarm,loc)
        Odexarm.move_to(relax[0], relax[1], relax[2])
        
        print(i);print(board[0:3]);print(board[3:6]);print(board[6:9]) # display matrix
        
    print("\nFinal:");print(board[0:3]);print(board[3:6]);print(board[6:9]) # display matrix
    
    # draw win line
    if wins != None:  # check if win
        winDraw(Xdexarm,Odexarm,loc,wins)

    # reset board
    #  move draw arms to relax position
    Xdexarm.move_to(relax[0], relax[1], relax[2])
    Odexarm.move_to(relax[0], relax[1], relax[2])

    # erase board
    erase(Edexarm,liftE,pressE)









