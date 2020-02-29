<?php


// globalni promenna pro xml writer
global $xml;

$type;
$order;
$test;
$args = 0;
$comments = 0;
$jumps = 0;
$order = 0;

// promenna pro rozsireni a kontrolu zda li neexistuje vic navesti

$labeldiff = array();

$xml = new XMLWriter();

function checkDuplicitLabels( $parsed, $index ){
    global $labeldiff;
    global $labels;

    if ( !in_array( $parsed[ $index ], $labeldiff ) ){
        array_push( $labeldiff, $parsed[ $index ] );
        $labels++;
    }
}

function incrementOrder(){
    global $order;
    $order++;
}

function incrementComment(){
    global $comments;
    $comments++;
}

function writeStatp( $arrayargs, $path ){
    global $comments;
    global $jumps;
    global $labels;
    global $order;

    $file = fopen( $path, "w" );

    foreach( $arrayargs as $arg ){
        if ( $arg == 'loc' ){
            fwrite( $file, "$order\n" );
        } elseif ( $arg == 'comments' ){
            fwrite( $file, "$comments\n" );
        } elseif( $arg == 'jumps' ){
            fwrite( $file, "$jumps\n" );
        } elseif( $arg == 'label' ){
            fwrite( $file, "$labels\n" );
        }
    }
    fclose( $file );
}

// kontrola spravnosti argumentu

function checkArgs( $help_argument, $arrayargs, $filePath ){
    global $statp;
    $statp = 0;

    // jestlize je --help nesmi byt zadny jiny
    if ( ( count( $help_argument ) == 1 ) && ( count( $arrayargs ) != 0 ) ){
        exit( 10 );
    } elseif( ( count( $help_argument ) == 1 ) && ( count( $arrayargs ) == 0 ) ){
        echo "Skript typu filtr (parse.php v jazyce PHP 7.4) nacte ze standardniho vstupu zdrojovy kod v IPP-code20, zkontroluje \nlexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu dle specifikace v sekci.\n";
        exit;
    } elseif( ( count( $help_argument ) == 0 ) && ( count( $arrayargs ) != 0 ) ){
        $stats = false;
        $different = false;
        // stats musi byt zadan i s cestou
        foreach( $arrayargs as $arg ){
            if ( preg_match( '/^(\-){1,2}stats=/', $arg ) ){
                $stats = true;
            } else {
                $different = true;
            }
        }
        if ( $stats == false ){
            exit ( 10 );
        }
    } elseif( ( count( $help_argument ) == 0 ) && ( count( $arrayargs ) == 0 ) ){ 
        
    } else {
        exit( 10 );
    }
    
}

/*
*
* Nasleduji kontroly formatu
*
*/

function checkVar( $parsed ){
    if ( !preg_match( '/(*UTF8)^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|(\p{L}))((\p{N})|(\p{L})|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$/', $parsed ) ){
        exit( 23 );
    }
}

function checkEnd( $parsed ){
     if ( preg_match( '/(*UTF8)^#((\S)*|(\s)*)*$/', $parsed ) ){
        $parsed = "";
    } 
    if ( $parsed != "" ){
        exit ( 23 );
    }
}

function definedVar( $parsed, $index ){
    if( isset( $parsed[ $index ] ) ){
        if ( preg_match( '/^(\s)*$/', $parsed[ $index ] ) ){
            exit( 23 );
        }
        checkVar( $parsed[ $index ] );
    } else {
        exit( 23 );
    }
}

function definedSymb( $parsed, $index ){
    if( isset( $parsed[ $index ] ) ){
        if ( preg_match( '/^(\s)*$/', $parsed[ $index ] ) ){
            exit( 23 );
        }
        checkSymb( $parsed[ $index ] );
    } else {
        exit( 23 );
    }
}

function definedEnd( $parsed, $index ){
    incrementOrder();
    if ( isset( $parsed[ $index ] ) ){
        checkEnd( $parsed[ $index ] );
    }

}

function definedLabel( $parsed, $index ){
    if( isset( $parsed[ $index ] ) ){
        if ( preg_match( '/^(\s)*$/', $parsed[ $index ] ) ){
            exit( 23 );
        }
        checkLabel( $parsed[ $index ] );
    } else {
        exit( 23 );
    }
}

