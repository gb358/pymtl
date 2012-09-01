#=========================================================================
# RegIncrStruct Unit Tests
#=========================================================================

from pymtl import *

from RegIncrStruct import RegIncrStruct

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def harness( inouts ):

  model = RegIncrStruct()
  model.elaborate()

  sim = SimulationTool( model )
  sim.dump_vcd( "RegIncrStruct_test.vcd" )
  sim.reset()

  for inout in inouts:
    model.in_.value = inout[0]
    sim.cycle()
    assert model.out.value == inout[1]

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics():
  harness([
    # in   out
    [  1,   2 ],
    [  2,   3 ],
    [ 13,  14 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 51,  52 ],
    [ 51,  52 ],
  ])
