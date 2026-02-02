---
allowed-tools: Read, Edit, Write, Glob, Grep, Bash(git ls-files:*), Bash(find:*), Bash(wc:*), Bash(du:*), Bash(npm:*), Bash(pnpm:*), Bash(yarn:*), Bash(turbo:*), mcp__browser-tools-mcp__runPerformanceAudit, mcp__browser-tools-mcp__getNetworkLogs
argument-hint: [optional: file/directory path, package name, or focus area]
description: Analyze and optimize performance: bundle size, loading speed, rendering efficiency, resource usage, and Core Web Vitals
---

# Performance Optimization

Analyze the codebase and optimize for speed, efficiency, and user experience by improving bundle size, rendering performance, data fetching, resource usage, and load times.

## Target Scope

$ARGUMENTS

## Initial Discovery

Before analysis, detect the project structure:
1. Check for monorepo indicators (pnpm-workspace.yaml, lerna.json, turbo.json, nx.json, packages/)
2. Identify the package manager (pnpm-lock.yaml, yarn.lock, package-lock.json)
3. Detect frameworks used (package.json dependencies)
4. Map the project/package structure

## Analysis Phase

Analyze the codebase (or specified path/package) for performance issues:

### 1. Bundle & Loading Analysis
- Identify large dependencies that could be code-split or lazy-loaded
- Find synchronous imports of heavy libraries (moment.js, lodash full, SDK clients)
- Look for barrel imports (index.ts re-exports) that prevent tree-shaking
- Check for duplicate dependencies across packages (monorepo)
- Identify redundant polyfills or shims
- Find third-party SDKs loaded synchronously (Firebase, AWS, Stripe, analytics)

### 2. Runtime Performance
- Find expensive computations in hot paths
- Identify missing memoization or caching
- Look for inline function/object definitions causing re-computations
- Check for memory leaks (unclosed listeners, timers, subscriptions)
- Spot large data structures being cloned unnecessarily
- Find synchronous operations that could be async

### 3. React/UI Framework Performance (if applicable)
- Components that re-render excessively
- Missing React.memo, useMemo, useCallback where beneficial
- State updates without proper cleanup in effects
- Large lists without virtualization
- Prop drilling causing unnecessary renders

### 4. Network & Data Fetching
- Sequential API calls that could be parallelized
- Missing caching strategies
- Data over-fetching (loading full objects when subsets needed)
- Request waterfalls (child fetching after parent)
- Uncached static data being fetched repeatedly
- Missing request deduplication

### 5. Asset Optimization
- Images without lazy loading or proper sizing
- Missing responsive images (srcset)
- Unoptimized images (>200KB for web)
- Font loading without display:swap or preload
- CSS that could be tree-shaken or split
- Unused CSS/JS being shipped

### 6. Monorepo-Specific (if applicable)
- Shared packages duplicated in node_modules
- Build dependencies not properly cached
- Packages rebuilding unnecessarily
- Missing workspace dependency optimization
- Shared utilities not extracted to common package

### 7. Core Web Vitals Blockers
- LCP: Large resources above the fold without prioritization
- CLS: Dynamic content without reserved space/dimensions
- INP: Event handlers with heavy synchronous work

## Execution Phase

After analysis, systematically optimize the code:

### Priority 1: Critical Performance Fixes
- Fix memory leaks (cleanup listeners, timers, subscriptions)
- Add dynamic/lazy imports for heavy dependencies
- Optimize blocking resources on critical path
- Fix obvious n+1 or waterfall patterns

### Priority 2: Bundle Size Reduction
- Replace barrel imports with direct imports
- Code-split routes and heavy features
- Lazy-load third-party SDKs and analytics
- Remove unused dependencies
- Use lighter alternatives (date-fns vs moment, lodash-es vs lodash)

### Priority 3: Runtime Optimization
- Add memoization for expensive computations
- Cache repeated calculations
- Debounce/throttle frequent operations
- Add virtualization for long lists (>50 items)
- Optimize hot code paths

### Priority 4: Network Optimization
- Parallelize independent data fetches
- Add caching layer (in-memory, SWR, React Query)
- Implement request deduplication
- Add optimistic updates where appropriate

## Framework-Specific Patterns

Apply optimizations based on detected frameworks:

### React
- `useMemo(() => expensive(deps), [deps])` for expensive computations
- `useCallback(fn, [deps])` for callback props
- `React.memo()` for pure components
- `React.lazy()` + `Suspense` for code splitting

### Next.js
- Server Components for static content
- `next/dynamic` for client-only components
- `next/image` for automatic image optimization
- Route-level `loading.tsx` for streaming

### Vue
- `computed` properties for derived state
- `v-memo` for list rendering
- `defineAsyncComponent` for lazy loading
- `<Suspense>` for async components

### Node.js / Backend
- Stream large responses instead of buffering
- Connection pooling for databases
- Async/await over callbacks for cleaner flow
- Worker threads for CPU-intensive tasks

### Monorepo (Turborepo/Nx/Lerna)
- Ensure proper caching configuration
- Use workspace protocol for internal deps
- Optimize build pipeline ordering
- Shared tsconfig/eslint for consistency

## Execution Guidelines

1. **Detect First**: Identify the tech stack before applying optimizations
2. **Measure**: Understand the actual bottleneck before optimizing
3. **Read Before Edit**: Always read the full file before making changes
4. **Incremental Changes**: Make one optimization at a time to isolate impact
5. **Preserve Functionality**: Ensure behavior remains unchanged
6. **Avoid Premature Optimization**: Focus on measurable improvements
7. **Document Trade-offs**: Note any complexity added for performance

## Report Format

After each optimization, report:
- File/package path
- Issue identified (with impact severity: critical/high/medium/low)
- Optimization applied
- Expected improvement
- Any trade-offs or risks

## Notes

- Focus on user-perceived performance, not micro-optimizations
- Prioritize fixes that affect the critical path
- Skip optimizations that add significant complexity for minimal gain
- Consider the full range of users (mobile, slow networks, older devices)
- If unsure about an optimization, explain the trade-offs
- Skip files that are auto-generated or vendored
- In monorepos, consider impact on dependent packages
