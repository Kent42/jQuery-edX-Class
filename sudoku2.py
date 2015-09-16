"""

Routines for generating and solving puzzles of "Sudoku" [1] are presented.

[1] https://en.wikipedia.org/wiki/Sudoku

The squares in the puzzle returned by the "scramble" routine are filled; 
"obscure" calls "solve" and adds blanks.  "Obscure rep" calls "obscure" the 
number of times specified by the caller, and returns the puzzle with the fewest 
filled.

"Strats" is passed to "solve" to specify the strategies that are used; "strats" 
is a container.  The numbers "2" and "3" and string "cross" are tested for 
membership and all enabled by default.  "2" specifies elimination of other items 
from the squares, and the participating items from other squares in the column, 
row, and block in which 2-item cycles occur; similarly for "3" and 3-item 
cycles. "Cross" specifies elimination of items from the column or row if it can 
only occur in one row or column in a block, and from other rows and columns in a 
block if it can only occur in one block in a row or column.

The exceptions "No Solution" and "Multiple Solutions" are defined and raised by 
"solve".  "Scramble" starts with a trivial solution, and randomly swaps items 
within cycles within a column or row of blocks until all the squares have been 
swapped "reps" times in both directions.  A grid of size "9" takes about "60 .. 
160" swaps, excluding swaps within cycles that contain all the items; size "16" 
takes about "130 .. 310".  The argument should be a perfect square.  It uses 3 
collections:
    - "A": the current sequence of sequences of items.  The left-most index
    specifies the row.
    - "Rn": rows: the sequence of the maps of the items to the index of the
    column in the row in which the item is.
    - "Cn": columns: the sequence of the maps of the items to the index of the
    row in the column in which the item is.

"Obscure" picks a random order of squares three each, and for each square, 
removes the item, and replaces it if it allows another solution.  If the 
"symmetric" argument is true, only the first half of squares are shuffled and 
then tried in pairs.  The "strats" and "symmetric" arguments are passed through 
to "solve".

"Solve" uses 4 collections:
    - "A": the original sequence of the sequences of the items with "0" for
    blank.
    - "B": the sequence of the sequences of the sets of the items in a square in
    which the item has not been eliminated.
    - "Rn": rows: the sequence of the maps of the items to the sets of the 
    indices of the columns in the row in which the item has not been eliminated.
    - "Cn": columns: the sequence of the maps of the items to the sets of the 
    indices of the rows in the column in which the item has not been eliminated.
    - "Bln": blocks: the sequence of sequences of the maps of the items to the 
    sets of the pairs of the indices of the columns and rows in which the item
    has not been eliminated.  The left-most index specifies the row among
    blocks.

{ Ck, ck0, ckA, rk, rk0, rkA, etc. } are indices.  "C" and "r" are column and 
row objects.  "N" is an item; "q" is the search queue; and "s" indicates a set.

The search loop in "solve" pops an entry from the search queue and checks the 
collections for other items that can consequently be removed.  "Elim" removes 
the specified item from the 4 above collections at the specified column and row 
and adds { the column, the row, and the item that was removed } to the search 
queue.  "Elim" is defined locally to obviate several parameters.  "Done ct" is 
an entry in a dictionary to allow updating by "elim".

This module is preliminary and might be flawed.

"""


import math, collections, itertools

class NoSolution( Exception ):
    pass

class MultipleSolutions( Exception ):
    pass

