<?php

global $xml;

$type;
$order;
$test;
$args = 0;
$comments = 0;
$jumps = 0;
$order = 0;

$xml = new XMLWriter();

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

function checkArgs( $help_argument, $arrayargs, $filePath ){
    global $statp;
    $statp = 0;

    if ( ( count( $help_argument ) == 1 ) && ( count( $arrayargs ) != 0 ) ){
        exit( 10 );
    } elseif( ( count( $help_argument ) == 1 ) && ( count( $arrayargs ) == 0 ) ){
        echo "Skript typu filtr (parse.php v jazyce PHP 7.4) nacte ze standardniho vstupu zdrojovy kod v IPP-code20, zkontroluje \nlexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu dle specifikace v sekci.\n";
        exit;
    } elseif( ( count( $help_argument ) == 0 ) && ( count( $arrayargs ) != 0 ) ){
        $stats = false;
        $different = false;
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

function checkVar( $parsed ){
    if ( !preg_match( '/(*UTF8)^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|(\p{L})){1}((\p{N})|(\p{L}))*$/i', $parsed ) ){
        echo $parsed."\n";
        exit( 23 );
    }
}

function checkEnd( $parsed ){
     if ( preg_match( '/(*UTF8)^#((\S)*|(\s)*)*$/', $parsed ) ){ //TODO je korektni uprava ?
        $parsed = "";
    } 
    if ( $parsed != "" ){
        echo $parsed."\n";
        exit ( 23 );
    }
}

function definedEnd( $parsed, $index ){
    incrementOrder();
    if ( isset( $parsed[ $index ] ) ){
        checkEnd( $parsed[ $index ] );
    }

}

function checkSymb( $parsed ){
    if ( !preg_match( '/(*UTF8)^([^#\s\\\\]|\\\\[0-9]{3})*$|^(int@((\-)|(\+)){0,1}(\p{N})*)$|(bool@((true)|(false)))$|^((GF)|(TF)|(LF))@(\S)*$|^(nil)@nil$/i', $parsed ) ){
        echo $parsed."\n";

        exit( 23 );
    }
}

function checkLabel( $parsed ){
    if ( !preg_match( '/(*UTF8)^(\S)*$/', $parsed ) ){
        echo $parsed."\n";

        exit( 23 );
    }
}

function checkType( $parsed ){
    if ( !preg_match( '/^((int)|(bool)|(string))$/i', $parsed ) ){
        echo $parsed."\n";

        exit( 23 );
    }
}

function parseArg( $parsed ){
    
    global $comments;
    global $type;
    
    if ( preg_match( '/(*UTF8)^((GF)|(TF)|(LF))@(\S)*$/i', $parsed ) ){
        $parsed = preg_replace( '/(GF)/i', "GF", $parsed );
        $parsed = preg_replace( '/(LF)/i', "LF", $parsed );
        $parsed = preg_replace( '/(TF)/i', "TF", $parsed );
        return array( "var", $parsed );
    } elseif( preg_match( '/^(\w)+$/',$parsed ) && $type == 0 ){
        return array( "label", $parsed );
    } elseif( preg_match( '/^(\w)+$/',$parsed ) && $type == 1 ){
        $type = 0;
        return array( "type", $parsed ); 
    } else {
        $pos = strpos( $parsed, "@" );
        $firstpiece = substr( $parsed, 0, $pos );
        $secondpiece = substr( $parsed, $pos + 1 );

        if ( preg_match( '/^#/', $secondpiece ) ){
            $comments++;
            $secondpiece = "";
        }
        return array( $firstpiece, $secondpiece );
    }
}

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

function checkSyntax( $parsed, $xml ){
    
    global $order;
    global $loc;
    global $labels;
    global $jumps;
    global $type;

    $type = 0;
    
    $parsed[ 0 ] = strtoupper( $parsed[ 0 ] );

    switch( $parsed[ 0 ] ){
        case "MOVE":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            definedEnd( $parsed, 3 );
            caseXml( 2, "MOVE", $order, $xml, $parsed );
            break;
        case "DEFVAR":
            checkVar( $parsed[ 1 ] );
            definedEnd( $parsed, 2 );
            caseXml( 1, "DEFVAR", $order, $xml, $parsed );
            break;
        case "LABEL":
            $labels++;
            checkLabel( $parsed[ 1 ] );
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
            checkLabel( $parsed[ 1 ] );
            definedEnd( $parsed, 2 );
            caseXml( 1, "CALL", $order, $xml, $parsed );
            break;
        case "READ":
            checkVar( $parsed[ 1 ] );
            checkType( $parsed[ 2 ] );
            $type = 1;
            definedEnd( $parsed, 3 );            
            caseXml( 2, "READ", $order, $xml, $parsed );
            break;
        case "RETURN":
            definedEnd( $parsed, 1 );
            caseXml( 0, "RETURN", $order, $xml, $parsed );
            break;
        case "PUSHS":
            checkSymb( $parsed[ 1 ] );
            definedEnd( $parsed, 2 );
            caseXml( 1, "PUSHS", $order, $xml, $parsed );
            break;
        case "POPS":
            checkVar( $parsed[ 1 ] );
            definedEnd( $parsed, 2 );
            caseXml( 1, "POPS", $order, $xml, $parsed );
            break;
        case "ADD":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "ADD", $order, $xml, $parsed );
            break;
        case "SUB":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "SUB", $order, $xml, $parsed );
            break;
        case "MUL":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "MUL", $order, $xml, $parsed );
            break;
        case "IDIV":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "IDIV", $order, $xml, $parsed );
            break;
        case "LT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "LT", $order, $xml, $parsed );
            break;
        case "GT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "GT", $order, $xml, $parsed );
            break;
        case "EQ":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "EQ", $order, $xml, $parsed );
            break;
        case "AND":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "AND", $order, $xml, $parsed );
            break;
        case "OR":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "OR", $order, $xml, $parsed );
            break;
        case "NOT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            definedEnd( $parsed, 3 );
            caseXml( 2, "NOT", $order, $xml, $parsed );
            break;
        case "INT2CHAR":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            definedEnd( $parsed, 3 );
            caseXml( 2, "INT2CHAR", $order, $xml, $parsed );
            break;
        case "STRI2INT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "STRI2INT", $order, $xml, $parsed );
            break;
        case "WRITE":
            checkSymb( $parsed[ 1 ] );
            definedEnd( $parsed, 2 );
            caseXml( 1, "WRITE", $order, $xml, $parsed );
            break;
        case "CONCAT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "CONCAT", $order, $xml, $parsed );
            break;
        case "STRLEN":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            definedEnd( $parsed, 3 );
            caseXml( 2, "STRLEN", $order, $xml, $parsed );
            break;
        case "GETCHAR":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "GETCHAR", $order, $xml, $parsed );
            break;
        case "SETCHAR":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "SETCHAR", $order, $xml, $parsed );
            break;
        case "TYPE":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            definedEnd( $parsed, 3 );
            caseXml( 2, "TYPE", $order, $xml, $parsed );
            break;
        case "JUMP":
            $jumps++;
            checkLabel( $parsed[ 1 ] );
            definedEnd( $parsed, 2 );
            caseXml( 1, "JUMP", $order, $xml, $parsed );
            break;
        case "JUMPIFEQ":
            $jumps++;
            checkLabel( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "JUMPIFEQ", $order, $xml, $parsed );
            break;
        case "JUMPIFNEQ":
            $jumps++;
            checkLabel( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            definedEnd( $parsed, 4 );
            caseXml( 3, "JUMPIFNEQ", $order, $xml, $parsed );
            break;
        case "EXIT":
            checkSymb( $parsed[ 1 ] );
            definedEnd( $parsed, 2 );
            caseXml( 1, "EXIT", $order, $xml, $parsed );    
            break;
        case "DPRINT":
            checkSymb( $parsed[ 1 ] );
            definedEnd( $parsed, 2 );
            caseXml( 1, "DPRINT", $order, $xml, $parsed );
            break;
        case "BREAK":
            definedEnd( $parsed, 1 );
            caseXml( 0, "BREAK", $order, $xml, $parsed );
            break;
        
    }
}

