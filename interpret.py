#!/usr/bin/env python3

###                                                         ###
###         Jakub Sekula ( xsekul01 ) 2019/2020 IPP         ###
###                                                         ###

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
JUMP = 0

GF = dict()
LF = dict()
TF = dict()
LABEL = dict()
UNTIL = dict()

GFT = dict()
LFT = dict()
TFT = dict()

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

def at_split( token ):
    token1 = token.split( "@", 1 )[ 0 ]
    token2 = token.split( "@", 1 )[ 1 ]

    return ( token1, token2 )

def symbget( token ):
    data_type = ''
    content = ''
    if( token[ 1 ] != None ):
        data_type, content = token[ 0 ], token[ 1 ]
    else:
        data_type, content = token[ 0 ], ''
    if ( data_type == "string" ):
        data_type = str
    if ( data_type == "nil" ):
        data_type = None
    return ( data_type, content )

def frameExists( frame, var ):
    
    global GF
    global TF
    global LF

    if( frame == "GF" ):
        if not var in GF:
            exit( 54 )
    elif( frame == "LF" ):
        if not var in LF:
            exit( 54 )
    elif( frame == "TF" ):
        if not var in TF:
            exit( 54 )

def getFromFrame( frame, variable ):
    frameExists( frame, variable )
    if ( frame == "GF" ):
        return ( GF[ variable ] )
    elif( frame == "TF" ):
        return ( TF[ variable ] )
    elif ( frame == "LF" ):
        return ( LF[ variable ] )

def writeTo( where, content, data_type ):
    frame, variable = at_split( where )
    frameExists( frame, variable )
    if( frame == "GF" ):
        GF[ variable ] = content
        GFT[ variable ] = data_type
    elif( frame == "TF" ):
        TF[ variable ] = content
        TFT[ variable ] = data_type
    elif( frame == "LF" ):
        LF[ variable ] = content
        LFT[ variable ] = data_type

def checkVar( argument ):
    if ( not ( re.search( '^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|([a-zA-Z]))(\d*|([a-zA-Z])|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$', argument ) ) ):
        exit( 23 )

def checkSymb( argument ):
    if( argument == None ):
        return
    if ( not ( re.search( '(int@((\-)|(\+)){0,1}(0-9)+)$|(bool@((true)|(false)))$|^((GF)|(TF)|(LF))@(\S)*$|^(nil)@nil$|^string@(\S)*$', argument ) ) ):
        exit( 23 )
    elif( not ( re.search( '([^#\s\\\\]|\\\\[0-9]{3})*$', argument ) ) ):
        exit( 23 )

def checkInt( argument ):
    if ( not ( re.search( '^(\d)*$', argument ) ) ):
        exit( 23 )

def checkString( argument ):
    if( argument == None ):
        return
    if ( not ( re.search( '^([^#\s\\\\]|\\\\[0-9]{3})*$', argument ) ) ):
        exit( 23 )

def checkBool( argument ):
    if ( not ( re.search( '^((true)|(false))$', argument ) ) ):
        exit( 23 )

def checkNil( argument ):
    if ( not ( re.search( '^nil$', argument ) ) ):
        exit( 23 )

def getBool( argument ):
    if( argument == "true" ):
        return( True )
    else:
        return ( False )

def check_args( args, expected ):
    i = 0
    maxe = len( expected )
    maxa = len ( args )
    
    while ( i < maxa ):
        if( expected[ i ] == "var" ):
            checkVar( args[ i ][ 1 ] )
        elif( expected[ i ] == "symb" ):
            if( args[ i ][ 0 ] == "GF" or args[ i ][ 0 ] == "TF" or args[ i ][ 0 ] == "LF" ):
                checkSymb( args[ i ][ 1 ] )
            elif( args[ i ][ 0 ] == "var" ):
                checkVar( args[ i ][ 1 ] )
            elif( args[ i ][ 0 ] == "int" ):     
                checkInt( args[ i ][ 1 ] )
            elif( args[ i ][ 0 ] == "string" ):     
                checkString( args[ i ][ 1 ] )
            elif( args[ i ][ 0 ] == "bool" ):
                checkBool( args[ i ][ 1 ] )
            elif( args[ i ][ 0 ] == "nil" ):
                checkNil( args[ i ][ 1 ] )
            else:
                print( "!!! Je potreba osetrit:" )
                print( args[ i ][ 0 ] ,args[ i ][ 1 ] )
        i += 1