function checkSymb( $parsed ){
    // prvni se kontroluje spravnost formalni v elseif jestli zde nejsou nepovolone znaky
    if ( !preg_match( '/(*UTF8)^(int@((\-)|(\+)){0,1}(\p{N})+)$|(bool@((true)|(false)))$|^((GF)|(TF)|(LF))@(\S)*$|^(nil)@nil$|^string@(\S)*$/', $parsed ) ){
        echo $parsed."\n";
        exit( 23 );
    } elseif( !preg_match( '/(*UTF8)^([^#\s\\\\]|\\\\[0-9]{3})*$/i', $parsed ) ){
        echo $parsed."\n";
        exit( 23 );
    }
}

function checkLabel( $parsed ){
    if ( !preg_match( '/(*UTF8)^((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|(\p{L}))((\p{N})|(\p{L})|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$/', $parsed ) ){
        echo $parsed."\n";
        exit( 23 );
    }
}

function checkType( $parsed ){
    if ( !preg_match( '/^((int)|(bool)|(string))$/', $parsed ) ){
        echo $parsed."\n";

        exit( 23 );
    }
}

function parseArg( $parsed ){
    
    global $comments;
    global $type;
    // parametry GF musi byt ve vyslednem xml vzdy velkym    
    if ( preg_match( '/(*UTF8)^((GF)|(TF)|(LF))@(\S)*$/i', $parsed ) ){
        $parsed = preg_replace( '/(GF)/i', "GF", $parsed );
        $parsed = preg_replace( '/(LF)/i', "LF", $parsed );
        $parsed = preg_replace( '/(TF)/i', "TF", $parsed );
        return array( "var", $parsed );
    } elseif( preg_match( '/(*UTF8)^((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|(\p{L}))((\p{N})|(\p{L})|(\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?))*$/',$parsed ) && $type == 0 ){
        // pro pripad ze se jedna o label
        return array( "label", $parsed );
    } elseif( preg_match( '/^(\w)+$/',$parsed ) && $type == 1 ){
        // pro type
        $type = 0;
        return array( "type", $parsed ); 
    } else {
        // jestlize se jedna o int, string, bool
        $pos = strpos( $parsed, "@" ); 
        $firstpiece = substr( $parsed, 0, $pos );
        $secondpiece = substr( $parsed, $pos + 1 );

        if( preg_match( '/bool/i', $firstpiece  ) ){
            $firstpiece = strtolower( $firstpiece );
            if ( !preg_match( '/^(true)|(false)$/', $secondpiece ) ){
                exit( 23 );
            }
            $secondpiece = strtolower( $secondpiece );
        }

        if ( preg_match( '/^#/', $secondpiece ) ){
            $comments++;
            $secondpiece = "";
        }
        return array( $firstpiece, $secondpiece );
    }
}

/*
*
* Vystup v xml formatu
*
*/

function caseXml( $iter, $opcode, $order, $xml, $parsed ){

    $xml->startElement('instruction');
    $xml->writeAttribute('order',"$order");
    $xml->writeAttribute('opcode',$opcode);

    $i = 0;

    while ( $i < $iter ){
        $i++;
        
        $arrayParse = parseArg( $parsed[ $i ] );
        $xml->startElement( 'arg'.$i );
        $xml->writeAttribute( 'type',$arrayParse[ 0 ] );
        $xml->text( $arrayParse[ 1 ] );
        $xml->endElement();
    }
    $xml->endElement();
}


/*
*
* Case pro jednotlive instrukce
*
*/

