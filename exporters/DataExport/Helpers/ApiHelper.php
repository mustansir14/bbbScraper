<?php
namespace DataExport\Helpers;

class ApiHelper
{
    private static string $apiUrl = "http://65.109.70.91:5000";

    public static function getLogo( string $fileName )
    {
        $result = static::request( "/api/v1/file?type=logo&name=".rawurlencode( $fileName ) );
        if ( !$result["success"] ) return false;

        print_r($result);
    }

    private static function request( string $url )
    {
        $ch = curl_init( static::$apiUrl.$url );

        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_VERBOSE, 1);

        // $output contains the output string
        $output = curl_exec($ch);
        $error = curl_error( $ch );
        $errno = curl_errno( $ch );
        $contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);

        curl_close($ch);

        return [
            "success" => $errno === 0,
            "error" => $error,
            "errno" => $errno,
            "content_type" => $contentType,
        ];
    }
}