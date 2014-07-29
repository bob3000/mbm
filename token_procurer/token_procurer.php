<?php
define('REQ_TOKEN_TTL', 86400);  // one day lifetime
define('TOKEN_STORE_PATH', '/tmp/tokens.db');

function register_request_token($token, $verifier) {
    $f = fopen(TOKEN_STORE_PATH, 'a') or
        die("Could not open ".TOKEN_STORE_PATH."\n");
    $entry = time().":".$token.":".$verifier."\n";
    if (!fwrite($f, $entry)) {
        die("Error: Could not write to ".TOKEN_STORE_PATH."\n");
    }
    fclose($f);
}

function seek_n_destroy_req_token($token) {
    $found_token = false;
    $contents = file_get_contents(TOKEN_STORE_PATH);
    $f = fopen(TOKEN_STORE_PATH, 'w') or
        die("Could not open ".TOKEN_STORE_PATH."\n");
    foreach (split("\n", $contents) as $line) {
        list($timestamp, $request_token, $verifier) = split(":", trim($line));
        if ($token == $request_token) {
            $found_token = true;
            continue;
        }
        fwrite($f, $line."\n") or
            die("Error: Could not write to ".TOKEN_STORE_PATH."\n");
    }
    fclose($f);
    return $found_token;
}

function procure_access_token($request_token, $verifier) {
    echo "found\n";
}

function remove_outdated_req_tokens($ttl) {
    $contents = file_get_contents(TOKEN_STORE_PATH) or
        die("Could not open ".TOKEN_STORE_PATH."\n");
    $f = fopen(TOKEN_STORE_PATH, 'w') or
        die("Could not open ".TOKEN_STORE_PATH."\n");
    foreach (explode("\n", $contents) as $line) {
        list($timestamp, $token, $verifier) = split(":", trim($line));
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
if (isset($_POST['oauth_token']) && isset($_POST['oauth_verifier'])) {
    register_request_token($_POST['oauth_token'], $_POST['oauth_verifier']);
} elseif (isset($_GET['oauth_token']) && isset($_GET['oauth_verifier'])) {
    if (seek_n_destroy_req_token($_GET['oauth_token'])) {
        procure_access_token($_GET['oauth_token'], $_GET['oauth_verifier']);
    } else {
        echo "Error: Requested token not found\n";
    }
}
remove_outdated_req_tokens(REQ_TOKEN_TTL);
?>
