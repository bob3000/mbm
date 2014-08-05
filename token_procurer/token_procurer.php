<?php
require_once __DIR__ . '/vendor/autoload.php';
use ohmy\Auth1;


$caller_url = parse_url("http".(!empty($_SERVER['HTTPS'])?"s":"").
    "://".$_SERVER['SERVER_NAME'].$_SERVER['REQUEST_URI']);
define('CALLBACK_URL',
    $caller_url['scheme']."://".$caller_url['host'].$caller_url['path']);


# start a session to save oauth data in-between redirects
session_start();

# initialize 3-legged oauth
$access = Auth1::init(3)
               # configuration
               ->set('key', $_GET['consumer_key'])
               ->set('secret', $_GET['consumer_secret'])
               ->set('callback', CALLBACK_URL)

               # oauth flow
               ->request($_GET['request_url'])
               ->authorize($_GET['authorize_url'])
               ->access($_GET['access_url'])
               ->finally(session_destroy);

echo '<h1>Micro Bog Magic</h1>';
echo '<pre>';
echo "Token: ".$access->value['oauth_token']."\n";
echo "Secret: ".$access->value['oauth_token_secret']."\n";
echo '</pre>';

