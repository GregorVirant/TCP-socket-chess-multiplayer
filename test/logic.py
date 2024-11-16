def clearLegalMoves(legalMoves):
    for i in range(8):
        for j in range(8):
            legalMoves[i][j]=0

def isLegal(row,column,board):
    if row<0 or row>7 or column<0 or column>7: 
        return False
    return board[row][column]==0

def isLegalTake(isMovingPieceWhite,row,column,board):
    if row<0 or row>7 or column<0 or column>7: 
        return False
    
    if isMovingPieceWhite and board[row][column]>=0:
        return False
    if (not isMovingPieceWhite) and board[row][column]<=0:
        return False
    return True

def legalMovesPawn(row,column,board,legalMoves):
    if board[row][column]==1: #if white pawn
        if isLegal(row-1,column,board):
            legalMoves[row-1][column]=2
        if row == 6 and isLegal(row-2,column,board):
            legalMoves[row-2][column]=2
        if isLegalTake(True,row-1,column-1,board): 
            legalMoves[row-1][column-1]=3
        if isLegalTake(True,row-1,column+1,board): 
            legalMoves[row-1][column+1]=3
    #else: #if black pawn



def calculateLegalMoves(row,column,board,legalMoves):
    legalMoves[row][column]=1
    if board[row][column] == 0:
        return
    
    if board[row][column]==1 or board[row][column]==-1:
        legalMovesPawn(row,column,board,legalMoves)

    
def move(pieceRow,pieceColumn,clickedRow,clickedColumn,board):
    board[clickedRow][clickedColumn]=board[pieceRow][pieceColumn]
    board[pieceRow][pieceColumn]=0

