<?php

function getLine( $file ){
    $line = fgets( $file );
    if ( ( $line ) || ( $line ) != 'EOF' ){
        return $line;
    } else {
        return NULL;
    }
}

if ( $argc > 1 && $argv[1] == "--help" ){
    echo "Skript typu filtr (parse.php v jazyce PHP 7.4) nacte ze standardniho vstupu zdrojovy kod v IPP-code20, zkontroluje \nlexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu dle specifikace v sekci.\n";
    exit;
}

$file = fopen( "program", "r" ) or die( "Soubor nelze otevrit nebo neexistuje" );

$FLine = fgets( $file );

$header = "/^.IPPCODE20$/";

if ( !( preg_match( $header,$FLine ) ) ){
    exit( 21 );
}

while ( ( $line = getLine( $file ) ) != NULL ){
    echo $line;
}

fclose( $file );
?>