function returnLine( $line ){
    if ( ( $line ) || ( $line ) != 'EOF' ){
        return $line;
    } else {
        return NULL;
    }
}

function getLine( $file ){
    $line = fgets( STDIN );
    while ( $line == "\n" ){
        $line = fgets( STDIN );
    }
    return returnLine( $line );
}

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

function parseLine( $line, $xml ){

    global $comments;

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

$help_argument = array();
$arrayargs = array();
$filePath = "";

if ( $argc > 1 ){
    foreach( $argv as $current ){
        if ( $current == "parse.php" ){
            continue;
        }
        if ( preg_match( '/^(\-){1,2}help$/', $current ) ){
            array_push( $help_argument, 'help' );
        } elseif ( preg_match( '/^(\-){1,2}stats=((..\/)*(\w+)(\/){0,1})+$/', $current ) ) {
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

if ( !( $FLine = fgets( STDIN ) ) ) exit( 21 );

$FLine = preg_replace( '/^(\s)*/', '', $FLine );

while ( $FLine == "\n" || preg_match( '/^#/',$FLine ) || preg_match( '/^(\s)*$/', $FLine ) ){
    if ( preg_match( '/^#/',$FLine ) ){
        incrementComment();
    }
    $FLine = fgets( STDIN );
    $FLine = preg_replace( '/^(\s)*/', '', $FLine );
}

$xml->openMemory();
$xml->setIndent(true);
$xml->startDocument('1.0','UTF-8');

$xml->startElement('program');
$xml->writeAttribute('language','IPPcode20');

$header = "/^[ ]*.IPPcode20$|^[ ]*.IPPcode20(((\s)+(\#))|(\#))/";

if ( !( preg_match( $header,$FLine ) ) ){
    exit( 21 );
} 
if ( preg_match( '/#((\s)*(\S)*)*/', $FLine ) ){
    incrementComment();
}

while ( ( $line = getLine( $FLine ) ) != NULL ){
    if ( preg_match( '/#((\s)*(\S)*)*/', $line ) ){
        incrementComment();
        $line = preg_replace( '/#((\s)*(\S)*)*/',' ',$line );
    }
    $line = preg_replace( '/^(\s)*/', '', $line );
    parseLine( $line, $xml );
}
$xml->endElement();
$xml->endDocument();

echo $xml->outputMemory();

if ( $args ==  1 ){
    writeStatp( $arrayargs, $filePath );
}
// TODO prazdny soubor na vstupu
?>