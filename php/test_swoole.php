<?php
require __DIR__."/vendor/autoload.php";

if(!extension_loaded('openswoole')) {
    die("Error: no swoole");
}

use OpenSwoole\Coroutine\Http\Client;
use OpenSwoole\Core\Coroutine\WaitGroup;

co::run(function()
{
    $data = get('http://94.140.123.40:25000/');
    $proxies = explode("\n", $data->body);
    $proxies = array_map("trim", $proxies);
    $proxies = array_filter($proxies, "strlen");
    $proxies = array_values($proxies);
    
    $wg = new WaitGroup();
    $totalProxies = count($proxies);
    $totalChecked = 0;
    
    $validProxies = [];
    
    foreach ($proxies as $proxy) {
        go(function () use (&$wg, $proxy, &$return, &$totalChecked, $totalProxies, &$validProxies)
        {
            $wg->add();

            try {
                $response = get(
                    "https://www.consumercomplaints.in/get-ip-info/?get-my-ip=1&token=5b98020644a27a8477d95b66e5337f3e7222d866&providers=cloudflare",
                    $proxy
                );

                echo ($totalChecked."/".$totalProxies.") IN check for ".$proxy.": ".var_export($response->body, true))."\n";
                $validProxies[] = $proxy;

                $return[] = $proxy;
            } catch(\Exception $error) {
                echo ($totalChecked."/".$totalProxies.") IN check for ".$proxy.": exception ".$error->getMessage())."\n";
            }

            $totalChecked++;

            $wg->done();
        });
    }
    
    $wg->wait(300);
    
    $bbbNotBanned = [];
    $totalProxies = count($validProxies);
    $totalChecked = 0;
    
    foreach ($validProxies as $proxy) {
        go(function () use (&$wg, $proxy, &$return, &$totalChecked, $totalProxies, &$bbbNotBanned)
        {
            $wg->add();

            try {
                $response = get(
                    "https://www.bbb.org/",
                    $proxy
                );

                echo ($totalChecked."/".$totalProxies.") BBB check for ".$proxy.": ".var_export($response->code, true))."\n";
                
                if($response->code == 200) {
                    $bbbNotBanned[] = $proxy;
                }

                $return[] = $proxy;
            } catch(\Exception $error) {
                echo ($totalChecked."/".$totalProxies.") BBB check for ".$proxy.": exception ".$error->getMessage())."\n";
            }

            $totalChecked++;

            $wg->done();
        });
    }
    
    $wg->wait(300);
    
    echo "Total proxies: ".count($proxies)."\n";
    echo "Valid proxies: ".count($validProxies)."\n";
    echo "Valid proxies: ".count($bbbNotBanned)."\n";
});

function parseUrlMy(string $url): object
{
    if(!$url) {
        throw new RuntimeException("Empty url");
    }

    $parse = parse_url($url);
    $isSSL = $parse['scheme'] === 'https';

    return (object)[
        'ssl' => $isSSL,
        'host' => $parse['host'],
        'port' => $parse['port'] ?? ($isSSL ? 443 : 80),
        'path' => ($parse['path'] ?: '/').($parse['query'] ? '?'.$parse['query'] : ''),
    ];
}

function get(string $url, ?string $proxy = null): object
{
    $parsedUrl = parseUrlMy($url);
    
    $settings = [
        'reconnect'          => 1, # do not set zero, or no connection
        'connect_timeout'    => 15,
        'timeout'            => 60,
        'http_compression'   => true,
        'body_decompression' => true,
    ];
    
    if ($proxy) {
        [$host, $port] = explode(":", $proxy, 2);

        $settings['socks5_host'] = $host;
        $settings['socks5_port'] = $port;
    }

    $client = new Client($parsedUrl->host, $parsedUrl->port, $parsedUrl->ssl);
    $client->set($settings);
    $client->setHeaders([
        'Host' => $parsedUrl->host,
    ]);
    $client->get($parsedUrl->path);

    if($client->errCode) {
        throw new RuntimeException("Error {$client->errCode}: {$client->errMsg}");
    }

    $client->close();
    
    return (object)[
        'code' => $client->getStatusCode(), 
        'body' => $client->getBody(),
    ];
}