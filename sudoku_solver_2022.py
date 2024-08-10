# -*- coding: utf-8 -*-
# Python code to solve a sudoku puzzle

import numpy as np
import itertools

## To do
# When you have boolean for rows and cols, use np.outer to create array of booleans.
#

class SudokuSolver:
    def __init__(self,puzzle_string):

        self.puzzle = self.parse_input(puzzle_string)
        self.initialize_pmarks()
        
        self.unknowns = np.sum(self.puzzle==0)
        self.iteration = 0 
        self.tot_pmarks = self.pmarks.sum()
        self.finished = False

    def increment(self):
        self.iteration += 1
        
    def check_errors(self):
        '''Check for errors in puzzle.'''
        for integer in np.arange(9)+1:
            int_solved = self.puzzle==integer
            # Check row or columns for multiples
            if (int_solved.sum(axis=0)>1).any() or (int_solved.sum(axis=1)>1).any():
                print(f'Multiple of {integer} in same row/column')
                self.print_sudoku()
                return True

                
            # Check boxes for multiples
            for ibox in np.arange(9):
                irow = 3 * (ibox//3)
                icol = 3 * (ibox%3)
                if int_solved[irow:irow+3,icol:icol+3].sum()>1:
                    print(f'Multiple of {integer} in box {ibox+1} ')
                    self.print_sudoku()
                    return True

        return False
    
        
    def report_pmarks(self, row=None, col=None):
        ''' Report pencilmarks of the sudoku puzzle.'''
        # Report by row
        if row:
            irow = row-1
            for icol in np.arange(9):
                if self.pmarks[:,irow,icol].sum()>0:
                    print(f'Row={irow+1}, Col={icol+1}: {np.arange(9)[self.pmarks[:,irow,icol]]+1}')
            return
           
        # Report by column
        if col:
            icol = col-1
            for irow in np.arange(9):
                if self.pmarks[:,irow,icol].sum()>0:
                    print(f'Row={irow+1}, Col={icol+1}: {np.arange(9)[self.pmarks[:,irow,icol]]+1}')
            return
        
        # Report all
        for irow in np.arange(9):
            for icol in np.arange(9):
                if self.pmarks[:,irow,icol].sum()>0:
                    print(f'Row={irow+1}, Col={icol+1}: {np.arange(9)[self.pmarks[:,irow,icol]]+1}')
                    
        return 
    

    def guess_and_check(self):
        ''' Check whether all possible options in a cell would give same conclusion'''
        
        irows, icols = np.where(self.pmarks.sum(axis=0)==2)
        for (irow,icol) in list(zip(irows, icols)):
            
            # Find values, continue if none (cell known)
            ints = np.arange(9)[self.pmarks[:,irow,icol]]+1
            if not len(ints):
                continue
            
            # Save reference
            saved = self.pmarks.copy()
            saved_puzzle = self.puzzle.copy()
            
            # Compute poss for each guess
            pmarks_list = []
            for index,integer in enumerate(ints):
                # Append to poss_list
                self.puzzle[irow,icol] = integer
                self.update_pmarks()
                pmarks_list.append(self.pmarks.copy())
                
                # Reset to saved
                self.pmarks = saved.copy()
                self.puzzle[irow,icol] = 0
            
            # Find the matches
            summed = np.sum(pmarks_list, axis=0)
            matches = np.logical_or( summed==0, summed==len(pmarks_list))

            # Update
            updated = saved.copy()
            updated[matches] = pmarks_list[0][matches].copy()
            updated[:,irow,icol] = saved[:,irow,icol].copy()          
            different = np.logical_not(updated==saved)

            if different.any():
                #self.print_sudoku()
                #self.report_pmarks()
                #print(f'Try values {values} in row {irow+1} and col = {icol+1}')
                #(c_ints, c_rows, c_cols) = np.where(different==True)
                #for (c_int, c_row, c_col) in list(zip(c_ints, c_rows, c_cols)):
                #    print(f'Removed {c_int+1} possibility from row {c_row+1} and col {c_col+1}')
            
                self.pmarks = updated.copy()
                self.find_solutions()
        return

        
    def advanced_checks(self):
        ''' Check for hidden pairs, naked pairs.'''
        
        # Check for pairs by row
        for irow in np.arange(9):
            array = self.pmarks[:,irow,:]
            cell_map = np.stack( (np.full(9,irow), np.arange(9)), axis=1)
            self.check_hiddenpairs( array, cell_map )
            self.check_nakedpairs( array, cell_map )
            
        # Check for pairs by column
        for icol in np.arange(9):
            array = self.pmarks[:,:,icol]
            cell_map = np.stack( (np.arange(9), np.full(9,icol)), axis=1)
            self.check_hiddenpairs( array, cell_map )
            self.check_nakedpairs( array, cell_map )
        
        
        # Check for pairs by box
        for ibox in np.arange(9):
            irow = 3 * (ibox//3)
            icol = 3 * (ibox%3)
            array = self.pmarks[:,irow:irow+3,icol:icol+3].reshape(9,9)
            cell_map = np.stack( (irow+np.arange(9)//3, icol+np.arange(9)%3), axis=1)
            self.check_hiddenpairs( array, cell_map)
            self.check_nakedpairs( array, cell_map)

        # Check Pointing Pairs
        self.check_pointing_pairs()


    def expert_checks(self):
        ''' Check hidden and naked groups with N>2, Xwings, and others.'''
        
        # Check for pairs by row
        for irow in np.arange(9):
            array = self.pmarks[:,irow,:]
            cell_map = np.stack( (np.full(9,irow), np.arange(9)), axis=1)
            self.check_hiddenpairs( array, cell_map,3 )
            self.check_nakedpairs( array, cell_map,3 )
            self.check_hiddenpairs( array, cell_map,4 )
            self.check_nakedpairs( array, cell_map,4 )
            
        # Check for pairs by column
        for icol in np.arange(9):
            array = self.pmarks[:,:,icol]
            cell_map = np.stack( (np.arange(9), np.full(9,icol)), axis=1)
            self.check_hiddenpairs( array, cell_map, 3 )
            self.check_nakedpairs( array, cell_map, 3)
            self.check_hiddenpairs( array, cell_map, 4 )
            self.check_nakedpairs( array, cell_map, 4 )
        
        # Check for pairs by box
        for ibox in np.arange(9):
            irow = 3 * (ibox//3)
            icol = 3 * (ibox%3)
            array = self.pmarks[:,irow:irow+3,icol:icol+3].reshape(9,9)
            cell_map = np.stack( (irow+np.arange(9)//3, icol+np.arange(9)%3), axis=1)
            self.check_hiddenpairs( array, cell_map, 3 )
            self.check_nakedpairs( array, cell_map, 3)
            self.check_hiddenpairs( array, cell_map, 4 )
            self.check_nakedpairs( array, cell_map, 4 )
            
        # Check XWings
        self.check_xwing()
        
        # Check Pointing Pairs
        self.check_pointing_pairs()
        
        return
    
    def check_hiddenpairs(self, array, cell_map, N=2):
        ''' N numbers only appear in N cells. Remove other pencilmarks in those cells. '''
        # Currently coded for N=2.
        int_counts = array.sum(axis=1)
        candidate_ints = np.arange(9)[int_counts==N]+1
        
        # Check subsets for equality
        for Nints in itertools.combinations(candidate_ints, N):
            if np.isin( array[np.array(Nints)-1,:].sum(axis=0), [0,N]).all():

                # Remove all other pencilmarks
                cells = cell_map[array[Nints[0]-1],:]
                for cell in cells:
                    irow, icol = cell
                    self.pmarks[:,irow,icol] = False
                    self.pmarks[np.array(Nints)-1,irow,icol] = True
                    #print(f'Found hidden pair of {subset} in cells {cell_map[array[subset[0]],:]+1}')
                        
    def check_nakedpairs(self, array, cell_map, N=2):
        ''' The only pencilmarks in two cells are two numbers. Remove those two numbers from other cells. '''
        # Currently coded for N=2.
        cells = (array.sum(axis=0)==N)
        candidate_cells = np.arange(9)[cells]
        
        # Check if only N ints appear in N cells.
        for Ncells in itertools.combinations(candidate_cells, 2):
            if np.isin( array[:,Ncells].sum(axis=1), [0,N]).all():
        
                # Remove the naked integers from all other cells
                naked_int_bool = array[:,Ncells[0]]
                for cell in cell_map[np.isin(np.arange(9),Ncells, invert=True), :]:
                    irow, icol = cell
                    self.pmarks[naked_int_bool, irow, icol]=False

    def check_xwing(self):
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
            # Perform swordfish check
            #for subset in itertools.combinations(row_set, 3):
                
            
                    
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
                
            # Perform swordfish check
            # to be done
        return
    def parse_input(self, puzzle_string):
        '''Parse puzzle_string into 2d array.'''
        rows = puzzle_string.split('-')
        array = [list(map(int, list(row))) for row in rows]
        return np.array(array)
    
    def print_sudoku(self):
        ''' Print array with sudoku formatting.'''
        for irow in np.arange(9):
            rowstring = ''
            for icol in np.arange(9):
                char = str(self.puzzle[irow,icol])
                char = char if char!='0' else ' ' #replace 0 with empty space
                rowstring += char + ' '
                if icol in [2,5]:
                    rowstring = rowstring + '|'
            print(rowstring)
            if irow in [2,5]:
                print('-------------------')
        print('\n\n')
        return
    
    def update_pmarks(self):
        for integer in np.arange(9)+1:
            # Find locations of integer in solved array
            int_solved = self.puzzle==integer
            
            # Invalidate cells in same row/col/box as integer
            for irow, icol in zip(*np.where(int_solved)):
                self.pmarks[integer-1,irow,:] = False
                self.pmarks[integer-1,:,icol] = False
                self.pmarks[integer-1,3*(irow//3):3*(irow//3+1),3*(icol//3):3*(icol//3+1)] = False
            
        self.pmarks[:,self.puzzle>0]=False
        
        self.check_pointing_pairs()
        self.advanced_checks()
                
        return
        
    def initialize_pmarks(self):
        ''' Find the possible locations of a given integer.'''
        
        self.pmarks = np.full((9,9,9), True)
        for integer in np.arange(9)+1:
            # Find locations of integer in solved array
            int_solved = self.puzzle==integer
           
            # Initialize possible array
            self.pmarks[integer-1,:,:] = ~(self.puzzle>0)
           
            # Invalidate cells in same row/col/box as integer
            for irow, icol in zip(*np.where(int_solved)):
                self.pmarks[integer-1,irow,:] = False
                self.pmarks[integer-1,:,icol] = False
                self.pmarks[integer-1,3*(irow//3):3*(irow//3+1),3*(icol//3):3*(icol//3+1)] = False
                    
        return
    
    def check_pointing_pairs(self):
        ''' Find pointing_pairs in cells and remove the corresponding pencil marks.'''
        for integer in np.arange(9)+1:
            for ibox in np.arange(9):
                irow = 3 * (ibox//3)
                icol = 3 * (ibox%3)
    
                # Check if all trues are in same column
                cols_any = self.pmarks[integer-1,irow:irow+3, icol:icol+3].any(axis=0)
                if cols_any.sum()==1:
                    true_col = cols_any.argmax()
                    rows = np.isin( np.arange(9), np.arange(irow,irow+3), invert=True)
                    self.pmarks[integer-1,rows, icol+true_col] = False
        
                # Check if all trues are in same row
                rows_any = self.pmarks[integer-1,irow:irow+3, icol:icol+3].any(axis=1)
                if rows_any.sum()==1:
                    true_row = rows_any.argmax()
                    cols = np.isin( np.arange(9), np.arange(icol,icol+3), invert=True)
                    self.pmarks[integer-1,irow+true_row, cols] = False

        return
          
    def find_solutions(self):
        '''Check for singular integer solutions over boxes, rows, and columns.'''
        # Singleint Solutions
        for integer in np.arange(9):
            int_poss = self.pmarks[integer, :, :]
            
            # Check if only one possible location in column/row
            for irow in np.arange(9):
                if np.sum(int_poss[irow,:])==1:
                    self.puzzle[irow,:][int_poss[irow,:]] = integer+1
                    
            for icol in np.arange(9):
                if np.sum(int_poss[:,icol])==1:
                    self.puzzle[:,icol][int_poss[:,icol]] = integer+1  
                    
            # Check if only one possible location in box
            for ibox in np.arange(9):
                irow = 3*(ibox//3)
                icol = 3*(ibox%3)
                box_slice = np.s_[irow:irow+3, icol:icol+3]
                box_poss = int_poss[box_slice].copy()
                if np.sum(box_poss)==1:
                    self.puzzle[box_slice][box_poss] = integer+1
        
        # Multiint Solutions
        for irow, icol in zip(*np.where(self.pmarks.sum(axis=0)==1)):
            self.puzzle[irow, icol] = self.pmarks[:,irow,icol].argmax() + 1
            
        self.update_pmarks()
        return
       


hard = '400008060-700020105-000061070-150030400-000745000-200006000-070084030-800200000-509000020'
solver = SudokuSolver(hard)


while not solver.finished:
    # Print current solution
    print(f'Iteration={solver.iteration}, {solver.unknowns} unknowns left, {solver.tot_pmarks} pencil marks left...')
    solver.print_sudoku()
    solver.increment()

    # Check for inconsistencies
    if solver.check_errors():
        solver.finished = True
        continue
    
    solver.update_pmarks()
    solver.find_solutions()

    # Find current unknowns
    current_unknowns = np.sum(solver.puzzle==0)
    current_tot_pmarks = solver.pmarks.sum()
    
    # Break conditions
    if current_tot_pmarks == solver.tot_pmarks:
        # If stuck, try guess_and_check
        solver.guess_and_check()
        solver.expert_checks()
        if current_tot_pmarks == solver.pmarks.sum():
            print(f"Can't find solution. {solver.unknowns} unknowns left, {solver.tot_pmarks} pencil marks left...")
            solver.report_pmarks()
            solver.finished = True

    elif current_unknowns==0:
        print('Solved!')
        solver.print_sudoku()
        solver.finished = True
    else:
        solver.unknowns = current_unknowns
        solver.tot_pmarks = current_tot_pmarks