def getValue( argument ):
    if( re.search( '^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|([a-zA-Z]))(\d*|([a-zA-Z])|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$', argument ) ):
        frame, variable = at_split( argument )
        code = getFromFrame( frame, variable )
        return code
    else:
        return argument

def getType( argument ):

    global GFT
    global TFT
    global LFT

    if( argument[ 0 ] == "var" ):
        frame, content = at_split( argument[ 1 ] )
        if( frame == "GF" ):
            return ( GFT[ content ] )
        elif( frame == "LF" ):
            return ( LFT[ content ] )
        elif( frame == "TF" ):
            return ( TFT[ content ] )
    elif( argument[ 0 ] == "int" ):
        return ( int )
    elif( argument[ 0 ] == "string" ):
        return ( str )
    elif( argument[ 0 ] == "bool" ):
        return ( bool )


def line_handler( key_word, args, i ):
    global GF
    global TF
    global LF
    global LABEL
    global UNTIL
    global JUMP

    global GFT
    global TFT
    global LFT

    if ( JUMP == 1 and key_word != "LABEL" ):
        return i
    if ( key_word == "DEFVAR" ):
        check_args( args, [ 'var' ] )
        for word in args:
            if( word[ 0 ] == "var" ):
                frame, variable = at_split( word[ 1 ] )
                if( frame == "GF" ):
                    if variable in GF:
                        exit( 52 )
                    GF[ variable ] = ''
                elif( frame == "TF" ):
                    if variable in TF:
                        exit( 52 )
                    TF[ variable ] = ''
                elif( frame == "LF" ):
                    if variable in LF:
                        exit( 52 )
                    LF[ variable ] = ''
                else:
                    exit( 55 )
    elif( key_word == "MOVE" ):
        check_args( args, [ 'var', 'symb' ] )
        frame = ''
        data_type = ''
        content = ''
        count = 0
        to_frame = ''
        for word in args:
            count = count + 1
            if( word[ 0 ] == "var" and count == 1 ):
                to_frame = word[ 1 ]
            else:
                data_type, content = symbget( word )
            if( data_type != '' ):
                writeTo( to_frame, content, data_type )
    elif( key_word == "LABEL" ): # co se ma stat kdyz budu skakat a narazim na label ktery neni ten na ktery skacu mel bych ho zapsat nebo ne ?
        if( JUMP == 1 ):
            if ( UNTIL[ 'LOOK' ] == args[ 0 ][ 1 ] ):
                dict.clear( UNTIL )
                JUMP = 0
                return i
        for word in args:
            if ( word[ 0 ] == "label" ):
                LABEL[ word[ 1 ] ] = i
    elif( key_word == "JUMPIFEQ" ):
        first = ''
        second = ''
        secondT = ''
        label = ''
        for word in args:
            if( word[ 0 ] == "label" ):
                label = word[ 1 ]
            elif( word[ 0 ] == "var" ):
                var = getValue( word[ 1 ] )
                first = var
            else:
                data_type, content = symbget( word )
                second = content
                secondT = data_type
        if ( ( not ( type( first ) is secondT ) ) or ( type( first ) is None or secondT == None ) ):
            exit( 53 )
        if( first == second ):
            UNTIL[ 'LOOK' ] = label
            JUMP = 1
    elif( key_word == "WRITE" ):
        for word in args:
            if ( word[ 0 ] == "var" ):
                var = getValue( word[ 1 ] )
                print( var, end='' )
            elif( word[ 0 ] == "string" ):
                write = re.sub( '\\\\032', ' ', word[ 1 ] )
                write = re.sub( '\\\\010', '\n', write )
                write = re.sub( '\\\\092', '\\\\', write )
                write = re.sub( '\\\\035', '#', write )
                print( write, end='' )
            elif( word[ 0 ] == "nil" ):
                print( '', end='' )
            elif( word[ 0 ] == "bool" ):
                if( word[ 1 ] == "true" ):
                    print( 'true', end='' )
                elif( word[ 1 ] == "false" ):
                    print( 'false', end='' )
    elif( key_word == "CONCAT" ):
        where = ''
        count = 0
        first = ''
        second = ''
        write = ''
        for word in args:
            count = count + 1
            if ( word[ 0 ] == "var" ):
                var = getValue( word[ 1 ] )
                if( count == 1 ):
                    where = word[ 1 ]
                elif( count == 2 ):
                    first = var
                else:
                    second = var
            else:
                if ( count == 0 ):
                    exit( 105 )
                data_type, content = symbget( word )
                second = content
                secondT = data_type
        first = first + second
        writeTo( where, first, data_type )
    elif( key_word == "JUMP" ):
        for word in args:
            if ( word[ 0 ] == "label" ):
                return( LABEL[ word[ 1 ] ] )
    elif( key_word == "STRLEN" ):
        to_frame = ''
        chars = 0
        count = 0
        for word in args:
            count = count + 1
            if( count == 1 ):
                if( word[ 0 ] == "var" ):
                    to_frame = word[ 1 ]   
            elif( count == 2 ):
                if( word[ 0 ] == "var" ):
                    var = getValue( word[ 1 ] )
                    chars = len( var )
        writeTo( to_frame, chars, type( chars ) )
    elif( key_word == "EXIT" ):
        #dodelat check symb
        for word in args:
            code = getValue( word[ 1 ] )
            if( code >= 0 and code <= 49 ):
                exit( 3 )
            else:
                exit( 57 )
    elif( key_word == "DPRINT" ): #je to opravdu na stderr ? :D
        # checksymb
        for word in args:
            code = getValue( word[ 1 ] )
            sys.stderr.write( str( code ) )
    elif( key_word == "ADD" or key_word == "SUB" or key_word == "MUL" or key_word == "IDIV" or key_word == "LT" or key_word == "GT" or key_word == "EQ"
          or key_word == "AND" or key_word == "OR" or key_word == "NOT" or key_word == "STRI2INT" ): # nyni umoznuji aby datovy typ nebyl jen int coz je chyba
        check_args( args, [ 'var','symb', 'symb' ] )
        counter = 0
        to_frame = ''
        op1 = 0
        op2 = 0
        op1t = ''
        op2t = ''

        for word in args:
            if( counter == 0 ):
                to_frame = word[ 1 ]
            elif( counter == 1 ):
                op1 = getValue( word[ 1 ] )
                op1t = getType( word )
            elif( counter == 2 ):
                op2 = getValue( word[ 1 ] )
                op2t = getType( word )
            counter += 1
        if( key_word == "ADD" ):
            if( op1t == op2t ):
                op1 = int( op1 ) + int( op2 )
            else:
                exit( 53 )
        elif( key_word == "SUB" ):
            if( op1t == op2t ):
                op1 = int( op1 ) - int( op2 )
            else:
                exit( 53 )
        elif( key_word == "MUL" ):
            if( op1t == op2t ):
                op1 = int( op1 ) * int( op2 )
            else:
                exit( 53 )
        elif( key_word == "IDIV" ):
            if( op1t == op2t ):
                if( int( op2 ) == 0 ):
                    exit( 57 )
                op1 = int( op1 ) / int( op2 )
                op1 = int( op1 )
            else:
                exit( 53 )
        elif( key_word == "LT" ): # jeste nil
            if( op1t == op2t ):
                vysledek = ''
                poradi = 0
                if( op1t is str ):
                    words = [ op1, op2 ]
                    words.sort()
                    for heej in words: 
                        if( poradi == 0 ):
                            vysledek = heej
                        poradi += 1 
                    if ( vysledek == op1 ):
                        op1 = True
                    else:
                        op1 = False
                elif( op1t is int ):
                    if( op1 < op2 ):
                        op1 = True
                    else:
                        op2 = False
                elif( op1t is bool ):
                    op1 = getBool( op1 )
                    op2 = getBool( op2 )
                    if( op1 < op2 ):
                        op1 = True
                    else:
                        op1 = False
        elif( key_word == "GT" ):
            if( op1t == op2t ):
                vysledek = ''
                poradi = 0
                if( op1t is str ):
                    words = [ op1, op2 ]
                    words.sort()
                    for heej in words: 
                        if( poradi == 0 ):
                            vysledek = heej
                        poradi += 1 
                    if ( vysledek == op1 ):
                        op1 = False
                    else:
                        op1 = True
                elif( op1t is int ):
                    if( op1 > op2 ):
                        op1 = True
                    else:
                        op1 = False
                elif( op1t is bool ):
                    op1 = getBool( op1 )
                    op2 = getBool( op2 )
                    if( op1 > op2 ):
                        op1 = True
                    else:
                        op1 = False
        elif( key_word == "EQ" ):
            if( op1t == op2t ):
                if( op1t is str ):
                    if( op1 == op2 ):
                        op1 = True
                    else:
                        op1 = False
                elif( op1t is int ):
                    if ( op1 == op2 ):
                        op1 = True
                    else:
                        op1 = False
                elif( op1t is bool ):
                    op1 = getBool( op1 )
                    op2 = getBool( op2 )
                    if( op1 == op2 ):
                        op1 = True
                    else:
                        op1 = False
        elif( key_word == "AND" ):
            if( op1t == op2t and op1t is bool ):
                op1 = getBool( op1 )
                op2 = getBool( op2 )
                op1 = op1 and op2
            else:
                exit( 53 )
        elif( key_word == "OR" ):
            if( op1t == op2t and op1t is bool ):
                op1 = getBool( op1 )
                op2 = getBool( op2 )
                op1 = op1 or op2
            else:
                exit( 53 )
        elif( key_word == "NOT" ):
            if( op1t is bool ):
                op1 = getBool( op1 )
                op2 = getBool( op2 )
                op1 = not op1
            else:
                exit( 53 )
        elif( key_word == "STRI2INT" ):
            if( op1t is not str ):
                exit( 53 )
            if( op2t is not int ):
                exit( 53 )
            try:
                op1 = ord( op1[ int( op2 ) ] )
            except:
                exit( 58 )
        writeTo( to_frame, op1, type( op1 ) )
    elif( key_word == "INT2CHAR" ):
        check_args( args, [ 'var','symb' ] )
        
        to_frame = ''
        counter = 0
        ip1 = 0
        op1t = ''
        
        for word in args:
            if( counter == 0 ):
                to_frame = word[ 1 ]
            elif( counter == 1 ):
                op1 = getValue( word[ 1 ] )
                op1t = getType( word )
            counter += 1
        if( op1t is not int ):
            exit( 53 )
        try:
            op1 = chr( int( op1 ) )
        except:
            exit( 58 )
        writeTo( to_frame, op1, type( op1 ) )
    else:
        exit( 32 )
    return i


def execute( program ):
    
    global order_inc
    
    i = 0

    while i < order_inc:
        i = line_handler( program[ i ][ 1 ], program[ i ][ 2 ], i )
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

""" for test in GF:
    print( test, GF[test] )

for test in TF:
    print( test, TF[test] )

for test in LF:
    print( test, LF[test] )

for test in LABEL:
    print( test, LABEL[test] )  """