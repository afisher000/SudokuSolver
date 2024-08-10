# -*- coding: utf-8 -*-
# Python code to solve a sudoku puzzle

import numpy as np
import itertools
from utils import get_box, check_errors, parse_input, display_sudoku
## To do
# When you have boolean for rows and cols, use np.outer to create array of booleans.
#

class SudokuSolver:
    def __init__(self,puzzle_string):

        # Setup puzzle and pencil_marks arrays
        self.iteration = 0 
        self.puzzle = parse_input(puzzle_string)
        self.pmarks = np.full((9,9,9), True)
        self.update_pmarks()

        # Main solving loop
        stopFlag = False
        while not stopFlag:
            self.print_sudoku()
            
            state = self.identify_solutions() #'stuck', 'solved', or 'normal'

            # Break conditions
            if state=='solved':
                self.print_sudoku()
                print('Solved!')
                stopFlag = True

            elif state=='stuck':
                print('Stuck!!!')
                stopFlag = True

            if check_errors(self.puzzle):
                print('ERROR!!!')
                break
        return


    def identify_solutions(self):
        '''Check for singular integer solutions over boxes, rows, and columns.'''
        # Singleint Solutions
        for integer in range(9):
            int_poss = self.pmarks[integer, :, :]
            
            # Check if only one possible location in box
            for ibox in range(9):
                box_mask = get_box(ibox)
                mask = int_poss[box_mask]
                if np.sum(mask)==1:
                    if self.puzzle[box_mask][mask]==0:
                        self.puzzle[box_mask][mask] = integer+1
                        print(f'Found {integer+1} in box {ibox+1} (only box position available)')


            # Check if only one possible location in column/row (only print if previously unsolved)
            for irow in range(9):
                mask = int_poss[irow,:]
                if np.sum(mask)==1:
                    if self.puzzle[irow, mask]==0:
                        self.puzzle[irow, mask]= integer+1
                        print(f'Found {integer+1} in row {irow+1}, column {mask.argmax()+1} (only row position available)')

                    
            for icol in range(9):
                mask = int_poss[:,icol]
                if np.sum(mask)==1:
                    if self.puzzle[mask, icol]==0:
                        self.puzzle[mask, icol] = integer+1  
                        print(f'Found {integer+1} in row {mask.argmax()+1}, column {icol+1} (only column position available)')
                    

        
        # Multiint Solutions
        for irow, icol in zip(*np.where(self.pmarks.sum(axis=0)==1)):
            integer = self.pmarks[:, irow, icol].argmax()
            if self.puzzle[irow, icol] == 0:
                self.puzzle[irow, icol] = integer + 1
                print(f'Found integer {integer+1} in row {irow+1}, column {icol+1} as the only valid integer.')
            
        if np.sum(self.puzzle==0)==0:
            return 'solved'
        else:
            removed_pmarks = self.update_pmarks()
            if removed_pmarks==0:
                return 'stuck'
            else:
                return 'normal'
            

    def apply_hiddenpairs(self):
        ''' Check for hidden pairs, naked pairs.'''
        
        # Check for pairs by row
        for irow in np.arange(9):
            array = self.pmarks[:,irow,:]
            cell_map = np.stack( (np.full(9,irow), np.arange(9)), axis=1)
            self.check_hiddenpairs( array, cell_map, f'row = {irow+1}', N=2)
            self.check_hiddenpairs( array, cell_map, f'row = {irow+1}', N=3)
            self.check_hiddenpairs( array, cell_map, f'row = {irow+1}', N=4)
            
        # Check for pairs by column
        for icol in np.arange(9):
            array = self.pmarks[:,:,icol]
            cell_map = np.stack( (np.arange(9), np.full(9,icol)), axis=1)
            self.check_hiddenpairs( array, cell_map, f'column = {icol+1}', N=2)
            self.check_hiddenpairs( array, cell_map, f'column = {icol+1}', N=3)
            self.check_hiddenpairs( array, cell_map, f'column = {icol+1}', N=4)
        
        
        # Check for pairs by box
        for ibox in np.arange(9):
            irow = 3 * (ibox//3)
            icol = 3 * (ibox%3)
            array = self.pmarks[:,irow:irow+3,icol:icol+3].reshape(9,9)
            cell_map = np.stack( (irow+np.arange(9)//3, icol+np.arange(9)%3), axis=1)
            self.check_hiddenpairs( array, cell_map, f'box = {ibox+1}', N=2)
            self.check_hiddenpairs( array, cell_map, f'box = {ibox+1}', N=3)
            self.check_hiddenpairs( array, cell_map, f'box = {ibox+1}', N=4)

    
    def check_hiddenpairs(self, array, cell_map, label, N=2):
        ''' N numbers only appear in N cells. Remove other pencilmarks in those cells. '''

        # Find integers with counts equal to N
        int_counts = array.sum(axis=1)
        candidate_ints = np.arange(9)[int_counts==N]+1
        
        # Check subsets of candidates for cell equality
        for Nints in itertools.combinations(candidate_ints, N):
            if np.isin( array[np.array(Nints)-1,:].sum(axis=0), [0,N]).all():

                # Remove all other pencilmarks
                cells = cell_map[array[Nints[0]-1],:]
                for irow, icol in cells:
                    self.pmarks[:,irow,icol] = False
                    self.pmarks[np.array(Nints)-1,irow,icol] = True

                print(f'Found hidden subset of {Nints} in {label}')
                        
    def print_sudoku(self):
        ''' Print array with sudoku formatting.'''

        # Header
        unknowns = np.sum(self.puzzle==0)
        tot_pmarks = self.pmarks.sum()
        print(f'Iteration={self.iteration}, {unknowns} unknowns left, {tot_pmarks} pencil marks left...\n')

        display_sudoku(self.puzzle)
        self.iteration += 1
        return 

    def update_pmarks(self):

        # Note initial pmarks
        initial_pmarks = self.pmarks.sum()   

        # Remove all pmarks at solved cells
        self.pmarks[:,self.puzzle>0]=False

        # Remove pmarks in same row/col as solutions
        for integer in range(9):
            int_solved = self.puzzle==(integer+1)
            for irow, icol in zip(*np.where(int_solved)):
                self.pmarks[integer,irow,:] = False
                self.pmarks[integer,:,icol] = False
                self.pmarks[integer,3*(irow//3):3*(irow//3+1),3*(icol//3):3*(icol//3+1)] = False
            
        # Remove pmarks using pointing pairs
        self.apply_pointing_pairs()

        # Remove pmarks using hidden pairs (or higher order subsets)
        self.apply_hiddenpairs()

        # Apply xwing
        self.apply_xwing()
                
        # Return number of pmarks removed
        final_pmarks = self.pmarks.sum()
        return initial_pmarks - final_pmarks
        
    def apply_pointing_pairs(self):
        ''' Find pointing_pairs in cells and remove the corresponding pencil marks.'''
        for integer in np.arange(9):
            for ibox in range(9):
                box_mask, irow_0, icol_0 = get_box(ibox, with_offset=True)
                box_pmarks = self.pmarks[integer][box_mask].sum()

                # Check if pmarks are all in same column
                cols_any = self.pmarks[integer][box_mask].any(axis=0)
                if box_pmarks>1 and cols_any.sum()==1:
                    icol = icol_0 + cols_any.argmax()
                    irows = np.s_[irow_0:irow_0+3]

                    # Check if pmarks would be removed by pointing pair
                    if self.pmarks[integer, :, icol].sum()!=self.pmarks[integer, irows, icol].sum():
                        print(f'Applied pointing pair for {integer+1} in box {ibox+1}')

                        # Remove all pmarks in col, then add back the pointing pmarks
                        temp_pmark_col = self.pmarks[integer, irows, icol].copy()
                        self.pmarks[integer, :, icol] = False
                        self.pmarks[integer, irows, icol] = temp_pmark_col


                # Check if pmarks are all in same column
                rows_any = self.pmarks[integer][box_mask].any(axis=1)
                if box_pmarks>1 and rows_any.sum()==1:
                    irow = irow_0 + rows_any.argmax()
                    icols = np.s_[icol_0:icol_0+3]

                    # Check if pmarks would be removed by pointing pair
                    if self.pmarks[integer, irow, :].sum()!=self.pmarks[integer, irow, icols].sum():
                        print(f'Applied pointing pair for {integer + 1} in box {ibox+1}')

                        # Remove all pmarks in row, then add back the pointing pmarks
                        temp_pmark_row = self.pmarks[integer, irow, icols].copy()
                        self.pmarks[integer, irow, :] = False
                        self.pmarks[integer, irow, icols] = temp_pmark_row

        return
          
    def apply_xwing(self):
        ''' Apply checks for Xwing and (in future) Swordfish '''
        for integer in np.arange(9)+1:
            array = self.pmarks[integer-1,:,:]
            
            # Check rows against rows
            candidate_rows = np.arange(9)[array.sum(axis=1)==2] #get rows with 2 possible
            if len(candidate_rows)>2:
                pass
            
            # Perform xwing check
            for Nrows in itertools.combinations(candidate_rows, 2):
                if np.array_equal(array[Nrows[0],:], array[Nrows[1],:]):
                    # Set all columns not in these rows to zero
                    rows = np.isin(np.arange(9), Nrows, invert=True)
                    cols = array[Nrows[0],:]
                    array[np.outer(rows,cols)] = False 

                    icols = np.where(cols)[0]
                    print(f'Applying xwing for integer {integer} in columns {icols+1}')


            # Check cols against cols
            candidate_cols = np.arange(9)[array.sum(axis=0)==2] #get cols with 2 possible
            if len(candidate_rows)>2:
                pass
            
            # Peform xwing check
            for Ncols in itertools.combinations(candidate_cols, 2):
                if np.array_equal(array[:,Ncols[0]], array[:,Ncols[1]]):

                    # Set all rows not in these columns to zero
                    rows = array[:,Ncols[0]]
                    cols = np.isin(np.arange(9), Ncols, invert=True)
                    array[np.outer(rows,cols)] = False 

                    irows = np.where(rows)[0]
                    print(f'Applying xwing for integer {integer} in rows {irows}')
                    
        return


