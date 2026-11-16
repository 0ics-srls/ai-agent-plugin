# Service Layers

For a service that keeps data and exposes it. It applies the principles of structure (principles §3)
to that shape.

---

1. **Four layers, and every reference goes one way only:**

   | Layer | Holds | Depends on |
   |---|---|---|
   | **Core** | the contracts: the generic ones of the base (entity, repository of an entity, unit of work, query and page, error codes) and the interfaces of each feature. A Core contract names no entity: the generic ones take the entity as a type parameter, a feature's speaks in identifiers, values and records. No type of the storage technology appears in them | none of the project's own modules (external packages are allowed) |
   | **Db** | the entities, with their storage mapping; the implementation of the Core data contracts, written once for every entity; the migrations | Core |
   | **Domain** | the business logic, working through the Core contracts only, never through the storage implementation; the operations every entity shares, written once | Db |
   | **Api** | the transport: the endpoints every entity gets, written once, and each feature's own; status codes | Domain |

   No reference goes the other way. A layer does not reach past the one it depends on to do that
   layer's job.

   What the references cannot forbid — a layer using the types of the storage technology that reach
   it through the layer below — a test of the architecture forbids, in the unit run.

2. **The base of a service** is what every entity repeats: create, read, update and delete; query with
   filter, sort and page; the unit of work that writes several changes at once; optimistic
   concurrency; the translation of errors. A new entity costs one declaration per layer.

3. **Each layer does only its own job.** Business logic sits in Domain, never in the transport or in
   the data access; the transport never talks to the storage.
