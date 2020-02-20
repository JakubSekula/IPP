<?php

include 'test_args.php';

function testThis( $testPath, $file ){
    global $parsescript;
    $file = preg_replace( '/\.src$/', '', $file );
    echo $testPath."\n";
    $file = $file."_parser.out";
    $command = "php "."$parsescript <"."$testPath >"."$file"; 
    exec( $command, $out, $rv );
    echo $rv."\n";
}

function goOver( $directory, $recursive ){
    $adresar = array_diff( scandir( "$directory"), array( '..', '.' ));

    foreach( $adresar as $file ){
        if ( !is_dir( "$directory"."/".$file ) ){
            $testPath = $directory."/".$file;
            testThis( $testPath, $file );
        }
        if ( $recursive == 1 ){
            if( is_dir( "$directory"."/".$soubor ) ){
                goOver( "$directory"."/".$soubor, $recursive  );
            }
        }
    }
}

goOver( $directory, $recursive );

?>