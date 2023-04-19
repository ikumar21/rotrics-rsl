def centerSquares(center,individualSquareLength,numColumns):
    squareCenters =[];
    yCenter = center[1]+(numColumns-1)*individualSquareLength/2

    
    for row in range(numColumns):
        rowCenters =[];
        xCenter = center[0]-(numColumns-1)*individualSquareLength/2
        for column in range(numColumns):
            rowCenters.append([xCenter,yCenter]);
            xCenter+= individualSquareLength;
        squareCenters.append(rowCenters);
        yCenter-=individualSquareLength;
    return squareCenters;



center = (0,300)

squareL = 20;
col = 5;

print(centerSquares(center,squareL,col))