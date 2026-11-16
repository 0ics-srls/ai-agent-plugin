# Security

For a system exposed to callers it does not control: the internet, other organizations, users outside
the team.

---

1. **Every endpoint requires an authenticated caller**; a public endpoint is declared public, one by
   one.

2. **An endpoint receives the caller's identity** from the authentication service, already verified.

3. **Traffic is encrypted** (TLS), and the server tells clients to stay on the encrypted channel.

4. **The load the system accepts is bounded** by a rate limit.

5. **Being authenticated is not being allowed.** What a caller may do is checked on the server, for every
   operation and on the record it touches; a refusal is a domain error like the others.
