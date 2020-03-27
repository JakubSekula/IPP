<?php

/*                                                  */
/*             Jakub Sekula ( xsekul01 )            */
/*                                                  */

/*
** Skript test_args.php slouzi pouze pro parsovani argumentu skriptu test.php
*/

$directory = ".";
global $parsescript;
$parsescript = "parse.php";
$intscript = "interpret.py";
$jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
$help_argument = 0;
$parseonly = 0;
$intonly = 0;
$recursive = 0;

if ( $argc > 1 ){
    foreach( $argv as $current ){
        // prvni argument je samotny skript ktery spoustim
        if ( preg_match( '/test\.php/', $current ) ){
            continue;
        }
        if ( preg_match( '/^(\-){2}help$/', $current ) ){
            $help_argument = 1;
        } elseif ( preg_match( '/^(\-){2}directory=/', $current ) ) {
            // do path nastavim string za =
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            if ( !is_dir( "$path" ) ){
                exit( 11 );
            }
            if ( $path != "" ){
                $directory = $path;
            }
        } elseif( preg_match( '/^(\-){2}recursive$/', $current ) ){
            $recursive = 1;
        } elseif( preg_match( '/^(\-){2}parse-script=/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            if ( is_file( $path ) ){
                $parsescript = $path;
            } else {
                exit( 11 );
            }
        } elseif( preg_match( '/^(\-){2}int-script=/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            if ( is_file( $path ) ){
                $intscript = $path;
            } else {
                exit( 11 );
            }
        } elseif( preg_match( '/^(\-){2}parse-only$/', $current ) ){
            $parseonly = 1;
        } elseif( preg_match( '/^(\-){2}int-only$/', $current ) ){
            $intonly = 1;
        } elseif( preg_match( '/^(\-){2}jexamxml=/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            if ( is_file( $path ) ){
                $jexamxml = $path;
            } else {
                exit( 11 );
            }
        } else {
            // jine argumenty jsou chybou
            exit( 10 );
        }
    }
}

// jestlize je zadan --help musi byt jediny parametr
if ( $argc > 2 ){
    if ( $help_argument == 1 ){
        exit( 10 );
    }
}

if ( $help_argument == 1 ){
    echo "Skript (test.phpv jazyce PHP 7.4) bude sloužit pro automatické testování postupné\naplikaceparse.phpainterpret.py12. Skript projde zadaný adresář s testy a využije\nje pro automatickéotestování správné funkčnosti obou předchozích programů včetně\nvygenerování přehledného souhrnuv HTML 5 do standardního výstupu. \n";
    exit( 0 );
}
// kombinace parametru ktere spolu nemohou byt
if ( $parseonly == 1 && ( $intonly == 1 || $intscript != "interpret.py" ) ){
    exit( 10 );
} elseif( $intonly == 1 && ( $parseonly == 1 || $intscript != "interpret.py" ) ){
    exit( 10 );
}
// jestlize soubor neexistuje 
if ( !file_exists( $parsescript ) ){
    exit( 11 );
}

?>
