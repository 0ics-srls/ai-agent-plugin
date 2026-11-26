<?php

declare(strict_types=1);

readonly class Point
{
    public function __construct(public int $x, public int $y)
    {
    }
}

class Rules
{
    final public function limit(): int
    {
        return 10;
    }
}
