# Operations

For a program that runs as a process others depend on.

---

1. **Logs go to files.** The console is only one more sink of the same structured logger (code
   principles 4.9). Only the entry point knows the logger's implementation. Levels and sinks live in
   configuration. If you can't see it in the logs, it's not happening.

2. **Every build has a unique version, and the running program reports it.** After a deploy you can
   verify that the right code is running.

3. **The program reports its state**: a liveness check (the process works) and a readiness check (its
   dependencies answer), plus traces and metrics that follow a request across services.

4. **Shutdown is orderly**: on stop, the program stops accepting work, lets the work in flight finish
   or cancels it through its cancellation signal, and releases its resources.
