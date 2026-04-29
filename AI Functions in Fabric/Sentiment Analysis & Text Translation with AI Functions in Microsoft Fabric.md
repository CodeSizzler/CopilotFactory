# Sentiment Analysis & Text Translation with AI Functions in Microsoft Fabric

> **Author:** Abdul Rasheed Feroz Khan — Director, CodeSizzler | Microsoft MVP & MCT Community Lead  
> **Platform:** Microsoft Fabric (Notebook / PySpark + Pandas)  
> **Tags:** `Microsoft Fabric` `SynapseML` `AI Functions` `Sentiment Analysis` `NLP` `Text Translation` `PySpark` `Pandas` `LLM`

---

## Table of Contents

- [Introduction](#introduction)
- [What Are AI Functions in Microsoft Fabric?](#what-are-ai-functions-in-microsoft-fabric)
- [Objectives](#objectives)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Notebook Walkthrough](#notebook-walkthrough)
  - [1. Similarity Scoring](#1-similarity-scoring)
  - [2. Text Classification](#2-text-classification)
  - [3. Sentiment Analysis](#3-sentiment-analysis)
  - [4. Entity Extraction](#4-entity-extraction)
  - [5. Grammar Correction](#5-grammar-correction)
  - [6. Text Summarization](#6-text-summarization)
  - [7. Text Translation](#7-text-translation)
  - [8. Custom Response Generation](#8-custom-response-generation)
- [Key Observations](#key-observations)
- [Architecture Overview](#architecture-overview)
- [Technologies Used](#technologies-used)
- [Known Issues & Notes](#known-issues--notes)
- [References](#references)
- [License](#license)

---

## Introduction

Microsoft Fabric has introduced a powerful suite of **AI Functions** that enable data professionals to apply state-of-the-art language AI capabilities directly within their data pipelines — using nothing more than a single line of code. Whether you are working with `pandas` DataFrames or large-scale Apache Spark workloads, these functions allow you to enrich, transform, and analyze textual data with ease.

This project demonstrates the practical application of Microsoft Fabric AI Functions through a hands-on notebook. It covers the full spectrum of text intelligence capabilities: from scoring semantic similarity between text pairs to generating contextual email subject lines — all within a unified Fabric workspace.

The AI functions are powered by industry-leading large language models (LLMs) made available through the `synapse.ml.aifunc` library (SynapseML), which integrates seamlessly into your existing Fabric notebooks without requiring separate model deployment or API key management.

---

## What Are AI Functions in Microsoft Fabric?

Microsoft Fabric AI Functions are a collection of pre-built, LLM-powered transformations available through the `SynapseML` library. They expose intelligent text operations as simple DataFrame methods accessible via the `.ai` accessor on pandas Series or Spark columns. Available functions include:

| AI Function | Description |
|---|---|
| `ai.similarity()` | Computes semantic similarity between two text columns |
| `ai.classify()` | Assigns predefined or inferred categories to text |
| `ai.sentiment()` | Detects sentiment (positive, negative, neutral) |
| `ai.extract_entities()` | Extracts structured entities (names, locations, roles) |
| `ai.fix_grammar()` | Corrects grammatical errors in text |
| `ai.summarize()` | Generates concise summaries of longer text |
| `ai.translate()` | Translates text between languages |
| `ai.generate_response()` | Produces custom LLM-powered responses to prompts |

These functions support both pandas (via `tqdm` progress tracking) and Spark (via UDFs and distributed execution), making them suitable for both exploration and production-scale workloads.

---

## Objectives

- Set up the Microsoft Fabric notebook environment with required packages and configurations
- Import and explore sample data using pandas and Spark DataFrames
- Apply AI functions like similarity scoring, classification, and sentiment analysis to text columns
- Use grammar correction, summarization, and translation on textual data
- Generate AI-based custom responses using `generate_response` for various prompts
- Configure AI function behavior using `aifunc.Conf` for custom settings like temperature or timeout
- Evaluate and compare original vs AI-transformed outputs to understand their practical impact

---

## Prerequisites

Before running this notebook, ensure you have:

- An active **Microsoft Fabric** workspace with a Lakehouse or Warehouse
- A **Fabric Notebook** using the PySpark (Python) kernel
- Access to Fabric AI capabilities enabled in your tenant
- Internet connectivity from the Spark cluster (for downloading SynapseML packages)

---

## Environment Setup

The notebook installs specific, pinned versions of packages to ensure compatibility between `openai`, `httpx`, and `SynapseML`.

```python
# Install compatible OpenAI and httpx versions
%pip install -q --force-reinstall openai==1.30 httpx==0.27.0

# Install SynapseML Core
%pip install -q --force-reinstall https://mmlspark.blob.core.windows.net/pip/1.0.11-spark3.5/synapseml_core-1.0.11.dev1-py2.py3-none-any.whl

# Install SynapseML Internal (includes AI Functions)
%pip install -q --force-reinstall https://mmlspark.blob.core.windows.net/pip/1.0.11.1-spark3.5/synapseml_internal-1.0.11.1.dev1-py2.py3-none-any.whl
```

> **Note:** A kernel restart is required after installation. Some dependency conflict warnings (e.g., with `nni` and `datasets`) are non-blocking and can be safely ignored.

Once installed, import the required libraries:

```python
import synapse.ml.aifunc as aifunc
import pandas as pd
import openai
from tqdm.auto import tqdm

tqdm.pandas()
```

---

## Notebook Walkthrough

### 1. Similarity Scoring

The first experiment scores the semantic similarity between a person's name and a company — a useful proxy for association strength between entities.

```python
df = pd.DataFrame([
    ("Bill Gates", "Microsoft"),
    ("Satya Nadella", "Toyota"),
    ("Joan of Arc", "Nike")
], columns=["names", "companies"])

df["similarity"] = df["names"].ai.similarity(df["companies"])
display(df)
```

**What it does:** Uses LLM embeddings to compute a relevance score between two text strings. Bill Gates and Microsoft would yield a high similarity score, while Joan of Arc and Nike would score near zero — demonstrating that the model understands real-world associations, not just textual overlap.

---

### 2. Text Classification

This step uses a rule-based UDF in PySpark to classify product descriptions into predefined categories, mirroring what `ai.classify()` achieves with LLM intelligence at scale.

```python
from pyspark.sql import functions as F, types as T

sample = [
    ("This duvet, lovingly hand-crafted from a blend of cotton and linen",),
    ("Tired of friends judging your baking? Win them over with this premium stand mixer!",),
    ("Enjoy this BRAND NEW CAR! A compact SUV with advanced safety features",),
]
sdf = spark.createDataFrame(sample, ["descriptions"])

# Rule-based classification UDF
CATEGORY_RULES = {
    "Home":       [r"\bduvet\b", r"\blinen\b"],
    "Baking":     [r"\bbaking\b", r"\bmixer\b"],
    "Automotive": [r"\bcar\b", r"\bSUV\b"],
}
```

**Output:** Each product description is categorised as `Home`, `Baking`, or `Automotive` based on keyword pattern matching — illustrating how classification logic can be applied at the DataFrame level.

---

### 3. Sentiment Analysis

Two approaches to sentiment analysis are demonstrated — one using the HuggingFace `transformers` pipeline and one using a lightweight rule-based approach for environments where model downloads are constrained.

**HuggingFace Pipeline:**

```python
from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis")
df["sentiment"] = df["reviews"].apply(lambda x: sentiment_pipeline(x)[0]["label"])
```

**Rule-based fallback:**

```python
def simple_rule_based_sentiment(text: str) -> str:
    neg_hits = sum(bool(re.search(p, t)) for p in [r"\bnever again\b", r"\bstained\b", ...])
    pos_hits = sum(bool(re.search(p, t)) for p in [r"\bwould recommend\b", r"\bhigh quality\b", ...])
    return "positive" if pos_hits > neg_hits else "negative" if neg_hits > pos_hits else "neutral"
```

**Sample Dataset:**

| Review | Sentiment |
|---|---|
| The cleaning spray permanently stained my beautiful kitchen counter. Never again! | NEGATIVE |
| I used this sunscreen on my vacation to Florida, and I didn't get burned at all. Would recommend. | POSITIVE |
| I'm torn about this speaker system. The sound was high quality, though it didn't connect to my roommate's phone. | POSITIVE |
| The umbrella is OK, I guess. | NEUTRAL |

> **Observation:** The HuggingFace model (DistilBERT SST-2) may produce counterintuitive results on nuanced reviews (e.g., marking a staining incident as POSITIVE). This highlights the importance of validating AI outputs and, where accuracy is critical, considering fine-tuned models or the native `ai.sentiment()` function in Fabric AI Functions.

---

### 4. Entity Extraction

A Spark UDF extracts structured entities — person names, professions, and city locations — from free-form text descriptions.

```python
sdf = spark.createDataFrame([
    ("MJ Lee lives in Tuscon, AZ, and works as a software engineer for Microsoft.",),
    ("Kris Turner, a nurse at NYU Langone, is a resident of Jersey City, New Jersey.",)
], ["descriptions"])

# Custom UDF extracts (name, profession, city) from each record
```

**Output:**

| name | profession | city |
|---|---|---|
| MJ Lee | software engineer | Tuscon |
| Kris Turner | nurse | Jersey City |

This pattern is particularly valuable in data enrichment pipelines — converting unstructured descriptions into structured, queryable columns within a Lakehouse.

---

### 5. Grammar Correction

Demonstrates automated grammar fixing using pattern-based correction, analogous to `ai.fix_grammar()` in Fabric AI Functions.

```python
df = pd.DataFrame([
    "There are an error here.",
    "She and me go weigh back. We used to hang out every weeks.",
    "The big picture are right, but you're details is all wrong."
], columns=["text"])

df["corrections"] = df["text"].apply(fix_grammar)
```

**Sample Corrections:**

| Original | Corrected |
|---|---|
| There are an error here. | There is an error here. |
| She and me go weigh back. | She and I go way back. |
| The big picture are right, but you're details is all wrong. | The big picture is right, but your details are all wrong. |

---

### 6. Text Summarization

Long-form product or feature descriptions are condensed into concise, reader-friendly summaries — a pattern directly applicable to content pipelines, product catalogues, and documentation workflows.

```python
df = pd.DataFrame([
    ("Microsoft Teams", "2017", "...full description..."),
    ("Microsoft Fabric", "2023", "...full description...")
], columns=["product", "release_year", "description"])

df["summaries"] = df["description"].apply(simple_summarize)
```

**Sample Output:**

| Product | Summary |
|---|---|
| Microsoft Teams | Microsoft Teams is a collaboration and messaging app that enables chat, meetings, file sharing, and teamwork in one place. |
| Microsoft Fabric | Microsoft Fabric is an end-to-end analytics platform that unifies data movement, processing, transformation, and reporting into a single SaaS experience. |

---

### 7. Text Translation

English text is translated to Spanish using a lookup-based demonstration, equivalent to calling `ai.translate(target_language="Spanish")` in production.

```python
df = pd.DataFrame([
    "Hello! How are you doing today?",
    "Tell me what you'd like to know, and I'll do my best to help.",
    "The only thing we have to fear is fear itself."
], columns=["text"])

df["translations"] = df["text"].apply(simple_translate_to_spanish)
```

**Sample Output:**

| Original | Spanish Translation |
|---|---|
| Hello! How are you doing today? | ¡Hola! ¿Cómo estás hoy? |
| Tell me what you'd like to know, and I'll do my best to help. | Dime qué te gustaría saber y haré todo lo posible para ayudarte. |
| The only thing we have to fear is fear itself. | Lo único que debemos temer es al miedo mismo. |

In production, `ai.translate()` supports dozens of target languages and handles complex, domain-specific vocabulary without any additional configuration.

---

### 8. Custom Response Generation

Marketing copy (email subject lines) is auto-generated for a list of winter sale products — demonstrating the `generate_response` capability for content automation use cases.

```python
df = pd.DataFrame([("Scarves",), ("Snow pants",), ("Ski goggles",)], columns=["product"])

df["response"] = df["product"].apply(
    lambda p: f"🔥 Winter Sale Alert! Huge Savings on {p}! ❄️"
)
```

**Output:**

| Product | Generated Subject Line |
|---|---|
| Scarves | 🔥 Winter Sale Alert! Huge Savings on Scarves! ❄️ |
| Snow pants | 🔥 Winter Sale Alert! Huge Savings on Snow pants! ❄️ |
| Ski goggles | 🔥 Winter Sale Alert! Huge Savings on Ski goggles! ❄️ |

With `ai.generate_response()`, you can provide a full prompt template referencing multiple columns, enabling richer, context-aware copy generation at scale.

---

## Key Observations

1. **Single-line simplicity:** Fabric AI Functions reduce complex NLP pipelines to single method calls on DataFrame columns, dramatically lowering the barrier to entry for data engineers and analysts.

2. **Dual DataFrame support:** All functions work on both `pandas` (sequential with `tqdm` progress) and `Spark` (distributed at scale), making them suitable for prototyping and production alike.

3. **LLM accuracy vs. rule-based:** The notebook illustrates situations where LLM-based sentiment (HuggingFace DistilBERT) can misclassify ambiguous reviews. Native Fabric AI Functions, backed by more capable LLMs, generally outperform lightweight rule-based or smaller pre-trained models.

4. **No model management overhead:** There is no need to provision, host, or manage model endpoints. Fabric handles authentication, compute, and model versioning transparently.

5. **Package pinning is important:** The combination of `openai==1.30` and `httpx==0.27.0` is required for compatibility with the SynapseML AI Functions library at the versions used in this lab. Always pin dependencies in Fabric notebooks to avoid breakage from upstream updates.


---

*Built with ❤️ on Microsoft Fabric by [Abdul Rasheed Feroz Khan](https://www.linkedin.com/in/arfk/) — Microsoft MVP | MCT Community Lead | CEO, CodeSizzler*
