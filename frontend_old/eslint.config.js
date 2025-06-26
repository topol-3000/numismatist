import pluginImport from "eslint-plugin-import";
import eslint from '@eslint/js';
import eslintConfigPrettier from 'eslint-config-prettier';
import eslintPluginVue from 'eslint-plugin-vue';
import globals from 'globals';
import typescriptEslint from 'typescript-eslint';

export default typescriptEslint.config(
  { ignores: ['*.d.ts', '**/node_modules', '**/dist'] },
  {
    extends: [
      eslint.configs.recommended,
      ...typescriptEslint.configs.strict,
      ...eslintPluginVue.configs['flat/strongly-recommended'],
    ],
    files: ['**/*.{ts,vue}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: globals.browser,
      parserOptions: {
        parser: typescriptEslint.parser,
      },
    },
    plugins: { import: pluginImport },
    rules: {
      "import/order": [
        "warn",
        {
          groups: [
            ["builtin", "external"],    // Node.js modules and external libraries (e.g., fs, axios)
            ["internal"],               // Internal project code (e.g., @/utils)
            ["parent", "sibling", "index"], // Relative imports
          ],
          pathGroups: [
            {
              pattern: "@/**",         // Add alias for internal paths (if applicable)
              group: "internal",
              position: "before",
            },
          ],
          pathGroupsExcludedImportTypes: ["builtin"],
          alphabetize: {
            order: "asc",               // Sort imports alphabetically within groups
            caseInsensitive: true,      // Ignore case when sorting
          },
          "newlines-between": "always", // Add a newline between different groups
        },
      ],
    },
  },
  eslintConfigPrettier
);