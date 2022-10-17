<?php
namespace DataExport\Helpers;

class TextFormatter
{
    # taked from IW project
    public static function removeAbbreviationsFromCompanyName( $companyName )
    {
        # ATTENTION: please update tests/misc-removeAbbreviationsFromCompanyName.php after function update

        $words = [  "LLC", "PLLC", "Inc", "co", "lpa", "unl", "mba", "ltd", "corp", "cpa",
                    "md", "phd", "psc", "dds", "bs", "fsb", "as", "cc", "ma", "dc",
                    "fiaca", "ra", "dr", "pa", "fa", "pc", "sa", "li", "na", "sc",
                    "hvac", "cmi", "lc", "plc", "phd", "ctr", "dmd", "do", "llp",
                    "esq", "lp", "pls", "od", "dvm", "sr", "pl", "int", "svc" ];

        usort( $words, function ( $a, $b ) {
            $len = strlen( $b ) - strlen( $a );
            if ( $len == 0 )
            {
                return strcmp( $a, $b );
            }
            return $len;
        });

        $counter = 0;
        do{
            $oldCompanyName = $companyName;

            foreach( [ "#Ph\s*?\.\s*?d\.?$#si" ] as $pattern )
            {
                $companyName = preg_replace( $pattern, "", $companyName );
                $companyName = trim( $companyName, " -," );
            }

            $before = $companyName;
            foreach( $words as $word )
            {
                $wordDots = implode( "\s*?\.\s*?", str_split( $word ) );

                $companyName = preg_replace( "#[,\.]? ({$word}|{$wordDots})\.?$#si", "", $companyName );
                $companyName = preg_replace( "#[,\.]\s*?({$word}|{$wordDots})\.?$#si", "", $companyName );
                $companyName = trim( $companyName, " -," );

                # we must replaces longest words first, if replaces done then break, because may be errors
                if ( $before != $companyName ) break;
            }

        }while( strcasecmp( $oldCompanyName, $companyName ) != 0 && $counter++ < 3 );

        return $companyName;
    }

    public static function fixAdvText( $text, $domain )
    {
        // /* (1000, 5, 2020/11/09) */
        $text = preg_replace( '#/\*\s*?\([0-9/, ]{1,}\)\s*?\*/#si', "", $text );
        $text = trim( $text );

        return $text;
    }

    # taked from IW project tests/api_bbb.php
    public static function fixText( $text, $domain )
    {
        $text = str_ireplace( [ "<p>", "</p>", "\r" ], [ "\n", "\n", "" ], $text );
        $text = strip_tags( $text );
        $text = html_entity_decode( $text );
        $text = preg_replace( "~\x{00a0}~siu", " ", $text ); # c2 a0 --> space
        $text = str_ireplace('BBB', 'Complaintsboard.com', $text);
        $text = preg_replace('#Better[\s\xA0]Business[\s\xA0]Bureau#si', $domain, $text);

        $text = static::fixAdvText( $text, $domain );

        $text = preg_replace( "#(Mr|Mrs|Ms|Miss)\.[ ]*?\*{1,}('s)?#si", "$1.", $text );
        $text = preg_replace( "#(Mr|Mrs|Ms|Miss)\.[ ]+?([a-z])\*{1,}#si", "$1. $2", $text );
        $text = preg_replace( "# ID\s*?\*+#si", " ID", $text );
        $text = preg_replace( "# ([A-Z])\*+#s", " $1", $text );
        $text = preg_replace( "|#[#\-]{2,}[ \t]*|si", "", $text );
        $text = preg_replace_callback( "|\*[ \t\*]+|si", function ( $matches ) {
            $ending = substr( $matches[0], -1 ) != '*' ? substr( $matches[0], -1 ) : '';
            return strlen( $matches[0] ) >= 3 ? "***".$ending : "";
        }, $text );
        $text = preg_replace( "|[ ]{2,}|si", " ", $text );

        $text = preg_replace( "#^[ \t]{1,}#im", "", $text );
        $text = preg_replace( "#(\n){2,}#si", "\n\n", $text );

        $text = trim( $text, " \t\r\n\*," );

        return $text;
    }
}