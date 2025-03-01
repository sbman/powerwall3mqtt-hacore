# Changelog

## [0.2.0] - 2025-03-01

### Fixed

- [Issue #22](https://github.com/slyglif/powerwall3mqtt/issues/22): Added better error handling of errors fetching individual PW vitals (such as PV string info).  Now the app should log an error and continue running, but mark the individual PWs as unavailable in HA.

### Changed

- This release had a major code cleanup and refactoring, simplifying a lot of the individual functions and classes.  With the exception of the protobuf class, it now passes pylint cleanly using the default settings.  It's possible some edge cases could have issues, so please report any stack traces.  This was preparation for adding unit tests in the future.

## [0.1.3] - 2025-02-27

### Fixed

- [Issue #18](https://github.com/slyglif/powerwall3mqtt/issues/18): Fixed multiple instance of exceptions not being properly handled
- [Issue #19](https://github.com/slyglif/powerwall3mqtt/issues/18): Fixed leaking of passwords into debug logs


## [0.1.2] - 2025-02-26

### Added

- This changelog!
- A loose [roadmap](./ROADMAP.md)

### Fixed

- [Issue #14](https://github.com/slyglif/powerwall3mqtt/issues/14): A better message is logged with a clean exit if unable to connect to PW on startup.
- [Issue #15](https://github.com/slyglif/powerwall3mqtt/issues/15): Fixed handling of throttling so it can properly increase the poll interval.

### Changed

- Converted the git repo to a separate submodule to allow better release tracking

## 0.1.1 - 2025-02-24

### Fixed

- Reverse Battery Power Charge / Discharge calculations
- Fix placement of logging about discovery delay
- Fix the URL for the project


## 0.1.0 - 2025-02-24

### Added

- [Issue #12](https://github.com/slyglif/powerwall3mqtt/issues/12): Import and Export power entities to help support the Energy Dashboard
- Added gradual backoff of loop_interval if throttling is encountered

### Fixed

- [Issue #10](https://github.com/slyglif/powerwall3mqtt/issues/10): Threading shutdown issue that manifested as a hang
- [Issue #2](https://github.com/slyglif/powerwall3mqtt/issues/2): Race condition at startup causing an initial delay in metrics loading in HA
- Check for pw3 on startup


## 0.0.6 - 2025-02-19

### Fixed

- [Issue #1](https://github.com/slyglif/powerwall3mqtt/issues/1): Entities becoming unavailable after an HA restart or reconnect to MQTT


## 0.0.5 - 2025-02-18

### Fixed

- [Issue #9](https://github.com/slyglif/powerwall3mqtt/issues/9): Missing state_class on some entities causes HA warnings


## 0.0.4 - 2025-02-18

### Fixed

- [Issue #8](https://github.com/slyglif/powerwall3mqtt/issues/8): Shutdowns weren't clean, preventing relavent logs from showing

[unreleased]: https://github.com/slyglif/powerwall3mqtt/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/slyglif/powerwall3mqtt/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/slyglif/powerwall3mqtt/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/slyglif/powerwall3mqtt/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/slyglif/powerwall3mqtt/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/slyglif/powerwall3mqtt/compare/v0.0.6...v0.1.0
[0.0.6]: https://github.com/slyglif/powerwall3mqtt/compare/v0.0.5...v0.1.6
[0.0.5]: https://github.com/slyglif/powerwall3mqtt/compare/v0.0.4...v0.1.5
[0.0.4]: https://github.com/slyglif/powerwall3mqtt/compare/v0.0.3...v0.1.4