function checkSyntax( $parsed, $xml ){
    
    global $order;
    global $loc; 
    global $labels;
    global $jumps;
    global $type;

    $type = 0;
    
    // instrukce muze byt zapsana na vstupu i malym, ale porovnavam s velkym
    $parsed[ 0 ] = strtoupper( $parsed[ 0 ] );

    switch( $parsed[ 0 ] ){
        case "MOVE":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedEnd( $parsed, 3 );
            caseXml( 2, "MOVE", $order, $xml, $parsed );
            break;
        case "DEFVAR":
            definedVar( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "DEFVAR", $order, $xml, $parsed );
            break;
        case "LABEL":
            definedLabel( $parsed, 1 );
            checkDuplicitLabels( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "LABEL", $order, $xml, $parsed );
            break;
        case "CREATEFRAME":
            definedEnd( $parsed, 1 );
            caseXml( 0, "CREATEFRAME", $order, $xml, $parsed );
            break;
        case "PUSHFRAME":
            definedEnd( $parsed, 1 );
            caseXml( 0, "PUSHFRAME", $order, $xml, $parsed );
            break;
        case "POPFRAME":
            definedEnd( $parsed, 1 );
            caseXml( 0, "POPFRAME", $order, $xml, $parsed );
            break;
        case "CALL":
            $jumps++;
            definedLabel( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "CALL", $order, $xml, $parsed );
            break;
        case "READ":
            definedVar( $parsed, 1 );
            checkType( $parsed[ 2 ] );
            $type = 1;
            definedEnd( $parsed, 3 );            
            caseXml( 2, "READ", $order, $xml, $parsed );
            break;
        case "RETURN":
            $jumps++;
            definedEnd( $parsed, 1 );
            caseXml( 0, "RETURN", $order, $xml, $parsed );
            break;
        case "PUSHS":
            definedSymb( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "PUSHS", $order, $xml, $parsed );
            break;
        case "POPS":
            definedVar( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "POPS", $order, $xml, $parsed );
            break;
        case "ADD":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "ADD", $order, $xml, $parsed );
            break;
        case "SUB":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "SUB", $order, $xml, $parsed );
            break;
        case "MUL":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "MUL", $order, $xml, $parsed );
            break;
        case "IDIV":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "IDIV", $order, $xml, $parsed );
            break;
        case "LT":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "LT", $order, $xml, $parsed );
            break;
        case "GT":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "GT", $order, $xml, $parsed );
            break;
        case "EQ":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "EQ", $order, $xml, $parsed );
            break;
        case "AND":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "AND", $order, $xml, $parsed );
            break;
        case "OR":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "OR", $order, $xml, $parsed );
            break;
        case "NOT":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedEnd( $parsed, 3 );
            caseXml( 2, "NOT", $order, $xml, $parsed );
            break;
        case "INT2CHAR":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedEnd( $parsed, 3 );
            caseXml( 2, "INT2CHAR", $order, $xml, $parsed );
            break;
        case "STRI2INT":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "STRI2INT", $order, $xml, $parsed );
            break;
        case "WRITE":
            definedSymb( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "WRITE", $order, $xml, $parsed );
            break;
        case "CONCAT":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "CONCAT", $order, $xml, $parsed );
            break;
        case "STRLEN":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedEnd( $parsed, 3 );
            caseXml( 2, "STRLEN", $order, $xml, $parsed );
            break;
        case "GETCHAR":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "GETCHAR", $order, $xml, $parsed );
            break;
        case "SETCHAR":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "SETCHAR", $order, $xml, $parsed );
            break;
        case "TYPE":
            definedVar( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedEnd( $parsed, 3 );
            caseXml( 2, "TYPE", $order, $xml, $parsed );
            break;
        case "JUMP":
            $jumps++;
            definedLabel( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "JUMP", $order, $xml, $parsed );
            break;
        case "JUMPIFEQ":
            $jumps++;
            definedLabel( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "JUMPIFEQ", $order, $xml, $parsed );
            break;
        case "JUMPIFNEQ":
            $jumps++;
            definedLabel( $parsed, 1 );
            definedSymb( $parsed, 2 );
            definedSymb( $parsed, 3 );
            definedEnd( $parsed, 4 );
            caseXml( 3, "JUMPIFNEQ", $order, $xml, $parsed );
            break;
        case "EXIT":
            definedSymb( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "EXIT", $order, $xml, $parsed );    
            break;
        case "DPRINT":
            definedSymb( $parsed, 1 );
            definedEnd( $parsed, 2 );
            caseXml( 1, "DPRINT", $order, $xml, $parsed );
            break;
        case "BREAK":
            definedEnd( $parsed, 1 );
            caseXml( 0, "BREAK", $order, $xml, $parsed );
            break;
        
    }
}

// navraci 1 a kontroluje radek ze vstupu
function returnLine( $line ){
    if ( ( $line ) || ( $line ) != 'EOF' ){
        return $line;
    } else {
        return NULL;
    }
}

// ziska radek vstupu
function getLine( $file ){
    $line = fgets( STDIN );
    // dokud neni radek jen odradkovani
    while ( $line == "\n" ){
        $line = fgets( STDIN );
    }
    return returnLine( $line );
}

// kontrola pro chybu 22, jestli je keyword spravne
function isKeyWord( $token ){

    $token = strtoupper( $token );

    $keyWords = array(  "MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL",
                        "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT",
                        "EQ", "AND", "OR", "INT2CHAR", "STRI2INT", "READ", "WRITE", "STRLEN",
                        "GETCHAR", "SETCHAR", "NOT", "LABEL", "JUMPIFEQ", "JUMPIFNEQ", "CONCAT", "JUMP",
                        "TYPE",  "EXIT", "DPRINT", "BREAK","", " " );
    if ( !( in_array( $token,$keyWords ) ) ){
        exit ( 22 );
    }
    return;
}

