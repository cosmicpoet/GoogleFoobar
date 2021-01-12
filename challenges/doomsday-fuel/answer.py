from fractions import Fraction

def matrixMultiplication(m1, m2):
    # Return the product of 2 matrix multiplication
    if len(m1[0]) != len(m2):
        return
    result = []
    for i in range(len(m1)):
        result.append([0 for _ in range(len(m2[0]))])
        for j in range(len(m2[0])):
            for k in range(len(m2)):
                result[i][j] += m1[i][k] * m2[k][j]
    
    return result


def matrixMinor(m, i, j):
    # Return the minor of matrix m by removing ith row and jth column
    return [row[:j] + row[j+1:] for row in m[:i] + m[i+1:]]


def matrixDeterminant(m):
    # Return the determinant of the square matrix m
    determinant = 0
    # Base case when matrix is 1x1
    if len(m) == 1:
        return m[0][0]
    # Base case when matrix is 2x2
    if len(m) == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    # Otherwise, calculate recursively the determinant
    # by m[0][j] * det(minor(m, 0, j)), with alternating +/- signs
    for j in range(len(m)):
        determinant += m[0][j] * matrixDeterminant(matrixMinor(m, 0, j)) * ((-1)**j)

    return determinant


def matrixTranspose(m):
    # Return the transpose of matrix m
    # works for non-square matrices as well :)
    T = []
    for i in range(len(m[0])):
        T.append([0 for _ in range(len(m))])
        for j in range(len(m)):
            T[i][j] = m[j][i]
    
    return T


def matrixInverse(m):
    # Retrurn the inverse of matrix m

    determinant = matrixDeterminant(m)
    # Special case when m is 1x1
    if len(m) == 1:
        return [[1 / m[0][0]]]
    
    # Special case when m is 2x2
    if len(m) == 2:
        return [
            [ m[1][1] * Fraction(1, determinant), m[0][1] * Fraction(1, determinant) * -1 ],
            [ m[1][0] * Fraction(1, determinant) * -1, m[0][0] * Fraction(1, determinant) ]
        ]
    
    # First, get a matrix C of cofactors open
    # where C[i][j] = (-1)^(i+j) * det(minor(m[i][j]))
    C = []
    for i in range(len(m)):
        C.append([0 for _ in range(len(m))])
        for j in range(len(m)):
            C[i][j] = ( (-1) ** (i+j) ) * matrixDeterminant(matrixMinor(m, i, j))
    
    # Then, the inverse of m is (1/det(m)) * transpose(C)
    if determinant == 0:
        print('This matrix is not invertible!!')
        return None
    factor = Fraction(1, determinant)
    inverse = matrixTranspose(C)
    for i in range(len(m)):
        for j in range(len(m)):
            inverse[i][j] *= factor
    
    return inverse


def allEqual(nums):
    # Return True if all the numbers in the list are equal
    checkVal = nums[0]
    for val in nums:
        if val != checkVal:
            return False
    return True


def findLCD(fracs):
    # find a common least denominator from a list of fractions
    # implemented for the fun
    # use gcd() when you can, I myself got mixed because foobar uses Py2.7 which is different from Py3.9 on how gcd() is used
    # too lazy to find out ;)
    denoms = []
    for frac in fracs:
        denoms.append(frac.denominator)
    temp = denoms[:]

    while True:
        # First, if all the values are equal, return the only value as LCD
        checkVal = temp[0]
        if allEqual(temp):
            return checkVal
        
        # Then, keep adding multiples to the smallest value in the list of denoms
        minIndex = 0
        minVal = temp[minIndex]
        for i in range(len(temp)):
            if temp[i] < minVal:
                minVal = temp[i]
                minIndex = i
        temp[minIndex] += denoms[minIndex]
    

def convertProbMatrix(m):
    # Converting the input m to a proper Probablility Matrix probM, i.e. each row sums to 1
    probM = []
    terminalCount = 0
    numStates = len(m)
    for row in range(numStates):
        probM.append([0 for _ in range(numStates)])
        denom = sum(m[row])
        if denom == 0:
            probM[row][row] = 1
            terminalCount += 1
        else:
            for col in range(len(m[row])):
                probM[row][col] = Fraction(m[row][col], denom)
    
    return probM


def transformInput(m):
    # Transform the input matrix
    # 1. Group transient states at the beginning of the matrix
    # 2. Reorder each rows according to the grouping operations done in 1)
    # 3. Convert the input matrix into a proper probablity matrix where each row sums to 1
    
    numStates = len(m)
    transientStates = []
    terminalStates = []

    ### 1. Grouping non-terminal and terminal states separately first
    for row in m:
        if sum(row) == 0:
            terminalStates.append(row)
        else:
            transientStates.append(row)

    ### 2. (Additional step) Need to also convert the ordering of each transient state row accordingly
    ### The loop will use 2 counters
    ### steps -> how many rows have gone through in the input m, and use as index for accessing rows in m, += 1 every row
    ### index -> index of the col in transientStates, only += 1 when the row iterated in m is a transient state row
    ### This ensures that after we push a column to back of the rows, we DO NOT skip the immediate next column
    steps = 0
    index = 0
    while steps < numStates:
        if sum(m[steps]) == 0:
            for transientRow in transientStates:
                temp = transientRow.pop(index)
                transientRow.append(temp)
        else:
            index += 1        
        steps += 1

    ### Combine the transient and terminal states
    m = transientStates + terminalStates

    ### 3. Converting the input m to a proper Probablility Matrix probM, i.e. each row sums to 1
    probM = convertProbMatrix(m)
    
    return probM

def answer(m):
    # Absorbing Markov chain problem, where there are terminal states that can be exited
    # Need to find the absorbing probablilities
    # Very brute-force implementation, because of the constrains of len(m) <= 10, didn't bother optimize too much
    
    probM = []
    terminalCount = 0
    numStates = len(m)

    # Get the # of terminal states
    for row in m:
        if sum(row) == 0:
            terminalCount += 1

    ###### Special Case: Since we always start at state 0 - if state 0 is terminating, then we should return [1, 0, ..., 1]
    if sum(m[0]) == 0:
        answer = [0 for _ in range(terminalCount)]
        answer[0] = 1
        answer.append(1)
        return answer
    
    # Transform the input matrix m into a proper probablity matrix probM
    probM = transformInput(m)

    # Fundatmental matrix: F = inv(I - Q)
    Q = []
    I = []
    temp = []
    for row in range(numStates - terminalCount):
        Q.append([0 for _ in range(numStates - terminalCount)])
        I.append([0 for _ in range(numStates - terminalCount)])
        temp.append([0 for _ in range(numStates - terminalCount)])
        I[row][row] = 1
        for col in range(numStates - terminalCount):
            Q[row][col] = probM[row][col]
            temp[row][col] = I[row][col] - Q[row][col]

    # print(Q, I, temp)
    F = matrixInverse(temp)

    # Absobring probabilities are FR[0]
    R = []
    for row in range(numStates - terminalCount):
        R.append(probM[row][(numStates - terminalCount):])
    
    result = matrixMultiplication(F, R)[0]
    
    # Formatting data accordingly
    lcd = findLCD(result)
    answer = []
    for val in result:
        answer.append(int(val * lcd))
    answer.append(lcd)
    
    return answer
