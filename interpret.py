#!/usr/bin/env python3


# -----------------------------------------------------------
# Interpret IPP-19
#
# (C) 2020 Jakub Sekula, Brno, Ceska republika
# login xsekul01
# email xsekul01@fit.vutbr.cz
# -----------------------------------------------------------

import sys
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from glob import glob

#
#  Promenne pro praci s argumenty programu
#

source = ""
input_file = ""
input_is = "stdin"
source_is = "stdin"
stati_file = ""
order_inc = 0
instruction_counter = 0
JUMP = 0
RUN = 0
STATI = 0
STATI_VARS = 0

# pole pro zasobnikove instrukce 

PUSHS = []

#
# dictionary pro promenne
#

GF = dict()
LF = dict()
TF = dict()

#
# dictionary pro umisteni labelu
#

LABEL = dict()

#
# dictionary pro datove typy promennych
#

GFT = dict()
LFT = dict()
TFT = dict()

#
# zasobniky pro ramce a zasobnik volani
#

FRAME_STACK = []
FRAME_STACK_T = []
CALL_STACK = []

#
# promenne pro pristupnost ramcu
#

tf_accessible = 0
lf_accessible = 0

#
# Funkce prochazi vsechny parametry ze vstupu a na zaklade techto parametru upravuje globalni promenne programu
#
def params():

    count = 0
    entered = 0
    help = 0

    global source
    global STATI
    extension = 0
    global input_file
    global stati_file

    global source_is
    global input_is

    for arg in sys.argv:
        if( arg == "--help" ):
            help = 1
        elif( re.search( '^(\-){2}source=', arg ) ):
            # rozdeluje string podle = a bere si z nej cast za =
            source = arg.split( "=" )[ 1 ]
            source_is = "file"
            if Path( source ).is_file():
                ...
            else:
                sys.exit( 11 )
            # kontroluji jake parametry byly zadany
            entered = entered + 1
        elif( re.search( '^(\-){2}input=', arg ) ):
            input_file = arg.split( "=" )[ 1 ]
            if Path( input_file ).is_file():
                input_is = "file"
            else:
                sys.exit( 11 )
            entered = entered + 1
        elif( re.search( '^(\-){2}stats=', arg ) ):
            stati_file = arg.split( "=" )[ 1 ]
            STATI = 1
        elif( re.search( '^(\-){2}insts$', arg ) ):
            extension = 1
        elif( re.search( '^(\-){2}vars$', arg ) ):
            extension = 1
        else:
            if( count == 0 ):
                ...
            else:
                sys.exit( 10 )
        count += 1

    # jestlize bylo zadano --help, nesmi byt zadan zadny jiny argument
    if( ( help == 1 ) and entered >= 1 ):
        sys.exit( 10 )
    
    # jestlize nebyly zadany zadne parametry koncim s 10
    elif( entered == 0 ):
        sys.exit( 10 )
    
    # jestlize neni zadane --testlist=, ale --vars nebo --insts je, koncim s chybou 
    if( STATI == 0 and extension == 1 ):
        sys.exit( 10 )

# -----------------------------------------------------------
# Funkce convertor
#
# Parametr argument string pro kontrolu 
#
# Funkce prozkouma zadany string a hleda zpetne lomitko, jestlize je nalezeno, vyjme ciselne znaky za nim a premeni je na ascii znak
#
# Return string s odpovidajicimi ascii hodnotami
# -----------------------------------------------------------
def convertor( argument ):
    position = 0
    # zmenim string na list, abych mohl pracovat se znaky na indexech 
    argument = list( argument )
    converted = ''
    for char in argument:
        if( char == "\\" ):
            if( argument[ position + 1 ] == "0" ):
                convert = argument[ position + 2 ] + argument[ position + 3 ]
                try:
                    converted = chr( int( convert ) )
                except:
                    sys.exit( 105 )
            else:
                convert = argument[ position + 1 ] + argument[ position + 2 ] + argument[ position + 3 ]
                try:
                    converted = chr( int( convert ) )
                except:
                    sys.exit( 105 )
            # nahrazuji znaky \ddd za jedena znak a zbytek mezery
            argument[ position ] = converted
            argument[ position + 1 ] = ''
            argument[ position + 2 ] = ''
            argument[ position + 3 ] = ''
        position += 1
    # zmenim list zpet na string
    argument = ''.join( argument )
    return( argument )

def getFromStack():
    try:
        op1 = PUSHS.pop()
        op1t = op1[ 1 ]
        op1 = op1[ 0 ]
    except:
        print( 185 )
        sys.exit( 56 )
    op1 = getValue( op1 )
    return ( op1, op1t )

# -----------------------------------------------------------
# Funkce checkRegisters
#
# Parametr none
#
# Funkce prozkouma obsah registru, toto dela kvuli rozsireni STATI 
#
# Return none
# -----------------------------------------------------------
def checkRegisters():
    
    global GF
    global TF
    global LF
    global GFT
    global TFT
    global LFT
    global STATI_VARS
    global tf_accessible
    global lf_accessible
    
    gf = 0
    tf = 0
    lf = 0

    # kontroluji vsechny ramce a pocitam v nich promenne s hodnotou
    for var in GF:
        if( var in GFT ):
            gf += 1
    if( tf_accessible == 1):
        for var in TF:
            if( var in TFT ):
                tf += 1
    if( lf_accessible == 1 ):
        for var in LF:
            if( var in LFT ):
                lf += 1
    total = gf + tf + lf
    
    # nastavuji maximalni pocet inicializovanych promennych 
    if( STATI_VARS <= total ):
        STATI_VARS = total

# -----------------------------------------------------------
# Funkce writeStats
#
# Parametr none
#
# Funkce zapisuje hodnoty pro rozsireni STATI do souboru 
#
# Return none
# -----------------------------------------------------------
def writeStats():
    
    global STATI
    global instruction_counter
    global stati_file
    global STATI_VARS

    if( STATI == 1 ):
        stati = open( stati_file, 'w+')

        #podle zadanych parametru zapisuju
        for arg in sys.argv:
            if( re.search( '^(\-){2}insts$', arg ) ):
                stati.write( str( instruction_counter ) + "\n" )
            elif( re.search( '^(\-){2}vars$', arg ) ):
                stati.write( str( STATI_VARS ) + "\n" )
        stati.close()

# -----------------------------------------------------------
# Funkce well_formatted
#
# Parametr source je string s nactenym xml kodem
#
# Funkce kontroluj, zda-li je vstupni xml "well formed" 
#
# Return none
# -----------------------------------------------------------
def well_formatted( source ):
    try:
        xml = ET.fromstring( source )
    except:
        sys.exit( 31 )

# -----------------------------------------------------------
# Funkce at_split
#
# Parametr source token
#
# Funkce vraci rozdeleny string na ramec a promennou 
#
# Return ramec a jmeno promenne
# -----------------------------------------------------------
def at_split( token ):
    token1 = token.split( "@", 1 )[ 0 ]
    token2 = token.split( "@", 1 )[ 1 ]

    return ( token1, token2 )