def scramble( size= 9, reps= 10 ):
    import random
    sizeB= int( math.sqrt( size ) )
    idx_tup= tuple( range( size ) )
    cidx_bl_set= tuple( { ck0+ ck for ck in range( sizeB ) } for ck0 in range(
        0, size, sizeB ) )
    ridx_bl_set= tuple( { rk0+ rk for rk in range( sizeB ) } for rk0 in range(
        0, size, sizeB ) )
    item_list= list( range( 1, size+ 1 ) )
    #random.shuffle( item_list )
    _item_list2= item_list* 2
    a= [ list( _item_list2[ m: m+ size ] ) for k in range( sizeB ) for m in
        range( k, size, sizeB ) ]
    print1 (a)
    rn= [ dict( ( n, a[ rk ].index( n ) ) for n in item_list ) for rk in range(
        size ) ]
    cn= [ dict( ( n, tuple( a[ rk ][ ck ] for rk in range( size ) ).index( n ) )
        for n in item_list ) for ck in range( size ) ]
    _done_ct= 0
    _done_c= [ [ 0 ]* size for _ in range( size ) ]
    _done_r= [ [ 0 ]* size for _ in range( size ) ]
    while _done_ct< reps* 2* size** 2:
        ck0, rk0= random.choice( idx_tup ), random.choice( idx_tup )
        _op= random.choice( ( "column", "row" ) )
        if _op== "column":
            ck1= random.choice( tuple( cidx_bl_set[ ck0// sizeB ]- { ck0 } ) )
            rk= rk0
            s_rk= collections.deque( )
            while True:
                s_rk.append( rk )
                rk= cn[ ck0 ][ a[ rk ][ ck1 ] ]
                if rk== rk0:
                    break
            if len( s_rk )== size:
                continue
            for rk in s_rk:
                a[ rk ][ ck0 ], a[ rk ][ ck1 ]= a[ rk ][ ck1 ], a[ rk ][ ck0 ]
                for ck in ( ck0, ck1 ):
                    cn[ ck ][ a[ rk ][ ck ] ]= rk
                    rn[ rk ][ a[ rk ][ ck ] ]= ck
                    if _done_c[ rk ][ ck ]< reps:
                        _done_c[ rk ][ ck ]+= 1
                        _done_ct+= 1
        else:
            rk1= random.choice( tuple( ridx_bl_set[ rk0// sizeB ]- { rk0 } ) )
            ck= ck0
            s_ck= collections.deque( )
            while True:
                s_ck.append( ck )
                ck= rn[ rk0 ][ a[ rk1 ][ ck ] ]
                if ck== ck0:
                    break
            if len( s_ck )== size:
                continue
            for ck in s_ck:
                a[ rk0 ][ ck ], a[ rk1 ][ ck ]= a[ rk1 ][ ck ], a[ rk0 ][ ck ]
                for rk in ( rk0, rk1 ):
                    cn[ ck ][ a[ rk ][ ck ] ]= rk
                    rn[ rk ][ a[ rk ][ ck ] ]= ck
                    if _done_r[ rk ][ ck ]< reps:
                        _done_r[ rk ][ ck ]+= 1
                        _done_ct+= 1
        #break
    return tuple( tuple( r ) for r in a )

def obscure( a, strats= None, symmetric= True, print_progress= False ):
    import random
    size= len( a )
    sizeB= int( math.sqrt( size ) )
    b= [ list( r ) for r in a ]
    if not symmetric:
        for _ in range( 3 ):
            s_crk= [ ( ck, rk ) for rk in range( size ) for ck in range( size )
                ]
            random.shuffle( s_crk )
            for ck, rk in s_crk:
                if print_progress:
                    print( ".", end= "", flush= True )
                b[ rk ][ ck ]= 0
                try:
                    solve( b, strats )
                except MultipleSolutions:
                    b[ rk ][ ck ]= a[ rk ][ ck ]
    else:
        for _ in range( 3 ):
            s_crk= [ ( ck, rk ) for rk in range( size// 2 ) for ck in range(
                size ) ]
            if size% 2== 1:
                s_crk+= [ ( ck, size// 2 ) for ck in range( size// 2+ 1 ) ]
            random.shuffle( s_crk )
            for ck, rk in s_crk:
                if print_progress:
                    print( ".", end= "", flush= True )
                b[ rk ][ ck ]= b[ size- rk- 1 ][ size- ck- 1 ]= 0
                try:
                    solve( b, strats )
                except MultipleSolutions:
                    b[ rk ][ ck ]= a[ rk ][ ck ]
                    b[ size- rk- 1 ][ size- ck- 1 ]= a[ size- rk- 1 ][ size- ck-
                        1 ]
    if print_progress:
        print( "", sum( 1 for r in b for n in r if n!= 0 ) )
    return tuple( tuple( r ) for r in b )

def obscure_rep( a, reps= 3, strats= None, symmetric= True, print_progress=
        False ):
    min_obj= None
    for rep in range( reps ):
        b= obscure( a, strats, symmetric, print_progress )
        ct= sum( 1 for r in b for n in r if n!= 0 )
        if min_obj is None or ct< min_val:
            min_obj, min_val= b, ct
    return min_obj

def solve( a, strats= None ):
    if strats is None:
        strats= 2, 3, "cross"
    size= len( a )
    sizeB= int( math.sqrt( size ) )
    idxB_set= frozenset( range( sizeB ) )
    idx_set= frozenset( range( size ) )
    idx_bl_set= tuple( tuple( { ( ck0+ ck, rk0+ rk ) for rk in range( sizeB )
        for ck in range( sizeB ) } for ck0 in range( 0, size, sizeB ) ) for rk0
        in range( 0, size, sizeB ) )
    item_set= frozenset( range( 1, size+ 1 ) )
    b= tuple( tuple( set( item_set ) for _ in idx_set ) for _ in idx_set )
    rn= tuple( dict( ( n, set( idx_set ) ) for n in item_set ) for _ in idx_set
        )
    cn= tuple( dict( ( n, set( idx_set ) ) for n in item_set ) for _ in idx_set
        )
    bln= tuple( tuple( dict( ( n, set( ) ) for n in item_set ) for _ in range(
        sizeB ) ) for _ in range( sizeB ) )
    for rk in idx_set:
        for ck in idx_set:
            for n in item_set:
                bln[ rk// sizeB ][ ck// sizeB ][ n ].add( ( ck, rk ) )
    q= collections.deque( )
    locals0= { "done ct": 0 }
    def elim( ck, rk, n ):
        if n in b[ rk ][ ck ]:
            b[ rk ][ ck ].remove( n )
            if not b[ rk ][ ck ]:
                raise NoSolution
            rn[ rk ][ n ].remove( ck )
            cn[ ck ][ n ].remove( rk )
            bln[ rk// sizeB ][ ck// sizeB ][ n ].remove( ( ck, rk ) )
            if len( b[ rk ][ ck ] )== 1:
                locals0[ "done ct" ]+= 1
            q.append( ( ck, rk, n ) )
    for rk in idx_set:
        for ck in idx_set:
            i= a[ rk ][ ck ]
            if i== 0:
                continue
            for n in item_set- { i }:
                elim( ck, rk, n )
    while locals0[ "done ct" ]!= size** 2:
        if not q:
            raise MultipleSolutions
        ck0, rk0, rem0= q.popleft( )
        # 1^. 1*23456789. 1*23456789 . 1*23456789. 1*23456789. 1*23456789 .
        # The length of the set of the items in column A is 1 from 2.
        # "^" indicates "rem0", the item that was removed in the entry in the
        # history queue that is being examined.  "*" indicates items that can
        # newly be removed.
        if len( b[ rk0 ][ ck0 ] )== 1:
            n= next( iter( b[ rk0 ][ ck0 ] ) )
            for ck in idx_set- { ck0 }:
                elim( ck, rk0, n )
            for rk in idx_set- { rk0 }:
                elim( ck0, rk, n )
            for ck, rk in idx_bl_set[ rk0// sizeB ][ ck0// sizeB ]- { ( ck0, rk0
                    ) }:
                elim( ck, rk, n )
        # 12*3*4*5*6*7*8*. ^2345678.  2345678 .  2345678.  2345678.  2345678 .
        # The length of the set of the columns that A can occur in is 1 from 2.
        if len( rn[ rk0 ][ rem0 ] )== 1:
            ck= next( iter( rn[ rk0 ][ rem0 ] ) )
            for n in item_set- { rem0 }:
                elim( ck, rk0, n )
        if len( cn[ ck0 ][ rem0 ] )== 1:
            rk= next( iter( cn[ ck0 ][ rem0 ] ) )
            for n in item_set- { rem0 }:
                elim( ck0, rk, n )
        if len( bln[ rk0// sizeB ][ ck0// sizeB ][ rem0 ] )== 1:
            ck, rk= next( iter( bln[ rk0// sizeB ][ ck0// sizeB ][ rem0 ] ) )
            for n in item_set- { rem0 }:
                elim( ck, rk, n )
        if 2 in strats:
            # 12^. 12. 1*2*34567 . 1*2*34567. 1*2*34567. 1*2*34567 . 1*2*34567.
            # The length of the union of the items in columns AB is 2 from 3.
            if len( b[ rk0 ][ ck0 ] )== 2:
                for ckA in idx_set- { ck0 }:
                    s_n= b[ rk0 ][ ck0 ]| b[ rk0 ][ ckA ]
                    if len( s_n )== 2:
                        for ck in idx_set- { ck0, ckA }:
                            for n in s_n:
                                elim( ck, rk0, n )
                for rkA in idx_set- { rk0 }:
                    s_n= b[ rk0 ][ ck0 ]| b[ rkA ][ ck0 ]
                    if len( s_n )== 2:
                        for rk in idx_set- { rk0, rkA }:
                            for n in s_n:
                                elim( ck0, rk, n )
                for crkA in idx_bl_set[ rk0// sizeB ][ ck0// sizeB ]- { ( ck0,
                        rk0 ) }:
                    ckA, rkA= crkA
                    s_n= b[ rk0 ][ ck0 ]| b[ rkA ][ ckA ]
                    if len( s_n )== 2:
                        for ck, rk in idx_bl_set[ rk0// sizeB ][ ck0// sizeB
                                ]- { ( ck0, rk0 ), crkA }:
                            for n in s_n:
                                elim( ck, rk, n )
            # 12 3*4*. 12 3*4*. ^3456789 . 3456789. 3456789 . 3456789 . 3456789.
            # The length of the union of the columns that AB can occur in is 2
            # from 3.
            if len( b[ rk0 ][ ck0 ] )<= size- 2:
                for nA in item_set- b[ rk0 ][ ck0 ]- { rem0 }:
                    s_ck= rn[ rk0 ][ rem0 ]| rn[ rk0 ][ nA ]
                    if len( s_ck )== 2:
                        for ck in s_ck:
                            for n in item_set- { rem0, nA }:
                                elim( ck, rk0, n )
                for nA in item_set- b[ rk0 ][ ck0 ]- { rem0 }:
                    s_rk= cn[ ck0 ][ rem0 ]| cn[ ck0 ][ nA ]
                    if len( s_rk )== 2:
                        for rk in s_rk:
                            for n in item_set- { rem0, nA }:
                                elim( ck0, rk, n )
                for nA in item_set- b[ rk0 ][ ck0 ]- { rem0 }:
                    s_crk= bln[ rk0// sizeB ][ ck0// sizeB ][ rem0 ]| bln[ rk0//
                        sizeB ][ ck0// sizeB ][ nA ]
                    if len( s_crk )== 2:
                        for ck, rk in s_crk:
                            for n in item_set- { rem0, nA }:
                                elim( ck, rk, n )
        if 3 in strats:
            # 12^. 23. 13 . 1*2*3*45678. 1*2*3*45678. 1*2*3*45678 . 1*2*3*45678.
            # The length of the union of the items in columns ABC is 3 from 4.
            if 2<= len( b[ rk0 ][ ck0 ] )<= 3:
                for ckA, ckB in itertools.combinations( idx_set- { ck0 }, 2 ):
                    s_n= b[ rk0 ][ ck0 ]| b[ rk0 ][ ckA ]| b[ rk0 ][ ckB ]
                    if len( s_n )== 3:
                        for ck in idx_set- { ck0, ckA, ckB }:
                            for n in s_n:
                                elim( ck, rk0, n )
                for rkA, rkB in itertools.combinations( idx_set- { rk0 }, 2 ):
                    s_n= b[ rk0 ][ ck0 ]| b[ rkA ][ ck0 ]| b[ rkB ][ ck0 ]
                    if len( s_n )== 3:
                        for rk in idx_set- { rk0, rkA, rkB }:
                            for n in s_n:
                                elim( ck0, rk, n )
                for crkA, crkB in itertools.combinations( idx_bl_set[ rk0//
                        sizeB ][ ck0// sizeB ]- { ( ck0, rk0 ) }, 2 ):
                    ckA, rkA= crkA
                    ckB, rkB= crkB
                    s_n= b[ rk0 ][ ck0 ]| b[ rkA ][ ckA ]| b[ rkB ][ ckB ]
                    if len( s_n )== 3:
                        for ck, rk in idx_bl_set[ rk0// sizeB ][ ck0// sizeB
                                ]- { ( ck0, rk0 ), crkA, crkB }:
                            for n in s_n:
                                elim( ck, rk, n )
            # 12 4*5*. 23 4*5*. 13 4*5* . ^456789. 456789. 456789 . 456789.
            # The length of the union of the columns that ABC can occur in is 3
            # from 4.
            if len( b[ rk0 ][ ck0 ] )<= size- 3:
                for nA, nB in itertools.combinations( item_set- b[ rk0 ][ ck0 ]-
                        { rem0 }, 2 ):
                    s_ck= rn[ rk0 ][ rem0 ]| rn[ rk0 ][ nA ]| rn[ rk0 ][ nB ]
                    if len( s_ck )== 3:
                        for ck in s_ck:
                            for n in item_set- { rem0, nA, nB }:
                                elim( ck, rk0, n )
                for nA, nB in itertools.combinations( item_set- b[ rk0 ][ ck0 ]-
                        { rem0 }, 2 ):
                    s_rk= cn[ ck0 ][ rem0 ]| cn[ ck0 ][ nA ]| cn[ ck0 ][ nB ]
                    if len( s_rk )== 3:
                        for rk in s_rk:
                            for n in item_set- { rem0, nA, nB }:
                                elim( ck0, rk, n )
                for nA, nB in itertools.combinations( item_set- b[ rk0 ][ ck0 ]-
                        { rem0 }, 2 ):
                    s_crk= bln[ rk0// sizeB ][ ck0// sizeB ][ rem0 ]| bln[ rk0//
                        sizeB ][ ck0// sizeB ][ nA ]| bln[ rk0// sizeB ][ ck0//
                        sizeB ][ nB ]
                    if len( s_crk )== 3:
                        for ck, rk in s_crk:
                            for n in item_set- { rem0, nA, nB }:
                                elim( ck, rk, n )
        if "cross" in strats:
            # ^234567.  234567.  234567. |
            # 1234567. 1234567. 1234567. | 1*234567. 1*234567. 1*234567.
            # The length of the set of the rows that A can occur in in the block
            # it was removed from is 1 from 2.
            s_ck= { ck for ck, rk in bln[ rk0// sizeB ][ ck0// sizeB ][ rem0 ] }
            s_rk= { rk for ck, rk in bln[ rk0// sizeB ][ ck0// sizeB ][ rem0 ] }
            if len( s_ck )== 1:
                ck= next( iter( s_ck ) )
                for rk in idx_set- s_rk:
                    elim( ck, rk, rem0 )
            if len( s_rk )== 1:
                rk= next( iter( s_rk ) )
                for ck in idx_set- s_ck:
                    elim( ck, rk, rem0 )
            # 1*234567. 1*234567. 1*234567. |
            # 1 234567. 1 234567. 1 234567. | ^234567. 234567. 234567.
            # The set of the columns that A can occur in in a row is a subset of
            # the set of columns in a block.
            for bl_ck in idxB_set- { ck0// sizeB }:
                s_ck_bl= { ck for ck, rk in bln[ rk0// sizeB ][ bl_ck ][ rem0 ]
                    }
                if rn[ rk0 ][ rem0 ]<= s_ck_bl:
                    for ck, rk in bln[ rk0// sizeB ][ bl_ck ][ rem0 ].copy( ):
                        if rk!= rk0:
                            elim( ck, rk, rem0 )
            for bl_rk in idxB_set- { rk0// sizeB }:
                s_rk_bl= { rk for ck, rk in bln[ bl_rk ][ ck0// sizeB ][ rem0 ]
                    }
                if cn[ ck0 ][ rem0 ]<= s_rk_bl:
                    for ck, rk in bln[ bl_rk ][ ck0// sizeB ][ rem0 ].copy( ):
                        if ck!= ck0:
                            elim( ck, rk, rem0 )
    
    res= tuple( tuple( next( iter( s ) ) for s in r ) for r in b )
    return res

def verify( a ):
    size= len( a )
    sizeB= int( math.sqrt( size ) )
    assert all( len( r )== size for r in a )
    range0= set( range( 1, size+ 1 ) )
    for r in a:
        assert set( r )== range0
    for ck in range( size ):
        assert set( r[ ck ] for r in a )== range0
    for rk0 in range( 0, size, sizeB ):
        for ck0 in range( 0, size, sizeB ):
            assert set( a[ rk0+ rk ][ ck0+ ck ] for ck in range( sizeB ) for rk
                in range( sizeB ) )== range0

def print0( a ):
    for r in a:
        print( " ".join( "".join( str( k ) if k in s else " " for k in range( 1,
            10 ) )+ "." for s in r ) )
    print( )

def print0r( rn ):
    size= len( rn )
    for r in rn:
        print( " ".join( "".join( str( k ) if k in s else " " for k in range(
            size ) )+ "." for _, s in sorted( r.items( ) ) ) )
    print( )

def print0c( cn ):
    size= len( rn )
    for c in cn:
        print( " ".join( "".join( str( k ) if k in s else " " for k in range(
            size ) )+ "." for _, s in sorted( c.items( ) ) ) )
    print( )

def print1( a ):
    for r in a:
        print( r )
    print( )


if __name__== "__main__":
    a= scramble( 9,1 )
    print1( a )
    verify( a )
    strats= ( "cross", 2 )
    b= obscure_rep( a, 3, strats, print_progress= True )
    print1( b )
    c= solve( b, strats )
    assert c== a
