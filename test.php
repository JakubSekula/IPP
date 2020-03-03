<!--         
        Jakub Sekula

     IPP - VUT-FIT 2020
 -->

<!DOCTYPE html>
<html>
<head>
<style>
body {
  padding: 0;
  margin: 0;
    font-family: Arial;
  background-color: white;
}
.returns {
  border-collapse: collapse;
}

.returns td, .returns th {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

#test{
    width: 10%;
}
#navrat{
    text-align: center;
}

.returns tr:nth-child(even){background-color: #f2f2f2;}

.returns th {
  padding-top: 12px;
  padding-bottom: 12px;
  background-color: #1B526B; 
  color: white;
}

.tabulka{
    width: 50%;
    margin: 0 auto;
    margin-top: 20px;
}

h1{
    text-align: center;
    color: #1B526B;
}

#prosel{
    background-color: #20c79d;
}

#neprosel{
    background-color: #ff0000;
}

.proc{
    border-bottom: 1.5px solid #aaa;
    padding-bottom: 1px;
}

.celkova{
    width: 18%;
    position:fixed;
    bottom:2%;
    margin-left: 1%;
}

.author{
    width: 18%;
    position:fixed;
    bottom:3%;
    margin-left: 88%;
    color: #1B526B;
}

#login{
    width: 18%;
    position:fixed;
    bottom:1%;
}

.params{
    width: 18%;
    position:fixed;
    top: 10.7%;
    margin-left: 0.5%;
}

.params td{
    text-align:left;
}

#anone{
    text-align:center;
}

</style>
</head>
<body>
<div class="proc">
 <h1>Vysledkova tabulka IPP projektu</h1>
</div>    

<?php

$successful = 0;
$failed = 0;

include 'test_args.php';

$nowRoute = getcwd();

mkdir( $nowRoute."/"."TmpTestFolder" );

$testOutDir = $nowRoute."/"."TmpTestFolder";

/* 
** Funkce vypise html tabulku ve ktere je videt ktere parametry byly predany skriptu
*/

function writeParams(){
    global $parsescript;
    global $directory;
    global $intscript;
    global $jexamxml;
    global $help_argument;
    global $parseonly;
    global $intonly;
    global $recursive;

    $zmenaDirectory = 0;
    $zmenaParsesscript = 0;
    $zmenaIntscript = 0;
    $zmenaJexamxml = 0;
    $zmenaHelp_argument = 0;
    $zmenaParseonly = 0;
    $zmenaIntonly = 0;
    $zmenaRecursive = 0;

    if( $parsescript != "parse.php" ){ $zmenaParsesscript = 1; };
    if( $directory != "." ){ $zmenaDirectory = 1; };
    if( $intscript != "interpret.py" ){ $zmenaIntscript = 1; };
    if( $jexamxml != "/pub/courses/ipp/jexamxml/jexamxml.jar" ){ $zmenaJexamxml = 1; };
    if( $help_argument != 0 ){ $zmenaHelp_argument = 1; };
    if( $parseonly != 0 ){ $zmenaParseonly = 1; };
    if( $intonly != 0 ){ $zmenaIntonly = 1; };
    if( $recursive != 0 ){ $zmenaRecursive = 1; };

    $args = array( '-1' => "--help", '0' => "--directory=path", '1' => "--recursive", '2' => "--parse-script=path", '3' => "--int-script=file", '4' => "--parse-only", '5' => "--int-only", '6' => "--jexamxml=file" );
    $zadany = array( '-1' => "$zmenaHelp_argument", '0' => "$zmenaDirectory", '1' => "$zmenaRecursive", '2' => "$zmenaParsesscript", '3' => "$zmenaIntscript", '4' => "$zmenaParseonly", '5' => "$zmenaIntonly", '6' => "$zmenaJexamxml" );

    $i = 0;

    echo "<div class='params'>";
        echo "<table class='returns params'>";
            echo "<tr>";
                echo "<th>Parametr</th>";
                echo "<th>Zadan</th>";
            echo "</tr>";
            while( $i < 8 ){
                echo "<tr>";
                    echo "<td><b>".$args[ $i-1 ]."</b></td>";
                    if( $zadany[ $i-1 ] == 1 ){
                        echo "<td id='anone'><b>ANO</b></td>";
                    } else {
                        echo "<td id='anone'><b>NE</b></td>";
                    }
                echo "</tr>";
                $i++;
            }
        echo "</table>";
    echo "</div>";

    echo "<div class='tabulka'>";
        echo "<table class='returns'>";
          echo "<tr>";
            echo "<th>Test</th>";
            echo "<th id='test'>Navratovy kod</th>";
            echo "<th id='test'>Ocekavany kod</th>";
            echo "<th>Vysledek</th>";
          echo "</tr>";

}

/* 
** Na konec se vypise pocet projitych testu a jejich uspesnost
*/