# -----------------------------------------------------------
# Funkce varExists
#
# Parametr frame nazec ramce
# Parametr var nazev promenne
#
# Funkce kontroluje, jestli promenna existuje v zadanem ramci 
#
# Return none
# -----------------------------------------------------------
def varExists( frame, var ):
    
    global GF
    global TF
    global LF

    if( frame == "GF" ):
        if not var in GF:
            sys.exit( 54 )
    elif( frame == "LF" ):
        if not var in LF:
            sys.exit( 54 )
    elif( frame == "TF" ):
        if not var in TF:
            sys.exit( 54 )

# -----------------------------------------------------------
# Funkce getFromFrame
#
# Parametr frame nazec ramce
# Parametr variable nazev promenne
#
# Funkce ziska obsah variable ze zadaneho ramce
#
# Return obsah promenne
# -----------------------------------------------------------
def getFromFrame( frame, variable ):
    #if( frame == "LF" ):
        #print( "1",frame,variable )
    varExists( frame, variable )
    #if( frame == "LF" ):
        #print( "2",frame,variable )
    frameExists( frame )
    if ( frame == "GF" ):
        return ( GF[ variable ] )
    elif( frame == "TF" ):
        return ( TF[ variable ] )
    elif ( frame == "LF" ):
        return ( LF[ variable ] )

# -----------------------------------------------------------
# Funkce frameExists
#
# Parametr frame nazec ramce
#
# Funkce kontroluje, jestli ramec existuje
#
# Return none
# -----------------------------------------------------------
def frameExists( frame ):
    global tf_accessible
    global lf_accessible

    if( ( frame == "TF" and tf_accessible == 0 ) or ( frame == "LF" and lf_accessible == 0 ) ):
        sys.exit( 55 )

# -----------------------------------------------------------
# Funkce writeTo
#
# Parametr where kam se ma zapisovat, format GF@smth
# Parametr content obsah co je treba zapsat
# Parametr data_type zapisovany datovy typ
#
# Funkce zapisuje hodnotu do ramce k promenne smth
#
# Return none
# -----------------------------------------------------------
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
        #print( content, data_type )
        LF[ variable ] = content
        LFT[ variable ] = data_type

# -----------------------------------------------------------
# Funkce missingValue
#
# Parametr op1 operand pro kontrolu
# Parametr op2 
#
# Funkce kontroluje, jestli jsou zadane obe hodnoty
#
# Return none
# -----------------------------------------------------------
def missingValue( op1, op2 ):
    if( op1 == '' or op2 == '' ):
        print( 400 )
        sys.exit( 56 )

# -----------------------------------------------------------
# Funkce checkVar, checkSymb, checkInt, checkFloat, checkString, checkBool, checkNil, checkType
#
# Parametr argument string
#
# Funkce kontroluji, jestli zadane hodnoty odpovidaji datovym typum a spravnemu tvaru celkove
#
# Return none
# -----------------------------------------------------------
def checkVar( argument ):
    if ( not ( re.search( '^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|([a-zA-Z]))(\d*|([a-zA-Z])|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$', argument ) ) ):
        print( 412 )
        sys.exit( 32 )

def checkSymb( argument ):
    if( argument == None ):
        return
    if ( not ( re.search( '(int@((\-)|(\+)){0,1}(0-9)+)$|(bool@((true)|(false)))$|^((GF)|(TF)|(LF))@(\S)*$|^(nil)@nil$|^string@(\S)*$', argument ) ) ):
        print( 419 )
        sys.exit( 32 )
    elif( not ( re.search( '([^#\s\\\\]|\\\\[0-9]{3})*$', argument ) ) ):
        print( 422 )
        sys.exit( 32 )

def checkInt( argument ):
    if ( not ( re.search( '^((\-)|(\+)){0,1}(\d)*$', argument ) ) ):
        print( 427 )
        sys.exit( 32 )

def checkFloat( argument ):
    try:
        float.fromhex( argument )
    except:
        print( 434 )
        sys.exit( 32 )


def checkString( argument ):
    if( argument == None ):
        return
    if ( not ( re.search( '^([^#\s\\\\]|\\\\[0-9]{3})*$', argument ) ) ):
        print( 442 )
        sys.exit( 32 )

def checkBool( argument ):
    if ( not ( re.search( '^((true)|(false))$', argument ) ) ):
        print( 447 )
        sys.exit( 32 )

def checkNil( argument ):
    if ( not ( re.search( '^nil$', argument ) ) ):
        print( 452 )
        sys.exit( 32 )

def checkType( argument ):
    if( not ( argument == "int" or argument == "bool" or argument == "string" ) ):
        print( 457 )
        sys.exit( 32 )

# -----------------------------------------------------------
# Funkce getBool
#
# Parametr argument string
#
# Funkce vraci odpovidaji bool hodnoty, podle vstupniho stringu
#
# Return Bool honota
# -----------------------------------------------------------
def getBool( argument ):
    if( argument == "true" ):
        return( True )
    else:
        return ( False )

# -----------------------------------------------------------
# Funkce check_args
#
# Parametr args argumenty v poli
# Paramet expected pole ocekavanych datovych typu
#
# Funkce kontroluje, jestli zadane argumentu odpovidaji ocekavanym argumentum
#
# Return none
# -----------------------------------------------------------
def check_args( args, expected ):
    i = 0
    maxe = len( expected )
    maxa = len ( args )

    # jestlize jsou obe pole stejne velke, neni co kontrolovat
    if( maxe == 0 and maxa == 0 ):
        return
    
    # jestlize nemaji stejnou velikost, jedna se o chybu
    elif( maxe == 0 and maxa != 0 ):
        print( "480" )
        sys.exit( 53 )

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
            elif( args[ i ][ 0 ] == "float" ):
                checkFloat( args[ i ][ 1 ] )
            else:
                print( "!!! Je potreba osetrit:" )
                print( args[ i ][ 0 ] ,args[ i ][ 1 ] )
        i += 1

# -----------------------------------------------------------
# Funkce getValue
#
# Parametr argument ramec a promenna, nebo datovy typ a hodnota
#
# Funkce ziska hodnotu z ramce, nebo z promenne
#
# Return hodnota
# -----------------------------------------------------------
def getValue( argument ):
    if( argument is None ):
        return argument
    # jedna se o ramec
    if( re.search( '^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|([a-zA-Z]))(\d*|([a-zA-Z])|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$', str( argument ) ) ):
        frame, variable = at_split( argument )
        frameExists( frame )
        code = getFromFrame( frame, variable )
        return code
    else:
        return argument

def getFloat( op1, op2 ):
    try:
        #print( op1,"op11" )
        op1 = getValue( op1 )
        #print( op1,"op12" )
        op1 = float.fromhex( op1 )
    except:
        ...
    try:
        #print( op2,"op21" )
        op2 = getValue( op2 )
        #print( op2, "op22" )
        op2 = float.fromhex( op2 )
    except:
        ...
    return( op1, op2 )

