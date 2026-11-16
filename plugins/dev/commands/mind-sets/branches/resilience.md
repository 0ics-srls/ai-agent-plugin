# Resilience

For a program that calls something outside its own process: a database, a service, a queue, a file
share.

---

1. **Every call outside the process has a timeout**, and the timeout is configuration.

2. **A transient failure is retried a bounded number of times, with exponential backoff and jitter**,
   and only for an operation that is safe to repeat: a repeated attempt finds the effect of the first
   one instead of doubling it.

3. **A dependency that keeps failing is cut off by a circuit breaker**: while it is open, calls fail at
   once with a clear error; after the break a trial call decides whether it closes again.

4. **The load on a dependency is bounded** by a limit on concurrent calls to it.

5. **A call outside the process is awaited with a deadline**, and its result reaches the rest of the
   code as a signal (code principles 4.7, 4.8).
