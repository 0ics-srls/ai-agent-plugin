// The TypeScript lint gate, imported by eslint.config.js: the rules listed here and only them, with the
// type information of the project. Each one finds a defect — a promise nobody awaits, a check of the
// compiler silenced, an error of logic — and was chosen one by one for that. The rules of style, of
// order, of naming and of counts are not here: they find no defect, and on code that exists they only
// make it be rewritten. A rule joins or leaves the list by the project owner's decision, with its
// reason. The generated client is generated code and is not linted. A framework adds its own rules
// after this configuration.
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";

export default defineConfig(
  {
    ignores: [
      "src/api/**",
      "src/.devextreme/**",
      "dist/**",
      "coverage/**",
      "node_modules/**",
      ".angular/**",
      "playwright-report/**",
      "test-results/**",
    ],
  },
  {
    // JavaScript and TypeScript, the scripts of Vue's single-file components included (their parser
    // comes with Vue's configuration). typescript-eslint's base gives the parser and the plugin, no rule.
    files: ["**/*.{js,mjs,cjs,ts,mts,cts,tsx,vue}"],
    extends: [tseslint.configs.base],
    languageOptions: {
      parserOptions: {
        projectService: { allowDefaultProject: ["*.js", "*.mjs"] },
      },
    },
    rules: {
      // ---- ESLint
      // Enforce `return` statements in callbacks of array methods.
      "array-callback-return": "error",
      // Require the use of `===` and `!==`.
      eqeqeq: ["error", "always", { null: "ignore" }],
      // Enforce `for` loop update clause moving the counter in the right direction.
      "for-direction": "error",
      // Disallow using an async function as a Promise executor.
      "no-async-promise-executor": "error",
      // Disallow assignment operators in conditional expressions.
      "no-cond-assign": "error",
      // Disallow expressions where the operation doesn't affect the value.
      "no-constant-binary-expression": "error",
      // Disallow constant expressions in conditions.
      "no-constant-condition": "error",
      // Disallow the use of `debugger`.
      "no-debugger": "error",
      // Disallow duplicate conditions in if-else-if chains.
      "no-dupe-else-if": "error",
      // Disallow duplicate case labels.
      "no-duplicate-case": "error",
      // Disallow empty block statements.
      "no-empty": "error",
      // Disallow the use of `eval()`.
      "no-eval": "error",
      // Disallow reassigning exceptions in `catch` clauses.
      "no-ex-assign": "error",
      // Disallow assignments to native objects or read-only global variables.
      "no-global-assign": "error",
      // Disallow invalid regular expression strings in `RegExp` constructors.
      "no-invalid-regexp": "error",
      // Disallow literal numbers that lose precision.
      "no-loss-of-precision": "error",
      // Disallow `new` operators with the `Function` object.
      "no-new-func": "error",
      // Disallow returning values from Promise executor functions.
      "no-promise-executor-return": "error",
      // Disallow assignments where both sides are exactly the same.
      "no-self-assign": "error",
      // Disallow comparisons where both sides are exactly the same.
      "no-self-compare": "error",
      // Disallow template literal placeholder syntax in regular strings.
      "no-template-curly-in-string": "error",
      // Disallow `let` or `var` variables that are read but never assigned.
      "no-unassigned-vars": "error",
      // Disallow confusing multiline expressions.
      "no-unexpected-multiline": "error",
      // Disallow unmodified loop conditions.
      "no-unmodified-loop-condition": "error",
      // Disallow loops with a body that allows only one iteration.
      "no-unreachable-loop": "error",
      // Disallow control flow statements in `finally` blocks.
      "no-unsafe-finally": "error",
      // Disallow use of optional chaining in contexts where the `undefined` value is not allowed.
      "no-unsafe-optional-chaining": "error",
      // Disallow losing originally caught error when re-throwing custom errors.
      "preserve-caught-error": "error",
      // Require calls to `isNaN()` when checking for `NaN`.
      "use-isnan": "error",
      // Enforce comparing `typeof` expressions against valid strings.
      "valid-typeof": "error",
      // ---- typescript-eslint
      // Disallow awaiting a value that is not a Thenable.
      "@typescript-eslint/await-thenable": "error",
      // Disallow `@ts-<directive>` comments or require descriptions after directives.
      "@typescript-eslint/ban-ts-comment": "error",
      // Disallow using the `delete` operator on array values.
      "@typescript-eslint/no-array-delete": "error",
      // Require `.toString()` and `.toLocaleString()` to only be called on objects which provide useful information when stringified.
      "@typescript-eslint/no-base-to-string": "error",
      // Disallow duplicate enum member values.
      "@typescript-eslint/no-duplicate-enum-values": "error",
      // Disallow the `any` type.
      "@typescript-eslint/no-explicit-any": "error",
      // Disallow extra non-null assertions.
      "@typescript-eslint/no-extra-non-null-assertion": "error",
      // Require Promise-like statements to be handled appropriately.
      "@typescript-eslint/no-floating-promises": "error",
      // Disallow iterating over an array with a for-in loop.
      "@typescript-eslint/no-for-in-array": "error",
      // Disallow the use of `eval()`-like functions.
      "@typescript-eslint/no-implied-eval": "error",
      // Disallow Promises in places not designed to handle them.
      "@typescript-eslint/no-misused-promises": "error",
      // Disallow using the spread operator when it might cause unexpected behavior.
      "@typescript-eslint/no-misused-spread": "error",
      // Disallow non-null assertions in the left operand of a nullish coalescing operator.
      "@typescript-eslint/no-non-null-asserted-nullish-coalescing": "error",
      // Disallow non-null assertions after an optional chain expression.
      "@typescript-eslint/no-non-null-asserted-optional-chain": "error",
      // Disallow non-null assertions using the `!` postfix operator.
      "@typescript-eslint/no-non-null-assertion": "error",
      // Disallow conditionals where the type is always truthy or always falsy.
      "@typescript-eslint/no-unnecessary-condition": "error",
      // Disallow calling a function with a value with type `any`.
      "@typescript-eslint/no-unsafe-argument": "error",
      // Disallow assigning a value with type `any` to variables and properties.
      "@typescript-eslint/no-unsafe-assignment": "error",
      // Disallow calling a value with type `any`.
      "@typescript-eslint/no-unsafe-call": "error",
      // Disallow member access on a value with type `any`.
      "@typescript-eslint/no-unsafe-member-access": "error",
      // Disallow returning a value with type `any` from a function.
      "@typescript-eslint/no-unsafe-return": "error",
      // Disallow unused expressions.
      "@typescript-eslint/no-unused-expressions": "error",
      // Disallow throwing non-`Error` values as exceptions.
      "@typescript-eslint/only-throw-error": "error",
      // Require `Array#sort` and `Array#toSorted` calls to always provide a `compareFunction`.
      "@typescript-eslint/require-array-sort-compare": "error",
      // Require both operands of addition to be the same type and be `bigint`, `number`, or `string`.
      "@typescript-eslint/restrict-plus-operands": "error",
      // Enforce template literal expressions to be of `string` type.
      "@typescript-eslint/restrict-template-expressions": "error",
      // Enforce consistent awaiting of returned promises.
      "@typescript-eslint/return-await": "error",
      // Require switch-case statements to be exhaustive.
      "@typescript-eslint/switch-exhaustiveness-check": "error",
      // Enforce unbound methods are called with their expected scope.
      "@typescript-eslint/unbound-method": "error",
    },
  },
);