// rozcleneni radku na tokeny
function parseLine( $line, $xml ){

    global $comments;

    // nahrazeni 2+ mezer za 1

    $line = preg_replace( '/\s+/', " ",$line );
    $parsed = explode( " ", $line );

    if ( !( preg_match( '/\#/', $parsed[0] ) ) ){
        isKeyWord( $parsed[0] );
        checkSyntax( $parsed, $xml );
    }
    foreach( $parsed as $token ){
        if ( preg_match( '/^#/', $token ) ){
            $comments++;
            return;
        }
    }
}

// pomocne promenne pro argumenty

$help_argument = array();
$arrayargs = array();
$filePath = "";

// kopntrola vstupnich argumentu

if ( $argc > 1 ){
    foreach( $argv as $current ){
        // preskakuju spousteny skript
        if ( $current == "parse.php" ){
            continue;
        }
        if ( preg_match( '/^(\-){1,2}help$/', $current ) ){
            array_push( $help_argument, 'help' );
        } elseif ( preg_match( '/^(\-){1,2}stats=((..\/)*(\w+)(\/){0,1})+$/', $current ) ) {
            // rozdeleni podle =
            $pos = strpos( $current, "=" );
            $path = substr( $current, $pos + 1 );
            array_push( $arrayargs, "$current" );
            $filePath = $path;
            $args = 1;
        } elseif( preg_match( '/^(\-){1,2}loc$/', $current ) ){
            array_push( $arrayargs, 'loc' );
        } elseif( preg_match( '/^(-){1,2}comments$/', $current ) ){
            array_push( $arrayargs, 'comments' );
        } elseif( preg_match( '/^(\-){1,2}labels$/', $current ) ){
            array_push( $arrayargs, 'label' );
        } elseif( preg_match( '/^(\-){1,2}jumps$/', $current ) ){
            array_push( $arrayargs, 'jumps' );
        } else {
            exit( 10 );
        }
    }
}

checkArgs( $help_argument, $arrayargs, $filePath );

//  jestlize je vstup prazdny
if ( !( $FLine = fgets( STDIN ) ) ){
echo "Dick\n";
exit( 21 );
}
// nahradim bile znaky na zacatku radku za ''
$FLine = preg_replace( '/^(\s)*/', '', $FLine );

// dokud je na radku \n nebo komentar nebo je radek prazdny jen s bilymi znaky
while ( $FLine == "\n" || preg_match( '/^#/',$FLine ) || preg_match( '/^(\s)*$/', $FLine ) ){
    if ( preg_match( '/^#/',$FLine ) ){
        // inkrementace pro rozsireni
        incrementComment();
    }
    $FLine = fgets( STDIN );
    // nahradim bile znaky
    $FLine = preg_replace( '/^(\s)*/', '', $FLine );
}

// xml Writer prikazy
$xml->openMemory();
$xml->setIndent(true);
$xml->startDocument('1.0','UTF-8');

$xml->startElement('program');
$xml->writeAttribute('language','IPPcode20');

// kontrola kvuli chybe 21
$header = "/^[ ]*.IPPcode20(\s)*$/i";

// komentar je soucasti hlavicky
if ( preg_match( '/#((\s)*(\S)*)*/', $FLine ) ){
    incrementComment();
}

$FLine = preg_replace( '/#((\s)*(\S)*)*/', '', $FLine );

//print( "$FLine\n" );

if ( !( preg_match( $header,$FLine ) ) ){
    exit( 21 );
} 

// dokud je co cist tak ctu
while ( ( $line = getLine( $FLine ) ) != NULL ){
    // kontrola kvuli komentarum
    if ( preg_match( '/#((\s)*(\S)*)*/', $line ) ){
        incrementComment();
        // nahradim komentar za mezeru
        $line = preg_replace( '/#((\s)*(\S)*)*/',' ',$line );
    }
    //  nahrazeni bilych znaku na zacatku radku
    $line = preg_replace( '/^(\s)*/', '', $line );
    parseLine( $line, $xml );
}
// ukonceni xml
$xml->endElement();
$xml->endDocument();

echo $xml->outputMemory();

// jestlize je zadane rozsireni
if ( $args ==  1 ){
    writeStatp( $arrayargs, $filePath );
}

//TODO zkusit READ
?>