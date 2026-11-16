<?php
declare(strict_types=1);
function find(int $id) {
    return DB::select("SELECT * FROM users WHERE id = $id");
}