function writeStats(){
    global $successful;
    global $failed;
    $percentage = ( $successful + $failed ) / 100;
    if( $percentage != 0 ){
        $percentage = $successful / $percentage;
    } else {
        $percentage = 0;
    }

    echo "</table>";
    echo "</div>";
    echo "<div class='vysledkovka'>";
    echo "<table class='returns celkova'>";
        echo "<tr>";
            echo "<th>Proslo</th>";
            echo "<th>Neproslo</th>";
            echo "<th>Uspesnost v %</th>";
          echo "</tr>";
        echo "<tr>";
            echo "<td><b>$successful</b></td>";
            echo "<td><b>$failed</b></td>";
            echo "<td><b>$percentage %</b></td>";
        echo "</tr>";
    echo "</table>";
echo "</div>";
    echo "<div class='author'>";
    echo "<h2>Jakub Sekula</h2>";
    echo "<br>";
    echo "<h2 id='login'>xsekul01</h2>";
echo "</div>";
}

/*
** Nasledujici funkce slouzi k zmene pripon souboru
*/

function outToSrc( $File ){
    return ( $File = preg_replace( '/\.out/', '.src', $File ) );
}

function rcTosrc( $File ){
    return ( $File = preg_replace( '/\.rc/', '.src', $File ) );
}

function srcToin( $File ){
    return ( $File = preg_replace( '/\.src/', '.in', $File ) );
}

function inToOut( $File ){
    return ( $File = preg_replace( '/\.in/', '.out', $File ) );
}

function outToRc( $File ){
    return ( $File = preg_replace( '/\.out/', '.rc', $File ) );
}

function srcToOut( $File ){
    return ( $File = preg_replace( '/\.src/', '.out', $File ) );
}

/*
** Funkce addFile otevira vstupni soubry, pokud nejsou vytvari je
*/

function addFiles( $origFile ){
    $origFile = srcToin( $origFile );
    if ( !file_exists( "$origFile" ) ){
        $in = fopen( "$origFile", "w+" );
        fclose( $in );
    }
    $origFile = inToOut( $origFile );
    if ( !file_exists( "$origFile" ) ){
        $out = fopen( "$origFile", "w+" );
        fclose( $out );
    }
    $origFile = outToRc( $origFile );
    if ( !file_exists( "$origFile" ) ){
        $rc = fopen( "$origFile", "w+" );
        fclose( $rc );
    }
    return;
}

/*
** writeSucces zapisuje html kod pro uspesny kod
*/

function writeSucces( $parseOut, $cmpFile, $expectedRv, $parseRv ){
    global $successful;
    $successful++;
    $cmpFile = rcToSrc( $cmpFile );
    $cmpFile = getcwd()."/".$cmpFile;
    echo "<tr>";
    echo    "<td>$cmpFile</td>";
    echo    "<td id='navrat'>$parseRv</td>";
    echo    "<td id='navrat'>$expectedRv</td>";
    echo    "<td id='prosel'>Prosel</td>";
    echo    "</tr>";
}

/*
** writeError je opak funkce writeSucces
*/

function writeError( $parseFile, $cmpFile, $expectedRv, $parseRv ){
    global $failed;
    $failed++;
    $cmpFile = rcToSrc( $cmpFile );

    $cmpFile = getcwd()."/".$cmpFile;

    echo "<tr>";
    echo    "<td>$cmpFile</td>";
    echo    "<td id='navrat'>$parseRv</td>";
    echo    "<td id='navrat'>$expectedRv</td>";
    echo    "<td id='neprosel'>Neprosel</td>";
    echo    "</tr>";
}

/*
** checkJexamxml kontroluje vystupy pomoci nastroje jexam
*/

function checkJexamxml( $parseFile, $cmpFile, $expectedRv, $parseRv ){
    global $jexamxml;
    global $successful;
    global $failed;
    global $parsescript;
    $cmpFile = $cmpFile;
    $command = "java -jar $jexamxml $parseFile $cmpFile";
    $cmpFile = outToSrc( $cmpFile );
    exec( $command, $out, $rv );

    echo "<tr>";
    echo    "<td>$cmpFile</td>";
    echo    "<td id='navrat'>$parseRv</td>";
    echo    "<td id='navrat'>$expectedRv</td>";
    if ( $rv == 0 ){
        $successful++;
        echo    "<td id='prosel'>Prosel</td>";
    } else {
        $failed++;
        echo    "<td id='neprosel'>Neprosel</td>";
    }
    echo    "</tr>";
}

/*
** provede pruchod interpretem
*/

function  testInterpret( $input, $output, $in ){
    global $intscript;
    $command = "python3 $intscript"." --input=$in"." < $input > $output";
    //print( "\n\n$command\n\n" );
    exec( $command, $out, $rv );
    $rcFile = outToRc( $output );
    $rcFileH = fopen( "$rcFile", "w+" );
    fwrite( $rcFileH, $rv );
    fclose( $rcFileH );
    return $rv;
}

/*
** funkce testuje ocekavan hodnotu a hodnotu testu a potom vypisuje bud uspesny test nebo test, ktery selhal
*/

