<!--         
        Jakub Sekula

     IPP - VUT-FIT 2020 test.php
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

declare( ticks = 1 );

pcntl_signal( SIGINT, 'signalHandler' );

function signalHandler($signal) {
    global $pidFile;
    $command = "rm -rf TmpTestFolder";
    exec( $command, $out, $rv );
    exit( 0 );
}

$successful = 0;
$failed = 0;

include 'test_args.php';

$nowRoute = getcwd();

mkdir( $nowRoute."/"."TmpTestFolder" );

$testOutDir = $nowRoute."/"."TmpTestFolder";

# -----------------------------------------------------------
# Funkce writeParams
#
# Parametr none
#
# Funkce projde vsechny parametry zadane skriptu a vypise prehlednou html tabulku, kde je viditelne, jake parametry byly skriptu zadane 
#
# Return none
# -----------------------------------------------------------
function writeParams(){
    global $parsescript;
    global $directory;
    global $intscript;
    global $jexamxml;
    global $help_argument;
    global $parseonly;
    global $intonly;
    global $recursive;
    global $testlist;

    $zmenaDirectory = 0;
    $zmenaParsesscript = 0;
    $zmenaIntscript = 0;
    $zmenaJexamxml = 0;
    $zmenaHelp_argument = 0;
    $zmenaParseonly = 0;
    $zmenaIntonly = 0;
    $zmenaRecursive = 0;
    $zmenaTestfile = 0;

    if( $parsescript != "parse.php" ){ $zmenaParsesscript = 1; };
    if( $directory != "." ){ $zmenaDirectory = 1; };
    if( $intscript != "interpret.py" ){ $zmenaIntscript = 1; };
    if( $jexamxml != "/pub/courses/ipp/jexamxml/jexamxml.jar" ){ $zmenaJexamxml = 1; };
    if( $help_argument != 0 ){ $zmenaHelp_argument = 1; };
    if( $parseonly != 0 ){ $zmenaParseonly = 1; };
    if( $intonly != 0 ){ $zmenaIntonly = 1; };
    if( $recursive != 0 ){ $zmenaRecursive = 1; };
    if( $testlist != '' ){ $zmenaTestfile = 1; };

    $args = array( '-1' => "--help", '0' => "--directory=path", '1' => "--recursive", '2' => "--parse-script=path", '3' => "--int-script=file", '4' => "--parse-only", '5' => "--int-only", '6' => "--jexamxml=file", '7' => "--testlist" );
    $zadany = array( '-1' => "$zmenaHelp_argument", '0' => "$zmenaDirectory", '1' => "$zmenaRecursive", '2' => "$zmenaParsesscript", '3' => "$zmenaIntscript", '4' => "$zmenaParseonly", '5' => "$zmenaIntonly", '6' => "$zmenaJexamxml", '7' => "$zmenaTestfile" );

    $i = 0;

    echo "<div class='params'>";
        echo "<table class='returns params'>";
            echo "<tr>";
                echo "<th>Parametr</th>";
                echo "<th>Zadan</th>";
            echo "</tr>";
            while( $i < 9 ){
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

# -----------------------------------------------------------
# Funkce writeStats
#
# Parametr none
#
# Funkce vypise na konci behu skriptu statistiky prubehu testu
#
# Return none
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# Funkce outToSrc, rcTosrc, srcToin, inToOut, outToRc, srcToOut
#
# Parametr cesta k souboru
#
# Funkce zmeni koncovku souboru
#
# Return cesta k souboru se zmenenou koncovkou
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# Funkce addFiles
#
# Parametr cesta k souboru
#
# Pri zadani testu musi byt ve slozce testu soubor .src a ostatni pokud nejsou, se musi dogenerovat 
#
# Return cesta k souboru se zmenenou koncovkou
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# Funkce writeSucces
#
# Parametr parseOut soubor s vystupem parseru
# Parametr cmpFile soubor s ocekavanym vystupem 
# Parametr expectedRv soubor s ocekavanym rc kodem
# Parametr parseRv soubor s rc parseru
#
# Vypisuje html kod pro uspesny test 
#
# Return none
# -----------------------------------------------------------
function writeSucces( $parseOut, $cmpFile, $expectedRv, $parseRv ){
    global $successful;
    $successful++;
    $cmpFile = rcToSrc( $cmpFile );
    $cmpFile = $cmpFile;
    $cmpFile = outToSrc( $cmpFile );
    echo "<tr>";
    echo    "<td>$cmpFile</td>";
    echo    "<td id='navrat'>$parseRv</td>";
    echo    "<td id='navrat'>$expectedRv</td>";
    echo    "<td id='prosel'>Prosel</td>";
    echo    "</tr>";
}

# -----------------------------------------------------------
# Funkce writeError
#
# Parametr parseFile soubor s vystupem parseru
# Parametr cmpFile soubor s ocekavanym vystupem 
# Parametr expectedRv soubor s ocekavanym rc kodem
# Parametr parseRv soubor s rc parseru
#
# Vypisuje html kod pro neuspesny test 
#
# Return none
# -----------------------------------------------------------
function writeError( $parseFile, $cmpFile, $expectedRv, $parseRv ){
    global $failed;
    $failed++;
    $cmpFile = rcToSrc( $cmpFile );

    $cmpFile = $cmpFile;

    $cmpFile = outToSrc( $cmpFile );

    echo "<tr>";
    echo    "<td>$cmpFile</td>";
    echo    "<td id='navrat'>$parseRv</td>";
    echo    "<td id='navrat'>$expectedRv</td>";
    echo    "<td id='neprosel'>Neprosel</td>";
    echo    "</tr>";
}

# -----------------------------------------------------------
# Funkce checkJexamxml
#
# Parametr parseFile soubor s vystupem parseru
# Parametr cmpFile soubor s ocekavanym vystupem 
# Parametr expectedRv soubor s ocekavanym rc kodem
# Parametr parseRv soubor s rc parseru
#
# Funkce provede porovnani vystupu v xml podobe s ocekavanym xml pomoci nastroje jexaxml a vypise odpovidaji html vystup
#
# Return none
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# Funkce testInterpret
#
# Parametr source src soubor interpretu
# Parametr output soubor s vystupem parseru 
# Parametr in soubor se vstupem interpretu
#
# Funkce spusti skript interpretu a vysledny rc zapise do souboru
#
# Return navratovy kod 
# -----------------------------------------------------------
function  testInterpret( $source, $output, $in ){
    global $intscript;
    $command = "python3 $intscript"." --input=$in"." < $source > $output";
    exec( $command, $out, $rv );
    $rcFile = outToRc( $output );
    $rcFileH = fopen( "$rcFile", "w+" );
    fwrite( $rcFileH, $rv );
    fclose( $rcFileH );
    return $rv;
}

# -----------------------------------------------------------
# Funkce testRc
#
# Parametr testPath cesta k prave provadenemu testu
# Parametr file soubor s vystupem 
# Parametr rv return code interpretu  
#
# Funkce otestuje vysledek vyslednou navratovou hodnotu, pokud jsou obe 0 tak se pomoci nastroje diff. Funkce se pouziva pro vystup interpretu.
#
# Return none 
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# Funkce getRv
#
# Parametr origFile cesta k prave provadenemu testu
# Parametr parseRv soubor s return kodem parseru
# Parametr parseOut soubor s vysledkem parseru v xml podobe  
#
# Funkce spusti skript interpretu a vysledny rc zapise do souboru
#
# Return navratovy kod 
# -----------------------------------------------------------
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
    if( $parseRv != 0 ){
        $srcFile = inToOut( $inFile );
        $srcFile = outToRc( $srcFile );
        $expectedFile = fopen( $srcFile, "r" );
        $expectedRv = fgets( $expectedFile );
        $srcFIle = rcToSrc( $srcFile );
        if( $expectedRv == $parseRv ){
            writeSucces( '', $origFile, $expectedRv, $parseRv );
        } else {
            writeError( '', $origFile, $expectedRv, $parseRv );
        }
        return;
    }
    $rv = testInterpret( $parseOut, $intOut, $inFile );
    $origFile = rcTosrc( $origFile );
    testRc( $origFile, $intOut, $rv );
    
    
}

# -----------------------------------------------------------
# Funkce existsRcFile
#
# Parametr origFile cesta k prave provadenemu testu
#
# Funkce slouzi pro zjisteni, jestli existuje .rc soubor, jestlize neexistuje tak ho vytvori a zapise do nej 0. 0 taky zapise, jestli je .rc soubor prazdny
#
# Return none 
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# Funkce executeCommand
#
# Parametr command je string, ktery obsahuje prikaz, ktery chceme provest
# Parametr outFile cesta k souboru, kam ulozim vystup funkce exec()
#
# Funkce slouzi pro zjisteni, jestli existuje .rc soubor, jestlize neexistuje tak ho vytvori a zapise do nej 0. 0 taky zapise, jestli je .rc soubor prazdny
#
# Return none 
# -----------------------------------------------------------
function executeCommand( $command, $outFile ){
    exec( $command, $out, $rv );
    $file = preg_replace( '/\.out/', '.rc', $outFile );
    $rcFile = fopen( "$file", "w" );
    fwrite( $rcFile, $rv );
    fclose( $rcFile );
    return $rv;
}

# -----------------------------------------------------------
# Funkce testThis
#
# Parametr testPath cesta k souboru s testy
# Parametr file cesta k souboru se soucasnym testem
#
# Funkce zpracuje cestu k souboru s testy, pak podle zadanych argumentu bud testuje parser nebo interpret
#
# Return none 
# -----------------------------------------------------------
function testThis( $testPath, $file ){
    global $testOutDir;
    global $parsescript;
    global $intscript;
    global $parseonly;
    global $intonly;
    global $successful;
    global $failed;
    global $match_regex;

    if( $match_regex != '' ){
        $arr = explode( ".", $file, 2 );
        $filef = $arr[ 0 ];
        $match_regex = $match_regex;
        if( @preg_match( $match_regex, NULL ) === false ){
            exit( 10 ); 
        }
        if( !preg_match( $match_regex, $filef ) ){
            return;
        }
    }

    if ( preg_match( '/\.src/', $file ) ){
        $testPath = realpath( $testPath );
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

# -----------------------------------------------------------
# Funkce goOver
#
# Parametr directory cesta k testum
# Parametr recursive zadany parametr --recursive
#
# Funkce kontroluje jestli je v directory cesta k souboru nebo samotny .src soubor a podle toho bude vola funkci pro soubor nebo pro adresar.
# Funkce take pri zadanem parametru --recursive prochazi adresar a jestli najde slozku, tak se zavola znova na sebe s toutu slozkou
#
# Return none 
# -----------------------------------------------------------
function goOver( $directory, $recursive ){

    if( is_dir( $directory ) ){
        $adresar = array_diff( scandir( "$directory"), array( '..', '.' ));
    } elseif( is_file( $directory ) ) {
        if( !( preg_match( '/.src$/', $directory ) ) ){
            exit( 11 );
        }
        $file = $dir = substr( strrchr( $directory, "/" ), 1 );
        testThis( $directory, $file );
        return;
    } else {
        exit( 10 ); 
    }

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

if( $testlist != '' ){
    $tests = fopen( $testlist, "r" );
    while( ( $line = fgets( $tests ) ) != false ){
        goOver( trim( $line ), $recursive );
    }
    fclose( $tests );
} else {
    goOver( $directory, $recursive );
}
writeStats();

/*
** odstranuje temp soubor
*/

$command = "rm -rf TmpTestFolder";
exec( $command, $out, $rv );

?>
    </body>
</html>