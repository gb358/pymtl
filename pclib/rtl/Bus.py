#=======================================================================
# Bus.py
#=======================================================================

from pymtl import *

class Bus( Model ):

  def __init__( s, nports, dtype ):

    sel_nbits = clog2( nports )

    s.in_ = [ InPort  ( dtype )     for _ in range( nports ) ]
    s.out = [ OutPort ( dtype )     for _ in range( nports ) ]
    s.sel =   InPort  ( sel_nbits )

    @s.combinational
    def comb_logic():

      for i in range( nports ):
        s.out[i].value = s.in_[ s.sel ]

  def line_trace( s ):
    in_str  = ' '.join( [ str(x) for x in s.in_ ] )
    sel_str = str( s.sel )
    out_str = ' '.join( [ str(x) for x in s.out ] )
    return '{} ( {} ) {}'.format( in_str, sel_str, out_str )