function testRc( $testPath, $file, $rv ){
    $input = srcToOut( $testPath );
    $testPath = outToRc( $input );
    $expectedRvFile = fopen( $testPath, "r+" );
    $expectedRv = fgets( $expectedRvFile );
    $testPath = rcTosrc( $testPath );
    $testPath = srcToOut( $testPath );
    $parseRv = $rv;
    if( $expectedRv == 0 && $rv == 0 ){
        $srcFile = rcTosrc( $file );
        $outFile = srcToOut( $srcFile );
        $command = "diff $testPath $outFile";
        exec( $command, $out, $rv );
        $testPath = outToSrc( $testPath );
        if( $rv == 0 ){
            writeSucces( '', $testPath, $expectedRv, $parseRv );
        } else {
            writeError( '', $testPath, $expectedRv, $parseRv );
        }
    } elseif( $expectedRv == $rv ){
        writeSucces( '', $testPath, $expectedRv, $parseRv );
    } else {
        writeError( '', $testPath, $expectedRv, $parseRv );
    } 
}

/*
** getRv provadi zapis return hodnot do slozek pripadne do in .rc souboru doplni 0 
*/

function getRv( $origFile, $parseRv, $parseOut ){
    global $parseonly;
    $origFile = preg_replace( '/\.src/', '.rc', $origFile );
    $rvFile = fopen( $origFile, "r+" );
    $expectedRv = fgets( $rvFile );
    if ( $expectedRv == "" ){
        fwrite( $rvFile, 0 );
        $expectedRv = 0;
    }
    fclose( $rvFile );

    if ( $parseonly == 1 ){
        if ( ( $expectedRv == 0 ) && ( $parseRv == 0 ) ){
            $origFile = preg_replace( '/\.rc/', '.out', $origFile );
            checkJexamxml( $parseOut, $origFile, $expectedRv, $parseRv );
        } elseif( $expectedRv == $parseRv ){
            writeSucces( $parseOut, $origFile, $expectedRv, $parseRv );
        } else {
            writeError( $parseOut, $origFile, $expectedRv, $parseRv );
        }
        return;
    }
    $intOut = $parseOut;
    $intOut = preg_replace( '/_parser.out/', '_int.out', $intOut );
    $inFile = rcTosrc( $origFile );
    $inFile = srcToin( $inFile );
    $rv = testInterpret( $parseOut, $intOut, $inFile );
    $origFile = rcTosrc( $origFile );
    testRc( $origFile, $intOut, $rv );
    
    
}

/*
** existsRcFile doplni do input rc souboru 0 pokud je prazdny
*/

function existsRcFile( $origFile ){
    $origFile = preg_replace( '/\.src/', '.rc', $origFile );
    $rvFile = fopen( $origFile, "a+" );
    $expectedRv = fgets( $rvFile );
    if ( $expectedRv == "" ){
        fwrite( $rvFile, 0 );
        $expectedRv = 0;
    }
    fclose( $rvFile );
}

/*
** funkce provede command
*/

function executeCommand( $command, $outFile ){
    exec( $command, $out, $rv );
    $file = preg_replace( '/\.out/', '.rc', $outFile );
    $rcFile = fopen( "$file", "w" );
    fwrite( $rcFile, $rv );
    fclose( $rcFile );
    return $rv;
}

/*
** testThis testuje konkretni soubor
*/

function testThis( $testPath, $file ){
    global $testOutDir;
    global $parsescript;
    global $intscript;
    global $parseonly;
    global $intonly;
    global $successful;
    global $failed;
    if ( preg_match( '/\.src/', $file ) ){
        $testPath = getcwd()."/".$testPath;
        $origFile = $testPath;
        existsRcFile( $origFile );
        addFiles( $origFile );
        $file = preg_replace( '/\.src$/', '', $file );
        if( $parseonly == 1 || ( $parseonly == 0 && $intonly == 0 ) ){
            $file = $testOutDir."/".$file."_parser.out";
            $command = "php "."$parsescript <"."$testPath >"."$file";
            $parseRv = executeCommand( $command, $file );
            getRv( $origFile, $parseRv, $file );
        } else {
            $file = $testOutDir."/".$file."_int.out";
            $inFile = rcTosrc( $testPath );
            $inFile = srcToin( $inFile );
            $rv = testInterpret( $testPath, $file, $inFile );
            testRc( $testPath, $file, $rv );
        }
        return;
    }
}

/*
** goOver prochazi adresare
*/

function goOver( $directory, $recursive ){
    $adresar = array_diff( scandir( "$directory"), array( '..', '.' ));

    foreach( $adresar as $file ){
        if ( !is_dir( "$directory"."/".$file ) ){
            $testPath = $directory."/".$file;
            testThis( $testPath, $file );
        }
        if ( $recursive == 1 ){
            if( is_dir( "$directory"."/".$file ) ){
                $test = $directory."/".$file;
                goOver( "$directory"."/".$file, $recursive  );
            }
        }
    }
}

writeParams();
goOver( $directory, $recursive );
writeStats();

/*
** odstranuje temp soubor
*/

$command = "rm -rf TmpTestFolder";
exec( $command, $out, $rv );

?>
    </body>
</html>
