def clearLegalMoves(legalMoves):
    for i in range(8):
        for j in range(8):
            legalMoves[i][j]=0

def isLegal(row,column,board):
    if row<0 or row>7 or column<0 or column>7: 
        return False
    return board[row][column]==0

def isLegalTake(isMovingPieceWhite,row,column,board):
    if row < 0 or row > 7 or column < 0 or column > 7: 
        return False
    
    if isMovingPieceWhite and board[row][column] >= 0:
        return False
    if (not isMovingPieceWhite) and board[row][column] <= 0:
        return False
    return True

def legalMovesPawn(row,column,board,legalMoves):
    #nastavim barvo
    if board[row][column] > 0:
        color = -1
    else:
        color = 1
    
    if abs(board[row][column]) == 1:
        if isLegal(row + color, column ,board):
            legalMoves[row + color][column] = 2

        if (row == 6 and isLegal(row - 2, column, board) and color == -1) or (row == 1 and isLegal(row + 2, column, board) and color == 1): #dvojna poteza
            legalMoves[row + color * 2][column] = 2

        if isLegalTake(color - 1, row + color, column + color, board): 
            legalMoves[row + color][column + color] = 3

        if isLegalTake(color - 1, row + color, column - color, board): 
            legalMoves[row + color][column - color] = 3


def legalMovesBishop(row, column, board, legalMoves):
    # če je beli True sicer false
    if board[row][column] > 0:
        color = True
    else:
        color=False
    if abs(board[row][column]) == 4:
        for i in range(4):
            #najhitrejši način določanja vrednosti a in b (11,-1-1,1-1,-11)
            if i % 2 == 0 or i == 0:
                a = 1
            else:
                a = -1
            if i < 2:
                b = 1
            else:
                b = -1
            
            for j in range(1,7):
                if isLegal(row + j * a, column + j * b, board):
                    legalMoves[row + j * a][column + j * b] = 2    
                elif isLegalTake(color, row + j * a, column + j * b, board):
                    legalMoves[row + j * a][column + j * b] = 3
                    break
                else:
                    break
def legalMovesRook
                
    
        

def calculateLegalMoves(row,column,board,legalMoves):
    legalMoves[row][column]=1
    if board[row][column] == 0:
        return
    
    if board[row][column] == 1 or board[row][column] == -1:
        legalMovesPawn(row,column,board,legalMoves)
    if board[row][column] == 4 or board[row][column] == -4:
        legalMovesBishop(row,column,board,legalMoves)

    
def move(pieceRow,pieceColumn,clickedRow,clickedColumn,board):
    board[clickedRow][clickedColumn]=board[pieceRow][pieceColumn]
    board[pieceRow][pieceColumn]=0

