// The gate of a TypeScript project without a framework: the pack's configuration as it is. A framework
// replaces this file with its own, which starts from the pack's (overlays/typescript/<framework>.md).
import { defineConfig } from "eslint/config";
import pack from "./eslint.pack.js";

export default defineConfig(pack);
