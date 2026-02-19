# FlowMind (text-to-processflow)

FlowMind is an AI-assisted system that converts unstructured, natural-language process descriptions into a structured, machine-readable process flow representation.

Instead of generating static diagrams, FlowMind focuses on producing a deterministic intermediate representation (Process DSL) that can be validated, analyzed, and later rendered into diagrams or integrated into other systems.

# What Problem Does It Solve?

Process teams frequently need to convert procedures, work instructions, and workshop discussions into structured process flows.

This translation is typically:

- Manual
- Time-consuming
- Inconsistent across teams

FlowMind is designed to generate a structured first draft of a process model by extracting process elements from:

- Existing procedures and work instructions
- Transcribed workshops and interviews
- Free-text process descriptions

It helps process engineers move faster from "blank page" to a reviewable, structured draft — so teams can focus on validation and improvement rather than initial modeling.

# System Architecture (Current State)

FlowMind is intentionally built in layered stages:

- Text
- LLM Extraction (planned / in progress)
- Process DSL (JSON)
- Deterministic Format Validator
- (Next: Semantic Validator)
  
The deterministic validator ensures structural integrity before any higher-level reasoning occurs.

# How It Works (Conceptual)

1) Text Ingestion
The user provides free text or structured documentation.

2) Structured Extraction
An LLM extracts process elements strictly based on the provided content.

3) Deterministic Format Validation
The extracted DSL is validated using strict structural rules.

4) Structured Output
The result is returned as JSON-based Process DSL suitable for review and further modeling.

FlowMind does not invent missing information.

Structural gaps are surfaced as open questions.

## Output Format: Process DSL (v1)

FlowMind outputs a JSON-based Process DSL inspired by EPC logic.

The DSL contains:

- nodes
- edges
- open_questions
- assumptions
- notes

## Node Types

The DSL supports three node types:
- event
- activity
- decision

A valid process:
- starts with an event
- ends with an event
- may contain any combination of node types in between

Strict alternation is NOT enforced at format level.

## Node Structure (v1)
Each node contains:
```json
{
  "id": "EV00 | AC00 | DE00",
  "type": "event | activity | decision",
  "label": "string",
  "responsible": "position or team",
  "confidence": "low | mid | high",
  "reference": {
    "kind": "text | doc_clause | transcript | inferred_boundary",
    "value": ["one or more source references"]
  }
}
```

## ID Rules (Deterministic)

IDs follow a strict structural pattern:
- Events → EV00–EV99
- Activities → AC00–AC99
- Decisions → DE00–DE99

Regex:
```json
^(EV|AC|DE)\d{2}$
```

The ID prefix must match the node type.

This rule is enforced by the deterministic validator.

## Deterministic Format Validator (v1.2)
The format validator enforces:
- Required top-level structure (nodes, edges)
- Required node fields
- ID format and prefix alignment
- Allowed node types
- Allowed confidence values
- Reference structure integrity
- Edge structure validity
- Unknown field detection

All validation errors are returned in a structured format:
```json
{
  "entity": "node | edge | payload",
  "entity_id": "optional",
  "field": "field_name",
  "code": "error_code",
  "message": "human readable explanation",
  "expected": "...",
  "received": "..."
}
```

This structured error system enables:
- GUI-based validation feedback
- Selective repair logic
- LLM repair loops
- Future human-in-the-loop correction workflows

## Design Principles

FlowMind follows strict architectural principles:
- Deterministic before probabilistic
- Validation before rendering
- No invented information
- Human-in-the-loop by design
- Traceability to source text

## Limitations (By Design)

FlowMind:
- Does not optimize processes
- Does not guarantee business correctness
- Does not produce executable BPMN
- Does not replace expert judgment
- Does not auto-correct semantic inconsistencies (yet)

## How to Run (Local)
```json
cd backend
python app/main.py ../examples/input_sample.txt --out output.json
```

## Configuration

Future versions will require an OpenAI API key for LLM-based extraction.

The API key will be supplied via environment variable and never stored in the repository.

## Roadmap

Next development stages:
- Semantic Validator
- LLM-based DSL extraction
- Repair loop architecture
- GUI validation layer
- Diagram rendering layer

