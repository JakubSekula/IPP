<?php

function getChar( $file ){
    $line = fgets( $file );
    if ( ( $line ) || ( $line ) != 'EOF' ){
        return $line;
    } else {
        return NULL;
    }
}

// 1 = int
// 2 = char
// 3 = @
// 10 = \n
// 13 = \r
// 22 = neco jineho

function Type( $code ){
    if ( $code >= 48 && $code <= 57 ){
        return 1;
    } elseif ( ( $code >= 65 && $code <= 90 ) || ( $code >= 97 && $code <= 122 ) ){
        return 2;
    } elseif ( $code == 64 ){
        return 3;
    } elseif ( $code == 10 ){
        return 10;
    } elseif ( $code == 13 ){
        return 13;
    } else {
        return 22;
    }
}

if ( $argc > 1 && $argv[1] == "--help" ){
    echo "Skript typu filtr (parse.php v jazyce PHP 7.4) nacte ze standardniho vstupu zdrojovy kod v IPP-code20, zkontroluje \nlexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu dle specifikace v sekci.\n";
    exit;
}

$file = fopen( "program", "r" ) or die( "Soubor nelze otevrit nebo neexistuje" );

while ( ( $line = getChar( $file ) ) != NULL ){
    echo $line;
}

fclose( $file );
?>