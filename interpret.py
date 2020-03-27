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
input_file = ""
input_is = "stdin"
source_is = "stdin"
order_inc = 0
instruction_counter = 0
JUMP = 0
RUN = 0

PUSHS = []

GF = dict()
LF = dict()
TF = dict()
LABEL = dict()
UNTIL = dict()

GFT = dict()
LFT = dict()
TFT = dict()

FRAME_STACK = []
FRAME_STACK_T = []
CALL_STACK = []

tf_accessible = 0
lf_accessible = 0

def params():

    entered = 0
    help = 0
    global source
    global input_file

    global source_is
    global input_is

    for arg in sys.argv:
        if ( arg == "--help" ):
            help = 1
        elif ( re.search( '^(\-){2}source=(((\.\.\/)|(\S))+(\/)*)+$', arg ) ):
            source = arg.split( "=" )[ 1 ]
            source_is = "file"
            if Path( source ).is_file():
                ...
            else:
                exit( 11 )
            entered = entered + 1
        elif ( re.search( '^(\-){2}input=(((\.\.\/)|(\S))+(\/)*)+$', arg ) ):
            input_file = arg.split( "=" )[ 1 ]
            if Path( input_file ).is_file():
                input_is = "file"
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

def convertor( argument ):
    start = argument.split("\\")[ 0 ]
    finish = argument.split("\\")[ 1 ]
    if( finish[ 0 ] == str( 0 ) ):
        convert = finish[ 1 ] + finish[ 2 ]
        finish = list( finish )
        finish[ 0 ] = ''
        finish[ 1 ] = ''
        finish[ 2 ] = ''
        finish = ''.join( finish )
    else:
        convert = finish[ 0 ] + finish[ 1 ] + finish[ 2 ]
        finish = list( finish )
        finish[ 0 ] = ''
        finish[ 1 ] = ''
        finish[ 2 ] = ''
        finish = ''.join( finish )
    convert = chr( int( convert ) )
    return( start + str( convert ) + finish )

def well_formatted( source ):
    try:
        xml = ET.fromstring( source )
    except:
        exit( 105 )

def at_split( token ):
    token1 = token.split( "@", 1 )[ 0 ]
    token2 = token.split( "@", 1 )[ 1 ]

    return ( token1, token2 )

def varExists( frame, var ):
    
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
    varExists( frame, variable )
    frameExists( frame )
    if ( frame == "GF" ):
        return ( GF[ variable ] )
    elif( frame == "TF" ):
        return ( TF[ variable ] )
    elif ( frame == "LF" ):
        return ( LF[ variable ] )

def frameExists( frame ):
    global tf_accessible
    global lf_accessible

    if( ( frame == "TF" and tf_accessible == 0 ) or ( frame == "LF" and lf_accessible == 0 ) ):
        exit( 55 )

def writeTo( where, content, data_type ):
    frame, variable = at_split( where )
    frameExists( frame )
    varExists( frame, variable )
    if( data_type is str ):
        data_type = "str"
    if( frame == "GF" ):
        GF[ variable ] = content
        GFT[ variable ] = data_type
    elif( frame == "TF" ):
        TF[ variable ] = content
        TFT[ variable ] = data_type
    elif( frame == "LF" ):
        LF[ variable ] = content
        LFT[ variable ] = data_type

def missingValue( op1, op2 ):
    if( op1 == '' or op2 == '' ):
        exit( 56 )

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
    if ( not ( re.search( '^((\-)|(\+)){0,1}(\d)*$', argument ) ) ):
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

def checkType( argument ):
    if( not ( argument == "int" or argument == "bool" or argument == "string" ) ):
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

    if( maxe == 0 and maxa == 0 ):
        return
    elif( maxe == 0 and maxa != 0 ):
        exit( 53 )

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
            elif( args[ i ][ 0 ] == "nil" ):
                checkType( args[ i ][ 1 ] )
            else:
                print( "!!! Je potreba osetrit:" )
                print( args[ i ][ 0 ] ,args[ i ][ 1 ] )
        i += 1

def getValue( argument ):
    if( argument is None ):
        return
    if( re.search( '^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|([a-zA-Z]))(\d*|([a-zA-Z])|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$', argument ) ):
        frame, variable = at_split( argument )
        frameExists( frame )
        code = getFromFrame( frame, variable )
        return code
    else:
        return argument

