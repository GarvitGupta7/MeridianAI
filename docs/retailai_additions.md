# Historical RetailAI Nexus integration note

RetailAI Nexus was the historical name of the advanced modelling layer that was merged into MeridianAI. This file is retained only to explain that evolution; it is not a description of a separate current product.

## Current state

- MeridianAI is the authoritative project name.
- `src/retailai_engine/` remains the advanced ML package name for compatibility.
- The advanced functionality is integrated into `dashboard.py`.
- Advanced API routes are defined in `src/api/retailai.py`.
- The router is included by `src/retail_segmentation/api.py` without a path prefix.
- There is no current `/retailai/*` API namespace.

Integrated capabilities include advanced segmentation, Isolation Forest, churn model comparison, reusable preprocessing, forecast comparison and uncertainty, recommendation methods, explainability, customer scoring, and model comparison.

## Compatibility rule

Do not rename packages, artifacts, serialized class paths, or API routes solely to remove the historical `retailai` name without first evaluating import compatibility, model deserialization, tests, deployment configuration, and downstream clients.

Future user-facing documentation should use MeridianAI. The historical name should appear only where needed to explain evolution or match an existing technical identifier.