# -----------------------------------------------------------
# Funkce getType
#
# Parametr argument ramec a promenna, nebo datovy typ a hodnota
#
# Funkce datovy typ argumentu
#
# Return datovy typ
# -----------------------------------------------------------
def getType( argument ):

    global GFT
    global TFT
    global LFT

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
    elif( argument[ 0 ] == "float" ):
        return "float"
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

# -----------------------------------------------------------
# Funkce convert
#
# Parametr first string pro kontrolu
# Parametr second string pro kontrolu
#
# Funkce funkce posila stringy do funkce pro premenu ascii hodnot na znaky
#
# Return string bez escape sekvenci
# -----------------------------------------------------------
def convert( first, second ):
    if( ( first is None ) or ( second is None ) ):
        ...
    else:
        first = convertor( first )
        second = convertor( second )
    return ( first, second )

# -----------------------------------------------------------
# Funkce jump
#
# Parametr label nazev labelu
# Parametr i pozice labelu v kodu
#
# Funkce vraci pozici, kam se mam v programu vratit 
#
# Return index v poli
# -----------------------------------------------------------
def jump( label, i ):
    
    global LABEL

    if( label in LABEL ):
        return( LABEL[ label ] )
    else:
        sys.exit( 52 )

# -----------------------------------------------------------
# Funkce labelThing
#
# Parametr key_word 
# Parametr args pole argumentu
# Parametr i index v poli
#
# Funkce prochazi cele xml a hleda key_word LABEL a nasledne uklada nazev a pozici LABELU do dictionary 
#
# Return index v poli
# -----------------------------------------------------------
def labelThing( key_word, args, i ):
    
    global instruction_counter
    global LABEL

    # LABEL ⟨label⟩ Definice návěští
    # Speciální instrukce označující pomocí návěští ⟨label⟩ důležitou pozici v kódu jako potenciální cíl libovolné skokové instrukce. 
    # Pokus o redefinici existujícího návěští je chybou 52.
    if( key_word == "LABEL" ):
        check_args( args, [ 'label' ] )
        label = args[ 0 ][ 1 ]
        if( label in LABEL ):
            sys.exit( 52 )
        else:
            LABEL[ label ] = i
    return i

