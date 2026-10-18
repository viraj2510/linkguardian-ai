# Verification record

Checks run on October 18, 2026, before publication:

- Backend: `python -m unittest backend.test_backend -v` — all 9 tests passed.
- Frontend: production build, including TypeScript validation — passed after upgrading Next.js from 13.5.11 to 15.5.28.
- Initial browser run: live API health, recognized-domain scan, invalid protocol, suspicious-pattern scan, recent results, support navigation, FAQ, desktop/mobile overflow, and no runtime errors — passed.

## Dependency audit

The update also pins PostCSS 8.5.28 and overrides nested PostCSS, source-map-js, and postcss-selector-parser to patched versions. The subsequent npm audit still reports **5 high findings** through Tailwind 3's braces/chokidar/micromatch/fast-glob build dependency chain. The scanner does not pass submitted URLs into these build tools. Resolving this chain requires a separate Tailwind migration or upstream fixes; this deployment is not represented as having a clean security audit.

These checks validate application behavior and build compatibility. They do not measure the model's phishing-detection accuracy or constitute a penetration test.
