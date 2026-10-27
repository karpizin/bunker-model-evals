# Contributing

Contributions should improve reproducible model evaluation rather than add
product-specific behavior.

Before opening a change:

1. keep model weights, secrets, private inputs, and machine-local logs out of Git;
2. version the corpus or rubric whenever scoring behavior changes;
3. retain failed and excluded runs with an explicit reason;
4. document model provenance, quantization, runtime, hardware, and generation settings;
5. run `make test`, `make smoke`, and `make public-audit`.

Application and module tests belong in their owning private repositories, not
in this model-evaluation repository.
