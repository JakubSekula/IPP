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

</style>
</head>
<body>
<div class="proc">
 <h1>Vysledkova tabulka IPP projektu</h1>
</div>    
    <div class="tabulka">
        <table class='returns'>
          <tr>
            <th>Test</th>
            <th id='test'>Navratovy kod</th>
            <th id='test'>Ocekavany kod</th>
            <th>Vysledek</th>
          </tr>
<?php

$successful = 0;
$failed = 0;

include 'test_args.php';

function writeStats(){
    global $successful;
    global $failed;

    $percentage = ( $successful + $failed ) / 100;
    $percentage = $successful / $percentage;

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

function outToSrc( $File ){
    return ( $File = preg_replace( '/\.out/', '.src', $File ) );
}

function rcTosrc( $File ){
    return ( $File = preg_replace( '/\.rc/', '.src', $File ) );
}

function writeError( $parseFile, $cmpFile, $expectedRv, $parseRv ){
    global $failed;
    $failed++;
    $cmpFile = rcToSrc( $cmpFile );
    echo "<tr>";
    echo    "<td>$cmpFile</td>";
    echo    "<td id='navrat'>$parseRv</td>";
    echo    "<td id='navrat'>$expectedRv</td>";
    echo    "<td id='neprosel'>Neprosel</td>";
    echo    "</tr>";
}

function checkJexamxml( $parseFile, $cmpFile, $expectedRv, $parseRv ){
    global $jexamxml;
    global $successful;
    global $failed;
    global $parsescript;
    $cmpFile = getcwd()."/".$cmpFile;
    $parseFile = getcwd()."/".$parseFile;
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
        echo    "<td id='neprosel'>Nerosel</td>";
    }
    echo    "</tr>";
}

function getRv( $origFile, $parseRv, $parseOut ){
    $origFile = preg_replace( '/\.src/', '.rc', $origFile );
    $rvFile = fopen( $origFile, "r+" );
    $expectedRv = fgets( $rvFile );
    if ( $expectedRv == "" ){
        fwrite( $rvFile, 0 );
        $expectedRv = 0;
    }
    fclose( $rvFile );
    if ( $expectedRv == $parseRv ){
        $origFile = preg_replace( '/\.rc/', '.out', $origFile );
        checkJexamxml( $parseOut, $origFile, $expectedRv, $parseRv );
    } else {
        writeError( $parseOut, $origFile, $expectedRv, $parseRv );
    }

}

function executeCommand( $command, $outFile ){
    exec( $command, $out, $rv );
    $file = preg_replace( '/\.out/', '.rc', $outFile );
    $rcFile = fopen( "$file", "w" );
    fwrite( $rcFile, $rv );
    fclose( $rcFile );
    return $rv;
}

function testThis( $testPath, $file ){
    global $parsescript;
    if ( preg_match( '/\.src/', $file ) ){
        $origFile = $testPath;
        $file = preg_replace( '/\.src$/', '', $file );
        $file = $file."_parser.out";
        $command = "php7.4 "."$parsescript <"."$testPath >"."$file";
        //echo "\n\n\n||| $command |||\n\n\n";
        $parseRv = executeCommand( $command, $file );
        getRv( $origFile, $parseRv, $file );
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
            if( is_dir( "$directory"."/".$file ) ){
                $test = $directory."/".$file;
                goOver( "$directory"."/".$file, $recursive  );
            }
        }
    }
}
goOver( $directory, $recursive );
writeStats();

?>
    </body>
</html>