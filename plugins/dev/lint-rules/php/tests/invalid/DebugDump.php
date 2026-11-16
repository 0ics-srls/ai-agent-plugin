<?php
declare(strict_types=1);
function debug($user, $request) {
    var_dump($user);
    dd($request->all());
}