def convert( first, second ):
    if( ( first is None ) or ( second is None ) ):
        ...
    else:
        if( re.search( '\\\d{0,3}', first ) ):
            first = convertor( first )
        if( re.search( '\\\d{0,3}', second ) ):
            second = convertor( second )
    return ( first, second )

def getType( argument ):

    global GFT
    global TFT
    global LFT

    """ print( "!!!!!!" )
    print( argument ) """

    #print( "GETTYPE: ", argument )
    if( argument[ 0 ] == "var" ):
        frame, content = at_split( argument[ 1 ] )
        if( frame == "GF" ):
            try:
                return ( GFT[ content ] )
            except:
                return None
        elif( frame == "LF" ):
            try:
                return ( LFT[ content ] )
            except:
                return None
        elif( frame == "TF" ):
            try:
                return ( TFT[ content ] )
            except:
                return None
    elif( argument[ 0 ] == "int" ):
        return "int"
    elif( argument[ 0 ] == "string" ):
        return "str"
    elif( argument[ 0 ] == "bool" ):
        return "bool"
    elif( argument[ 0 ] == "nil" ):
        return( "nil" )
    elif( re.search( '^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|([a-zA-Z]))(\d*|([a-zA-Z])|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$', argument ) ):
        frame, content = at_split( argument )
        if( frame == "GF" ):
            try:
                return ( GFT[ content ] )
            except:
                return None
        elif( frame == "LF" ):
            try:
                return ( LFT[ content ] )
            except:
                return None
        elif( frame == "TF" ):
            try:
                return ( TFT[ content ] )
            except:
                return None

def jump( label, i ):
    
    global LABEL

    if( label in LABEL ):
        return( LABEL[ label ] )
    else:
        exit( 52 )

