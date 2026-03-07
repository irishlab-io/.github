---
hide:
  - toc
---

# Context[^1]

> "They say 'practice makes perfect,' but in testing, 'practice makes permanent errors if not caught early.'"

Saint‑Nulle‑part‑dans‑le‑fond‑du‑Bois is a tiny Québec town of 237 people. Everything important sits in one shared building: town hall, church, general store, and the only Québec branch of the Insecure Bank Corporation. Lucile is the bank’s lone teller. The bell over the door does every job—mass, meetings, and reminders.

In January, the bank was hacked. Lucile’s screen flashed a strange message, and it became clear that something bad had just happened. She rang the bell three times. The mayor gathered everyone and met with the Insecure Bank Corporation executives, who announced that major improvements would be undertaken to increase the security of the bank’s application.

A sole IT consultant was willing to drive a snowmobile to a town sitting like a pin in a quilt of spruce and snow. He made a slew of recommendations, but the IBC top brass focused only on financial profitability and wanted the bare minimum done. Together, they negotiated to implement the following security improvements:

- Scan the `insecure-bank` repository for Software Development Lifecycle (SDLC) bad practices
- Fix the vulnerability associated with the `PyYAML` package, deemed by the consultant the most critical of them all
- Mute all other dependency vulnerabilities until February 27, 2026; a new team will take over after that date
- Scan the `src/web/views.py` file for code vulnerabilities
- Apply the necessary corrections to `get_file_checksum`
- Focus scanning on new code and on dependency vulnerabilities for the time being
- Inspect the container’s upstream base image for vulnerabilities
- Identify upstream vulnerabilities relative to the project’s inherent vulnerabilities
- Implement corrections at the container level while staying on `python3.10.x-alpine-3.xx` to reduce the risk level of this application
- Generate a software bill of materials for the final container image shipped to production
- Parse the final software bill of materials to list all identified vulnerabilities

The mayor, Yvette (a part-time CS student), and the IBC C‑suite all agreed that before the service point can reopen, the IBC must demonstrate that these recommendations have been fulfilled and that the web application vulnerabilities are under control.

## TL;DR

[Security Overview](security/overview.md)

[^1]: Thanks, ChatGPT-5.
