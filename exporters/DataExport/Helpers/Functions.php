<?php
namespace DataExport\Helpers;

class Functions
{
    public static function getPostDate( string $date )
    {
        # Если жалоба старше 1 года, дату не публикуем совсем. Если жалобе 1 год и меньше выбираем рандомом дату за 3 месяца.
        $useDate = strtotime( $date );
        $useDate = $useDate < time() - 365*24*3600
            ? date("Y-m-d H:i:s", time() - 365*24*3600 )
            : date( "Y-m-d H:i:s", rand( time() - 85 * 24 * 3600, time() ) );

        return $useDate;
    }

    public static function getCommentDate(): string
    {
        return date( "Y-m-d", rand( time() - 7 * 24 * 3600, time() ) );
    }

    public static function getTextLines(string $text)
    {
        $parts = preg_split( '#([\.\!\?]{1,}(?!com|net|info|org|[0-9]{1,})\s*)#si', $text, -1 , PREG_SPLIT_DELIM_CAPTURE);
        $lines = [];

        for($i = 0; $i < count( $parts ); $i += 2 )
        {
            if ( $i == count( $parts ) - 1 && !$parts[$i]) break;
            $lines[] = $parts[$i].($parts[$i+1] ?? "");
        }

        return $lines;
    }
}