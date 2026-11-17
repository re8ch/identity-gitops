# Cross-organization context

References across organizations use `owner/repository#number` or a full GitHub
URL. A bare `#number` addresses this repository. The reviewed graph is stored in
`governance/cross-org-context.json` and connects parent Issues, sub-issues, pull
requests, Projects and evidence without creating a second tracker.

GitHub Pages publishes sanitized static context. Runtime observations, captured
Kubernetes output and investigations remain in Discussions, Wiki or the
observability backend.
