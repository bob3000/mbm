<?php
define('REQ_TOKEN_TTL', 86400);  // one day lifetime
define('TOKEN_STORE_PATH', '/tmp/tokens.db');
define('CONSUMER_KEY', '');
define('CONSUMER_SECRET', '');

function register_request_token($token, $verifier, $access_url) {
    $f = fopen(TOKEN_STORE_PATH, 'a') or
        die("Could not open ".TOKEN_STORE_PATH."\n");
    $entry = time()."|".$token."|".$verifier."|".$access_url."\n";
    fwrite($f, $entry) or
        die("Error: Could not write to ".TOKEN_STORE_PATH."\n");
    fclose($f);
}

function seek_n_destroy_req_token($token) {
    $access_data = array();
    $contents = file_get_contents(TOKEN_STORE_PATH);
    $f = fopen(TOKEN_STORE_PATH, 'w') or
        die("Could not open ".TOKEN_STORE_PATH."\n");
    foreach (split("\n", $contents) as $line) {
        list($timestamp, $request_token, $verifier,
            $access_url) = split("\|", trim($line));
        if ($token == $request_token) {
            $access_data = array("oauth_token" => $request_token,
                                 "oauth_verifier" => $verifier,
                                 "access_url" => $access_url,
                                );
            continue;
        }
        fwrite($f, $line."\n") or
            die("Error: Could not write to ".TOKEN_STORE_PATH."\n");
    }
    fclose($f);
    return $access_data;
}

function procure_access_token($token, $verifier, $access_url) {
    try {
        $oauth = new OAuth(CONSUMER_KEY, CONSUMER_SECRET,
            OAUTH_SIG_METHOD_HMACSHA1, OAUTH_AUTH_TYPE_URI);
        $oauth->enableDebug();
        $oauth->setToken($token, $verifier);
        return $oauth->getAccessToken($access_url);
    } catch(OAuthException $E) {
        die(print_r($E));
    }
}

function remove_outdated_req_tokens($ttl) {
    $contents = file_get_contents(TOKEN_STORE_PATH) or
        die("Could not open ".TOKEN_STORE_PATH."\n");
    $f = fopen(TOKEN_STORE_PATH, 'w') or
        die("Could not open ".TOKEN_STORE_PATH."\n");
    foreach (explode("\n", $contents) as $line) {
        list($timestamp, $token, $verifier,
            $access_url) = split("\|", trim($line));
        if ((time() - (int) $timestamp) > REQ_TOKEN_TTL) {
            continue;
        }
        fwrite($f, $line."\n") or
            die("Error: Could not write to ".TOKEN_STORE_PATH."\n");
    }
    fclose($f);
}


// main
if (!file_exists(TOKEN_STORE_PATH)) {
    $f = fopen(TOKEN_STORE_PATH, 'w') or
        die("Error: Could not write token database");
    fclose($f);
}
if (isset($_POST['oauth_token']) &&
    isset($_POST['oauth_verifier']) &&
    isset($_POST['access_url'])) {
        register_request_token($_POST['oauth_token'],
            $_POST['oauth_verifier'], $_POST['access_url']);
} elseif (isset($_GET['oauth_token']) && isset($_GET['oauth_verifier'])) {
    $access_data = seek_n_destroy_req_token($_GET['oauth_token']);
    if ($access_data) {
        if (trim($access_data['oauth_verifier']) != trim($_GET['oauth_verifier'])) {
            die("Error: Verifier mismatch\n");
        }
        $credentials = procure_access_token($access_data['oauth_token'],
            $access_data['oauth_verifier'], $access_data['access_url']);
        echo "OAuth token: ".$credentials['oauth_token'];
        echo "OAuth token secret: ".$credentials['oauth_token_secret'];
    } else {
        echo "Error: Requested token not found\n";
    }
}
remove_outdated_req_tokens(REQ_TOKEN_TTL);
?>