# -----------------------------------------------------------
# Funkce line_handler
#
# Parametr key_word 
# Parametr args pole argumentu
# Parametr i index v poli
#
# Jedna se o konecny automat, ktery na zaklade key_wordu a zadanych argumentu postupne zpracovava vstupni xml soubor 
#
# Return index v poli
# -----------------------------------------------------------
def line_handler( key_word, args, i ):
    
    # nasleduji deklarace promennych 
    global GF
    global TF
    global LF
    global LABEL
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
        # ziskam ramec
        for word in args:
            if( word[ 0 ] == "var" ):
                to_frame = word
        
        # DEFVAR ⟨var⟩ Definuj novou proměnnou v rámci
        # Definuje proměnnou v určeném rámci dle⟨var⟩. Tato proměnná je zatím neinicializovaná a bez určení typu, který bude určen až přiřazením nějaké hodnoty. 
        # Opakovaná definice proměnné již existující v daném rámci vede na chybu 52.
        if( key_word == "DEFVAR" ):
            frame, variable = at_split( to_frame[ 1 ] )
            frameExists( frame )
            if( frame == "GF" ):
                if variable in GF:
                    sys.exit( 52 )
                GF[ variable ] = ''
            elif( frame == "TF" ):
                if variable in TF:
                    sys.exit( 52 )
                TF[ variable ] = ''
            elif( frame == "LF" ):
                if variable in LF:
                    sys.exit( 52 )
                LF[ variable ] = ''
            else:
                sys.exit( 55 )
        # POPS ⟨var⟩ Vyjmi hodnotu z vrcholu datového zásobníku
        # Není-li zásobník prázdný, vyjme z něj hodnotu a uloží ji do proměnné⟨var⟩, jinak dojde k chybě 56.
        elif( key_word == "POPS" ):
            # zkousim ziskat vrchni prvek pole PUSHS, jeho datovy typ a hodnotu
            try:
                content = PUSHS.pop()
                data_type = content[ 1 ]
                content = content[ 0 ]
            except:
                print( 776 )
                sys.exit( 56 )
            writeTo( to_frame[ 1 ], content, data_type )
    # MOVE ⟨var⟩ ⟨symb⟩ Přiřazení hodnoty do proměnné
    # Zkopíruje hodnotu ⟨symb⟩ do ⟨var⟩. Např.MOVE LF@par GF@var provede zkopírování hodnoty proměnné var v globálním rámci do proměnné par v lokálním rámci.
    elif( key_word == "MOVE" ):
        check_args( args, [ 'var', 'symb' ] )
        for word in args:
            count = count + 1
            # kam zapisi
            if( word[ 0 ] == "var" and count == 1 ):
                to_frame = word[ 1 ]
                wtf = word
                #print( "!!!" )
            else:
                content = getValue( word[ 1 ] )
                data_type = getType( word )
                if( content == '' and data_type is None ):
                    print( 797 )
                    sys.exit( 56 )
            # jestlize existuje datovy typ
            if( data_type != '' ):
                if ( content == "nil" ):
                    content = ''
                    data_type = "nil"
                if( data_type == "str" and content is None ):
                    content = ''
                elif( data_type == "str" ):
                    content = convertor( content )
                if( data_type == "float" ):
                    try:
                        content = float.fromhex( content )
                    except:
                        ...
                #print( to_frame, content, data_type )
                writeTo( to_frame, content, data_type )
    # LABELY resim pri prvnim pruchodu, takze zde uz nic nedelaji
    elif( key_word == "LABEL" ):
        ...
    elif( key_word == "JUMPIFEQ" or key_word == "JUMPIFNEQ" or key_word == "JUMPIFEQS" or key_word == "JUMPIFNEQS" ):
        # zpracovani vstupnich argumentu
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
            sys.exit( 52 )
        if ( ( ( firstT != secondT ) or ( secondT != firstT  ) ) ):
            if( ( firstT is None or secondT is None ) or ( firstT == "nil" or secondT == "nil" ) ):
                ...
            else:
                print( "817" )
                sys.exit( 53 )
        # JUMPIFEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩ Podmíněný skok na návěští při rovnosti
        # Pokud jsou⟨symb1⟩a⟨symb2⟩stejného typu nebo je některý operand nil (jinak chyba 53) azároveň se jejich hodnoty rovnají, tak provede skok na návěští⟨label⟩.
        if( key_word == "JUMPIFEQ" or key_word == "JUMPIFEQS" ):
            if( key_word == "JUMPIFEQS" ):
                first, firstT = getFromStack()
                second, secondT = getFromStack()
            first, second = convert( first, second )
            if( ( firstT is None or secondT is None ) or ( firstT != secondT ) ):
                if( firstT == "nil" or secondT == "nil" ):
                    ...
                else:
                    if( key_word == "JUMPIFEQS" ):
                        print( "832" )
                        sys.exit( 53 )
                    else:
                        print( "870" )
                        sys.exit( 56 )
            if( ( first == second ) and ( firstT == secondT ) ):
                instruction_counter += 1
                return( jump( label, i ) )
        # JUMPIFNEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩ Podmíněný skok na návěští při nerovnosti
        # Jsou-li⟨symb1⟩a⟨symb2⟩stejného typu nebo je některý operand nil (jinak chyba 53), tak v případě různých hodnot provede skok na návěští⟨label⟩
        elif( key_word == "JUMPIFNEQ" or key_word == "JUMPIFNEQS" ):
            if( key_word == "JUMPIFNEQS" ):
                first, firstT = getFromStack()
                second, secondT = getFromStack()
            if( first == "nil" or second == "nil" ):
                if( first == "nil" and second == "nil" ):
                    ...
                else:
                    instruction_counter += 1
                    return( jump( label, i ) )
            elif( firstT != secondT ):
                if( key_word == "JUMPIFNEQS" ):
                    print( "881" )
                    sys.exit( 53 )
                else:
                    print( 925 )
                    sys.exit( 56 )
            elif( firstT is None and secondT is None ):
                if( first != second ):
                    instruction_counter += 1
                    return( jump( label, i ) )
            elif( firstT == "int" or secondT == "int" ):
                if( secondT is None or firstT is None ):
                    print( 933 )
                    sys.exit( 56 )
                elif( int( first ) != int( second ) ):
                    instruction_counter += 1
                    return( jump( label, i ) )
            elif( firstT == "float" or secondT == "float" ):
                first, second = getFloat( first, second )
                if( secondT is None or firstT is None ):
                    print( 941 )
                    sys.exit( 56 )
                elif( firstT == "float" or secondT == "float" ):
                    instruction_counter += 1
                    return( jump( label, i ) )
            elif( firstT == "str" or secondT == "str" ):
                if( secondT is None or firstT is None ):
                    instruction_counter += 1
                    return( jump( label, i ) )
                first, second = convert( first, second )
                if( secondT is None ):
                    ...
                elif( str( first ) != str( second ) ):
                    instruction_counter += 1
                    return( jump( label, i ) )
            elif( firstT == "bool" or secondT == "bool" ):
                if( secondT is None or firstT is None ):
                    instruction_counter += 1
                    return( jump( label, i ) )
                if( first !=  second  ):
                    instruction_counter += 1
                    return( jump( label, i ) )

    # CALL ⟨label⟩ Skok na návěští s podporou návratu 
    # Uloží inkrementovanou aktuální pozici z interního čítače instrukcí do zásobníku volání a provede skok na zadané návěští (případnou přípravu rámce musí zajistit jiné instrukce)
    elif( key_word == "CALL" ):
        check_args( args, [ 'label' ] )
        for word in args:
            label = word[ 1 ]
        # dam novy index na zasobnik volani
        CALL_STACK.append( i )
        instruction_counter += 1
        return( jump( label, i ) )
    # RETURN 
    # Návrat na pozici uloženou instrukcí CALL Vyjme pozici ze zásobníku volání a skočí na tuto pozici nastavením interního čítače instrukcí(úklid lokálních rámců musí zajistit jiné instrukce). 
    # Provedení instrukce při prázdném zásobníku volání vede na chybu 56
    elif( key_word == "RETURN" ):
        check_args( args, [] )
        try:
            # vracim se na vrchni hodnotu ze zasobniku volani
            return( int( CALL_STACK.pop() ) )
        except:
            print( 983 )
            sys.exit( 56 )
    # WRITE ⟨symb⟩
    # Výpis hodnoty na standardní výstup Vypíše hodnotu ⟨symb⟩ na standardní výstup. Až na typ bool a hodnotu nil@nil je formát
    # výpisu kompatibilní s příkazem print jazyka Python 3 s doplňujícím parametrem end=''(za-mezí dodatečnému odřádkování). 
    # Pravdivostní hodnota se vypíše jako true a nepravda jako false. 
    # Hodnota nil@nil se vypíše jako prázdný řetězec
    elif( key_word == "WRITE" ):
        for word in args:
            if ( word[ 0 ] == "var" ):
                var = getValue( word[ 1 ] )
                data_type = getType( word[ 1 ] )
                if( var == '' and data_type is None ):
                    sys.exit( 56 )
                if( data_type == "string" ):
                    var = convertor( var )
                if( data_type == "float" ):
                    try:
                        print( hex( var ), end='' )
                        return i
                    except:
                        ...
                    try:
                        print( float.hex( var ), end='' )
                        return i
                    except:
                        ...
                print( var, end='' )
            elif( word[ 0 ] == "string" ):
                write = word[ 1 ]
                write = convertor( write )
                print( write, end='' )
            elif( word[ 0 ] == "nil" ):
                print( '', end='' )
            elif( word[ 0 ] == "int" ):
                print( word[ 1 ], end='' )
            elif( word[ 0 ] == "float" ):
                print(  float.fromhex( word[ 1 ] ).hex() , end='' )
            elif( word[ 0 ] == "bool" ):
                if( word[ 1 ] == "true" ):
                    print( 'true', end='' )
                elif( word[ 1 ] == "false" ):
                    print( 'false', end='' )
    # CONCAT⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Konkatenace dvou řetězců
    # Do proměnné ⟨var⟩ uloží řetězec vzniklý konkatenací dvou řetězcových operandů ⟨symb1⟩ a ⟨symb2⟩ (jiné typy nejsou povoleny).
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
                    sys.exit( 105 )
                content = getValue( word[ 1 ] )
                data_type = getType( word )
                if( count == 2 ):
                    first = content
                    firstT = data_type
                elif( count == 3 ):
                    second = content
                    secondT = data_type
        #print( first, firstT, second, secondT )
        if( firstT is None or secondT is None ):
            print( 1058 )
            sys.exit( 56 )
        if( not ( firstT == secondT ) ):
            if( firstT == '' or secondT == '' ):
                ...
            else:
                print( first, second )
                print( "1019" )
                sys.exit( 53 )
        if( not( first is None and second is None ) ):
            first = first + second
            data_type = "str"
        else:
            first = ''
        #print( where, first, data_type )
        writeTo( where, first, data_type )
    # JUMP ⟨label⟩ Nepodmíněný skok na návěští
    # Provede nepodmíněný skok na zadané návěští⟨label⟩.
    elif( key_word == "JUMP" ):        
        label = ''

        for word in args:
            if ( word[ 0 ] == "label" ):
                label = word[ 1 ]
            instruction_counter += 1
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
        # STRLEN ⟨var⟩ ⟨symb⟩ Zjisti délku řetězce
        # Zjistí počet znaků (délku) řetězce v ⟨symb⟩ a tato délka je uložena jako celé číslo do ⟨var⟩.
        if( key_word == "STRLEN" ):
            if( firstT is None ):
                print( 1102 )
                sys.exit( 56 )
            if( firstT != "str" ):
                print( "1050" )
                sys.exit( 53 )
            if( first is None ):
                heej = 0
            else:
                heej = len( first )
            result = heej
            if( word[ 1 ] == "int" ):
                print( "1057" )
                sys.exit( 53 )
            elif( word[ 1 ] == "string" ):
                print( "1060" )
                sys.exit( 53 )
            elif( word[ 1 ] == "bool" ):
                print( "1063" )
                sys.exit( 53 )
            firstT = "int"
            writeTo( to_frame, result, firstT )
        # TYPE ⟨var⟩ ⟨symb⟩ Zjisti typ daného symbolu 
        # Dynamicky zjistí typ symbolu ⟨symb⟩ a do ⟨var⟩ zapíše řetězec značící tento typ (int, bool,string nebo nil). 
        # Je-li ⟨symb⟩ neinicializovaná proměnná, označí její typ prázdným řetězcem.
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
    # EXIT ⟨symb⟩ Ukončení interpretace s návratovým kódem
    # Ukončí vykonávání programu a ukončí interpret s návratovým kódem ⟨symb⟩, kde ⟨symb⟩ je celé číslo v intervalu 0 až 49 (včetně). 
    # Nevalidní celočíselná hodnota ⟨symb⟩ vede na chybu 57.
    elif( key_word == "EXIT" ):
        for word in args:
            code = getValue( word[ 1 ] )
            data_type = getType( word[ 1 ] )
            if( code == '' and data_type == "nil" ):
                print( "1088" )
                sys.exit( 53 )
            if( code == '' and data_type == None ):
                print( 1150 )
                sys.exit( 56 )
            if( not code ):
                print( 1153 )
                sys.exit( 56 )
            if ( getType( word ) != "int" ):
                sys.exit( 53 )
            if( int( code ) >= 0 and int( code ) <= 49 ):
                writeStats()
                sys.exit( int( code ) )
            else:
                sys.exit( 57 )
    # DPRINT ⟨symb⟩ Výpis hodnoty nastderr
    # Předpokládá se, že vypíše zadanou hodnotu ⟨symb⟩ na standardní chybový výstup (stderr).
    elif( key_word == "DPRINT" ): 
        for word in args:
            code = getValue( word[ 1 ] )
            sys.stderr.write( str( code ) )
    elif( key_word == "ADD" or key_word == "SUB" or key_word == "MUL" or key_word == "IDIV" or key_word == "LT" or key_word == "GT" or key_word == "EQ"
          or key_word == "AND" or key_word == "OR" or key_word == "NOT" or key_word == "STRI2INT" or key_word == "GETCHAR" or key_word == "SETCHAR" 
          or key_word == "DIV" or key_word == "ADDS" or key_word == "ANDS" or key_word == "SUBS" or key_word == "ORS" or key_word == "MULS" 
          or key_word == "IDIVS" or key_word == "CLEARS" or key_word == "LTS" or key_word == "GTS" or key_word == "EQS" or key_word == "NOTS" 
          or key_word == "STRI2INTS" or key_word == "DIVS" ):
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

        if( key_word == "CLEARS" ):
            PUSHS.clear()
            return i 

        elif( key_word == "ADDS" or key_word == "SUBS" or key_word == "MULS" or key_word == "IDIVS" ):
            push_element = []
            op1, op1t = getFromStack()
            op2, op2t = getFromStack()

            if( op1t == op2t ):
                if( op1t == "int" ):
                    if( key_word == "ADDS" ):
                        op1 = int( op1 ) + int( op2 )
                    elif( key_word == "SUBS" ):
                        op1 =  int( op2 ) - int( op1 )
                    elif( key_word == "MULS" ):
                        op1 =  int( op1 ) * int( op2 )
                    elif( key_word == "IDIVS" ):
                        op1 =  int( op2 ) // int( op1 )
                elif( op2t == "float" ):
                    if( key_word == "ADDS" ):
                        op1 = float( op1 ) + float( op2 )
                    elif( key_word == "SUBS" ):
                        op1 = float( op2 ) - float( op1 )
                    elif( key_word == "MULS" ):
                        op1 = float( op1 ) * float( op2 )
                    else:
                        print( 1185 )
                        sys.exit( 32 )
            else:
                print( "1152" )
                sys.exit( 53 )
            push_element.append( op1 )
            push_element.append( op1t )
            PUSHS.append( push_element )
            return i
        elif( key_word == "ANDS" or key_word == "ORS" ):
            push_element = []
            op1, op1t = getFromStack() 
            op2, op2t = getFromStack()

            op1, op2 = convert( op1, op2 )

            if( op1t == op2t and op1t == "bool" ):
                op1 = getBool( op1 )
                op2 = getBool( op2 )
                if( key_word == "ANDS" ):
                    op1 = op1 and op2
                else:
                    op1 = op1 or op2
                if( op1 == True ):
                    op1 = "true"
                else:
                    op1 = "false"
            else:
                print( "1176" )
                sys.exit( 53 )
            op1t = "bool"

            push_element.append( op1 )
            push_element.append( op1t )
            PUSHS.append( push_element )
            return i

        # ADD ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Součet dvou číselných hodnot
        # Sečte ⟨symb1⟩ a ⟨symb2⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné ⟨var⟩.
        if( key_word == "ADD" ):
            missingValue( op1, op2 )
            if( op1t == op2t and op1t == "int" or op1t == "float" ):
                if( op1t == "float" ):
                    if( op2t != "float" ):
                        sys.exit( 53 )
                    op1, op2 = getFloat( op1, op2 )
                    op1 = float( op1 ) + float( op2 )
                    op1t = "float"
                else:
                    op1 = int( op1 ) + int( op2 )
                    op1t = "int"
            else:
                sys.exit( 53 )
        # SUB ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Odečítání dvou číselných hodnot
        # Odečte ⟨symb2⟩ od ⟨symb1⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné ⟨var⟩.
        elif( key_word == "SUB"  ):
            missingValue( op1, op2 )
            if( op1t == op2t and op1t == "int" or op1t == "float" ):
                if( op1t == "int" ):
                    op1 = int( op1 ) - int( op2 )
                    op1t = "int"
                else:
                    if( op1t == "float" and op2t == "float" ):
                        op1, op2 = getFloat( op1, op2 )
                        op1 = float( op1 ) - float( op2 )
                        op1t = "float"
                    else:
                        sys.exit( 53 )
            else:
                sys.exit( 53 )
        # MUL ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Násobení dvou číselných hodnot
        # Vynásobí ⟨symb1⟩ a ⟨symb2⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné ⟨var⟩.
        elif( key_word == "MUL" ):
            missingValue( op1, op2 )
            if( op1t == op2t and op1t == "int" or op1t == "float" ):
                if( op1t == "int" ):
                    op1 = int( op1 ) * int( op2 )
                    op1t = "int"
                elif( op1t == "float" ):
                    if( op2t != "float" ):
                        sys.exit( 53 )
                    op1, op2 = getFloat( op1, op2 )
                    op1 = float( op1 ) * float( op2 )
                    op1t = "float"
            else:
                sys.exit( 53 )
        elif( key_word == "DIV" or key_word == "DIVS" ):
            if( key_word == "DIVS" ):
                if( key_word == "DIVS" ):
                    push_element = []
                    op2, op2t = getFromStack()
                    op1, op1t = getFromStack() 
            missingValue( op1, op2 )
            if( op1t == op2t and op1t == "float" ):
                op1, op2 = getFloat( op1, op2 )
                if( float( op2 ) == 0 ):
                    sys.exit( 57 )
                op1 = float( op1 ) / float( op2 )
                op1 = float( op1 )
            else:
                sys.exit( 53 )
            op1t = "float"
            if( key_word == "DIVS" ):
                push_element.append( op1 )
                push_element.append( op1t )
                PUSHS.append( push_element )
                return i
        # IDIV ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Dělení dvou celočíselných hodnot
        # Celočíselně podělí celočíselnou hodnotu ze ⟨symb1⟩ druhou celočíselnou hodnotou ze ⟨symb2⟩ (musí být oba typu int) a výsledek typu int přiřadí do proměnné ⟨var⟩. 
        # Dělení nulou způsobí chybu 57.
        elif( key_word == "IDIV" ):
            missingValue( op1, op2 )
            if( op1t == op2t and op1t == "int" ):
                if( int( op2 ) == 0 ):
                    sys.exit( 57 )
                op1 = int( op1 ) / int( op2 )
                op1 = int( op1 )
            else:
                sys.exit( 53 )
            op1t = "int"
        # LT/GT/EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Relační operátory menší, větší, rovno 
        # Instrukce vyhodnotí relační operátor mezi ⟨symb1⟩ a ⟨symb2⟩ (stejného typu; int, bool nebo string) a do ⟨var⟩ zapíše výsledek typu 
        # bool (false při neplatnosti nebo true v případě platnosti odpovídající relace). Řetězce jsou porovnávány lexikograficky a false je menší než true. 
        # S operandem typu nil (další zdrojový operand je libovolného typu) lze porovnávat pouze instrukcí EQ, jinak chyba 53.
        elif( key_word == "LT" or key_word == "LTS" ):
            
            if( key_word == "LTS" ):
                push_element = []
                op2, op2t = getFromStack()
                op1, op1t = getFromStack() 

            missingValue( op1, op2 )
            if( op1t == "nil" or op2t == "nil" ):
                sys.exit( 53 )
            if( ( op1t is None ) or ( op2t is None ) ):
                sys.exit( 53 )
            if( op1t == op2t ):
                vysledek = ''
                poradi = 0
                if( op1t == "str" ):
                    op1, op2 = convert( op1, op2 )
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
                elif( op1t == "float" ):
                    op1, op2 = getFloat( op1, op2 )
                    if( float( op1 ) < float( op2 ) ):
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
                sys.exit( 53 )
            op1t = "bool"
            if( key_word == "LTS" ):
                push_element.append( op1 )
                push_element.append( op1t )
                PUSHS.append( push_element )
                return i
                        
        elif( key_word == "GT" or key_word == "GTS" ):
            
            if( key_word == "GTS" ):
                push_element = []
                op2, op2t = getFromStack() 
                op1, op1t = getFromStack()

            missingValue( op1, op2 )
            if( op1t == "nil" or op2t == "nil" ):
                sys.exit( 53 )

            if( ( op1t is None ) or ( op2t is None ) ):
                sys.exit( 53 )
            if( op1t == op2t ):
                vysledek = ''
                poradi = 0
                if( op1 is None ):
                    op1 = "true"
                elif( op2 is None ):
                    op1 = "true"
                elif( op1t == "str" ):
                    op1, op2 = convert( op1, op2 )
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
                elif( op1t == "float" ):
                    op1, op2 = getFloat( op1, op2 )
                    if( float( op1 ) > float( op2 ) ):
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
                sys.exit( 53 )
            op1t = "bool"
            if( key_word == "GTS" ):
                push_element.append( op1 )
                push_element.append( op1t )
                PUSHS.append( push_element )
                return i
        elif( key_word == "EQ" or key_word == "EQS" ):
            if( key_word == "EQS" ):
                push_element = []
                op2, op2t = getFromStack()                
                op1, op1t = getFromStack()
            if( op1t == "nil" or op2t == "nil" ):
                ...
            elif( op1t is None or op2t is None ):
                print( 1462 )
                sys.exit( 56 )
            else:
                ...
            
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
                    op1, op2 = convert( op1, op2 )
                    if( op1 == op2 ):
                        op1 = "true"
                    else:
                        op1 = "false"
                elif( op1t == "int" ):
                    if ( int( op1 ) == int( op2 ) ):
                        op1 = "true"
                    else:
                        op1 = "false"
                elif( op1t == "float" ):
                    op1, op2 = getFloat( op1, op2 )
                    if ( float( op1 ) == float( op2 ) ):
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
                sys.exit( 53 )
            op1t = "bool"
            if( key_word == "EQS" ):
                push_element.append( op1 )
                push_element.append( op1t )
                PUSHS.append( push_element )
                return i
        # AND/OR/NOT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Základní booleovské operátory
        # Aplikuje konjunkci (logické A)/disjunkci (logické NEBO) na operandy typu bool ⟨symb1⟩ a ⟨symb2⟩ nebo negaci na ⟨symb1⟩ (NOT má pouze 2 operandy) a výsledek typu bool zapíše do ⟨var⟩.
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
                sys.exit( 53 )
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
                sys.exit( 53 )
            op1t = "bool"
        elif( key_word == "NOT" or key_word == "NOTS" ):
            if( key_word == "NOT" ):
                data_type = getType( word[ 1 ] )
            if( key_word == "NOTS" ):
                push_element = []
                op1, op1t = getFromStack()
            if( data_type == "nil" ):
                sys.exit( 53 )
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
                sys.exit( 53 )
            op1t = "bool"
            if( key_word == "NOTS" ):
                push_element.append( op1 )
                push_element.append( op1t )
                PUSHS.append( push_element )
                return i
        # STRI2INT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Ordinální hodnota znaku
        # Do ⟨var⟩ uloží ordinální hodnotu znaku (dle Unicode) v řetězci ⟨symb1⟩ na pozici ⟨symb2⟩ (indexováno od nuly). 
        # Indexace mimo daný řetězec vede na chybu 58. Viz funkce ord v Python 3.
        elif( key_word == "STRI2INT" or key_word == "STRI2INTS" ):
            if( key_word == "STRI2INTS" ):
                push_element = []
                op2, op2t = getFromStack()
                op1, op1t = getFromStack()
            if( ( op2t is None ) or ( op1t is None ) ):
                print( 1575 )
                sys.exit( 56 )
            if( ( op1t != "str" and op1 == "nil" ) or ( op2t != "int" and op2 == "nil" ) or ( op1t != "str" and op1 != "nil" ) or ( op2t != "int" and op2 != "nil" ) ):
                sys.exit( 53 )
            if( int( op2 ) < 0 ):
                sys.exit( 58 )
            try:
                op1 = ord( op1[ int( op2 ) ] )
            except:
                sys.exit( 58 )
            op1t = "int"
            if( key_word == "STRI2INTS" ):
                push_element.append( op1 )
                push_element.append( op1t )
                PUSHS.append( push_element )
                return i
        # GETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Vrať znak řetězce 
        # Do ⟨var⟩ uloží řetězec z jednoho znaku v řetězci ⟨symb1⟩ na pozici ⟨symb2⟩ (indexováno celýmčíslem od nuly). Indexace mimo daný řetězec vede na chybu 58.
        elif( key_word == "GETCHAR" ):
            sample = len( op1 )
            if( op1 == '' or op2 == '' ):
                print( 1596 )
                sys.exit( 56 )
            if( ( op1t != "str" ) or ( op2t != "int" ) ):
                sys.exit( 53 )
            if( sample <= int( op2 ) or int( op2 ) < 0 ):
                sys.exit( 58 )
            op1 = op1[ int( op2 ) ]
            op1t = "str"
        # SETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ Změň znak řetězce
        # Zmodifikuje znak řetězce uloženého v proměnné ⟨var⟩ na pozici ⟨symb1⟩ (indexováno celočíselněod nuly) na znak v řetězci ⟨symb2⟩ (první znak, pokud obsahuje⟨symb2⟩více znaků). 
        # Výsledný řetězec je opět uložen do ⟨var⟩. Při indexaci mimo řetězec ⟨var⟩ nebo v případě prázdného řetězce v ⟨symb2⟩ dojde k chybě 58.
        elif( key_word == "SETCHAR" ):
            sentence = getValue( to_frame )
            sentenceT = getType( to_frame )
            if( sentenceT is None ):
                print( 1611 )
                sys.exit( 56 )
            if( sentenceT != "str" ):
                sys.exit( 53 )
            sentence = list( sentence )
            sentence_length = len ( sentence )
            if( op2 == '' ):
                print( 1618 )
                sys.exit( 56 )
            if( op1 == "nil" ):
                sys.exit( 53 )
            if( op1t is None ):
                print( 1623 )
                sys.exit( 56 )
            if( op2 is None ):
                sys.exit( 58 )
            if( op1t != "int" ):
                sys.exit( 53 )
            if( sentence_length <= int( op1 ) or int( op1 ) < 0 ):
                sys.exit( 58 )
            if( op1t != "int" ):
                sys.exit( 53 )
            if( op2t != "str" ):
                sys.exit( 53 )
            op1, op2 = convert( op1, op2 )
            sentence[ int( op1 ) ] = op2[ 0 ]
            op1 = ''.join( sentence )
            op1t = "str"
        writeTo( to_frame, op1, op1t )
    elif( key_word == "INT2CHAR" or key_word == "INT2FLOAT" or key_word == "FLOAT2INT" or key_word == "INT2CHARS" or key_word == "INT2FLOATS" ):
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
            sys.exit( 53 )
        if( op1 == "" ):
            print( 1656 )
            sys.exit( 56 )
        # INT2CHAR ⟨var⟩ ⟨symb⟩ Převod celého čísla na znak
        # Číselná hodnota ⟨symb⟩ je dle Unicode převedena na znak, který tvoří jednoznakový řetězec přiřazený do ⟨var⟩. 
        # Není-li ⟨symb⟩ validní ordinální hodnota znaku v Unicode (viz funkce chr v Python 3), dojde k chybě 58.
        if( key_word == "INT2CHAR" or key_word == "INT2CHARS" ):
            if( key_word == "INT2CHARS" ):
                push_element = []
                op1, op1t = getFromStack()
            if( op1t != "int" ):
                sys.exit( 53 )
            try:
                op1 = chr( int( op1 ) )
                op1t = "str"
            except:
                sys.exit( 58 )
            if( key_word == "INT2CHARS" ):
                push_element.append( op1 )
                push_element.append( op1t )
                PUSHS.append( push_element )
                return i
        # INT2FLOAT ⟨var⟩ ⟨symb⟩ Převod čísla na float
        # Číselná hodnota ⟨symb⟩ je dle Unicode převedena na float.
        # Není-li ⟨symb⟩ validní ciselna hodnota, dojde k chybě 58.
        elif( key_word == "INT2FLOAT" or key_word == "INT2FLOATS" ):
            if( key_word == "INT2FLOATS" ):
                push_element = []
                op1, op1t = getFromStack()
            if( op1t == "int" ):
                op1 = float( op1 )
                op1t = "float"
            else:
                sys.exit( 53 ) #je to spravne ?
            if( key_word == "INT2FLOATS" ):
                push_element.append( op1 )
                push_element.append( op1t )
                PUSHS.append( push_element )
                return i
        # FLOAT2INT ⟨var⟩ ⟨symb⟩ Převod float na číslo
        # Float hodnota ⟨symb⟩ je dle Unicode převedena na int.
        # Není-li ⟨symb⟩ validní float hodnota, dojde k chybě 58.
        elif( key_word == "FLOAT2INT" ):
            if( op1t == "float" ):
                op1, op2 = getFloat( op1, op2 )
                op1 = int( op1 )
                op1t = "int"
            else:
                sys.exit( 53 ) #je to spravne ?
        writeTo( to_frame, op1, op1t )
    # BREAK Výpis stavu interpretu nastderr
    # Předpokládá se, že na standardní chybový výstup (stderr) vypíše 
    # stav interpretu (např. pozicev kódu, obsah rámců, počet vykonaných instrukcí) v danou chvíli (tj. během vykonávání tétoinstrukce).
    elif( key_word == "BREAK" ):
        sys.stderr.write( str( instruction_counter ) )
    # READ ⟨var⟩ ⟨type⟩ Načtení hodnoty ze standardního vstupu
    # Načte jednu hodnotu dle zadaného typu⟨type⟩ ∈ {int, string, bool} a uloží tuto hodnotu doproměnné⟨var⟩. 
    # Načtení provadi vestavěnou funkcí input() jazyka Python 3, pak se provadi konverze na specifikovaný typ ⟨type⟩. 
    # Při převodu vstupu na typ bool nezáleží na velikosti písmena řetězec ”true“ se převádí na bool@true, vše ostatní na bool@false. 
    # V případě chybného nebo chybějícího vstupu bude do proměnné ⟨var⟩ uložena hodnota nil@nil.
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
            line = line.rstrip()
        else:
            # kontroluje EOF
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
                    writeTo( to_frame, line, "str" )
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
            elif( rtype == "float" ):
                if( line == '' ):
                    line = ''
                    writeTo( to_frame, line, "float" )
                else:
                    line = float.fromhex( line )
                    writeTo( to_frame, line, "float" )
        else:
            ...
    # PUSHS ⟨symb⟩ Vlož hodnotu na vrchol datového zásobníku
    # Uloží hodnotu ⟨symb⟩ na datový zásobník.
    elif( key_word == "PUSHS" ):
        check_args( args, [ 'symb' ] )
        
        what = ""
        push_element = []
        check = 0
        frame_from = ''

        for word in args:
            what = word[ 1 ]
            data_type = getType( word )
            frame_from = word

        try:
            frame, var = at_split( what )
            check = 1
        except:
            ...
        if( check == 1 ):
            if( frame == "GF" ):
                if not var in GF:
                    sys.exit( 54 )
            elif( frame == "LF" ):
                if not var in LF:
                    sys.exit( 54 )
            elif( frame == "TF" ):
                if not var in TF:
                    sys.exit( 54 )
            if( data_type is None ):
                print( 1804 )
                sys.exit( 56 )
        if( data_type == "float" ):
            try:
                what = float.fromhex( what )
            except:
                ...
        what = getValue( what )
        #print( what, data_type, frame_from )
        #if( frame_from[ 1 ] == "GF@%result" ):
            #print( GF )
            #print( what, data_type )
        if( data_type == "str" ):
            what = convertor( what )
        push_element.append( what )
        push_element.append( data_type )
        PUSHS.append( push_element )
    # CREATEFRAME Vytvoř nový dočasný rámec
    # Vytvoří nový dočasný rámec a zahodí případný obsah původního dočasného rámce.
    elif( key_word == "CREATEFRAME" ):
        check_args( args, [] )
        TF.clear()
        tf_accessible = 1
    # PUSHFRAME Přesun dočasného rámce na zásobník rámců 
    # Přesuň TF na zásobník rámců. Rámec bude k dispozici přes LF a překryje původní rámce na zásobníku rámců.
    # TF bude po provedení instrukce nedefinován a je třeba jej před dalším použitím vytvořit pomocí CREATEFRAME. 
    # Pokus o přístup k nedefinovanému rámci vede nachybu 55.
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
            sys.exit( 55 )
    # POPFRAME Přesun aktuálního rámce do dočasného
    # Přesuň vrcholový rámec LF ze zásobníku rámců do TF. 
    # Pokud žádný rámec v LF není k dispozici, dojde k chybě 55.
    elif( key_word == "POPFRAME" ):
        check_args( args, [] )
        values = len( FRAME_STACK )
        if( len( FRAME_STACK ) == 0 ):
            sys.exit( 55 )
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
        print( 1814 )
        print( key_word )
        sys.exit( 32 )
    return i

