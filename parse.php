<?php

global $xml;
global $order;

$order = 0;
$xml = new XMLWriter();

function checkVar( $parsed ){
    if ( !preg_match( '/^((TF)|(GF)|(LF))@((\_)|(\-)|(\$)|(\&)|(\%)|(\*)|(\!)|(\?)|[a-zA-Z]){1}(\S)+$/', $parsed ) ){
        exit( 23 );
    }
}

function checkEnd( $parsed ){
     if ( preg_match( '/^#((\S)*|(\s)*)*$/', $parsed ) ){ //TODO je korektni uprava ?
        $parsed = "";
    } 
    if ( $parsed != "" ){
        exit ( 23 );
    }
}

function checkSymb( $parsed ){
    if ( !preg_match( '/^(string@(\S)*)$|^(int@(\d)*)$|(bool@((true)|(false)))$|^((GF)|(TF)|(LF))@(\S)*$|^(nil)@nil$/', $parsed ) ){
        exit( 23 );
    }
}

function checkLabel( $parsed ){
    if ( !preg_match( '/^(\w)*$/', $parsed ) ){
        exit( 23 );
    }
}

function checkType( $parsed ){
    if ( !preg_match( '/^((int)|(bool)|(string))$/', $parsed ) ){
        exit( 23 );
    }
}

function parseArg( $parsed ){
    if ( preg_match( '/^((GF)|(TF)|(LF))@(\S)*$/', $parsed ) ){
        return array( "var", $parsed );
    } elseif( preg_match( '/^(\w)+$/',$parsed ) ){
        return array( "label", $parsed );
    } else {
        $pos = strpos( $parsed, "@" );
        $firstpiece = substr( $parsed, 0, $pos );
        $secondpiece = substr( $parsed, $pos + 1 );
        $secondpiece = preg_replace( '/\&/', "&amp;", $secondpiece );
        $secondpiece = preg_replace( '/\</', "&lt;", $secondpiece );
        $secondpiece = preg_replace( '/\>/', "&gt;", $secondpiece );
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

function checkSyntax( $parsed, $xml, $order ){
    switch( $parsed[ 0 ] ){
        case "MOVE":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkEnd( $parsed[ 3 ] );
            caseXml( 2, "MOVE", $order, $xml, $parsed );
            break;
        case "DEFVAR":
            checkVar( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "DEFVAR", $order, $xml, $parsed );
            break;
        case "LABEL":
            checkLabel( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "LABEL", $order, $xml, $parsed );
            break;
        case "CREATEFRAME":
            checkEnd( $parsed[ 1 ] );
            caseXml( 0, "CREATEFRAME", $order, $xml, $parsed );
            break;
        case "PUSHFRAME":
            checkEnd( $parsed[ 1 ] );
            caseXml( 0, "PUSHFRAME", $order, $xml, $parsed );
            break;
        case "POPFRAME":
            checkEnd( $parsed[ 1 ] );
            caseXml( 0, "POPFRAME", $order, $xml, $parsed );
            break;
        case "CALL":
            checkLabel( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "CALL", $order, $xml, $parsed );
            break;
        case "RETURN":
            checkEnd( $parsed[ 1 ] );
            caseXml( 0, "RETURN", $order, $xml, $parsed );
            break;
        case "PUSHS":
            checkSymb( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "PUSHS", $order, $xml, $parsed );
            break;
        case "POPS":
            checkVar( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "POPS", $order, $xml, $parsed );
            break;
        case "ADD":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "ADD", $order, $xml, $parsed );
            break;
        case "SUB":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "SUB", $order, $xml, $parsed );
            break;
        case "MUL":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "MUL", $order, $xml, $parsed );
            break;
        case "IDIV":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "IDIV", $order, $xml, $parsed );
            break;
        case "LT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "LT", $order, $xml, $parsed );
            break;
        case "GT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "GT", $order, $xml, $parsed );
            break;
        case "EQ":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "EQ", $order, $xml, $parsed );
            break;
        case "AND":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "AND", $order, $xml, $parsed );
            break;
        case "OR":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "OR", $order, $xml, $parsed );
            break;
        case "NOT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkEnd( $parsed[ 3 ] );
            caseXml( 2, "NOT", $order, $xml, $parsed );
            break;
        case "INT2CHAR":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkEnd( $parsed[ 3 ] );
            caseXml( 2, "INT2CHAR", $order, $xml, $parsed );
            break;
        case "STRI2INT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "STRI2INT", $order, $xml, $parsed );
            break;
        case "WRITE":
            checkSymb( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "WRITE", $order, $xml, $parsed );
            break;
        case "CONCAT":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "CONCAT", $order, $xml, $parsed );
            break;
        case "STRLEN":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkEnd( $parsed[ 3 ] );
            caseXml( 2, "STRLEN", $order, $xml, $parsed );
            break;
        case "GETCHAR":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "GETCHAR", $order, $xml, $parsed );
            break;
        case "SETCHAR":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "SETCHAR", $order, $xml, $parsed );
            break;
        case "TYPE":
            checkVar( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkEnd( $parsed[ 3 ] );
            caseXml( 2, "TYPE", $order, $xml, $parsed );
            break;
        case "JUMP":
            checkLabel( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "JUMP", $order, $xml, $parsed );
            break;
        case "JUMPIFEQ":
            checkLabel( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "JUMPIFEQ", $order, $xml, $parsed );
            break;
        case "JUMPIFNEQ":
            checkLabel( $parsed[ 1 ] );
            checkSymb( $parsed[ 2 ] );
            checkSymb( $parsed[ 3 ] );
            checkEnd( $parsed[ 4 ] );
            caseXml( 3, "JUMPIFNEQ", $order, $xml, $parsed );
            break;
        case "EXIT":
            checkSymb( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "EXIT", $order, $xml, $parsed );    
            break;
        case "DPRINT":
            checkSymb( $parsed[ 1 ] );
            checkEnd( $parsed[ 2 ] );
            caseXml( 1, "DPRINT", $order, $xml, $parsed );
            break;
        case "BREAK":
            checkEnd( $parsed[ 1 ] );
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
    return returnLine( $line );
}

