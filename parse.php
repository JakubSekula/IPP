<?php

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
}

function parseLine( $line ){
    $line = preg_replace( '/\s+/', " ",$line );
    $parsed = explode( " ", $line );
    
    if ( !( preg_match( '/\#/', $parsed[0] ) ) ){
        isKeyWord( $parsed[0] );
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

?>