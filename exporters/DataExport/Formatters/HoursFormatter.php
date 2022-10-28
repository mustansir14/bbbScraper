<?php
namespace DataExport\Formatters;

class HoursFormatter
{
    private static array $weekDays = [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ];

    public static function fromString( ?string $text ): ?array
    {
        if ( !$text ) return null;

        $dayIndex = [
            "m"  => "monday",
            "t"  => "tuesday",
            "w"  => "wednesday",
            "th" => "thursday",
            "f"  => "friday",
            "sa" => "saturday",
            "su" => "sunday",
        ];

        $days = implode( "|", array_keys( $dayIndex ) );

        if ( !preg_match_all( '#('.$days.')\:\s+?(Closed|Open 24 Hours|[0-9]{1,2}\:[0-9]{1,2}\s(?:AM|PM) \- [0-9]{1,2}\:[0-9]{1,2}\s(?:AM|PM))#si', $text, $m ) )
        {
            return null;
        }

        $return = array_combine( array_values( $dayIndex ), array_fill( 0, 7, [ "type" => "closed" ] ) );

        foreach( $m[1] as $nbr => $dayShort )
        {
            $dayShort = strtolower( $dayShort );
            if ( !isset( $dayIndex[ $dayShort ] ) ) return null;

            $index = $dayIndex[ $dayShort ];
            $value = strtolower( $m[2][$nbr] );

            if ( $value === "closed" )
            {
                $return[ $index ] = [
                    "type" => "closed"
                ];
            }elseif( $value === "open 24 hours" )
            {
                $return[ $index ] = [
                    "type" => "open24"
                ];
            } else {
                $parts = explode( "-", $value );
                $parts = array_map( "trim", $parts );
                $parts = array_map( function( $value ) {
                    [ $time, $ampm ] = explode( " ", $value );
                    [ $hours, $minutes ] = explode( ":", $time );

                    $hours = trim( $hours );
                    $minutes = trim( $minutes );

                    $hours = strtoupper( $ampm ) == "PM" ? $hours + 12 : $hours;

                    return sprintf( "%'.02d:%'.02d", $hours, $minutes );
                }, $parts );

                $return[ $index ] = [
                    "type" => "range",
                    "from" => $parts[0],
                    "to"   => $parts[1],
                ];
            }
        }

        # check if all closed
        $count = 0;
        foreach( $return as $value )
        {
            if ( $value["type"] == "closed" )
            {
                $count++;
            }
        }

        # if all closed then no hours
        if ( $count > 6 ) return null;

        #print_r($return);exit;

        return $return;
    }

    public static function convertToCBInternalFormat( array $hours ): string
    {
        $return = [];

        foreach( static::$weekDays as $weekDay )
        {
            $value = $hours[ $weekDay ];
            if ( $value["type"] == "closed" )
            {
                $return[] = 0;
            }elseif( $value["type"] == "open24" )
            {
                $return[] = "0:24";
            }elseif( $value["type"] == "range" )
            {
                $return[] = str_replace( ":", ".", $value["from"] ).":".str_replace( ":", ".", $value["to"] );
            }else{
                $return[] = 0;
            }
        }

        return implode( ";", $return );
    }
}