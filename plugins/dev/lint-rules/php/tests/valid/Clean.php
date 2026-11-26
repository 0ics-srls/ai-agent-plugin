<?php

declare(strict_types=1);

class Clean
{
    public function store(CreateUserDTO $dto): void
    {
        Log::debug('creating user', ['email' => $dto->email]);
        $hash = Hash::make($dto->password);
        DB::select('SELECT * FROM users WHERE id = ?', [$dto->id]);
    }
}
