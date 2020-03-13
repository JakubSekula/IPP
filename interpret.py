#!/usr/bin/env python3

import sys
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from glob import glob

source = ""
input = ""
order_inc = 0

def params():

    entered = 0
    help = 0
    global source
    global input

    for arg in sys.argv:
        if ( arg == "--help" ):
            help = 1
        elif ( re.search( '^(\-){2}source=(((\.\.\/)|(\S))+(\/)*)+$', arg ) ):
            source = arg.split( "=" )[ 1 ]
            if Path( source ).is_file():
                ...
            else:
                exit( 11 )
            entered = entered + 1
        elif ( re.search( '^(\-){2}input=(((\.\.\/)|(\S))+(\/)*)+$', arg ) ):
            input = arg.split( "=" )[ 1 ]
            if Path( input ).is_file():
                ...
            else:
                exit( 11 )
            entered = entered + 1
        elif ( arg == "interpret.py" ):
            ...
        else:
            exit( 10 )
    if ( ( help == 1 ) and entered >= 1 ):
        exit( 10 )
    elif ( entered == 0 ):
        exit( 10 )

def well_formatted():
    global source
    
    def parsefile( file ):
        parser = make_parser(  )
        parser.setContentHandler(ContentHandler(  ))
        parser.parse( file )

    try:
        parsefile( source )
    except:
        exit( 31 )

def execute( program ):
    
    global order_inc
    
    i = 0

    while i < order_inc:
        print( program[ i ] )
        i = i + 1

params()
well_formatted()

tree = ET.parse( source )
root = tree.getroot()

program = root.tag

if( program != 'program' ):
    exit(105)

header = root.attrib

if( header[ 'language' ] != "IPPcode20" ):
    exit( 105 )

instructions = []

for instr in root.findall( 'instruction' ):

    array_test = []

    order = instr.get( 'order' )
    order_inc = order_inc + 1

    if ( not( order_inc <= int( order ) ) ):
        exit( 32 )

    opcode = instr.get( 'opcode' )
    #print( order,opcode )
    array_test.append( order_inc )
    array_test.append( opcode )
    i = 0

    args = []

    for test in instr:
        arg_array = []
        arg_array.append( test.attrib[ 'type' ] )
        arg_array.append( test.text )
        args.append( arg_array )
       #print( test.attrib, test.text )
    array_test.append( args )
    instructions.append( array_test )

execute( instructions )