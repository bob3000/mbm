<?php
require_once __DIR__ . '/vendor/autoload.php';
use ohmy\Auth1;

$caller_url = parse_url("http".(!empty($_SERVER['HTTPS'])?"s":"").
    "://".$_SERVER['SERVER_NAME'].$_SERVER['REQUEST_URI']);
define('CALLBACK_URL',
    $caller_url['scheme']."://".$caller_url['host'].$caller_url['path']);


function insert_from() {
    print "<p>I'm a procurer. I can get you access tokens.</p>\n";
    print
      '<form action="'.CALLBACK_URL.'">'."\n"
    . '    <label for="consumer_key">Consumer Key</label><br>'."\n"
    . '    <input type="text" name="consumer_key" id="consumer_key"><br><br>'."\n"
    . '    <label for="consumer_secret">Consumer Secret</label><br>'."\n"
    . '    <input type="text" name="consumer_secret" id="consumer_secret"><br><br>'."\n"
    . '    <select name="account_type">'."\n"
    . '       <option value="twitter" selected>Twitter</option>'."\n"
    . '       <option value="tumblr">Tumblr</option>'."\n"
    . '    </select><br><br>'."\n"
    . '    <input type="submit" value="Submit">'."\n"
    . '</form>'."\n"
    . '<br>'."\n";
}

# start a session to save oauth data in-between redirects
session_start();

if (isset($_REQUEST['consumer_key']) &&
    isset($_REQUEST['consumer_secret']) &&
    isset($_REQUEST['account_type'])) {
        $_SESSION['mbm']['consumer_key'] = $_REQUEST['consumer_key'];
        $_SESSION['mbm']['consumer_secret'] = $_REQUEST['consumer_secret'];

    if ($_REQUEST['account_type'] === 'tumblr') {
        $_SESSION['mbm']['request_url'] = "https://www.tumblr.com/oauth/request_token";
        $_SESSION['mbm']['authorize_url'] = "https://www.tumblr.com/oauth/authorize";
        $_SESSION['mbm']['access_url'] = "https://www.tumblr.com/oauth/access_token";
        $_SESSION['mbm']['test_url'] = "https://api.tumblr.com/v2/user/info";
    }

    if ($_REQUEST['account_type'] === 'twitter') {
        $_SESSION['mbm']['request_url'] = "https://api.twitter.com/oauth/request_token";
        $_SESSION['mbm']['authorize_url'] = "https://api.twitter.com/oauth/authorize";
        $_SESSION['mbm']['access_url'] = "https://api.twitter.com/oauth/access_token";
        $_SESSION['mbm']['test_url'] = "https://api.twitter.com/1.1/statuses/home_timeline.json";
    }
}

if (!empty($_SESSION)) {
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
}
?>

<!DOCTYPE html>
<html>
<head>
<title>Micro Bog Magic</title>
<meta charset="utf-8">
</head>
<body>
<h1>Micro Bog Magic</h1>

<?php
if (!empty($_SESSION)) {
    # test GET method
    $access->GET($_SESSION['mbm']['test_url'])
           ->then(function($response) {
               $data = $response->json();
               if  (property_exists($response->headers) &&
                   $response->headers['status'] == '200 OK' ||
                   isset($data['meta']) && $data['meta']['status'] != '200') {
                       print '<strong>';;
                       print $data['meta']['status'].' '.$data['meta']['msg']."<br>\n";
                       print '</strong>';
                       print "<p>Check consumer credentials</p>\n";
                       print "<pre>\n";
                       print "Consumer Key: ".$_SESSION['mbm']['consumer_key']."\n";
                       print "Consumer Secret: ".$_SESSION['mbm']['consumer_secret']."\n";
                       print "</pre>\n";
                       die();
                   }
               return $data;
           })
           ->then(function($data) use($access){
                  $show_form = "javascript:document.getElementById('consumer_form').style.display = 'block';";
                  print "<pre>\n";
                  print "Token: ".$access->value['oauth_token']."\n";
                  print "Secret: ".$access->value['oauth_token_secret']."\n";
                  print "</pre>\n";
                  print "\n<button type=\"button\" onclick=\"".$show_form."\">Get new token</button>\n";
                  print "<div id=\"consumer_form\" style=\"display: none;\">";
                  insert_from();
                  print "</div>";
                  return $data;
           });
}

if (empty($_SESSION)) {
    insert_from();
}
?>

<footer style="margin-top: 20px;">
    Copyright © 2014 Robin Kautz&nbsp;-&nbsp;
    Contact: <a href='https://github.com/bob3000'>https://github.com/bob3000</a>
</footer>
</body>
</html>