# -----------------------------------------------------------
# Funkce execute
#
# Parametr program nacteny xml format v poli
#
# Funkce prochazi nacteny xml v poli. Jedna se o dvoupruchodovou implementaci, kdy pri prvnim pruchodu se zpracuji LABELY a pri druhem zbytek progamu 
#
# Return none
# -----------------------------------------------------------
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
                checkRegisters()
                i = i + 1 
        r += 1
        i = 0

params() 


#
## Podle toho, jestli se ma brat vstup ze stdin nebo ze souboru se nastavi promenna
#
source_content = ""

if( source_is == "file" ):
    with open(source, 'r') as file:
        source_content = file.read()

if( source_is == "stdin" ):
    
    for line in sys.stdin:
        source_content = source_content + line

well_formatted( source_content )

#
## pomoci element tree prasuji xml soubor
#
tree = ET.ElementTree( ET.fromstring( source_content ) )
root = tree.getroot()

program = root.tag

if( program != 'program' ):
    print( 1877 )
    sys.exit( 32 )

header = root.attrib

if( header[ 'language' ] != "IPPcode20" ):
    print( 1883 )
    sys.exit( 32 )

instructions = []

if( input_is == "file" ):
    file1 = open( input_file, 'r')

opcode_insts = 0

#
## Dictionary pro uchovani argumentu a casti xml. Pomoci techto dictionary pak jednotlive xml casti davam do pole.
#
TESTING = dict()
ARGS = dict()

