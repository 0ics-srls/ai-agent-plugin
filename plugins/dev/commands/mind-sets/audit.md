---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "The cards of the code audit — one per rule of the mindsets that is verified by reading the code: the rule it quotes, the defect, where the tool points, how it is found on a project of thousands of files, the questions, what is not a violation, the confirmation and the gravity. Read by /dev:x-audit-code: the agent reads the map against them, and confirms by reading only where it points."
---

# The code audit — the cards

One card for each rule of the mindsets that is verified by reading the code. Each card says:
- **Rule**: the text of the mindset, with its file and section; it is what the report quotes.
- **The defect**: what is looked for, in one sentence.
- **Where to look**: the facts the tool gives; they say where to read, never a verdict.
- **At scale**: how it is found on the whole project, from facts computed on all of it.
- **The questions**: what the agent decides by reading, one question at a time, with the facts in hand.
- **Not a violation**: the cases that have the shape of the defect and are not one.
- **Confirmation**: the evidence written for the problem to enter the report.
- **Gravity**: `grave` (it already breaks a behaviour, or it will at the next change) or `da correggere`.

**Nothing from memory.** Every statement of a confirmation cites the code it comes from, read in that
session:
- the project's code, with `@code-nav-local`;
- the code of a dependency, in the version the project references, with `@code-nav-external` or in its
  source;
- the line, and the query with its result.

What the agent «knows» about a framework is not evidence: a statement without the code that shows it
does not enter the report.

**A project not made with the set.** The rules of the mindsets are the measure; the structure they
measure is the project's own. The map derives the architecture the project gave itself from its
structure, its documents and the Memory Bank's `systemPatterns.md` (which `/dev:j-new-project` writes for an
existing project too). The code says the real one, and the problem is where the two do not match: the
method of reflexion models. The layers of `service-layers.md` are the guide for the projects made with
the set, not a name demanded of somebody else's project.

The form in the project's language (the serializer of C#, the logger of Rust…) is the one of the overlay
`j-settings.md` names: a card has no language, like the mindsets.

---

## The facts: what the tool gives

Computed, never judged. Each one only says «look here».

| Fact | From | What it says |
|---|---|---|
| **F-cap** | the description of the project, written by the agent module by module | the capabilities of each module, said by what they do (principles 2.1): «converts an amount into another currency», not «CurrencyHelper» |
| **F-copy** | the copy detector (tree-sitter) | similar fragments of code; mostly they are not copies, or harmless ones: a hint only |
| **F-nav** | `@code-nav-local` (LSAI) | the definition, the callers, the callees, the implementations, the hierarchy, the uses of a symbol |
| **F-ref** | the project files and the imports | who refers to whom among projects, packages and modules |
| **F-hist** | git | the files and the methods changed together; a copy changed alone |
| **F-oo** | the parser | overrides that are empty or only throw; type tests; the same switch on the type in several places; private members used from outside |
| **F-cx** | lizard | where the complexity concentrates |
| **F-conf** | the build and configuration files | serializers, loggers, package versions, options |

A fact never enters the report. The violation of the rule does, with the evidence read.

---

## How the audit works on a large project

From the top down:

1. **The map, deterministic, in seconds.** The modules and folders, who depends on whom (F-ref), the
   *shape* of each module: its types and functions with their signatures (F-nav, the parser), without
   reading the bodies. The sibling folders with the same skeleton, and the missing common module, are
   already visible here.
2. **The capabilities of each module** (F-cap). The agent writes them from the module's shape, in
   blocks of modules: the cost follows the number of modules, not of lines. Out of it comes the table
   capability × module, which is also the description of the project in the report.
3. **The facts of every card, computed on the whole project**: the edges against the layers, the switches
   on the same set of cases, the overrides that refuse the base, the empty catches, the symbols without
   callers, the similar code, the complexity, the history. None is a verdict: each says where to read.
4. **The candidates, from the map.** The agent reads the map, the capabilities and the facts against
   the cards, makes the searches each card's **At scale** line names on the whole project, and writes
   what they point at, with its places. A card with nothing pointing at it has no candidate.
5. **The confirmation by reading**, module by module: the places of the candidates opened once, for
   every card they concern, with LSAI and the cards' questions. Two or three members of a family are
   read, not all of them. On a project too large for one session, the command splits this reading into a
   Step plan and executes it itself.
6. **The report per family**: «the flight model is written in 12 maps (list); no shared module; the
   stall fix is missing in 3 (commits); the differences are data of the map». One line of work, not a
   hundred fragments.

---

## A. Duplication and reuse

### A1. DRY: the same knowledge, or the same subsystem, written in several places
- **Rule**: `code-principles.md` 1.2 «The same rule in several places, which must change together, is written once. Two things that look alike but change for different reasons are not the same rule»; `principles.md` 2.1 «A capability is implemented once … A second implementation is a defect»; `principles.md` 3.2 and `code-principles.md` 1.3 for what every entity repeats; in a game, `branches/game.md` 1 and 8 (a level is loaded under the world; the content is data).
- **The defect**, by weight:
  1. **a whole subsystem rewritten for each unit**: the game engine for each map, the complete service for each customer, the CRUD for each entity; the units should be data, or cases, over one implementation;
  2. **a capability written twice**, with different names and shapes (retry with backoff, currency conversion, normalizing a text);
  3. **a rule copied** into several functions: a condition on our data, a formula.
