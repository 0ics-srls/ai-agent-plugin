namespace App;

public class Rules { public virtual int Limit() => 10; }

public class StrictRules : Rules { public sealed override int Limit() => 5; }

public static class Helpers { }

public abstract class Base { }

// Sealed on the owner's request: instances are compared by reference in a cache key.
// ast-grep-ignore: no-sealed-class
public sealed class CacheKey { }