#
## Mozne hodnoty pro parametr  v program xml parametru
#
for arg in root.attrib:
    if( arg == "language" ):
        ...
    elif( arg == "name" ):
        ...
    elif( arg == "description" ):
        ...
    else:
        print( 1910 )
        sys.exit( 32 )

for child in root:
    if( str( child.tag ) != "instruction" ):
        print( 1915 )
        sys.exit( 32 )
    # jestlize order uz byl pouzit nebo byl mensi nez 0
    try:
        int( child.attrib[ 'order' ] )
    except:
        print( 1921 )
        sys.exit( 32 )
    if( ( int( child.attrib[ 'order' ] ) in TESTING ) or ( int( child.attrib[ 'order' ] ) < 0 ) ):
        print( 1924 )
        sys.exit( 32 )
    TESTING[ int( child.attrib[ 'order' ] ) ] = child


#
## Tato cast skriptu kompletne zpracovava xml soubor a dava hodnoty do pole
#
for element in sorted( TESTING.keys() ):
    instruction = []
    instruction.append( int( element ) )
    try:
        instruction.append( TESTING[ element ].attrib[ 'opcode' ] )
    except:
        print( 1938 )
        sys.exit( 32 )
    for supr in TESTING[ element ].attrib:
        if( supr == "opcode" ):
            ...
        elif( supr == "order" ):
            ...
        else:
            print( 1946 )
            sys.exit( 32 )
    order_inc = order_inc + 1
    counter = len( TESTING[ element ] )
    for test in TESTING[ element ]:
        if( test.tag == "arg1" ):
            ...
        elif( test.tag == "arg2" ):
            ...
        elif( test.tag == "arg3" ):
            ...
        else:
            print( 1958 )
            sys.exit( 32 )
        if( int( test.tag[ 3: ] ) > counter ):
            print( 1961 )
            sys.exit( 32 )
        ARGS[ test.tag[ 3: ] ] = test
    args = []
    for test in sorted( ARGS.keys() ):
        arg_array = []
        arg_array.append( ARGS[ test ].attrib[ 'type' ] )
        typeT = ARGS[ test ].attrib[ 'type' ]
        if( ( typeT == "int" ) or ( typeT == "float" ) or ( typeT == "string" ) or ( typeT == "bool" ) or ( typeT == "nil" ) or ( typeT == "type" ) or ( typeT == "label" ) or ( typeT == "var" ) ):
            ...
        else:
            print( 1972 )
            sys.exit( 32 )
        arg_array.append( ARGS[ test ].text )
        args.append( arg_array )
    ARGS.clear()
    instruction.append( args )
    instructions.append( instruction)

execute( instructions )

if( input_is == "file" ):
    file1.close() 

writeStats()