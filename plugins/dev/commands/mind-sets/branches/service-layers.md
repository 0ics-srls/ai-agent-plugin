# Service Layers

For a service that keeps data and exposes it. It applies the principles of structure (principles §3)
to that shape.

---

1. **Four layers, and every reference goes one way only:**

   | Layer | Holds | Depends on |
   |---|---|---|
   | **Core** | the contracts: the generic ones of the base (entity, repository of an entity, unit of work, query and page, error codes) and the interfaces of each feature. A Core contract names no entity: the generic ones take the entity as a type parameter, a feature's speaks in identifiers, values and records. No type of the storage technology appears in them | none of the project's own modules (external packages are allowed) |
   | **Db** | the entities, with their storage mapping; the implementation of the Core data contracts, written once for every entity; the migrations. The layer exists to hide what is internal to the storage — its context, its sets, its connection | Core |
   | **Domain** | the business logic, working through the Core contracts; the operations every entity shares, written once | Db |
   | **Api** | the transport: the endpoints every entity gets, written once, and each feature's own; status codes | Domain |

   No reference goes the other way.

2. **The base of a service** is what every entity repeats: create, read, update and delete; query with
   filter, sort and page; the unit of work that writes several changes at once; optimistic
   concurrency; the translation of errors. A new entity costs one declaration per layer.

3. **Each layer does only its own job.** Business logic sits in Domain, not in the transport and not
   in the data access.
