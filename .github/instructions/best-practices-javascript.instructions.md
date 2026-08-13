---
description: JavaScript best practices for modern web and Node.js projects. Covers ESLint, Prettier, Jest unit testing, ES module conventions, async patterns, and common framework guidelines for beginners through intermediate developers.
applyTo: "**/*.js,**/*.jsx,**/*.mjs,**/*.cjs"
---

# JavaScript Best Practices

All JavaScript code in this organization must follow these standards. These guidelines apply to every JavaScript file across all repositories and are enforced through ESLint, Prettier, and Jest.

## Toolchain

| Tool | Purpose |
|------|---------|
| [Node.js](https://nodejs.org/) | JavaScript runtime (use LTS version) |
| [npm](https://www.npmjs.com/) | Package manager (use `npm ci` in CI) |
| [ESLint](https://eslint.org/) | Linter — catches bugs and enforces code style |
| [Prettier](https://prettier.io/) | Opinionated code formatter |
| [Jest](https://jestjs.io/) | Unit test runner and assertion library |

```bash
# Install project dependencies (exact versions from lockfile)
npm ci

# Run linter
npx eslint .

# Auto-fix lint issues
npx eslint . --fix

# Format code
npx prettier --write .

# Run all tests
npx jest

# Run tests in watch mode (during development)
npx jest --watch

# Run tests with coverage report
npx jest --coverage
```

### Recommended `package.json` scripts

```json
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

## Code Style and Formatting

- Use **Prettier** as the single source of truth for formatting — do not debate style in code reviews
- Maximum line length: **100 characters**
- Use **2 spaces** for indentation — never tabs
- Always use **semicolons** at end of statements
- Use **single quotes** for strings (double quotes inside JSX attributes is fine)
- Add a **trailing comma** in multi-line arrays and objects (makes diffs cleaner)

### Recommended `.eslintrc.json`

```json
{
  "env": {
    "es2022": true,
    "node": true,
    "jest": true
  },
  "extends": ["eslint:recommended"],
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "no-var": "error",
    "prefer-const": "error",
    "eqeqeq": ["error", "always"],
    "no-console": "warn",
    "no-unused-vars": "error"
  }
}
```

### Recommended `.prettierrc`

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2
}
```

## Variables — Always `const` or `let`, Never `var`

`var` has confusing scoping rules. Use `const` by default; use `let` only when the value must be reassigned.

```js
// Good
const MAX_RETRIES = 3;
const user = { name: 'Alice' };

let counter = 0;
counter += 1;

// Bad — var leaks out of blocks and is hoisted
var retries = 3;
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables & functions | `camelCase` | `getUserById` |
| Classes | `PascalCase` | `UserService` |
| Constants (module-level) | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Files (plain JS) | `kebab-case` | `user-service.js` |
| Files (React components) | `PascalCase` | `UserCard.jsx` |
| Private class fields | `#camelCase` | `#apiKey` |

```js
// Good
const MAX_RETRIES = 3;

class UserService {
  #apiKey;

  constructor(apiKey) {
    this.#apiKey = apiKey;
  }

  async getUserById(userId) {
    // ...
  }
}

// Bad
var max_retries = 3;

class user_service {
  GetUser(Id) { ... }
}
```

## Functions

### Prefer Arrow Functions for Callbacks

```js
// Good
const doubled = [1, 2, 3].map((n) => n * 2);

// Bad — verbose for simple callbacks
const doubled = [1, 2, 3].map(function (n) { return n * 2; });
```

### Use Regular Functions for Named, Standalone Functions

```js
// Good — named function declaration for top-level logic
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Good — arrow function for short, inline callbacks
const prices = items.map((item) => item.price);
```

### Default Parameters Over Conditional Assignments

```js
// Good
function greet(name = 'World') {
  return `Hello, ${name}!`;
}

// Bad
function greet(name) {
  name = name || 'World';
  return `Hello, ${name}!`;
}
```

## Async / Await

Always use `async/await` over raw `.then()` chains for readability. Always handle errors with `try/catch`.

```js
// Good
async function fetchUser(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('fetchUser error:', error);
    throw error; // re-throw so callers can handle it
  }
}

// Bad — .then() chains are harder to read and harder to debug
function fetchUser(userId) {
  return fetch(`/api/users/${userId}`)
    .then((res) => res.json())
    .catch((err) => console.error(err));
}
```

## Modules (ES Modules)

Use ES module syntax (`import`/`export`). Avoid `require()` in new code unless the project is explicitly CommonJS.

```js
// Good — named exports (preferred for utilities)
export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

// Good — default export (preferred for classes and React components)
export default class UserService { ... }

// Importing
import { add, subtract } from './math.js';
import UserService from './user-service.js';

// Bad — CommonJS in a modern project
const { add } = require('./math');
module.exports = { add };
```

## Error Handling

- Never swallow errors silently — always log or re-throw
- Use `Error` objects (not plain strings) when throwing
- Include context in error messages so they are actionable

```js
// Good
function parseConfig(raw) {
  if (!raw) {
    throw new Error('parseConfig: raw config must not be empty');
  }
  try {
    return JSON.parse(raw);
  } catch (cause) {
    throw new Error(`parseConfig: invalid JSON — ${cause.message}`);
  }
}

// Bad
function parseConfig(raw) {
  try {
    return JSON.parse(raw);
  } catch (e) {
    // silently swallowed — never do this
  }
}
```

## Unit Testing with Jest

### File Structure

Place test files alongside the source they test, using the `.test.js` suffix.

```
src/
  math.js
  math.test.js
  user-service.js
  user-service.test.js
```

### Recommended `jest.config.js`

```js
/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'node',       // use 'jsdom' for browser/React projects
  collectCoverageFrom: ['src/**/*.js'],
  coverageThreshold: {
    global: {
      lines: 80,
      functions: 80,
    },
  },
};

export default config;
```

### Writing Tests

Follow the **Arrange → Act → Assert** pattern. One concept per test.

```js
// math.test.js
import { add, subtract } from './math.js';

describe('add()', () => {
  it('returns the sum of two positive numbers', () => {
    // Arrange
    const a = 2;
    const b = 3;

    // Act
    const result = add(a, b);

    // Assert
    expect(result).toBe(5);
  });

  it('handles negative numbers', () => {
    expect(add(-1, 1)).toBe(0);
  });
});

describe('subtract()', () => {
  it('returns the difference of two numbers', () => {
    expect(subtract(10, 4)).toBe(6);
  });
});
```

### Mocking with Jest

Use `jest.fn()` to mock dependencies and isolate the unit under test.

```js
// user-service.test.js
import { UserService } from './user-service.js';

describe('UserService.getUser()', () => {
  it('returns a user when the fetch succeeds', async () => {
    // Arrange — mock the fetch dependency
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, name: 'Alice' }),
    });
    const service = new UserService(mockFetch);

    // Act
    const user = await service.getUser(1);

    // Assert
    expect(user).toEqual({ id: 1, name: 'Alice' });
    expect(mockFetch).toHaveBeenCalledWith('/api/users/1');
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('throws when the fetch fails', async () => {
    const mockFetch = jest.fn().mockResolvedValue({ ok: false, status: 404 });
    const service = new UserService(mockFetch);

    await expect(service.getUser(99)).rejects.toThrow('404');
  });
});
```

### Test Naming Rules

- Test file: `<module>.test.js`
- Top-level `describe`: the module or function name — e.g., `describe('UserService', ...)`
- Nested `describe` (optional): the method — e.g., `describe('.getUser()', ...)`
- `it`/`test` label: plain English describing the **expected behaviour** — e.g., `'returns null when user is not found'`

```js
// Good
it('returns null when user is not found', () => { ... });
it('throws ValidationError when email is missing', () => { ... });

// Bad
it('test1', () => { ... });
it('works', () => { ... });
```

## Common Patterns

### Destructuring

```js
// Object destructuring
const { name, age, email = 'n/a' } = user;

// Array destructuring
const [first, second, ...rest] = items;

// In function parameters
function displayUser({ name, role = 'viewer' }) {
  console.log(`${name} (${role})`);
}
```

### Spread and Rest

```js
// Spread — shallow copy and merge objects
const updated = { ...user, email: 'new@example.com' };
const combined = [...listA, ...listB];

// Rest — collect remaining arguments
function sum(...numbers) {
  return numbers.reduce((total, n) => total + n, 0);
}
```

### Optional Chaining and Nullish Coalescing

```js
// Optional chaining — safe navigation without if-null checks
const city = user?.address?.city;
const first = items?.[0]?.name;

// Nullish coalescing — default only for null/undefined (not 0 or '')
const displayName = user.name ?? 'Anonymous';
const port = config.port ?? 3000;
```

## Security

- **Never trust user input** — validate and sanitize all data at system boundaries
- **Never use `eval()`** — it executes arbitrary code and is a major XSS vector
- **Never construct HTML with string concatenation** — use DOM APIs or a templating library
- **Never log secrets** — filter tokens, passwords, and API keys from all log output
- **Pin dependency versions** — use `package-lock.json` and run `npm audit` regularly

```js
// Bad — XSS vulnerability
element.innerHTML = `Welcome, ${userInput}!`;

// Good — safe DOM manipulation
element.textContent = `Welcome, ${userInput}!`;

// Bad — arbitrary code execution
eval(userSuppliedExpression);
```

## What to Avoid

| Anti-pattern | Why | Use instead |
|--|--|--|
| `var` | Function-scoped, causes bugs | `const` / `let` |
| `==` | Coerces types unexpectedly | `===` |
| `eval()` | Security risk | Structured logic |
| Callback hell | Hard to read and debug | `async/await` |
| Mutating function arguments | Causes hidden side-effects | Return a new value |
| Ignoring `catch` blocks | Hides failures | Log and re-throw |
| `console.log` left in production code | Leaks internal state | Use a logger library |
