# Game

For a program that runs a real-time loop: a game, a simulation, an interactive application driven by
frames and input.

---

1. **One entry point composes the program.** The main scene — or the engine's equivalent — is the
   composition root (principles 3.6): it builds the services once and hands each part what it needs.
   Under it, the world (the levels, the characters, everything the game simulates) and the interface
   (menus, the HUD) are separate parts; a level is loaded and unloaded as a whole, by swapping it under
   the world.

2. **The rules of the game are separate from their presentation.** Health, damage, inventory, score,
   the rules of a turn: plain objects that do not depend on the scene tree, the frame loop or the
   renderer, tested without them. The nodes on screen present those objects and forward the player's
   input to them; they do not hold the rules (code principles 1.4).

3. **Calls go down, events go up.** A parent calls methods of its children; a child reports what
   happened with an event (a signal) named in the past tense, and does not know who listens. Two
   siblings talk through their common parent. Nothing reaches a part by its absolute place in the tree.

4. **A global is a system that keeps its own data.** A part every scene reaches (an audio mixer, a
   save slot) is global only when it keeps its own data, is needed everywhere, and changes no other
   part's data; anything else is handed in by the composition root.

5. **An entity whose legal actions depend on its state has a state machine** (code principles 2.1): a
   character idle, running, jumping, stunned; an enemy patrolling, chasing, attacking. Scattered flags
   are not one.

6. **Input is read as named actions**, never as raw keys or buttons inside the game's logic: the
   actions are declared once, mapped to devices in configuration, and rebound without touching code.

7. **Time is the engine's step, never an assumed frame rate.** Movement and simulation advance by the
   step they receive (the physics step for physics, the frame's delta for the rest); a delay is a timer
   or an awaited event (code principles 4.7), not a count of frames.

8. **Content is data.** The stats of a character, the waves of a level, the prices of a shop live in
   data files the designers edit (code principles 2.5), loaded and validated once, at startup or when
   the level loads; the code reads them and holds no tuned number of its own (code principles 3.6).

9. **The frame has a budget.** Nothing is loaded from disk on the frame's path — what a scene needs is
   loaded ahead; the steady state of a frame allocates nothing it could keep; an object is configured
   before it joins the scene, where every change can cost an update.

10. **A save is versioned data, and the player's disk is untrusted.** A save holds data only, in a
    format that carries no code; it records its version, and a loader reads every version it supports
    or refuses the file with a message; what it reads is validated like any input (principles 4.3). It
    lives in the user's data folder, never beside the program.

11. **Each level of test proves its part** (testing principles §3): the rules as unit tests, without
    the frame loop; a scene, loaded headless, as an integration test of its wiring — its signals, its
    setup, the actions it reacts to; the main scene started headless as the smoke test of the whole.
