# Project Conventions

<!-- Copy this file to the root of your project as CONVENTIONS.md.
     Customize the sections relevant to your stack.
     The convention-checker agent reads this file to validate code. -->

## Stack

- backend: python 3.12+
<!-- - frontend: typescript (react) -->

## Python Rules

### Async I/O
- required: true
- asyncio_to_thread: allowed with warning (verify thread safety)

### Type Hints
- public-api: required
- syntax: modern (list[T], X | None — never List[T], Optional[X])
- typing-deprecated-imports: error (List, Dict, Tuple, Set, Optional, Union)

### Exceptions
- base-exception: <ProjectName>Error(Exception)
- chaining: required (raise ... from e)
- bare-except: error
- silent-swallow: error

### Logging
- style: structured (extra={})
- f-strings-in-messages: error
- pattern: logger.info("event_name", extra={"key": value})

### Testing
- naming: test_<function>_<scenario>_<expected_result>
- async: asyncio_mode=auto in pyproject.toml
- coverage: 100%

### Config Models
- base: Pydantic v2
- frozen: true
- fields: Field() with descriptions on public configs

### Docstrings
- style: google
- language: english
- public-api: required
- severity: info (only flag when asked for thorough review)

### Imports
- order: stdlib > third-party > local
- star-imports: error

## TypeScript Rules

<!-- Uncomment if project has TypeScript frontend -->

<!-- ### Type Safety
- explicit-any: error
- non-null-assertion: error
- null-handling: explicit
- strict-mode: required -->

<!-- ### Error Handling
- bare-catch: error
- error-types: typed (never catch unknown without narrowing) -->

<!-- ### Logging
- console-log: error (use logger) -->

<!-- ### Immutability
- prefer-const: true
- prefer-readonly: true
- as-const: prefer for literal types -->

## Security
- hardcoded-secrets: error
- unsafe-yaml: error (require SafeLoader)
- eval-or-exec: error
- dynamic-code-execution: error
- unsafe-deserialization: error
- unsafe-inner-html: error

## Custom Rules

<!-- Add project-specific rules below. Examples:
- max-function-lines: 30
- required-headers: MIT license header in all files
- api-versioning: all endpoints must be versioned (/api/v1/)
-->