function isKeyWord( $token ){
    $keyWords = array(  "MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL",
                        "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT",
                        "EQ", "AND", "OR", "INT2CHAR", "STRI2INT", "READ", "WRITE", "STRLEN",
                        "GETCHAR", "SETCHAR", "NOT", "LABEL", "JUMPIFEQ", "JUMPIFNEQ", "CONCAT", "JUMP",
                        "TYPE",  "EXIT", "DPRINT", "BREAK" );
    if ( !( in_array( $token,$keyWords ) ) ){
        exit ( 22 );
    }
    return;
}

function parseLine( $line, $xml, $order ){
    $line = preg_replace( '/\s+/', " ",$line );
    $parsed = explode( " ", $line );

    if ( !( preg_match( '/\#/', $parsed[0] ) ) ){
        isKeyWord( $parsed[0] );
        checkSyntax( $parsed, $xml, $order );
    }

    foreach( $parsed as $token ){
        if ( preg_match( '/^#/', $token ) ){
            $order;
            return;
        }
    }
}

$arguments = array( 'help' => false );

if ( $argc > 1 ){
    if ( $argv[ 1 ] == "--help" ){
        echo "Skript typu filtr (parse.php v jazyce PHP 7.4) nacte ze standardniho vstupu zdrojovy kod v IPP-code20, zkontroluje \nlexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu dle specifikace v sekci.\n";
        exit;
    } else {
        exit ( 10 );
    }
}

$FLine = fgets( STDIN );


$xml->openMemory();
$xml->setIndent(true);
$xml->startDocument('1.0','UTF-8');

$xml->startElement('program');
$xml->writeAttribute('language','IPPcode20');

$header = "/^[ ]*.IPPcode20$/";

if ( !( preg_match( $header,$FLine ) ) ){
    exit( 21 );
}

while ( ( $line = getLine( $FLine ) ) != NULL ){
    if ( !preg_match( '/^#/', $line ) ){
        $order++;
    }
    parseLine( $line, $xml, $order );
}

$xml->endElement();
$xml->endDocument();

echo $xml->outputMemory();

// TODO podoba label
// TODO napriklad WHILE bez parametru vyhodi chybu protoze neni definovan parametr
// TODO Zeptat se co delat kdyz je kurzor na novem radku na stdin. Kurzor ale na STDIN pokud neni soubor nemuze byt na novem radku ?...
// TODO je odstraneni prebytecnych mezer korektni osetreni ? Treba: MOVE     GF@counter neni chyba ci ?
// TODO Type
// TODO znamenka u cisel
// odstraneni mezer je korekntni ?
// substituce znaku <> a cosi jeste
// opravit mezery
// NOT ma pouze 2 operandy

?>