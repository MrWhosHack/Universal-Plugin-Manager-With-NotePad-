# Plugin Policy

This document defines the rules for creating, submitting, approving, distributing, and using plugins for Notepad++ Professional.

## 1. Definitions
- Software: Notepad++ Professional application.
- Plugin: Any module designed to run within the Software.
- Developer: An individual who creates a Plugin.
- Licensor: The Software owner/maintainer.

## 2. Approval Is Required
- Only approved plugins may be loaded by the Software.
- Approval is based on plugin integrity (hash), review, and compliance with policies.
- Any change to a plugin file invalidates approval and requires re-approval.

## 3. Submission Requirements
- Source file: a single `.py` file under `plugins/`.
- Recommended: include a short header block with: Name, Version, Author, Description, and Website/GitHub.
- Optional: `plugin.manifest.json` next to the plugin file with fields:
  - `plugin_id`, `name`, `version`, `developer_id`, `homepage`.

## 4. Prohibited Plugins
Plugins must not:
- Violate laws, platform rules, or game ToS.
- Implement cheats, bypass security, or enable unauthorized access.
- Exfiltrate data, perform crypto-mining, or include malware.
- Impersonate official plugins or misuse branding.

## 5. Security & Integrity
- The Software computes a SHA-256 hash of each plugin. Approval binds a plugin version (hash) to approval metadata.
- Modifying a plugin file changes its hash and removes approval; re-approval is required.
- Licensor may revoke approvals at any time.

## 6. Distribution
- Distribute only via Licensor-approved channels or repositories.
- Do not bundle the Software without permission.
- Do not sell or rent plugins without explicit written approval.

## 7. Updates
- Each update must be reviewed and approved.
- Changelogs are recommended for clarity and review.

## 8. Enforcement
- Unapproved plugins will not load.
- Revoked plugins may be automatically unloaded.
- Repeat violations may lead to developer key revocation and bans.

## 9. Contact
For submissions and questions, open an issue on the official GitHub repository.
