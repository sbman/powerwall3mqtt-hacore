# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-02-26

### Added

- This changelog!
- A loose [roadmap](./ROADMAP.md)

### Fixed

- [Issue #14](https://github.com/slyglif/haos-addons/issues/14): A better message is logged with a clean exit if unable to connect to PW on startup.
- [Issue #15](https://github.com/slyglif/haos-addons/issues/15): Fixed handling of throttling so it can properly increase the poll interval.

### Changed

- Converted the git repo to a separate submodule to allow better release tracking

## 0.1.1 - 2025-02-24

### Fixed

- Reverse Battery Power Charge / Discharge calculations
- Fix placement of logging about discovery delay
- Fix the URL for the project


## 0.1.0 - 2025-02-24

### Added

- [Issue #12](https://github.com/slyglif/haos-addons/issues/12): Import and Export power entities to help support the Energy Dashboard
- Added gradual backoff of loop_interval if throttling is encountered

### Fixed

- [Issue #10](https://github.com/slyglif/haos-addons/issues/10): Threading shutdown issue that manifested as a hang
- [Issue #2](https://github.com/slyglif/haos-addons/issues/2): Race condition at startup causing an initial delay in metrics loading in HA
- Check for pw3 on startup


## 0.0.6 - 2025-02-19

### Fixed

- [Issue #1](https://github.com/slyglif/haos-addons/issues/1): Entities becoming unavailable after an HA restart or reconnect to MQTT


## 0.0.5 - 2025-02-18

### Fixed

- [Issue #9](https://github.com/slyglif/haos-addons/issues/9): Missing state_class on some entities causes HA warnings


## 0.0.4 - 2025-02-18

### Fixed

- [Issue #8](https://github.com/slyglif/haos-addons/issues/8): Shutdowns weren't clean, preventing relavent logs from showing

[unreleased]: https://github.com/slyglif/powerwall3mqtt/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/slyglif/powerwall3mqtt/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/slyglif/powerwall3mqtt/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/slyglif/powerwall3mqtt/compare/v0.0.6...v0.1.0
[0.0.6]: https://github.com/slyglif/powerwall3mqtt/compare/v0.0.5...v0.1.6
[0.0.5]: https://github.com/slyglif/powerwall3mqtt/compare/v0.0.4...v0.1.5
[0.0.4]: https://github.com/slyglif/powerwall3mqtt/compare/v0.0.3...v0.1.4
