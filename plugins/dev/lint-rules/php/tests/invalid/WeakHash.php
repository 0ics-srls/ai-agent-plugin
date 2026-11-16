<?php
declare(strict_types=1);
function hashPw(string $password): void {
    $a = md5($password);
    $b = sha1($password);
}
