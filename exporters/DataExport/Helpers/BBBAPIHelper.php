<?php

namespace DataExport\Helpers;

use DataExport\Traits\WithError;
use GuzzleHttp\Client;
use GuzzleHttp\Exception\ClientException;

class BBBAPIHelper
{
    use WithError;

    private string $apiUrl = "http://65.109.70.91:5000";

    public function __construct()
    {

    }

    public function getLogo( string $fileName )
    {
        try
        {
            $client = new Client( [
                'base_uri' => $this->apiUrl,
                'verify'  => false,
                'timeout' => 20,
            ] );

            $response = $client->get( "/api/v1/file?type=logo&name=".rawurlencode( $fileName ) );

            if ( $response->getStatusCode() != 200 ) return $this->setError( "Http code not 200" );
            if ( stripos( $response->getHeader('content-type')[0], "image/" ) !== false )
            {
                return $response->getBody();
            }

            return $this->setError( "Not image" );
        }catch (\Exception $e ) {
            return $this->setError( $e->getMessage() );
        }
    }

}