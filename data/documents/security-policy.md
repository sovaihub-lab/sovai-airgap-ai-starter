# Security and Identity Policy

All enterprise AI applications must use single sign-on, multi-factor authentication, and least-privilege access controls.

Systems handling confidential or restricted documents must enforce access filtering before retrieval. Restricted document content must not enter model context unless the requesting user is authorized.

Runtime services in air-gapped environments must not download packages, models, prompts, or tools directly from the public internet. Approved artifacts must be imported through the internal artifact hub.

Agentic AI systems may execute only approved local tools. Any attempt to use unapproved tools, web search, or uncontrolled external APIs must be blocked and written to the audit log.

Security events must be retained in an append-only audit log with timestamp, action type, input reference, policy result, and runtime identity.
