<?php

include 'test_args.php';

function executeCommand( $command, $outFile ){
    exec( $command, $out, $rv );
    $file = preg_replace( '/\.out/', '.rc', $outFile );
    $rcFile = fopen( "$file", "w" );
    fwrite( $rcFile, $rv );
    fclose( $rcFile );
}

function testThis( $testPath, $file ){
    global $parsescript;
    if ( preg_match( '/\.src/', $file ) ){
        $file = preg_replace( '/\.src$/', '', $file );
        $file = $file."_parser.out";
        $command = "php7.4 "."$parsescript <"."$testPath >"."$file";
        executeCommand( $command, $file );
    }
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

$test = array( 'test' => 1, 'dalsi' => 2 );

?>