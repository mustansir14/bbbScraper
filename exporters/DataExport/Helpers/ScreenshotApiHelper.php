<?php

namespace DataExport\Helpers;

use DataExport\Traits\WithError;
use DataExport\Traits\WithAPIClient;
use GuzzleHttp\Client;
use GuzzleHttp\Exception\ClientException;

class ScreenshotApiHelper
{
    use WithError, WithAPIClient;

    public function __construct()
    {
        $this->setApiHost( "http://65.109.70.91:3030" );
        $this->setApiTimeout( 180 );
    }

    public function getScreenshot( string $website )
    {
        $reply = $this->sendApiRequest( "/api/v1/screenshot?url=".rawurlencode($website)."&type=short" );
        if ( !$reply ) return false;

        $reply["json"]->image_content = base64_decode( $reply['json']->image_base64_content );

        return $reply["json"];
    }
}