- **Where to look**, on the whole project:
  - the map: sibling folders or modules with the same skeleton (the same roles of types, the same signatures) and no common module they all depend on (F-ref);
  - the table capability × module (F-cap): a capability present in N modules is a **family**;
  - the history (F-hist): a commit that makes the same fix in N places (they must change together); a fix present in some members and not in others (a divergence);
  - the textual copies (F-copy), only as one more hint, for point 3.
- **At scale**: the map's sibling groups, the families of the capability table, the similar functions across modules and the history of the methods they share, computed on the whole project.
- **The questions**, per family, reading two or three members with LSAI:
  1. **What does each one do?** What it produces: the contract, the cases, the defaults, the errors.
  2. **How do they differ, and why?** Are the differences *data* of the unit (the relief, the wind, the airports of a map; the fields of an entity) or truly different *behaviour*? Data → the implementation is written once and the units become data. It is the part that decides.
  3. **Must it change together?** Does it depend on a concept internal to the project (yes) or does it face external systems that each evolve on their own (no: a platform variation)?
  4. **Is there already an owner** (a common module, a base, a library of the project) that the family ignores?
- **Not a violation**:
  - an adapter for each independent external system (a database, an operating system, a provider);
  - calls to the same function with different arguments: that is already the reuse;
  - idioms, boilerplate the language imposes, the usage protocol of an API;
  - formulas in the domain's notation; data written as code;
  - things that look alike today but change for different reasons;
  - a copy the project keeps on purpose and decided so (a test that pins it, a decision in the Memory Bank).
- **Confirmation**: the members of the family (the complete list, from the map), the two or three read with file:lines, what each one produces, the differences with their nature (data or behaviour), the commit that shows them changed together or diverging, the owner that is missing or ignored.
- **Gravity**: `grave` when the members already diverge without meaning to (a fix, a check, a case present in some and not in others): one unintended divergence in two is a bug (Juergens et al.), and the line of the report says which members have it and which do not. `da correggere` otherwise, ordered by the number of members.

### A3. A value without a single home
- **Rule**: `code-principles.md` 3.6: «Every value has one home … every place that needs the value reads that constant».
- **The defect**: the same value with a meaning (a threshold, a limit, a role name, a key) is written as a literal in several places, or it is in the code while it should be in configuration.
- **Where to look**: F-copy on the literals; F-nav on the constants that already exist.
- **At scale**: the literal with the same meaning in N modules, computed on everything (F-copy on the literals): the family is the value.
- **The questions**: is it the same meaning or only the same number? Is there already a constant or a configuration key that names it? Does it change with the environment, and then belong in configuration?
- **Not a violation**: 0, 1, the length of a platform buffer; two values equal by chance with different meanings; the data of a test.
- **Confirmation**: the places with the value, the common meaning, the constant that exists (or is missing).
- **Gravity**: `da correggere`; `grave` when the places already have different values for the same meaning.

### A4. The platform's mechanism rewritten by hand
- **Rule**: `principles.md` 1.1: «Each goal is reached with what the platform already provides … Code is written by hand only for what the platform does not provide».
- **The defect**: code written by hand for what the framework, the library or the platform already give: a DI container, a validation, a retry, a serializer, a pagination.
- **Where to look**: F-cap; F-conf (what the project already references); the library's documentation.
- **At scale**: from the capability table, each capability compared with what the project's dependencies (F-conf) and the platform offer.
- **The questions**: does the platform or a dependency of the project offer this capability? Does the hand-made version do something that one does not, and say so?
- **Not a violation**: a thin adapter over the platform's mechanism; a case the platform does not cover, written as such.
- **Confirmation**: the hand-written code (file:line), and the code of the mechanism that already offers it, in the version of the dependency the project references, read with `@code-nav-external` or in the package's source: the type or the function, with its path.
- **Gravity**: `da correggere`.

## B. Structure and boundaries

### B1. Dependencies go one way only
- **Rule**: `principles.md` 3.3: «a consumer depends on an interface … no dependency points back up»; for the projects made with the set, `branches/service-layers.md` 1: «every reference goes one way only».
- **The defect**: a reference against the direction the project gave itself; a cycle among modules; the type of a detail (the storage, the network) reaching the code that decides.
- **Where to look**: F-ref (the references of the projects, the imports); the types used beyond the declared references (F-nav).
- **At scale**: the map derives the layers, or the modules, of the project and their direction (from the structure, the documents, `systemPatterns.md`); the graph of the references on the whole project shows the edges against that direction and the cycles. Every edge is a place to read, without searching for it.
- **The questions**: what is the direction the project gave itself, and where is it derived from? Does this reference contradict it? Is it a type of a contract (allowed) or of an implementation?
- **Not a violation**: the composition root, which knows everything to compose; a test that refers to what it proves; a project without layers, which the description of the project says as such (logic in the wrong place stays B2).
- **Confirmation**: the project's direction with its source (the structure, the document, the line of the Memory Bank), the reference or the import that contradicts it (file:line).
- **Gravity**: `grave` for a cycle; `da correggere` otherwise.

