# AI Functions in Microsoft Fabric

> **Author:** Abdul Rasheed Feroz Khan — Director, CodeSizzler | Microsoft MVP & MCT Community Lead  
> **Platform:** Microsoft Fabric (Notebook / PySpark + Pandas)  
> **Tags:** `Microsoft Fabric` `SynapseML` `AI Functions` `Sentiment Analysis` `NLP` `Text Translation` `PySpark` `Pandas` `LLM`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Microsoft Fabric Workspace                  │
│                                                                 │
│  ┌──────────────┐    ┌────────────────────────────────────────┐ │
│  │   Lakehouse   │    │         Fabric Notebook (PySpark)      │ │
│  │  (Data Store) │◄──►│                                        │ │
│  └──────────────┘    │  pandas / Spark DataFrame               │ │
│                      │        │                                │ │
│                      │        ▼                                │ │
│                      │  synapse.ml.aifunc (.ai accessor)       │ │
│                      │        │                                │ │
│                      │        ▼                                │ │
│                      │  ┌─────────────────────────────────┐   │ │
│                      │  │  Fabric AI Functions (LLM-backed)│   │ │
│                      │  │  • similarity   • classify       │   │ │
│                      │  │  • sentiment    • extract        │   │ │
│                      │  │  • fix_grammar  • summarize      │   │ │
│                      │  │  • translate    • generate       │   │ │
│                      │  └─────────────────────────────────┘   │ │
│                      └────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| Microsoft Fabric | Latest | Cloud analytics platform |
| SynapseML Core | 1.0.11.dev1 | ML framework for Spark |
| SynapseML Internal | 1.0.11.1.dev1 | AI Functions library |
| Apache Spark | 3.5 | Distributed data processing |
| Python | 3.11 | Notebook runtime |
| OpenAI SDK | 1.30 | LLM API integration |
| httpx | 0.27.0 | HTTP client (pinned for compatibility) |
| HuggingFace Transformers | 4.37.2 | Pre-trained NLP models |
| pandas | 2.1.4 | DataFrame manipulation |
| tqdm | 4.65.0 | Progress visualization |

---

## Known Issues & Notes

- **Dependency conflicts:** `nni` requires `filelock<3.12` but the installed version is `3.13.1`; `datasets` requires `fsspec<=2024.3.1` but `2024.6.1` is installed. These conflicts are non-blocking for the AI functions demonstrated here.
- **Kernel restart required:** After the initial `%pip install` cells, the PySpark kernel must be restarted before importing `synapse.ml.aifunc`.
- **HuggingFace model download:** The first run of the `sentiment-analysis` pipeline downloads `distilbert-base-uncased-finetuned-sst-2-english` (~268 MB). Subsequent runs use the cached model.
- **AI output review:** As noted in the notebook, always review AI function outputs for errors or hallucinations before using them in downstream processes. Refer to [Azure AI Preview Terms](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) for usage guidance.

---

## References

- [Microsoft Fabric AI Functions Documentation](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/ai-functions-overview)
- [SynapseML GitHub Repository](https://github.com/microsoft/SynapseML)
- [HuggingFace DistilBERT SST-2](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english)
- [Azure AI Preview Supplemental Terms](https://azure.microsoft.com/support/legal/preview-supplemental-terms/)
- [Microsoft Fabric Documentation Hub](https://learn.microsoft.com/en-us/fabric/)

---

*Built with ❤️ on Microsoft Fabric by [Abdul Rasheed Feroz Khan](https://www.linkedin.com/in/arfk/) — Microsoft MVP | MCT Community Lead | CEO, CodeSizzler*
