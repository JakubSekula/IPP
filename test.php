<?php

include 'test_args.php';

function goOver( $directory, $recursive ){
    $adresar = array_diff( scandir( "$directory"), array( '..', '.' ));

    foreach( $adresar as $soubor ){
        if ( !is_dir( "$directory"."/".$soubor ) ){
            echo "$directory"."/".$soubor."\n";
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