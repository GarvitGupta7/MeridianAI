# Security policy

## Project status

MeridianAI is currently an academic and development project. The FastAPI service has no authentication or authorization and must not be exposed directly to the public internet in its current form.

## Reporting a vulnerability

Do not disclose suspected vulnerabilities, credentials, private datasets, or exploitable deployment details in a public issue.

Until a private security contact is formally published, report the problem privately to the repository owner through an appropriate private GitHub or institutional communication channel. Include:

- A concise description of the issue
- Affected commit, component, route, or deployment
- Reproduction steps or proof of concept
- Potential confidentiality, integrity, or availability impact
- Suggested mitigation, if known

Do not access, modify, retain, or publish data beyond what is necessary to demonstrate the issue safely.

## Supported versions

The repository does not yet publish versioned releases. Only the current `main` branch is maintained. A release and support policy should be introduced before production use.

## Known security limitations

- No API authentication or authorization
- No user or role model
- No rate limiting
- No audit-log facility
- No formal secrets-management integration
- No automated dependency or container vulnerability policy
- Uploaded files are processed by application code and require deployment-level size and resource controls
- Database writes replace named tables and require access control and backups
- Serialized joblib artifacts must be treated as trusted inputs; loading untrusted pickle/joblib data can execute code
- No formal privacy-impact assessment or retention policy

## Minimum controls before production

1. Add identity, authentication, and least-privilege authorization.
2. Terminate HTTPS and configure trusted origins and proxies.
3. Apply request, upload, rate, timeout, and resource limits.
4. Store secrets in the deployment platform, not in Git.
5. Restrict database and artifact access.
6. Validate file types and content, not only extensions.
7. Add structured security and access logging without exposing customer data.
8. Scan dependencies and deployment images.
9. Define backup, restoration, incident-response, and disclosure procedures.
10. Conduct threat modelling and privacy review for the intended deployment.

## Data handling

Do not use real retailer or customer data unless collection, processing, retention, access, and deletion are authorized. Customer identifiers should be pseudonymized where possible. Never place credentials, payment data, or unnecessary personal data in demonstration datasets, logs, screenshots, reports, or issue discussions.
