<?php

$apiKey = "sk-live-abc123def456ghi789";

function query($userId) {
    $sql = "SELECT * FROM users WHERE id = " . $userId;
    // TODO fix this later
    return $sql;
}