def labelThing( key_word, args, i ):
    
    global LABEL

    if( key_word == "LABEL" ):
        check_args( args, [ 'label' ] )
        label = args[ 0 ][ 1 ]
        if( label in LABEL ):
            exit( 52 )
        else:
            LABEL[ label ] = i
    return i

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

    global instruction_counter
    global input_is
    global tf_accessible
    global lf_accessible

    global FRAME_STACK
    global FRAME_STACK_T
    global CALL_STACK

    global PUSHS

    instruction_counter += 1

    to_frame = ""
    content = ''
    data_type = ""
    first = ''
    firstT = ''
    second = ''
    secondT = ''
    label = ''
    count = 0
    op1 = None
    op2 = None
    op1t = ''
    op2t = ''

    if ( key_word == "DEFVAR" or key_word == "POPS" ):
        check_args( args, [ 'var' ] )
        for word in args:
            if( word[ 0 ] == "var" ):
                to_frame = word
        if( key_word == "DEFVAR" ):
            frame, variable = at_split( to_frame[ 1 ] )
            frameExists( frame )
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
        elif( key_word == "POPS" ):
            try:
                content = PUSHS.pop()
                data_type = content[ 1 ]
                content = content[ 0 ]
            except:
                exit( 56 )
            writeTo( to_frame[ 1 ], content, data_type )
    elif( key_word == "MOVE" ):
        check_args( args, [ 'var', 'symb' ] )
        for word in args:
            count = count + 1
            if( word[ 0 ] == "var" and count == 1 ):
                to_frame = word[ 1 ]
            else:
                content = getValue( word[ 1 ] )
                data_type = getType( word )
                if( content == '' and data_type is None ):
                    exit( 56 )
            if( data_type != '' ):
                if ( content == "nil" ):
                    content = ''
                    data_type = "nil"
                if( data_type == "str" and content is None ):
                    content = ''
                writeTo( to_frame, content, data_type )
    elif( key_word == "LABEL" ):
        ...
    elif( key_word == "JUMPIFEQ" or key_word == "JUMPIFNEQ" ):
        for word in args:
            if( word[ 0 ] == "label" and count == 0 ):
                label = word[ 1 ]
            elif( word[ 0 ] == "var" ):
                var = getValue( word[ 1 ] )
                if( count == 1 ):
                    first = var
                    firstT = getType( word[ 1 ] )
                else:
                    second = var
                    secondT = getType( word[ 1 ] )
            else:
                content = getValue( word[ 1 ] )
                data_type = getType( word )
                if( count == 2 ):
                    second = content
                    secondT = data_type
                else:
                    first = content
                    firstT = data_type
            count += 1
        if( label in LABEL ):
            ...
        else:
            exit( 52 )
        if ( ( ( firstT != secondT ) or ( secondT != firstT  ) ) ):
            if( ( firstT is None or secondT is None ) or ( firstT == "nil" or secondT == "nil" ) ):
                ...
            else:
                exit( 53 )
        if( key_word == "JUMPIFEQ" ):
            if( first == "nil" or second == "nil" ):
                if( first == "nil" and second == "nil" ):
                    return( jump( label, i ) )
            elif( firstT is None and secondT is None ):
                if( first == second ):
                    return( jump( label, i ) )
            elif( firstT == "int" or secondT == "int" ):
                if( secondT is None or firstT is None ):
                    exit( 56 )
                elif( int( first ) == int( second ) ):
                    return( jump( label, i ) )
            elif( firstT == "str" or secondT == "str" ):
                if( secondT is None or firstT is None ):
                    return( jump( label, i ) )
                first, second = convert( first, second )
                if( secondT is None ):
                    ...
                elif( str( first ) == str( second ) ):
                    return( jump( label, i ) )
            elif( firstT == "bool" or secondT == "bool" ):
                if( secondT is None or firstT is None ):
                    return( jump( label, i ) )
                if( first ==  second  ):
                    return( jump( label, i ) )
        elif( key_word == "JUMPIFNEQ" ):
            if( first == "nil" or second == "nil" ):
                if( first == "nil" and second == "nil" ):
                    ...
                else:
                    return( jump( label, i ) )
            elif( firstT is None and secondT is None ):
                if( first != second ):
                    return( jump( label, i ) )
            elif( firstT == "int" or secondT == "int" ):
                if( secondT is None or firstT is None ):
                    exit( 56 )
                elif( int( first ) != int( second ) ):
                    return( jump( label, i ) )
            elif( firstT == "str" or secondT == "str" ):
                if( secondT is None or firstT is None ):
                    return( jump( label, i ) )
                first, second = convert( first, second )
                if( secondT is None ):
                    ...
                elif( str( first ) != str( second ) ):
                    return( jump( label, i ) )
            elif( firstT == "bool" or secondT == "bool" ):
                if( secondT is None or firstT is None ):
                    return( jump( label, i ) )
                if( first !=  second  ):
                    return( jump( label, i ) )

    elif( key_word == "CALL" ):
        check_args( args, [ 'label' ] )
        for word in args:
            label = word[ 1 ]
        CALL_STACK.append( i )
        return( jump( label, i ) )
    elif( key_word == "RETURN" ):
        check_args( args, [] )
        try:
            return( int( CALL_STACK.pop() ) )
        except:
            exit( 56 )
    elif( key_word == "WRITE" ):
        for word in args:
            if ( word[ 0 ] == "var" ):
                var = getValue( word[ 1 ] )
                data_type = getType( word[ 1 ] )
                if( var == '' and data_type is None ):
                    exit( 56 )
                print( var, end='' )
            elif( word[ 0 ] == "string" ):
                write = re.sub( '\\\\032', ' ', word[ 1 ] )
                write = re.sub( '\\\\010', '\n', write )
                write = re.sub( '\\\\092', '\\\\', write )
                write = re.sub( '\\\\035', '#', write )
                print( write, end='' )
            elif( word[ 0 ] == "nil" ):
                print( '', end='' )
            elif( word[ 0 ] == "int" ):
                print( word[ 1 ], end='' )
            elif( word[ 0 ] == "bool" ):
                if( word[ 1 ] == "true" ):
                    print( 'true', end='' )
                elif( word[ 1 ] == "false" ):
                    print( 'false', end='' )
    elif( key_word == "CONCAT" ):
        where = ''
        write = ''
        for word in args:
            count = count + 1
            if ( word[ 0 ] == "var" ):
                var = getValue( word[ 1 ] )
                typeT = getType( word[ 1 ] )

                if( count == 1 ):
                    where = word[ 1 ]
                elif( count == 2 ):
                    first = var
                    firstT = typeT
                else:
                    second = var
                    secondT = typeT
            else:
                if ( count == 1 ):
                    exit( 105 )
                content = getValue( word[ 1 ] )
                data_type = getType( word )
                if( count == 2 ):
                    first = content
                    firstT = data_type
                elif( count == 3 ):
                    second = content
                    secondT = data_type
        if( firstT is None or secondT is None ):
            exit( 56 )
        if( not ( firstT == secondT ) ):
            exit( 53 )
        if( not( first is None and second is None ) ):
            first = first + second
        else:
            first = ''
        writeTo( where, first, data_type )
    elif( key_word == "JUMP" ):        
        label = ''

        for word in args:
            if ( word[ 0 ] == "label" ):
                label = word[ 1 ]
            return( jump( label, i ) )

    elif( key_word == "STRLEN" or key_word == "TYPE" ):
        result = 0
        heej = 0
        for word in args:
            count = count + 1
            if( count == 1 ):
                if( word[ 0 ] == "var" ):
                    to_frame = word[ 1 ]   
            elif( count == 2 ):
                if( word[ 0 ] == "var" ):
                    first = getValue( word[ 1 ] )
                    firstT = getType( word[ 1 ] )
                elif( word[ 0 ] == "string" ):
                    first = getValue( word[ 1 ] )
                    firstT = getType( word )
        if( key_word == "STRLEN" ):
            if( firstT is None ):
                exit( 56 )
            if( firstT != "str" ):
                exit( 53 )
            if( first is None ):
                heej = 0
            else:
                heej = len( first )
            result = heej
            if( word[ 1 ] == "int" ):
                exit( 53 )
            elif( word[ 1 ] == "string" ):
                exit( 53 )
            elif( word[ 1 ] == "bool" ):
                exit( 53 )
            firstT = "int"
            writeTo( to_frame, result, firstT )
        elif( key_word == "TYPE" ):
            result = getType( word )
            if( result == "int" ):
                result = "int"
            elif( result == "str" ):
                result = "string"
            elif( result == "bool" ):
                result = "bool"
            elif( result == "nil" ):
                result = "nil"
            elif( result is None ):
                result = ''
            writeTo( to_frame, result, "str" )
    elif( key_word == "EXIT" ):
        for word in args:
            code = getValue( word[ 1 ] )
            data_type = getType( word[ 1 ] )
            if( code == '' and data_type == "nil" ):
                exit( 53 )
            if( code == '' and data_type == None ):
                exit( 56 )
            if( not code ):
                exit( 56 )
            if ( getType( word ) != "int" ):
                exit( 53 )
            if( int( code ) >= 0 and int( code ) <= 49 ):
                exit( int( code ) )
            else:
                exit( 57 )
    elif( key_word == "DPRINT" ): 
        for word in args:
            code = getValue( word[ 1 ] )
            sys.stderr.write( str( code ) )
    elif( key_word == "ADD" or key_word == "SUB" or key_word == "MUL" or key_word == "IDIV" or key_word == "LT" or key_word == "GT" or key_word == "EQ"
          or key_word == "AND" or key_word == "OR" or key_word == "NOT" or key_word == "STRI2INT" or key_word == "GETCHAR" or key_word == "SETCHAR" ): # nyni umoznuji aby datovy typ nebyl jen int coz je chyba
        check_args( args, [ 'var','symb', 'symb' ] )
        for word in args:
            if( count == 0 ):
                to_frame = word[ 1 ]
            elif( count == 1 ):
                op1 = getValue( word[ 1 ] )
                op1t = getType( word )
            elif( count == 2 ):
                op2 = getValue( word[ 1 ] )
                op2t = getType( word )
            count += 1
        if( key_word == "ADD" ):
            missingValue( op1, op2 )
            if( op1t == op2t ):
                op1 = int( op1 ) + int( op2 )
            else:
                exit( 53 )
            op1t = "int"
        elif( key_word == "SUB" ):
            missingValue( op1, op2 )
            if( op1t == op2t ):
                op1 = int( op1 ) - int( op2 )
            else:
                exit( 53 )
            op1t = "int"
        elif( key_word == "MUL" ):
            missingValue( op1, op2 )
            if( op1t == op2t ):
                op1 = int( op1 ) * int( op2 )
            else:
                exit( 53 )
            op1t = "int"
        elif( key_word == "IDIV" ):
            missingValue( op1, op2 )
            if( op1t == op2t ):
                if( int( op2 ) == 0 ):
                    exit( 57 )
                op1 = int( op1 ) / int( op2 )
                op1 = int( op1 )
            else:
                exit( 53 )
            op1t = "int"
        elif( key_word == "LT" ):
            missingValue( op1, op2 )
            if( op1t == "nil" or op2t == "nil" ):
                exit( 53 )
            if( ( op1t is None ) or ( op2t is None ) ):
                exit( 53 )
            op1, op2 = convert( op1, op2 )
            if( op1t == op2t ):
                vysledek = ''
                poradi = 0
                if( op1t == "str" ):
                    if( op1 is None or op2 is None ):
                        op1 = "false"
                    else:
                        words = [ op1, op2 ]
                        words.sort()
                        for heej in words: 
                            if( poradi == 0 ):
                                vysledek = heej
                            poradi += 1 
                        if( op1 == op2 ):
                            op1 = "false"
                        else:
                            if ( vysledek == op1 ):
                                op1 = "true"
                            else:
                                op1 = "false"
                elif( op1t == "int" ):
                    if( int( op1 ) < int( op2 ) ):
                        op1 = "true"
                    else:
                        op1 = "false"
                elif( op1t == "bool" ):
                    op1 = getBool( op1 )
                    op2 = getBool( op2 )
                    if( op1 < op2 ):
                        op1 = "true"
                    else:
                        op1 = "false"
            else:
                exit( 53 )
            op1t = "bool"
                        
        elif( key_word == "GT" ):
            missingValue( op1, op2 )
            if( op1t == "nil" or op2t == "nil" ):
                exit( 53 )
            op1, op2 = convert( op1, op2 )

            if( ( op1t is None ) or ( op2t is None ) ):
                exit( 53 )
            if( re.match( '^\\\d{0,3}', op1 ) ):
                op1 = op1.split("\\")[1]
                op1 = chr( int( op1 ) )
            if( op1t == op2t ):
                vysledek = ''
                poradi = 0
                if( op1 is None ):
                    op1 = "true"
                elif( op2 is None ):
                    op1 = "true"
                elif( op1t == "str" ):
                    words = [ op1, op2 ]
                    words.sort()
                    for heej in words:
                        if( poradi == 0 ):
                            vysledek = heej
                        poradi += 1 
                    if ( vysledek == op1 ):
                        op1 = "false"
                    else:
                        op1 = "true"
                elif( op1t == "int" ):
                    if( int( op1 ) > int( op2 ) ):
                        op1 = "true"
                    else:
                        op1 = "false"
                elif( op1t == "bool" ):
                    op1 = getBool( op1 )
                    op2 = getBool( op2 )
                    if( op1 > op2 ):
                        op1 = "true"
                    else:
                        op1 = "false"
            else:
                exit( 53 )
            op1t = "bool"
        elif( key_word == "EQ" ):
            if( op1t == "nil" or op2t == "nil" ):
                ...
            elif( op1t is None or op2t is None ):
                exit( 56 )
            else:
                ...
            
            op1, op2 = convert( op1, op2 )
            
            if( ( op1t is None ) or ( op2t is None ) ):
                if( op1 == op2 ):
                    op1 = "true"
                else:
                    op1 = "false"
            elif( ( op1t == "nil" ) or ( op2t == "nil" ) ):
                if( op1 == op2 ):
                    op1 = "true"
                else:
                    op1 = "false"
            elif( op1t == op2t ):
                if( op1t == "str" ):
                    if( op1 == op2 ):
                        op1 = "true"
                    else:
                        op1 = "false"
                elif( op1t == "int" ):
                    if ( int( op1 ) == int( op2 ) ):
                        op1 = "true"
                    else:
                        op1 = "false"
                elif( op1t == "bool" ):
                    op1 = getBool( op1 )
                    op2 = getBool( op2 )
                    if( op1 == op2 ):
                        op1 = "true"
                    else:
                        op1 = "false"
            else:
                exit( 53 )
            op1t = "bool"
        elif( key_word == "AND" ):
            missingValue( op1, op2 )

            op1, op2 = convert( op1, op2 )

            if( op1t == op2t and op1t == "bool" ):
                op1 = getBool( op1 )
                op2 = getBool( op2 )
                op1 = op1 and op2
                if( op1 == True ):
                    op1 = "true"
                else:
                    op1 = "false"
            else:
                exit( 53 )
            op1t = "bool"
        elif( key_word == "OR" ):
            missingValue( op1, op2 )
            if( op1t == op2t and op1t == "bool" ):
                op1 = getBool( op1 )
                op2 = getBool( op2 )
                op1 = op1 or op2
                if( op1 is True ):
                    op1 = "true"
                else:
                    op1 = "false"
            else:
                exit( 53 )
            op1t = "bool"
        elif( key_word == "NOT" ):
            data_type = getType( word[ 1 ] )
            if( data_type == "nil" ):
                exit( 53 )
            missingValue( op1, op2 )
            if( op1t == "bool" ):
                op1 = getBool( op1 )
                op2 = getBool( op2 )
                op1 = not op1
                if( op1 is True ):
                    op1 = "true"
                else:
                    op1 = "false"
            else:
                exit( 53 )
            op1t = "bool"
        elif( key_word == "STRI2INT" ):
            if( ( op2t is None ) or ( op1t is None ) ):
                exit( 56 )
            if( ( op1t != "str" and op1 == "nil" ) or ( op2t != "int" and op2 == "nil" ) or ( op1t != "str" and op1 != "nil" ) or ( op2t != "int" and op2 != "nil" ) ):
                exit( 53 )
            if( int( op2 ) < 0 ):
                exit( 58 )
            try:
                op1 = ord( op1[ int( op2 ) ] )
            except:
                exit( 58 )
            op1t = "int"
        elif( key_word == "GETCHAR" ):
            sample = len( op1 )
            if( op1 == '' or op2 == '' ):
                exit( 56 )
            if( ( op1t != "str" ) or ( op2t != "int" ) ):
                exit( 53 )
            if( sample <= int( op2 ) or int( op2 ) < 0 ):
                exit( 58 )
            op1 = op1[ int( op2 ) ]
            op1t = "str"
        elif( key_word == "SETCHAR" ):
            sentence = getValue( to_frame )
            sentenceT = getType( to_frame )
            if( sentenceT is None ):
                exit( 56 )
            if( sentenceT != "str" ):
                exit( 53 )
            sentence = list( sentence )
            sentence_length = len ( sentence )
            if( op2 == '' ):
                exit( 56 )
            if( op1 == "nil" ):
                exit( 53 )
            if( op1t is None ):
                exit( 56 )
            if( op2 is None ):
                exit( 58 )
            if( op1t != "int" ):
                exit( 53 )
            if( sentence_length <= int( op1 ) or int( op1 ) < 0 ):
                exit( 58 )
            if( op1t != "int" ):
                exit( 53 )
            if( op2t != "str" ):
                exit( 53 )
            op1, op2 = convert( op1, op2 )
            sentence[ int( op1 ) ] = op2[ 0 ]
            op1 = ''.join( sentence )
            op1t = "str"
        writeTo( to_frame, op1, op1t )
    elif( key_word == "INT2CHAR" ):
        check_args( args, [ 'var','symb' ] )
        
        ip1 = 0
        op1t = ''
        
        for word in args:
            if( count == 0 ):
                to_frame = word[ 1 ]
            elif( count == 1 ):
                op1 = getValue( word[ 1 ] )
                op1t = getType( word )
            count += 1
        
        if( op1t == "nil" ):
            exit( 53 )
        if( op1 == "" ):
            exit( 56 )
        if( op1t != "int" ):
            exit( 53 )
        try:
            op1 = chr( int( op1 ) )
        except:
            exit( 58 )
        writeTo( to_frame, op1, type( op1 ) )
    elif( key_word == "BREAK" ):
        sys.stderr.write( str( instruction_counter ) )
        exit( 0 )
    elif( key_word == "READ" ):
        check_args( args, [ 'var','type' ] )

        rtype = ''
        stop = 0
        
        for word in args:
            if( count == 0 ):
                to_frame = word[ 1 ]
            elif( count == 1 ):
                rtype = word[ 1 ]
            count += 1 
        if( input_is == "file" ):
            line = file1.readline()
            if( line == '' ):
                line = ''
                writeTo( to_frame, line, "nil" )
                stop = 1
            line = line[ :-1 ]
        else:
            try:
                line = input()
            except EOFError:
                line = ''
                writeTo( to_frame, line, "nil" )
                stop = 1
        if( stop == 0 ):
            if( rtype == "int" ):
                if( not( re.search( '^((\-)|(\+)){0,1}(\d)*$', line ) ) ):
                    line = ''
                    writeTo( to_frame, line, "nil" )
                else:
                    line = int( line )
                    writeTo( to_frame, line, "int" )
            elif( rtype == "string" ):
                if( line == '' ):
                    line = ''
                    writeTo( to_frame, line, "string" )
                else:
                    writeTo( to_frame, line, "str" )
            elif( rtype == "bool" ):
                if( line == '' ):
                    line = ''
                    writeTo( to_frame, line, "nil" )
                else:
                    if( re.search('true', line,  re.IGNORECASE) ):
                        line = "true"
                    else:
                        line = "false"
                    writeTo( to_frame, line, "bool" )
        else:
            ...
    elif( key_word == "PUSHS" ):
        check_args( args, [ 'symb' ] )
        
        what = ""
        push_element = []
        check = 0

        for word in args:
            what = word[ 1 ]
            data_type = getType( word )

        try:
            frame, var = at_split( what )
            check = 1
        except:
            ...
        if( check == 1 ):
            if( frame == "GF" ):
                if not var in GF:
                    exit( 54 )
            elif( frame == "LF" ):
                if not var in LF:
                    exit( 54 )
            elif( frame == "TF" ):
                if not var in TF:
                    exit( 54 )
            if( data_type is None ):
                exit( 56 )
        push_element.append( what )
        push_element.append( data_type )
        PUSHS.append( push_element )
    elif( key_word == "CREATEFRAME" ):
        check_args( args, [] )
        TF.clear()
        tf_accessible = 1
    elif( key_word == "PUSHFRAME" ):
        check_args( args, [] )
        if( tf_accessible != 0 ):
            FRAME_STACK.append( TF.copy() )
            FRAME_STACK_T.append( TFT.copy() )
            if( len( FRAME_STACK ) != 0 ):
                TEMPORARY = FRAME_STACK.pop()
                TEMPORARYT = FRAME_STACK_T.pop()
                TEMPORARY.clear()
                TEMPORARYT.clear()
                TEMPORARY = LF.copy()
                TEMPORARYT = LFT.copy()
                FRAME_STACK.append( TEMPORARY )
                FRAME_STACK_T.append( TEMPORARYT )
            LF = TF.copy()
            LFT = TFT.copy()
            TF.clear()
            TFT.clear()
            tf_accessible = 0
            if( len( FRAME_STACK ) != 0 ):
                lf_accessible = 1
        else:
            exit( 55 )
    elif( key_word == "POPFRAME" ):
        check_args( args, [] )
        values = len( FRAME_STACK )
        if( len( FRAME_STACK ) == 0 ):
            exit( 55 )
        tf_accessible = 1
        TF = LF.copy()
        TFT = LFT.copy()
        if( not( values == 1 ) ):
            LF = FRAME_STACK[ -1 ]
            LFT = FRAME_STACK_T[ -1 ]
            FRAME_STACK.pop()
            FRAME_STACK_T.pop()
        else:
            lf_accessible = 0  
    else:
        exit( 32 )
    return i


