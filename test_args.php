<?php

$directory = ".";
$parsescript = "parse.php";
$intscript = "interpret.py";
$jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
$help_argument = 0;
$parseonly = 0;
$intonly = 0;
$recursive = 0;

if ( $argc > 1 ){
    foreach( $argv as $current ){
        if ( $current == "test.php" ){
            continue;
        }
        if ( preg_match( '/^(\-){1,2}help$/', $current ) ){
            $help_argument = 1;
        } elseif ( preg_match( '/^(\-){1,2}directory=(((\.)|(\.\.)|(\.\.\/)+|(\/))|([a-zA-Z]+))$/', $current ) ) {
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            if ( !is_dir( "$path" ) ){
                exit( 11 );
            }
            if ( $path != "" ){
                $directory = $path;
            }
        } elseif( preg_match( '/^(\-){1,2}recursive$/', $current ) ){
            $recursive = 1;
        } elseif( preg_match( '/^(\-){1,2}parse-script=(((\.)|(\.\.)|(\.\.\/)+|(\/))|([a-zA-Z]+))$/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            if ( $path != "" ){
                $parsescript = $path;
            }
        } elseif( preg_match( '/^(\-){1,2}int-script=(((\.)|(\.\.)|(\.\.\/)+|(\/))|([a-zA-Z]+))$/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            if ( $path != "" ){
                $intscript = $path;
            }
        } elseif( preg_match( '/^(\-){1,2}parse-only$/', $current ) ){
            $parseonly = 1;
        } elseif( preg_match( '/^(\-){1,2}int-only$/', $current ) ){
            $intonly = 1;
        } elseif( preg_match( '/^(\-){1,2}jexamxml=(((\.)|(\.\.)|(\.\.\/)+|(\/))|([a-zA-Z]+))$/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            if ( $path != "" ){
                $jexamxml = $path;
            }
        } else {
            exit( 10 );
        }
    }
}

if ( $argc > 2 ){
    if ( $help_argument == 1 ){
        exit( 10 );
    }
}

if ( $help_argument == 1 ){
    echo "Skript (test.phpv jazyce PHP 7.4) bude sloužit pro automatické testování postupné\naplikaceparse.phpainterpret.py12. Skript projde zadaný adresář s testy a využije\nje pro automatickéotestování správné funkčnosti obou předchozích programů včetně\nvygenerování přehledného souhrnuv HTML 5 do standardního výstupu. \n";
    exit( 0 );
}

if ( $parseonly == 1 && ( $intonly == 1 || $intscript != "interpret.py" ) ){
    exit( 10 );
} elseif( $intonly == 1 && ( $parseonly == 1 || $intscript != "interpret.py" ) ){
    exit( 10 );
}

/* if ( !file_exists( $intscript."/interpret.py" ) ){
    exit( 11 );
} */

if ( !file_exists( $parsescript ) ){
    exit( 11 );
}

echo "--help: $help_argument\n";
echo "--directory=path: $directory\n";
echo "--recursive: $recursive\n";
echo "--parse-script: $parsescript\n";
echo "--int-script: $intscript\n";
echo "--parsed-only: $parseonly\n";
echo "--int-only: $intonly\n";
echo "--jexamxml: $jexamxml\n";



// TODO kontrola jexamxml jestli existuje
?>