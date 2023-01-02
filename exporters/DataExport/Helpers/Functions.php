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
}