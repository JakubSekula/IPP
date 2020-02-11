<?php

function returnLine( $line ){
    if ( ( $line ) || ( $line ) != 'EOF' ){
        return $line;
    } else {
        return NULL;
    }
}

function getLine( $file ){
    if ( $file ){
        $line = fgets( $file );
        return returnLine( $line );
    } else {
        $line = fgets( STDIN );
        return returnLine( $line );
    }
}

$arguments = array( 'help' => false, 'source' => '' );

if ( $argc > 1 ){
    foreach ( $argv as $arg ){
        if ( $arg == "--help" ){
            $arguments[ 'help' ] = true;
        } elseif ( preg_match( '/^--source=(")*(\.)*([a-zA-Z]*(\/)*)*(")*$/', $arg ) ){
            $arguments[ 'source' ] = substr( $arg, 9 );
        }
    }
}

if ( $arguments[ 'help' ] ){
    echo "Skript typu filtr (parse.php v jazyce PHP 7.4) nacte ze standardniho vstupu zdrojovy kod v IPP-code20, zkontroluje \nlexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu dle specifikace v sekci.\n";
    exit;
}

global $file;
if ( $arguments[ 'source' ] != '' ){
    if ( file_exists( $arguments[ 'source' ] ) ){
        $file = fopen( $arguments[ 'source' ], "r" ) or exit( 11 );
    } else {
        exit( 11 );
    }
}
/*
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
echo "<program language=\"IPPcode19\">\n";
*/
global $FLine;
if ( $file ){
    $FLine = fgets( $file );
} else {
    $FLine = fgets( STDIN );
}

$header = "/^[ ]*.IPPCODE20$/";

if ( !( preg_match( $header,$FLine ) ) ){
    exit( 21 );
}

while ( ( $line = getLine( $file ) ) != NULL ){
    echo $line;
}

//echo "</program>\n";
//fclose( $file );
?>