# Security policy

## Reporting a vulnerability

Open a [private security advisory](https://github.com/earbona23/intune-drift/security/advisories/new)
on this repository. Please do not open a public issue for a vulnerability.

You will get an acknowledgement within 72 hours and an assessment within seven days. There
is no bounty programme — this is a single-maintainer project — but every report is credited
in the advisory unless you ask me not to.

## What counts as a vulnerability here

`intune-drift` snapshots Microsoft Intune configuration and diffs two snapshots with a security lens.

The threat model is shaped by one fact: this tool is pointed at a real tenant by
someone with real privilege. These are in scope, in rough order of severity.

| Class | Why it matters |
|---|---|
| **Any write reaching a live tenant** | This tool is read-only. A code path that issues anything other than a read against Microsoft Graph is the most serious bug this project can have, whether or not it is reachable today. |
| **A token or secret leaving memory** | An access token written to disk, printed, included in a report, or sent to a log or crash handler. |
| **Tenant data escaping the operator's control** | User principal names, object identifiers, IP addresses and device names are all present in the output. Anything that transmits them anywhere, or writes them somewhere the operator did not choose, is in scope. |
| **A scope request wider than the work** | Asking for a Graph permission the tool does not need. Over-consent is a real vulnerability in a tool people grant access to. |
| **A finding reported as clean** | A change that weakens posture reported as neutral, or an unclassified setting treated as harmless instead of being marked unclassified. A query that failed, was denied, or was silently truncated must never be presented as an absence of findings. Silence and safety are different results. |
| **A snapshot is a configuration disclosure** | Snapshots describe your endpoint controls in detail — encryption, PIN policy, lock timeouts. They are versionable on purpose, which means they are easy to commit somewhere public by accident. |

## The read-only guarantee

`tests/test_readonly_guarantee.py` walks the source and fails the build if a write path appears. That is the
guarantee this tool is built on: it is enforced by the test suite, not by intention, and a
change that breaks it cannot merge green.

## Out of scope

- A finding you disagree with on the merits. Tune the catalogue and open a normal issue —
  the risk weights are data, not code, precisely so you can argue with them.
- Missing coverage of a technique or configuration. That is a feature request.
- Anything requiring credentials you were never entitled to. This tool reads what the
  signed-in identity may already read; it grants nothing.
