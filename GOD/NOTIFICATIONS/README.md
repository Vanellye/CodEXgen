# ERIA notifications

Default requested destination: vanellyetm@gmail.com.

Send only after the user connects and authorizes an email provider. Store credentials only in provider-managed secrets; never in Git, GOD originals, PLZ fingerprints, logs, or application config.

Suggested alert classes: critical preservation failure; authorization needed; repeated transmission failure; unresolved dependency; successful resolution. Include PLZ ID, timestamp, reason code, affected record IDs, and a secure link to the local/repository record where available. Avoid sending raw source payloads or secrets.

Delivery is best-effort. Record provider message ID and outcome without logging credentials. If email is unavailable, keep the alert queued and create a PLZ notification-delivery failure fingerprint. Do not claim an email was sent until the provider confirms acceptance.
