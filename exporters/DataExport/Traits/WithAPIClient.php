<?php
namespace DataExport\Traits;

use GuzzleHttp\Client;

trait WithAPIClient
{
    private array $apiClient = [
        "host" => null,
        "timeout" => 20,
    ];

    protected function setApiHost( string $host )
    {
        $this->apiClient['host'] = $host;
    }

    protected function setApiTimeout( int $timeout )
    {
        $this->apiClient['timeout'] = $timeout;
    }

    protected function sendApiRequest( string $url )
    {
        try
        {
            $client = new Client( [
                'base_uri' => $this->apiClient['host'],
                'verify'  => false,
                'timeout' => $this->apiClient['timeout'],
            ] );

            $response = $client->get( $url );

            return [
                "success" => $response->getStatusCode() == 200,
                "code" => $response->getStatusCode(),
                "body" => $response->getBody(),
                "json" => @json_decode( $response->getBody() ),
            ];
        }catch (\Exception $e ) {
            return $this->setError( $e->getMessage() );
        }
    }
}