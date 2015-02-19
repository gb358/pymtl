#=======================================================================
# verilog.py
#=======================================================================

from __future__ import print_function

import re
import os
import collections

from pymtl import *

from ..translation.verilog_structural import (
  tab, endl, port_delim, pretty_align,
  title_bar, header, start_mod, port_declarations, end_mod,
  start_param, end_param, start_ports, end_ports, connection,
)

#-----------------------------------------------------------------------
# VerilogModel
#-----------------------------------------------------------------------
class VerilogModel( Model ):
  """
  A PyMTL model for importing hand-written Verilog modules.

  Attributes:
    modulename  Name of the Verilog module to import.
    sourcefile  Location of the .v file containing the module.
  """

  modulename   = None
  sourcefile   = None

  _is_verilog  = True
  _param_dict  = None
  _port_dict   = None

  #---------------------------------------------------------------------
  # set_params
  #---------------------------------------------------------------------
  def set_params( self, param_dict ):
    """Specify values for each parameter in the imported Verilog module.

    Note that param_dict should be a dictionary that provides a mapping
    from parameter names (strings) to parameter values, for example:

    >>> s.set_params({
    >>>   'param1': 5,
    >>>   'param2': 0,
    >>> })
    """

    self._param_dict = collections.OrderedDict( sorted(param_dict.items()) )

  #---------------------------------------------------------------------
  # set_ports
  #---------------------------------------------------------------------
  def set_ports( self, port_dict ):
    """Specify values for each parameter in the imported Verilog module.

    Note that port_dict should be a dictionary that provides a mapping
    from port names (strings) to PyMTL InPort or OutPort objects, for
    examples:

    >>> s.set_ports({
    >>>   'clk':    s.clk,
    >>>   'reset':  s.reset,
    >>>   'input':  s.in_,
    >>>   'output': s.out,
    >>> })
    """

    self._port_dict = collections.OrderedDict( sorted(port_dict.items()) )

  #---------------------------------------------------------------------
  # _auto_init
  #---------------------------------------------------------------------
  def _auto_init( self ):
    """Infer fields not set by user based on Model attributes."""

    if not self.modulename:
      self.modulename = self.__class__.__name__

    if not self.sourcefile:
      self.sourcefile = os.path.join( os.path.dirname(__file__),
                                      'verilog',
                                      self.modulename+'.v' )

    if not self._param_dict:
      self._param_dict = self._args

    if not self._port_dict:
      self._port_dict = { port.name: port for port in self.get_ports() }

#-----------------------------------------------------------------------
# import_module
#-----------------------------------------------------------------------
def import_module( model, o ):
  """Generate Verilog source for a user-defined VerilogModule and return
  the name of the source file containing the imported component.
  """

  symtab = [()]*4

  print( header              ( model,    symtab ), file=o, end='' )
  print( start_mod.format    ( model.class_name ), file=o,        )
  print( port_declarations   ( model,    symtab ), file=o, end='' )
  print( _instantiate_verilog( model            ), file=o         )
  print( end_mod  .format    ( model.class_name ), file=o )
  print( file=o )

  return model.sourcefile

#-----------------------------------------------------------------------
# import_sources
#-----------------------------------------------------------------------
def import_sources( source_list, o ):
  """Import Verilog source from all Verilog files source_list, as well
  as any source files specified by `include within those files.
  """

  # Regex to extract verilog filenames from `include statements

  include_re = re.compile( r'"(?P<filename>[\w/\.-]*)"' )

  # Iterate through all source files and add any `include files to the
  # list of source files to import.

  for verilog_file in source_list:

    include_path = os.path.dirname( verilog_file )
    with open( verilog_file, 'r' ) as fp:
      for line in fp:
        if '`include' in line:
          filename = include_re.search( line ).group( 'filename' )
          fullname = os.path.join( include_path, filename )
          if fullname not in source_list:
            source_list.append( fullname )

  # Iterate through all source files in reverse order and write out all
  # source code from imported/`included verilog files. Do this in reverse
  # order to (hopefully) resolve any `define dependencies, and remove any
  # lines with `include statements.

  for verilog_file in reversed( source_list ):
    src = title_bar.replace('-','=').format( verilog_file )

    with open( verilog_file, 'r' ) as fp:
      for line in fp:
        if '`include' not in line:
          src += line

    print( src, file=o )

#-----------------------------------------------------------------------
# _instantiate_verilog
#-----------------------------------------------------------------------
def _instantiate_verilog( model ):

  model._auto_init()

  params = [ connection.format(k, v) for k,v in model._param_dict.items() ]

  connections = []
  for verilog_portname, port in model._port_dict.items():
    connections.append( connection.format( verilog_portname, port.name ) )
  connections = pretty_align( connections, '(' )

  s  = tab + '// Imported Verilog source from:' + endl
  s += tab + '// {}'.format( model.sourcefile ) + endl
  s += endl
  s += tab + model.modulename + start_param + endl
  s += port_delim.join( params ) + endl
  s += tab + end_param + tab + 'verilog_import' + endl
  s += tab + start_ports + endl
  s += port_delim.join( connections ) + endl
  s += tab + end_ports + endl

  return s