### B2. Each layer does only its own job
- **Rule**: `branches/service-layers.md` 3: «Business logic sits in Domain, never in the transport or in the data access; the transport never talks to the storage».
- **The defect**: a business rule in the endpoint or in the repository; an endpoint that talks to the storage.
- **Where to look**: F-nav (the callees of an endpoint, of a repository); F-cx (complexity concentrated in a transport layer).
- **At scale**: the paths in the call graph from an endpoint down to the storage, skipping the layer in between.
- **The questions**: does this code decide something of the domain (a condition on our data, a transition) or does it only translate? Does it call the storage skipping the layer below?
- **Not a violation**: the validation of the input at the boundary (its place, principles 4.3); the mapping of the errors.
- **Confirmation**: the decision in the wrong place (file:line), the layer it belongs to.
- **Gravity**: `da correggere`.

### B3. One part reaches into the insides of another
- **Rule**: `principles.md` 3.4: «hidden internals … One part cannot break another»; `code-principles.md` 4.4: «Nobody reads another object's internals».
- **The defect**: code that uses the private, or implementation, members of another object or module; an internal type exposed so that somebody can reach it.
- **Where to look**: F-oo (members private by convention used from outside, in the languages where private is a name); F-nav (uses of an internal member from another module); `InternalsVisibleTo` towards code that is not a test.
- **At scale**: the uses of an internal member from another module, computed on everything (F-oo, F-nav); family per member.
- **The questions**: is the member part of the contract or of the implementation? Should whoever uses it go through an operation of the owner?
- **Not a violation**: the tests that reach the inside by a declared way (the language provides it); a data type that is its fields.
- **Confirmation**: the use (file:line), the member and its owner.
- **Gravity**: `da correggere`.

### B4. Organized by type instead of by domain
- **Rule**: `principles.md` 3.5: «Organize by domain, not by type … The dumping ground is not: `utils/`, `helpers/`, `common/`, `misc/`».
- **The defect**: a drawer module that holds unrelated things, without a name that says the responsibility.
- **Where to look**: F-cap of the module; F-nav (who uses it and for what).
- **At scale**: the modules whose capabilities (the table) belong to different domains; the name `utils` is only a hint.
- **The questions**: do the capabilities of this module have one responsibility, which the name can say? Whom does each belong to?
- **Not a violation**: a shared library with one responsibility and a name that says it (`money`, `auth/tokens`).
- **Confirmation**: the module, its unrelated capabilities, the domain of each.
- **Gravity**: `da correggere`.

### B5. Dependencies are not injected, the composition does not read
- **Rule**: `principles.md` 3.6: «Dependencies are injected … Each module owns the registration of its own parts, and the composition root reads in ten seconds».
- **The defect**: a service that builds its dependencies or looks them up in a global registry at run time; registrations scattered outside the module that owns them.
- **Where to look**: F-nav (direct constructions of services, accesses to the container); F-oo.
- **At scale**: the constructions of services inside other services and the accesses to the container, from the parser on everything.
- **The questions**: is it a service (behaviour behind a contract) or a value? Should whoever builds it receive it?
- **Not a violation**: building a value or a datum; a declared and registered factory.
- **Confirmation**: the construction or the lookup (file:line), the dependency that should come from the constructor.
- **Gravity**: `da correggere`.

### B6. A datum that carries logic, a service without a contract
- **Rule**: `principles.md` 3.3: «Behaviour lives in services behind interfaces; data carries no logic»; `code-principles.md` 3.1: «the rules that govern its changes live in the domain services — except its state machine».
- **The defect**: an entity or a message with business rules; a service used directly through its concrete class.
- **Where to look**: F-oo (the methods of the entities); F-nav (the concrete types injected).
- **At scale**: the methods of the entities that call services or the storage (F-nav).
- **The questions**: is the method a business rule or the state machine of the entity (which belongs there)? Does the consumer use the contract or the implementation?
- **Not a violation**: the state machine inside the entity that owns the state (code principles 2.1); a constructor that enforces an invariant (2.4).
- **Confirmation**: the method or the dependency (file:line), and the right place.
- **Gravity**: `da correggere`.

---

## C. The design of the objects (SOLID)

### C1. KISS: complexity the problem does not ask for
- **Rule**: `code-principles.md` 1.1 «The simplest solution that works … If it cannot be explained in one sentence, it is too complex»; 4.2 «A function does one thing»; 4.3 «The main path reads top to bottom».
- **The defect**: accidental complexity, that is code more complicated than the problem it solves.
- **Where to look**: F-cx (where it concentrates); F-hist (complex *and* changed often: that is where it costs).
- **At scale**: lizard on everything, crossed with the history: the functions complex *and* changed often are read first; no threshold decides.
- **The questions**:
  1. Can what it does be said in one sentence? If two sentences with an «and» are needed, they are two things (4.2).
  2. Where does the complexity come from? The typical causes are:
     - several things in one function, such as a parameter that chooses disjoint blocks;
     - validation, computation and I/O mixed;
     - levels of abstraction mixed;
     - nesting instead of an early exit (4.3);
     - copied branches;
     - a switch on the type (C3);
     - boolean flags instead of a state (D1);
     - interwoven error handling.
  3. Is the complexity the problem's (an algorithm that is complex) or the code's?
- **Not a violation**: an algorithm complex by nature, written clearly; a table of data; a generated parser. The number of lizard alone is never a problem.
- **Confirmation**: the function (file:lines), the cause with the lines that show it, the sentence that should describe it.
- **Gravity**: `da correggere`.

