<?php

namespace DataExport\Helpers;

use DataExport\Traits\WithError;
use GuzzleHttp\Client;
use Exception;

class ScrapeWeb
{
    use WithError;

    public function __construct()
    {
    }

    private function getSocialsFromBody(string $body): array
    {
        $socials = [
            "#https?:\/\/[a-z]+\.linkedin\.com\/[^\"' ]+#is"                           => "linkedin_url",
            "#https?:\/\/www\.facebook\.com\/[^\"' ]+#is"                              => "facebook_url",
            "#https?:\/\/(www\.)?twitter\.com\/[^\"' ]+#is"                            => "twitter_url",
            "#https?:\/\/plus\.google\.com\/[^\"' ]+#is"                               => "google_url",
            "#https?:\/\/www\.youtube\.com\/[^\"' ]+#is"                               => "youtube_url",
            "#https?:\/\/www\.instagram\.com\/[^\"' ]+#is"                             => "instagram_url",
            "#https?:\/\/(pin\.it|www\.pinterest\.com|in\.pinterest\.com)/[^\"' ]+#is" => "pinterest_url",
        ];

        $return = [];

        foreach($socials as $pattern => $type ) {
            if ( preg_match_all($pattern,$body,$m) ) {
                if(!isset($return[$type])) {
                    $return[$type] = [];
                }
                foreach($m[0] as $url) {
                    $return[$type][] = $url;
                }
            }
        }

        return $return;
    }

    public function getSocials(string $url)
    {
        $url = $this->normalizeUrl($url);
        if (!$url) {
            return $this->setError("Url empty");
        }
        try {
            $client = new Client(['verify' => false, 'timeout' => 30]);
            $response = $client->get($url);

            if ($response->getStatusCode() != 200) {
                return $this->setError('Http response not 200');
            }

            $body = $response->getBody()->getContents();

            return $this->getSocialsFromBody($body);
        } catch (Exception $e) {
            return $this->setError($e->getMessage());
        }
    }

    private function normalizeUrl(string $url)
    {
        $url = trim($url);
        $url = !preg_match("#^https?\://#", $url) ? "http://{$url}" : $url;

        return $url;
    }

}