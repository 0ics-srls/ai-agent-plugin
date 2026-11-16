<?php

$apiKey = getenv("API_KEY");

function query($userId) {
    $sql = "SELECT * FROM users WHERE id = ?";
    // TODO(#123): revisit connection pooling
    return $sql;
}