### C2. SRP: a type with several reasons to change
- **Rule**: `code-principles.md` 1.4: «A type … has one reason to change, judged by WHO asks for the changes, whatever its length».
- **The defect**: a type that serves two requesters (the invoicing and the reporting) and changes for the one and for the other.
- **Where to look**: F-oo (groups of methods that share no field); F-hist (methods of the same type changed by commits for different reasons); F-cap.
- **At scale**: the types with groups of methods that share no field and are changed by different commits.
- **The questions**: who asks for the changes to this type? Are they two different whos? Do the groups of methods serve different responsibilities, or are they faces of the same one?
- **Not a violation**: a long type with one responsibility; a type with only static methods of one family (a module of pure functions).
- **Confirmation**: the two groups, with their requesters and the commits that show it.
- **Gravity**: `da correggere`.

### C3. OCP: a new case touches many places
- **Rule**: `code-principles.md` 1.5: «A new case is new code behind the contract; the code using the contract is not edited»; §2 intro.
- **The defect**: the same switch or if-else on the type, or on the same enum of kinds, repeated in several places: adding a kind means finding them all.
- **Where to look**: F-oo (the same set of cases tested in several places).
- **At scale**: the families of switches on the same set of cases, from the parser on everything.
- **The questions**: do the switches live in an owner (a factory, a registry) or are they scattered? Is the set of cases closed by nature (the days of the week) or does it grow?
- **Not a violation**: a factory or a deserializer, that is the single place that decides by type; an exhaustive switch on a closed set, in one place.
- **Confirmation**: the places of the switch, the common set, what a new case would touch.
- **Gravity**: `da correggere`; `grave` when one place already has a case the others do not.

### C4. LSP: a subtype that does not keep the promise
- **Rule**: `code-principles.md` 1.6: «No override refuses the base (an empty or throw-only body), and no caller type-tests what it receives».
- **The defect**: an override that refuses the base method; a caller that checks the subtype of what it receives; stronger preconditions, undeclared exceptions.
- **Where to look**: F-oo (overrides that are empty or only throw; type tests); F-nav (the base and its callers).
- **At scale**: the overrides that are empty or only throw and the type tests, from the parser, each with its base.
- **The questions**: does the base promise this behaviour (it is not abstract, it is not an optional hook with an empty default)? Is the caller that tests the type the place that decides by type, or ordinary code?
- **Not a violation**: a Null Object; an optional hook the base offers empty; a factory or a boundary that deserializes.
- **Confirmation**: the override or the type test (file:line), the promise of the base (file:line).
- **Gravity**: `da correggere`; `grave` when a caller already receives an exception the base does not declare.

### C5. ISP: a contract larger than its users
- **Rule**: `code-principles.md` 1.7: «Interfaces are small and shaped by their clients; nobody implements no-op methods».
- **The defect**: implementations with methods that are empty or only throw; an interface of which each client uses a different part.
- **Where to look**: F-oo (empty implementations); F-nav (which methods each client uses).
- **At scale**: the empty implementations from the parser; the use per client from F-nav.
- **The questions**: do the clients use disjoint parts? Is the empty method a refusal or a legitimately empty implementation?
- **Not a violation**: a small interface used whole; a double in the tests.
- **Confirmation**: the empty implementations or the use per client.
- **Gravity**: `da correggere`.

### C6. DIP: the code that decides depends on a detail
- **Rule**: `code-principles.md` 1.8: «The code that decides depends on contracts … the details — storage, network, external services, the clock — sit behind them».
- **The defect**: a domain rule that calls the database, the network, the file system, the system clock directly.
- **Where to look**: F-nav (the callees of the domain services); F-ref.
- **At scale**: from the graph: the domain services that reach types of storage, network, file system, clock.
- **The questions**: does this code decide, or coordinate details? Is the detail behind a contract shaped on what the caller needs?
- **Not a violation**: the composition root; an adapter, which is the detail itself.
- **Confirmation**: the call to the detail (file:line) inside the code that decides.
- **Gravity**: `da correggere`.

---

## D. The mechanism of the behaviour

### D1. A state machine nobody wrote
- **Rule**: `code-principles.md` 2.1: «Scattered boolean flags are a state machine nobody wrote down … the state is one value of a closed type and changes only through the transition».
- **The defect**: the state of an entity kept in several flags or strings, changed from different places without a transition.
- **Where to look**: F-nav (who writes the state fields); F-oo.
- **At scale**: the state fields (booleans, strings) written by several methods or several types (F-nav on the writes).
- **The questions**: does what is allowed depend on the state? Does the state change in several places? Is it a closed type with named transitions?
- **Not a violation**: an independent flag that combines with no other; a state machine library used as it says.
- **Confirmation**: the flags or the strings, the places that change them, an illegal combination that can be reached, if there is one.
- **Gravity**: `grave` when an illegal state can be reached; `da correggere` otherwise.

### D2. The same behaviour per kind, branched instead of a strategy
- **Rule**: `code-principles.md` 2.2: «One contract, one implementation per kind, the selection in one place».
- **The defect**: an operation that does different things per provider or format with scattered branches (it ties to C3).
- **Where to look**: F-oo; F-cap.
- **At scale**: the same families as C3.
- **The questions**: is there one selection? Is adding a kind a new file or ten edits?
- **Not a violation**: two kinds, in one place, with no prospect of growth.
- **Confirmation**: the branches, the selection that is missing.
- **Gravity**: `da correggere`.

