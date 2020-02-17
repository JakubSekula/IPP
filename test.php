<?php

$help_argument = 0;
$directory = "";
$recursive = 0;
$parsescript = "";
$intscript = "";
$parseonly = 0;
$intonly = 0;
$jexamxml = "";

if ( $argc > 1 ){
    foreach( $argv as $current ){
        if ( $current == "test.php" ){
            continue;
        }
        if ( preg_match( '/^(\-){1,2}help$/', $current ) ){
            $help_argument = 1;
        } elseif ( preg_match( '/^(\-){1,2}directory=((..\/)*(\w+)(\/){0,1})+$/', $current ) ) {
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            $directory = $path;
        } elseif( preg_match( '/^(\-){1,2}recursive$/', $current ) ){
            $recursive = 1;
        } elseif( preg_match( '/^(\-){1,2}parse-script=((..\/)*(\w+)(\/){0,1})+$/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            $parsescript = $path;
        } elseif( preg_match( '/^(\-){1,2}int-script=((..\/)*(\w+)(\/){0,1})+$/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            $intscript = $path;
        } elseif( preg_match( '/^(\-){1,2}parse-only$/', $current ) ){
            $parseonly = 1;
        } elseif( preg_match( '/^(\-){1,2}int-only$/', $current ) ){
            $intonly = 1;
        } elseif( preg_match( '/^(\-){1,2}jexamxml=((..\/)*(\w+)(\/){0,1})+$/', $current ) ){
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            $jexamxml = $path;
        } else {
            exit( 10 );
        }
    }
}

echo "--help: $help_argument\n";
echo "--directory=path: $directory\n";
echo "--recursive: $recursive\n";
echo "--parse-script: $parsescript\n";
echo "--int-script: $intscript\n";
echo "--parsed-only: $parseonly\n";
echo "--int-only: $intonly\n";
echo "--jexamxml: $jexamxml\n";


?>