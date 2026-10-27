# Repository scope

## Included

- evaluations comparing base, instruct, fine-tuned, abliterated, and uncensored models;
- quantization, inference-speed, stability, and context-window studies;
- model tool-call syntax and agent-contract compatibility;
- local and hosted model runners, corpora, scorers, and public result artifacts;
- deterministic rescoring and publication tooling.

## Excluded

- Bunker AI module or product acceptance tests;
- private runtime, deployment, release-lock, and cross-user isolation tests;
- Memory, EV News, Protocolist, Geo, or other application-specific pipelines;
- customer data, private corpora, credentials, model weights, and raw machine logs.

When a test answers “which model or serving configuration performs better?”, it
normally belongs here. When it answers “does a Bunker AI product or module work
correctly?”, it belongs in the private evaluation repository.