### D3. A sequence of transformations without names
- **Rule**: `code-principles.md` 2.3: «Each step has a name, one input and one output; the run stops at the first error and says which step failed».
- **The defect**: a stepwise job written as one block, which on an error does not say which step failed.
- **Where to look**: F-cx; F-cap.
- **At scale**: the long stepwise processing functions (F-cx), read first.
- **The questions**: is it a sequence of transformations? Is it known which step fails?
- **Not a violation**: two steps; a linear and clear function.
- **Confirmation**: the block, the steps it holds.
- **Gravity**: `da correggere`.

### D4. An invariant checked in every place instead of at construction
- **Rule**: `code-principles.md` 2.4: «Invariants enforced at construction, when a value has a rule of its own that must hold for its whole life and that several places rely on».
- **The defect**: the same check on a value (a range of dates, an amount with its currency) repeated where it is used (it ties to A1).
- **Where to look**: F-copy; F-nav (the uses of the value).
- **At scale**: the same check on the same type in several places (F-copy with the type).
- **The questions**: is it a rule of the value for its whole life, or only validation of the input (which belongs at the boundary, principles 4.3)?
- **Not a violation**: a field that is only required or limited in length: it is input, at the boundary.
- **Confirmation**: the repeated checks, the type that should enforce them.
- **Gravity**: `da correggere`.

### D5. Rules that change often written as branches
- **Rule**: `code-principles.md` 2.5: «The rules live in a table and the code reads it, instead of branching».
- **The defect**: thresholds, mappings, permissions wired into ifs that change at every request of the customer.
- **Where to look**: F-hist (branches changed often to change a value); F-cx.
- **At scale**: the branches touched by commits that change only a literal (F-hist).
- **The questions**: is what changes the values or the logic?
- **Not a violation**: stable rules; a branch for a truly different case.
- **Confirmation**: the branches, the commits that change them for a value.
- **Gravity**: `da correggere`.

---

## E. Data and types

### E1. Values that change, shared mutable state
- **Rule**: `code-principles.md` 3.1: «Requests, responses, messages and values keep the content they were built with … Shared state is immutable».
- **The defect**: a message or a value modified after its construction; a state shared among threads or requests and modifiable.
- **Where to look**: F-nav (who writes the fields after the construction); F-oo.
- **At scale**: the writes of fields after the construction, on message or value types (F-nav).
- **The questions**: is it a value or an entity (which is modifiable data, 3.1)? Is the state shared?
- **Not a violation**: an entity; a builder.
- **Confirmation**: the write (file:line), the type and who shares it.
- **Gravity**: `grave` for shared mutable state among threads; `da correggere` otherwise.

### E2. An entity copied into an equal shape to cross the layers
- **Rule**: `code-principles.md` 3.2: «An entity crosses the layers as itself; a shape of its own exists for composite data»; `branches/api.md` 4.
- **The defect**: DTOs equal to the entity field by field, with their mapping to keep aligned.
- **Where to look**: F-copy among types; F-nav (the mappings).
- **At scale**: the pairs of types with the same fields and a mapping between them (the parser).
- **The questions**: is the shape equal to the entity, or does it compose several entities or a computed summary?
- **Not a violation**: a composite datum; a shape imposed by an external contract.
- **Confirmation**: the two types, the equal fields, the mapping.
- **Gravity**: `da correggere`.

### E3. A closed set written as strings
- **Rule**: `code-principles.md` 3.3: «A closed set (status, kind, role, error code) is an enumeration or a closed type … Whether a value can be absent is part of its type».
- **The defect**: states, kinds, roles as strings or loose constants; an untyped datum at the boundary.
- **Where to look**: F-nav (comparisons with literals on the same field); F-copy.
- **At scale**: the fields compared with string literals in several places (the parser).
- **The questions**: is the set closed? Is it compared in several places?
- **Not a violation**: a free text; an open external identifier.
- **Confirmation**: the comparisons with the literals, the set.
- **Gravity**: `da correggere`.

### E4. The serialization transforms the names
- **Rule**: `code-principles.md` 3.5: «property names leave and arrive exactly as declared … enumerations as their declared names»; `branches/api.md` 1, `data.md` 6.
- **The defect**: a naming policy (camelCase, snake_case), a rename, an enum serialized as a number, in any serializer: HTTP, messages, files, storage.
- **Where to look**: F-conf (the options of the serializers); F-nav (the rename attributes).
- **At scale**: every place where the project builds a serializer or its options (F-conf, F-nav).
- **The questions**: does every serializer of the project use the overlay's options? Is there a second set of options?
- **Not a violation**: an external contract imposed by a third party, isolated in its adapter and said so.
- **Confirmation**: the option or the attribute (file:line), the serializer that uses it.
- **Gravity**: `da correggere`.

