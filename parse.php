<?php

function checkVar( $parsed ){
    if ( !preg_match( '/^((TF)|(GF)|(LT))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)){0,1}(\w)+$/', $parsed ) ){
        exit( 23 );
    }
}

function checkEnd( $parsed ){
    if ( $parsed != "" ){
        exit ( 23 );
    }
}

function checkSymb( $parsed ){
    if ( !preg_match( '/^(string@(\S)*)$|^(int@(\d)*)$|(bool@((true)|(false)))$|^((GF)|(TF)|(LT))@(\S)*$/', $parsed ) ){
        exit( 23 );
    }
}

function checkLabel( $parsed ){
    if ( !preg_match( '/^(\w)*/', $parsed ) ){
        exit( 23 );
    }
}

function checkSyntax( $parsed ){
    switch( $parsed[ 0 ] ){
        case "MOVE":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkEnd( $parsed[ 3 ] );
            break;
        case "DEFVAR":
            checkVar( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            break;
        case "AND":
            echo "Je to AND";
            break;
        case "WRITE":
            checkSymb( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            break;
        case "LABEL":
            checkLabel( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            break;
        case "JUMPIFEQ":
            checkLabel( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            break;
        case "CONCAT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            break;
        case "JUMP":
            checkLabel( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            break;
    }
}

function returnLine( $line ){
    if ( ( $line ) || ( $line ) != 'EOF' ){
        return $line;
    } else {
        return NULL;
    }
}

function getLine( $file ){
    $line = fgets( STDIN );
    return returnLine( $line );
}

function isKeyWord( $token ){
    $keyWords = array(  "MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL",
                        "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MULL", "IDIV", "LT", "GT",
                        "EQ", "AND", "OR", "INT2CHAR", "STRI2INT", "READ", "WRITE", "STRLEN",
                        "GETCHAR", "SETCHAR", "NOT", "LABEL", "JUMPIFEQ", "CONCAT", "JUMP",
                        "TYPE",  "EXIT", "DPRINT", "BREAK" );
    if ( !( in_array( $token,$keyWords ) ) ){
        exit ( 22 );
    }
    return;
}

function parseLine( $line ){
    $line = preg_replace( '/\s+/', " ",$line );
    $parsed = explode( " ", $line );
    
    if ( !( preg_match( '/\#/', $parsed[0] ) ) ){
        isKeyWord( $parsed[0] );
        checkSyntax( $parsed );
    }

    foreach( $parsed as $token ){
        if ( preg_match( '/^#/', $token ) ){
            return;
        }
    }
}

$arguments = array( 'help' => false );

if ( $argc > 1 ){
    if ( $argv[ 1 ] == "--help" ){
        echo "Skript typu filtr (parse.php v jazyce PHP 7.4) nacte ze standardniho vstupu zdrojovy kod v IPP-code20, zkontroluje \nlexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu dle specifikace v sekci.\n";
        exit;
    } else {
        exit ( 10 );
    }
}

$FLine = fgets( STDIN );

$header = "/^[ ]*.IPPcode20$/";

if ( !( preg_match( $header,$FLine ) ) ){
    exit( 21 );
}

while ( ( $line = getLine( $FLine ) ) != NULL ){
    parseLine( $line );
}

// TODO podoba label
// TODO napriklad WHILE bez parametru vyhodi chybu protoze neni definovan parametr
// TODO Zeptat se co delat kdyz je kurzor na novem radku na stdin. Kurzor ale na STDIN pokud neni soubor nemuze byt na novem radku ?...
// TODO je odstraneni prebytecnych mezer korektni osetreni ? Treba: MOVE     GF@counter neni chyba ci ?

?>