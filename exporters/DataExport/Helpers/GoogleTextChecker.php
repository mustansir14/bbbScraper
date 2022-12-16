<?php

namespace DataExport\Helpers;

use GuzzleHttp\Client;
use DataExport\Traits\WithError;
use DataExport\Traits\WithAPIClient;

class GoogleTextChecker
{
    use WithError, WithAPIClient;

    public function __construct()
    {
        $this->setApiHost("http://65.109.70.91:3000");
        $this->setApiTimeout( 180 );
    }

    public function test( string $text )
    {
        $text = trim( $text );
        if ( !$text ) return $this->setError( "Text is empty" );

        $response = $this->sendApiRequest( "/api/googleresp?q=".rawurlencode( $text ) );
        if ( !$response ) return false;

        if ( !$response["json"] ) return $this->setError("Response not json");

        $json = $response["json"];

        if ( !$json->success ) {
            return $this->setError( implode( "\n", $json->errors ) );
        }

        return $json;
    }

}