### E5. Serialized data handled by hand
- **Rule**: `code-principles.md` 3.7: «Whatever crosses a boundary serialized … is read into the program's types by a mapper … Walking the generic tree of a format by key, path or index, building one by hand, casting what was read to a type: forbidden»; the language's overlay names its mappers and the forms of the practice.
- **The defect**: data of a file, a message, the configuration, a request or a database row read by key, path or index, or built by hand, where a mapper would read it into a type: a JSON or XML tree walked, a value cast as it is read, a dictionary or a map of a parse passed on, the configuration or the query read by name where it is used, a row read by column. A key mistyped, a field renamed or missing, a value of another type pass the compiler and fail at run time — or yield a default in silence.
- **Where to look**: F-nav, the uses of the generic tree types and of the reading by name the overlay lists (the parse's result, the configuration's indexer, the request's collections, the row's indexer); F-conf, the serialization libraries the project depends on.
- **At scale**: the usages of those APIs on the whole project, grouped by module; one reader that maps into a type is one place, the same reading by key repeated where the data is used is a family.
- **The questions**: does the parsed tree, the dictionary or the raw value leave the reader? Is there a type for the data — and if not, is its shape known? Is a required field checked at the reading, or does its absence travel as a default? Is it data stored or forwarded untouched? Is there a measured need of performance, asked for by the user, said where?
- **Not a violation**: the one reader that maps the tree into types where the language has no mapper (C, Perl, GDScript, a format the library does not cover); data stored or forwarded untouched, as an opaque string or bytes, never read into; the performance exception the user asked for, in one reader, with its comment.
- **Confirmation**: the reading by hand (file:line), where the value goes (the callers, with the query), the type that is missing or that already exists and is not used.
- **Gravity**: `grave` when the hand-read data crosses a function or a layer, or a missing field turns into a default in silence; `da correggere` when the reading by hand stays in one function at the boundary and fails loudly.

### E6. The absence of a value silenced
- **Rule**: `code-principles.md` 3.3: «the type is not silenced: no assertion that a value is there … and no switch that turns the checks off»; the language's overlay names its rules.
- **The defect**: an assertion that a value is there where the language's lint gate cannot refuse it — Dart's `!`, a `!` or `!!` left under an exception that is not the overlay's, a `lateinit` of a test helper moved into production — and every exception the overlay allows used outside its place (a `null!` that is not a navigation property of an EF Core entity).
- **Where to look**: F-nav, the assertions of the language (`!`, `!!`, `unwrap`, `cast`) on the whole project; the lint gate's own report for the languages it covers.
- **At scale**: the usages, grouped by module; the exceptions the overlay allows read one by one.
- **The questions**: where can the value be absent? Is it given at construction, handled, or does the program fail where its absence is known? Is the place one the overlay excepts (the tests' setup, an entity's navigation property)?
- **Not a violation**: what the overlay excepts, in its place; an assertion right after a check the compiler cannot follow, in the same function, with the check quoted.
- **Confirmation**: the assertion (file:line), where the value comes from (with the query), how it can be absent.
- **Gravity**: `grave` when the value can be absent on a path the program takes (a query without its `Include`, a lifecycle not yet run); `da correggere` otherwise.

---

## F. Errors and input

