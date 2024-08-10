import numpy as np

def get_box(ibox, with_offset=False):
    irow = 3*(ibox//3)
    icol = 3*(ibox%3)
    if with_offset:
        return np.s_[irow:irow+3, icol:icol+3], irow, icol
    else:
        return np.s_[irow:irow+3, icol:icol+3]

def check_errors(puzzle):
    '''Check for errors in puzzle.'''
    for integer in np.arange(9)+1:
        int_solved = puzzle==integer

        # Check rows and columns for duplicates
        for irow in range(9):
            if int_solved[irow,:].sum()>1:
                print(f'Multiple of {integer} in row {irow+1}')
        
        for icol in range(9):
            if int_solved[:, icol].sum()>1:
                print(f'Multiple of {integer} in column {icol}')

        # Check boxes for duplicates
        for ibox in range(9):
            if int_solved[get_box(ibox)].sum()>1:
                print(f'Multiple of {integer} in box {ibox+1} ')
                return True

    return False


def report_pmarks(pmarks, row=None, col=None):
    ''' Report pencilmarks of the sudoku puzzle.'''

    # Report by row
    if row:
        irow = row-1
        for icol in np.arange(9):
            if pmarks[:,irow,icol].sum()>0:
                print(f'Row={irow+1}, Col={icol+1}: {np.arange(9)[pmarks[:,irow,icol]]+1}')
        return
        
    # Report by column
    if col:
        icol = col-1
        for irow in np.arange(9):
            if pmarks[:,irow,icol].sum()>0:
                print(f'Row={irow+1}, Col={icol+1}: {np.arange(9)[pmarks[:,irow,icol]]+1}')
        return
    
    # Report all
    for irow in np.arange(9):
        for icol in np.arange(9):
            if pmarks[:,irow,icol].sum()>0:
                print(f'Row={irow+1}, Col={icol+1}: {np.arange(9)[pmarks[:,irow,icol]]+1}')
                
    return 

def parse_input(puzzle_string):
    '''Parse puzzle_string into 2d array.'''

    row_strings = puzzle_string.split('-')
    rows = [list(row_string) for row_string in row_strings]

    puzzle = np.array([list(map(int, row)) for row in rows])
    return puzzle

def display_sudoku(puzzle):
    output = '-------------------\n'
    # Loop over rows
    for irow in range(9):
        row_string = '|'
        for icol in range(9):
            char = str(puzzle[irow,icol])
            char = char if char!='0' else ' ' #replace 0 with empty space

            sep = '|' if icol in [2,5,8] else ' '
            row_string += char + sep
        output += row_string + '\n'

        # Add box top/bottom
        if irow in [2,5,8]:
            output += '-------------------\n'

    print(output)
    return