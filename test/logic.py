
#narediti moram class ForsythEdwards, ki bo imel možnost
#   vračanja fe.getBoard - ki bo vrnil tabelo
#   vračanje fe.getMove - boolean ki pove če je na vrsti beli
#   vračanje fe.getEpSquare - vrne string
#   moram narediti vstavljanje potez

#   forsyth edward

#forsith edwards vsebuje notacijo in predhodne poteze



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
    
    # premik za 1 naprej
    if isLegal(row + color, column ,board):
        legalMoves[row + color][column] = 2
        # premik za 2 iz osnovnega polja
        if (row == 6 and isLegal(row - 2, column, board) and color == -1) or (row == 1 and isLegal(row + 2, column, board) and color == 1): #dvojna poteza
            legalMoves[row + color * 2][column] = 2
    # ujem figure v eno stran
    if isLegalTake(color - 1, row + color, column + color, board): 
        legalMoves[row + color][column + color] = 3
    # ujem figure v drugo stran
    if isLegalTake(color - 1, row + color, column - color, board): 
        legalMoves[row + color][column - color] = 3


def legalMovesBishop(row, column, board, legalMoves):
    # če je beli True sicer false
    if board[row][column] > 0:
        color = True
    else:
        color=False
    vectors = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # določimo smeri premika
    for i in range(4):
        a = vectors[i][0]
        b = vectors[i][1]
    
        for j in range(1,7):
            if isLegal(row + j * a, column + j * b, board):
                legalMoves[row + j * a][column + j * b] = 2    
            elif isLegalTake(color, row + j * a, column + j * b, board):
                legalMoves[row + j * a][column + j * b] = 3
                break
            else:
                break

def legalMovesRook(row, column, board, legalMoves):
    if board[row][column] > 0:
        color = True
    else:
        color=False
    vectors = [(0,1), (0,-1), (1,0), (-1,0)]

    for i in range(4):
        moveRow = vectors[i][0]
        moveColumn = vectors[i][1]
        for j in range(1,7):
            if isLegal(row + j * moveRow, column + j * moveColumn, board):
                legalMoves[row + j * moveRow][column + j * moveColumn] = 2
            elif isLegalTake(color, row + j * moveRow, column + j * moveColumn, board):
                legalMoves[row + j * moveRow][column + j * moveColumn] = 3
                break
            else:
                break


def legalMovesKnight(row, column, board, legalMoves):

    vectors = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
    if(board[row][column] > 0):
        color = True
    else:
        color = False

    for i in range(8):
        moveRow = vectors[i][0]
        moveColumn = vectors[i][1]
        if isLegal(row + moveRow, column + moveColumn, board):
            legalMoves[row + moveRow][column + moveColumn] = 2
        elif isLegalTake(color, row + moveRow, column + moveColumn, board):
            legalMoves[row + moveRow][column + moveColumn] = 3

def legalMovesKing(row, column, board, legalMoves):
    if board[row][column] > 0:
        color = True
    else:
        color = False
    
    vectors = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
    for i in vectors:
        moveRow = i[0]
        moveColumn = i[1]
        if isLegal(row + moveRow, column + moveColumn, board):
            legalMoves[row + moveRow][column + moveColumn] = 2
        elif isLegalTake(color, row + moveRow, column + moveColumn, board):
            legalMoves[row + moveRow][column + moveColumn] = 3


        

def calculateLegalMoves(row,column,board,legalMoves,isWhiteToMove):
    if(isWhiteToMove[0] and board[row][column] > 0 or (not isWhiteToMove[0] and board[row][column] < 0)):
        
        legalMoves[row][column] = 1
        if board[row][column] == 0:
            return
        piece = abs(board[row][column])
        
        if piece == 1: # kmet
            legalMovesPawn(row,column,board,legalMoves)
            
            return

        if piece == 2: # trdnjava
            legalMovesRook(row,column,board,legalMoves)
            
            return
        
        if piece == 3: # skakač
            legalMovesKnight(row,column,board,legalMoves)
            
            return
        
        if piece == 4: # tekač
            legalMovesBishop(row,column,board,legalMoves)
            
            return

        if piece == 5: # kraljica je kombinacija trdnjave in tekača
            legalMovesBishop(row,column,board,legalMoves)
            legalMovesRook(row,column,board,legalMoves)
            return


        if piece == 6: # kralj
            legalMovesKing(row,column,board,legalMoves)
            return

    

    
def move(pieceRow,pieceColumn,clickedRow,clickedColumn,board):
    board[clickedRow][clickedColumn]=board[pieceRow][pieceColumn]
    board[pieceRow][pieceColumn]=0