### F1. Domain errors as strings, translated in several places
- **Rule**: `principles.md` 4.1: «The domain reports its failures with codes … the boundary maps them to its own terms once, in one place … A lookup that finds nothing is a result»; `code-principles.md` 3.4; `branches/api.md` 6.
- **The defect**: domain errors as messages; the translation code-to-status made in several places; a «not found» thrown as an exception.
- **Where to look**: F-nav (where the domain's exceptions are born, where the statuses are mapped).
- **At scale**: every place that translates an error into a status or a message (F-nav).
- **The questions**: is there one place that translates? Does a new code without a mapping fail a test?
- **Not a violation**: a programming exception (a null argument).
- **Confirmation**: the places of translation, or the error without a code.
- **Gravity**: `da correggere`.

### F2. A swallowed error
- **Rule**: `principles.md` 4.2: «No error is swallowed silently … the error is recorded once, where it is handled».
- **The defect**: an empty catch, an ignored error, an error logged in several layers.
- **Where to look**: F-oo (catches that are empty or do nothing); F-nav.
- **At scale**: the catches that are empty or do nothing, from the parser on everything.
- **The questions**: is the error handled (and then where is it seen) or lost? Is it recorded once only?
- **Not a violation**: an error ignored with the comment that says why it does not matter.
- **Confirmation**: the place (file:line), what is lost.
- **Gravity**: `grave`.

### F3. Input validated outside the boundary, or several times
- **Rule**: `principles.md` 4.3: «Every rule about incoming data … is stated in one place and checked where the data enters … Code past the boundary trusts the data»; `branches/data.md` 4; `frontend.md` 6.
- **The defect**: the same input rule in several layers; data entering unvalidated; the rule rewritten in the frontend instead of taken from the contract.
- **Where to look**: F-copy; F-nav (the entry points and their callees).
- **At scale**: the entry points (endpoints, commands, handlers) from the graph, and for each where it validates.
- **The questions**: is the check an input rule or an invariant of the value (D4)? Is it at the boundary?
- **Not a violation**: a programming check on a public member (`code-principles.md` 4.5).
- **Confirmation**: the repeated checks, or the entry point without a check.
- **Gravity**: `grave` for an unvalidated entry; `da correggere` for the duplicates.

---

## G. Configuration

### G1. Hidden defaults, unchecked configuration
- **Rule**: `principles.md` 5.1: «No hidden defaults in code: if a required value is missing, the program does not start and says which one».
- **The defect**: a required value with a default in the code; configuration read around instead of in one place validated at the start.
- **Where to look**: F-conf; F-nav (the reads of the configuration).
- **At scale**: every read of the configuration (F-nav on the overlay's configuration API).
- **The questions**: is the value required? If it is missing, does the program start anyway?
- **Not a violation**: a documented default for a value that is truly optional.
- **Confirmation**: the read with the default (file:line).
- **Gravity**: `da correggere`.

---

## H. Writing

### H1. Code nobody uses
- **Rule**: `code-principles.md` 4.10: «Code that nothing uses is deleted».
- **The defect**: functions, types, branches never called.
- **Where to look**: F-nav (no caller); F-ref.
- **At scale**: the symbols without callers from the graph, the entry points removed.
- **The questions**: is it an entry point (an endpoint, a command, a registered handler, a call through reflection or a generator)? A public API of a library?
- **Not a violation**: an entry point; the API of a library; code reached by a generator. The index may not see generated code: it is confirmed as `code-navigation.md` says.
- **Confirmation**: the symbol, the query that finds no caller, why it is not an entry point.
- **Gravity**: `da correggere`.

### H2. A name that says something else
- **Rule**: `code-principles.md` 4.1: «Names say what they hold».
- **The defect**: a name that lies: `trimmed` that is not trimmed, `isValid` that modifies, `getX` that writes.
- **Where to look**: the reading of the blocks, while the other cards are decided.
- **At scale**: no search: it is noticed while the places of the other cards are read.
- **The questions**: does the name say what the code does?
- **Not a violation**: a short name in a short scope; a choice of style.
- **Confirmation**: the name and the line that belies it.
- **Gravity**: `da correggere`. Only when the name deceives, never for taste.

### H3. Asynchrony broken halfway
- **Rule**: `code-principles.md` 4.6: «A function that calls an asynchronous operation is itself asynchronous and awaits it; cancellation is passed through every call».
- **The defect**: a blocking wait on an asynchronous operation; the cancellation lost halfway down the chain; an operation started and never awaited.
- **Where to look**: F-nav (the call chains); the overlay's analyzers find a part of it (that part belongs to the gate).
- **At scale**: the chains of asynchronous calls from the graph, with a blocking wait along the chain.
- **The questions**: is the chain asynchronous up to the top? Does the token reach the I/O?
- **Not a violation**: the entry point the platform wants synchronous.
- **Confirmation**: the place (file:line), the chain.
- **Gravity**: `grave` for a blocking wait on a server; `da correggere` otherwise.

### H4. Waiting for time instead of the event
- **Rule**: `code-principles.md` 4.7, 4.8: «Every wait is a wait for an event … Polling is for a third party that offers no signal»; `branches/frontend.md` 9; `game.md` 7.
- **The defect**: a sleep in the code; a loop that checks and sleeps; polling towards a component of ours that has a signal.
- **Where to look**: F-nav on the waiting APIs of the language (the overlay names them).
- **At scale**: the calls to the waiting APIs of the language (F-nav), family per component.
- **The questions**: does whoever makes the thing happen offer a signal? Is it a third party without a signal, and then is the polling one only, configured?
- **Not a violation**: a backoff; a schedule; the polling towards a third party without events, in one component.
- **Confirmation**: the wait (file:line), the signal that exists.
- **Gravity**: `da correggere`.

### H5. Logs that do not go through the logger
- **Rule**: `code-principles.md` 4.9: «Every log entry is a constant message template with named values … a direct write to the console … is a defect»; `branches/operations.md` 1.
- **The defect**: messages built by concatenation; secrets or personal data in the logs; direct writes to the console (the ast-grep pack finds a part of them: that part belongs to the gate).
- **Where to look**: F-nav on the calls to the logger.
- **At scale**: the calls to the logger (F-nav).
- **The questions**: is the message a constant template? Does it carry a secret or a personal datum?
- **Not a violation**: the output of a command-line program, which is its product, written as the overlay says.
- **Confirmation**: the call (file:line).
- **Gravity**: `grave` for a secret in the log; `da correggere` otherwise.

---

For the cards in tables that follow the same holds: the facts are computed on the whole project (the
queries, the transactions, the out-of-process calls, the scenes), the places they point at are read, and
the family goes into the report.

## I. Data and storage (`branches/data.md`, when the project has it)

| Card | Rule | The defect | The questions | Gravity |
|---|---|---|---|---|
| I1 | data 1 | an operation that makes several commits | must the steps succeed or fail together? | grave |
| I2 | data 2 | a constraint of the storage that becomes a crash; «check, then write» in place of the constraint | does the violation of the constraint become a domain error? | da correggere |
| I3 | data 3 | a unique value not normalized before the constraint | do two spellings of the same value pass? | da correggere |
| I4 | data 7 | a list without a limit; one query per row (N+1); filters and orderings without an index | is the list paginated? do the related data arrive in the same query? | da correggere |
| I5 | data 8 | a value of the user concatenated into a query; a dynamic column name not taken from a fixed list | does the value arrive as a parameter? | grave (it goes to the security audit too) |
| I6 | data 9 | calls to other services inside a transaction | does the transaction hold only the writes? | da correggere |
| I7 | data 10 | time saved in local time | is it a UTC instant? | da correggere |
| I8 | data 11 | caches or queues without a limit | is there a limit and an expiry? | da correggere |
| I10 | data 5 | two entities compared by the values of their fields instead of by identity | does the equality use the identity? | da correggere |
| I9 | data 12-13 | the schema changed outside a migration; a migration that breaks the version in production | is every change a versioned migration? does it go through expand, migrate, switch, contract? | grave |

For each: where to look is F-nav (the queries, the transactions) and F-conf (the mapping); not a
violation is what the project's overlay does in another declared way (for instance the pagination by key);
the confirmation is the line.

---

## J. API (`branches/api.md`)

| Card | Rule | The defect | Gravity |
|---|---|---|---|
| J1 | api 2 | a request or response type written by hand in the client; the OpenAPI document not kept equal by a test; an operation without a name, a type not exact | da correggere |
| J2 | api 3, frontend 3 | a list loaded whole and filtered by the client; several list operations per entity | da correggere |
| J3 | api 5 | an error format different for one endpoint, or for the framework's errors; internal details (stack, SQL) in the response | grave for the internal details |
| J4 | api 7 | a published contract changed breaking the consumers, without a version | grave |

---

## K. Resilience (`branches/resilience.md`)

| Card | Rule | The defect | Gravity |
|---|---|---|---|
| K1 | resilience 1, 5 | an out-of-process call without a timeout or without a deadline | da correggere |
| K2 | resilience 2 | a retry on an operation that cannot be repeated without duplicating the effect; a retry without a limit or without a backoff | grave for the duplicated effect |
| K3 | resilience 3, 4 | a dependency that fails without a breaker; concurrent load without a limit | da correggere |

---

## L. Operation (`branches/operations.md`)

| Card | Rule | The defect | Gravity |
|---|---|---|---|
| L1 | operations 2 | the running version not readable | da correggere |
| L2 | operations 3 | no liveness or readiness check; a readiness that does not look at the dependencies | da correggere |
| L3 | operations 4 | the shutdown that does not complete or cancel the work in progress | da correggere |

---

## M. Frontend (`branches/frontend.md`)

| Card | Rule | The defect | Gravity |
|---|---|---|---|
| M1 | frontend 1 | a type of the API written by hand instead of the generated client; the generated client modified | da correggere |
| M2 | frontend 4 | the data of the API copied into the components instead of read from the layer that loaded them | da correggere |
| M3 | frontend 5 | an error of the API the user does not see; an unexpected error without a way out | grave |
| M4 | frontend 6 | the rules of the contract rewritten in the form instead of taken from the contract | da correggere |
| M5 | frontend 7 | organized by type (global `components/`, `services/` folders) instead of by feature | da correggere |
| M6 | frontend 8 | addresses and environment settings in the code | da correggere |

---

## N. Game (`branches/game.md`)

| Card | Rule | The defect | Gravity |
|---|---|---|---|
| N0 | game 1 | the main scene that does not compose; services built in the scenes; world and interface mixed | da correggere (B5) |
| N1 | game 2 | the rules of the game in the nodes of the scene instead of in objects of their own | da correggere |
| N2 | game 3 | a child that reaches a sibling or a node by absolute path; an event that does not go up as a signal | da correggere |
| N3 | game 4 | a global singleton that changes data of other parts | da correggere |
| N4 | game 5 | scattered flags in place of the state machine of a character | da correggere (D1) |
| N5 | game 6 | physical keys read in the logic instead of named actions | da correggere |
| N6 | game 7 | a delay counted in frames; a movement that assumes the frame rate | da correggere |
| N7 | game 8 | balance numbers in the code instead of in the data | da correggere |
| N8 | game 9 | loads from disk on the frame's path | da correggere |
| N9 | game 10 | a save without a version, or that carries code, or not validated | grave |

---

## O. The tests

These cards judge the *design* of the suite, which no tool judges. Whether a thing is covered by a test is
not read here: the tools measure it.

| Card | Rule | The defect |
|---|---|---|
| O1 | testing 3.2, 3.4 | the code that talks to the storage proved only with a double of the storage |
| O2 | testing 4.2, 4.3 | a mock of the calls internal to a unit; a double of a pure function |
| O3 | testing 5.1 | the same preparation copied from test to test instead of in a shared builder (the DRY of the tests) |
| O4 | testing 1.2 | a test without an assertion |
| O5 | testing 4.4, 4.5, 7.6 | a test that depends on the clock, on the order, or that waits for time instead of the event |
| O6 | testing 1.3, 1.4, 1.5, 5.2 | a name that does not say the behaviour; several actions in one test; a test that goes through the inside; a preparation that says more than what is needed |
| O7 | testing 3.1, 3.3 | the logic proved through the transport instead of with the doubles of its contracts; an end-to-end test with a double of the storage |

---

## The rules of the overlays

An overlay says how a rule is written in the language: it is the *form* of a card, not a new card.
`aspnetcore.md` §2 («Services resolve nothing from `IServiceProvider` at run time») is B5 in C#;
`language.md` §6 of C# (the JSON options in one place) is E4. The agent reads the cards with the
project's overlay beside them. A rule of an overlay that falls under no card (for instance C# «Native AOT
only on explicit request») is a choice of stack, decided in the project: it is not verified.

## What has no card, and why

| Rule | Why not here |
|---|---|
| principles 2.2, 2.3, 3.1 | they are the way of working (search first, decide the structure first): they show in the tasks, not in the code |
| principles 5.2, data 8, branch security | the security audit, separate |
| principles 6.1 (zero warnings), lint, analyzers, format | the project's gate decides them, and it is run by hand |
| principles 6.2-6.5 (versions in one place, output, licenses, patches) | facts of the build and of the dependency audit tools: the gate, or the security audit for the vulnerabilities |
| principles 7 | it is how a judgement is made: it is the way these cards are written |
| code principles 4.5 (guards on public members) | a guard that is missing shows as the failure it lets through, found by the cards of its kind; one that repeats what the type guarantees is noise, not a defect |
