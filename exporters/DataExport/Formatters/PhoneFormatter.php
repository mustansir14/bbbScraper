<?php
namespace DataExport\Formatters;

class PhoneFormatter
{
    public static function fromString( ?string $text ): array
    {
        if ( !$text ) return [];

        $phones = explode( "\n", $text );
        $phones = array_map( "trim", $phones );
        $phones = array_filter( $phones, "strlen" );

        $phones = array_map( [ __CLASS__ , "format" ], $phones );

        return $phones;
    }

    public static function format( string $phone ): string
    {
        $digits = preg_replace( "#[^0-9]#si", "", $phone );
        # (XXX) XXX-XXXX

        $part1 = substr( $digits, 0, 3 );
        $part2 = substr( $digits, 3,3 );
        $part3 = substr( $digits, 6 );

        return "+1 (".$part1.") ".$part2."-".$part3;
    }
}