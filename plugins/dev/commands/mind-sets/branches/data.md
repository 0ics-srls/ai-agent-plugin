# Data

For a program that keeps data in a storage.

---

1. **One operation, one commit.** An operation that changes several things commits once: all of it or
   none of it.

2. **A constraint the storage enforces is a domain error, not a crash.** A unique key, a foreign key,
   a concurrency token: when the storage rejects a write, the rejection is translated into the domain
   error it means ("conflict"), not left to surface as an unexpected failure. Checking first and
   writing after does not replace this: between the two, someone else can write.

3. **A value that must be unique is normalized before the constraint sees it**, so that two spellings
   of the same value (case, surrounding spaces) are the same value.

4. **Data is validated on the way in, not on every read.** What the storage returns was valid when it
   was written; reading it does not re-run the input rules, and a rule that changes later does not make
   existing rows unreadable — changing the rule is a migration.

5. **An entity is identified by its identity**, not by the values of its fields: two reads of the
   same row are the same entity, two rows with equal fields are not.

6. **The storage is as is** (code principles 3.5): tables and columns too.

7. **A list is read in a bounded amount, in one round trip.** Every list has a page size with a
   maximum; related data comes with the same query rather than one query per row; the columns lists
   filter and sort on are indexed.

8. **User values reach a query only as parameters**; a dynamic column or table name comes from a fixed
   list.

9. **A transaction holds only the writes**: the data is prepared before it opens, and calls to other
   services happen outside it.

10. **Time is stored as an instant in UTC**, with its offset where the local time matters, and
    converted to a time zone only at the edge that shows it.

11. **Caches and buffers are bounded**: every cache has a size limit and an expiry, every queue a
    capacity.

12. **The schema changes through versioned migrations**, kept with the code and applied by an explicit
    step of the deploy, before the new version starts, so that several instances never race on it.

13. **Every schema change works with the version already running**: expand (add the new shape),
    migrate the data, switch the code, contract (remove the old shape) in a later release.
