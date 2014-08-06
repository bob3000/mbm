<?php
require_once __DIR__ . '/vendor/autoload.php';
use ohmy\Auth1;

$caller_url = parse_url("http".(!empty($_SERVER['HTTPS'])?"s":"").
    "://".$_SERVER['SERVER_NAME'].$_SERVER['REQUEST_URI']);
define('CALLBACK_URL',
    $caller_url['scheme']."://".$caller_url['host'].$caller_url['path']);


# start a session to save oauth data in-between redirects
session_start();

if (isset($_GET['consumer_key']) &&
    isset($_GET['consumer_secret']) &&
    isset($_GET['account_type'])) {
        $_SESSION['mbm']['consumer_key'] = $_GET['consumer_key'];
        $_SESSION['mbm']['consumer_secret'] = $_GET['consumer_secret'];

    if ($_GET['account_type'] === 'tumblr') {
        $_SESSION['mbm']['request_url'] = "https://www.tumblr.com/oauth/request_token";
        $_SESSION['mbm']['authorize_url'] = "https://www.tumblr.com/oauth/authorize";
        $_SESSION['mbm']['access_url'] = "https://www.tumblr.com/oauth/access_token";
        $_SESSION['mbm']['test_url'] = "https://api.tumblr.com/v2/user/info";
    }

    if ($_GET['account_type'] === 'twitter') {
        $_SESSION['mbm']['request_url'] = "https://api.twitter.com/oauth/request_token";
        $_SESSION['mbm']['authorize_url'] = "https://api.twitter.com/oauth/authorize";
        $_SESSION['mbm']['access_url'] = "https://api.twitter.com/oauth/access_token";
        $_SESSION['mbm']['test_url'] = "https://api.twitter.com/1.1/statuses/home_timeline.json";
    }
}

# initialize 3-legged oauth
$access = Auth1::legs(3)
               # configuration
               ->set('key', $_SESSION['mbm']['consumer_key'])
               ->set('secret', $_SESSION['mbm']['consumer_secret'])
               ->set('callback', CALLBACK_URL)

               # oauth flow
               ->request($_SESSION['mbm']['request_url'])
               ->authorize($_SESSION['mbm']['authorize_url'])
               ->access($_SESSION['mbm']['access_url']);

?>

<!DOCTYPE html>
<html>
<head>
<title>Micro Bog Magic</title>
</head>
<body>
<h1>Micro Bog Magic</h1>

<?php
# test GET method
$access->GET($_SESSION['mbm']['test_url'])
       ->then(function($response) {
          $data = $response->json();
          if ($data['meta']['status'] !== 200) {
              print '<strong>';;
              print $data['meta']['status'].' '.$data['meta']['msg']."<br>\n";
              print '</strong>';
              print "<p>Check consumer credentials</p><br>\n";
              print "<pre>\n";
              print $_SESSION['mbm']['consumer_key']."\n";
              print $_SESSION['mbm']['consumer_secret']."\n";
              print "</pre>\n";
              die();
          }
          return $data;
       })
       ->then(function($data) use($access){
              print "<pre>\n";
              print "Token: ".$access->value['oauth_token']."\n";
              print "Secret: ".$access->value['oauth_token_secret']."\n";
              print "</pre>\n";
       })
       ->finally(session_destroy);
?>

<footer>
    Copyright 2014 Robin Kautz&nbsp;-&nbsp;
    Contact: <a href='https://github.com/bob3000'>https://github.com/bob3000</a>
</footer>
</body>
</html>