def execute( program ):
    
    global order_inc

    i = 0
    r = 0

    while( r <= 1 ):
        if( r == 0 ):
            while i < order_inc:
                key_word = program[ i ][ 1 ].upper()
                i = labelThing( key_word, program[ i ][ 2 ], i )
                i = i + 1 
        else:
            while i < order_inc:
                key_word = program[ i ][ 1 ].upper()
                i = line_handler( key_word, program[ i ][ 2 ], i )
                i = i + 1 
        r += 1
        i = 0

params() 

source_content = ""

if( source_is == "file" ):
    with open(source, 'r') as file:
        source_content = file.read()

if( source_is == "stdin" ):
    
    for line in sys.stdin:
        source_content = source_content + line

well_formatted( source_content )
tree = ET.ElementTree( ET.fromstring( source_content ) )
root = tree.getroot()

program = root.tag

if( program != 'program' ):
    exit(105)

header = root.attrib

if( header[ 'language' ] != "IPPcode20" ):
    exit( 105 )

instructions = []

if( input_is == "file" ):
    file1 = open( input_file, 'r')

for instr in root.findall( 'instruction' ):

    array_test = []

    order = instr.get( 'order' )
    order_inc = order_inc + 1

    if ( not( order_inc <= int( order ) ) ):
        exit( 32 )

    opcode = instr.get( 'opcode' )
    array_test.append( order_inc )
    array_test.append( opcode )
    i = 0

    args = []

    for test in instr:
        arg_array = []
        arg_array.append( test.attrib[ 'type' ] )
        arg_array.append( test.text )
        args.append( arg_array )
    array_test.append( args )
    instructions.append( array_test )

execute( instructions )

if( input_is == "file" ):
    file1.close()