# Approved ProsperoCraft authentication

Authentication development now uses the user-approved public application client ID `f0c7635e-8d50-4d7e-afa3-d15db4a0a3d3`. This is a source-only change. Public build 119, its release assets and ProsperoStore listing are unchanged; no app version bump, branch merge or Store publication is part of this task.

## Protocol changes

Microsoft device authorization uses `https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode`, with `client_id` and `scope=XboxLive.signin offline_access`. Device-code polling and refresh both use the matching `/consumers/oauth2/v2.0/token` endpoint. The device request no longer sends the legacy response_type field or Mojang service scope. No client secret is used in this public-client flow.

The Microsoft access token is passed to Xbox as an RPS ticket with the `d=` prefix. The existing Xbox user-token, XSTS relying party, user-hash consistency check, Minecraft token exchange, entitlement check and Java profile validation remain in place. Minecraft access tokens still reach only the existing authorized launch/session path; credentials and raw service responses remain excluded from diagnostics.

The consumer authority/device grant follows [Microsoft's device-code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-device-code). The Xbox custom-application ticket convention is also documented by the [XboxReplay authentication implementation](https://github.com/XboxReplay/xboxlive-auth/blob/master/docs/02-Custom_Azure_Application.md). Microsoft documents that [refresh credentials are bound to user and client](https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens), so changing the client ID cannot safely reuse an old app's refresh credential.

## Saved-login transition

The previous encrypted account format did not identify the issuing client. It is now treated as untrusted for this application's refresh flow. Loading it raises a dedicated fresh-sign-in result before decryption or any network request. The launcher stays signed out and displays: “Sign in again to use the approved ProsperoCraft application.” It does not silently submit the old refresh token with the new ID, request a device code without user action, or relabel the old token.

Fresh sign-ins save the refresh credential using an encrypted v2 format. Its public header contains the client ID and is authenticated as AES-GCM associated data. Another client's header is refused before refresh; changing a header to relabel foreign ciphertext fails authentication. Existing file bounds, private-mode attempts, symlink checks, staging, key handling and sign-out cleanup remain. The app-local encryption key is still not a hardware-backed keychain.

After a fresh sign-in, saved restoration uses the approved application's refresh credential, then performs the same Xbox/XSTS/Minecraft ownership/profile sequence. A rotated refresh token replaces the old value; omission of a replacement retains the current-app credential. Network failures retain it for retry. Revoked credentials follow the existing clear-and-sign-in-again behavior. Legacy files are left untouched until a successful new sign-in replaces the account credential or the user signs out. Instances, worlds, downloaded files and settings are outside the migration.

## Checks

- Scripted device authorization/polling: exact registered ID, consumer v2 endpoints and scopes; no secret or legacy service scope; pending/slowdown/cancellation/expiry/decline paths.
- Xbox ticket prefix, XSTS token/hash checks, Minecraft authorization, ownership rejection and profile validation.
- Refresh retention and rotation, with fresh sign-in refresh-token retention.
- Actual encrypted legacy and foreign-client fixtures through launcher restoration: zero network requests, fresh-sign-in prompt, no old credential decryption/relabeling, authenticated client binding and diagnostic redaction.
- Current-app restoration through the full ownership/profile pipeline, temporary-network-failure retention, revoked-credential cleanup and sign-out.
- Preserved world/cache bytes, instances and non-default settings; existing instance/account UI tests.
- Real local HTTPS transport regression: buffered OAuth errors, redirect refusal, body bounds, TLS certificate/hostname validation and sanitized diagnostics.

The account UI fixture's obsolete exact mailbox-size assertion was narrowed to the account fields it exercises; no UI shape or behavior changed. All relevant checks pass with synthetic credentials/local fixtures. No live Microsoft account was used. Actual PS5 fresh sign-in, Minecraft authorization/profile/skin, and saved restoration after reopening still require validation with the approved app. No Java runtime change is needed.
