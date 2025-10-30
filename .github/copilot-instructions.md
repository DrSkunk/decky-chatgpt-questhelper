# GitHub Copilot Instructions for Decky ChatGPT Quest Helper

## Project Overview

This is a Decky plugin for Steam Deck that provides ChatGPT-powered quest assistance. The project consists of:
- **Frontend**: TypeScript/React using Decky's UI components
- **Backend**: Python using the Decky plugin API
- **Build System**: Rollup for frontend bundling
- **Package Manager**: pnpm (v9)

## Project Structure

```
.
├── src/              # TypeScript/React frontend code
├── main.py           # Python backend entry point
├── backend/          # Backend source and build files
│   └── src/          # Backend source code
├── assets/           # Static assets (images, etc.)
├── defaults/         # Default configuration files
├── dist/             # Built frontend output (generated)
├── package.json      # Node.js dependencies
├── tsconfig.json     # TypeScript configuration
└── rollup.config.js  # Rollup bundler configuration
```

## Development Environment Setup

### Prerequisites
- Node.js v16.14+
- pnpm v9 (install with `npm i -g pnpm@9`)
- Docker (if working with custom backends)

### Initial Setup
1. Install dependencies: `pnpm install`
2. Build frontend: `pnpm run build`
3. Watch mode: `pnpm run watch`

## Coding Standards

### TypeScript/React Frontend

#### Style Guidelines
- Use TypeScript strict mode (already configured in tsconfig.json)
- Follow existing React patterns using Decky's `@decky/ui` components
- Use functional components with hooks (no class components)
- Import Decky UI components from `@decky/ui`
- Import Decky API utilities from `@decky/api`

#### Component Structure
```typescript
import { PanelSection, PanelSectionRow, ButtonItem } from "@decky/ui";
import { callable, definePlugin } from "@decky/api";

// Define callable Python functions with proper type annotations
const pythonFunction = callable<[arg1: Type1, arg2: Type2], ReturnType>("function_name");

// Use functional components
function MyComponent() {
  // Component logic
  return <PanelSection>...</PanelSection>;
}
```

#### Naming Conventions
- Use camelCase for variables and functions
- Use PascalCase for React components and TypeScript types
- Use UPPER_CASE for constants

### Python Backend

#### Style Guidelines
- Follow PEP 8 style guidelines
- Use async/await for all backend methods
- Use type hints for function parameters and return values
- Utilize the `decky` module for logging, settings, and events

#### Backend Patterns
```python
import decky
import asyncio

class Plugin:
    async def my_method(self, param: str) -> dict:
        """Docstring describing the method."""
        decky.logger.info(f"Method called with {param}")
        return {"result": "value"}
    
    async def _main(self):
        """Called when plugin loads."""
        self.loop = asyncio.get_event_loop()
        decky.logger.info("Plugin started")
    
    async def _unload(self):
        """Called when plugin stops."""
        decky.logger.info("Plugin stopping")
```

#### Communication Between Frontend and Backend
- Backend methods are called from frontend using `callable<>()` from `@decky/api`
- Backend can emit events to frontend using `await decky.emit("event_name", data)`
- Frontend listens to events using `addEventListener()` from `@decky/api`

## Testing

Currently, there is no test infrastructure in this project. When adding tests:
- Use Jest for TypeScript/React tests
- Follow existing testing patterns in the Decky ecosystem
- Ensure tests don't break the build process

## Build and Distribution

### Building
- Frontend builds to `dist/` directory
- Run `pnpm run build` before testing
- Use `pnpm run watch` for development with auto-rebuild

### Backend Building
- Backend binaries should be placed in `backend/out/`
- The build process moves them to a `bin/` folder in the final distribution
- Ensure backend build scripts create the `backend/out/` directory

### Plugin Distribution
A proper plugin zip should contain:
```
pluginname/
  ├── dist/index.js (required)
  ├── package.json (required)
  ├── plugin.json (required)
  ├── main.py (required for Python backend)
  ├── bin/ (optional, for backend binaries)
  ├── README.md (recommended)
  └── LICENSE (required)
```

## Security and Best Practices

### Security
- Never commit API keys, tokens, or secrets to the repository
- Sanitize and validate all user inputs in both frontend and backend
- Use the Decky settings API for storing user preferences securely
- Follow Steam Deck security guidelines for plugin development

### Logging
- Use `decky.logger.info()`, `.warning()`, `.error()` in Python
- Use `console.log()` sparingly in TypeScript; prefer Decky's logging mechanisms
- Log errors with sufficient context for debugging

### Performance
- This plugin targets Steam Deck hardware - be mindful of performance
- Avoid blocking operations in the frontend
- Use async operations for all backend calls
- Consider memory constraints of the Steam Deck

## Dependencies

### Adding Dependencies
- Use `pnpm add <package>` for runtime dependencies
- Use `pnpm add -D <package>` for dev dependencies
- Keep dependencies minimal to reduce plugin size
- Prefer using Decky's built-in UI components over external libraries

### Approved Libraries
- `@decky/ui` - Decky's UI component library (required)
- `@decky/api` - Decky's API utilities (required)
- `react-icons` - Icon library (already included)
- Additional libraries should be justified and kept minimal

## Documentation

- Update README.md when adding significant features
- Document all public Python methods with docstrings
- Add JSDoc comments for complex TypeScript functions
- Keep plugin.json metadata up to date

## Common Pitfalls to Avoid

1. **Don't remove unused imports** that are commented out - they serve as examples
2. **Don't modify rollup.config.js** unless necessary for build changes
3. **Don't change the JSX factory** in tsconfig.json - it's specific to Decky
4. **Don't use regular React imports** - use Decky's provided React via window.SP_REACT
5. **Don't forget to rebuild** after frontend changes - changes aren't live without a rebuild

## Decky-Specific Conventions

### Frontend
- Use `staticClasses` from `@decky/ui` for consistent styling
- Use `definePlugin()` to define the plugin structure
- Plugin must export a default plugin definition
- Icon can be any React component (often from react-icons)

### Backend
- Plugin class must have `_main()`, `_unload()`, and optionally `_uninstall()` methods
- Use `decky.migrate_*()` functions in `_migration()` for data migration
- Access Decky paths via `decky.DECKY_*` constants

### Settings Storage
- Use `decky.decky_SETTINGS_DIR` for persistent settings
- Use `decky.decky_RUNTIME_DIR` for temporary runtime data
- Use `decky.decky_LOG_DIR` for log files

## Issue Resolution Guidelines

When working on issues:
1. Understand the Decky plugin architecture before making changes
2. Test frontend changes by rebuilding and checking the plugin in Steam Deck UI
3. Check both frontend console and backend logs for errors
4. Ensure changes work within Steam Deck's gaming mode interface
5. Consider the plugin's resource usage on Steam Deck hardware

## Additional Resources

- [Decky Plugin Development Wiki](https://wiki.deckbrew.xyz/en/user-guide/home#plugin-development)
- [decky-frontend-lib](https://github.com/SteamDeckHomebrew/decky-frontend-lib)
- [decky-loader](https://github.com/SteamDeckHomebrew/decky-loader)
- [Decky Plugin Database](https://github.com/SteamDeckHomebrew/decky-plugin-database)
