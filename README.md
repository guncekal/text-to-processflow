# FlowMind (text-to-processflow)

FlowMind is an AI-powered system that converts unstructured, natural-language process descriptions into a structured, machine-readable process flow format.

Instead of generating static diagrams, FlowMind focuses on producing a deterministic intermediate representation that can be validated, analyzed, and later rendered into diagrams or integrated into other systems.

# What Problem Does It Solve?

Process teams often need to convert procedures and work instructions into process flows to align documentation with how work is actually executed. This translation is typically manual, time-consuming, and inconsistent across teams.

FlowMind is designed to provide a high-quality first draft of a process flow by extracting structured steps, decisions, roles, and transitions from:

-existing procedures and work instructions (documentation → process draft), and

-transcribed process workshops or interviews (spoken process knowledge → process draft)

This helps process engineers move faster from “blank page” to a reviewable model, so teams can focus on validation, improvement, and standardization rather than initial modeling effort.

# How It Works

FlowMind accepts either free text input or uploaded documents such as procedures, work instructions, or transcribed process discussions (including speech-to-text outputs).

The system operates in four conceptual stages:

1) Text ingestion
   
   The user provides unstructured content describing how a process works. This can be written text or speech-generated transcripts.

2) Process element extraction

   An LLM analyzes the input and extracts core process elements such as activities, decisions, transitions, and referenced roles — strictly based on the provided content.

3) Rule-based process validation
   
   The extracted structure is validated and refined using explicit process rules (e.g. existence of start and end nodes, branching logic for decision points, flow connectivity).

   No missing information is invented; instead, structural gaps or ambiguities are identified.

4) Text-based process flow output
   
   The resulting process flow is returned to the user in a structured, text-based format suitable for review, discussion, and further modeling.

Rather than completing or optimizing the process, FlowMind intentionally surfaces uncertainties (e.g. “a decision point may be required here”) to support critical discussion and collaborative refinement by process teams.

# Core Principles

FlowMind is intentionally designed as a draft-generation and clarification tool, not as an automated process designer.

Its core design principles are:

   - Text to structure, not completion
     
   The system converts unstructured descriptions into a structured process representation without attempting to complete or optimize the process.
   
   - No invented information
     
   Missing steps, roles, or rules are never assumed. Unclear or incomplete areas are explicitly surfaced instead of being filled in.

   - Uncertainty as a feature
     
   Structural gaps (e.g. potential decision points or undefined transitions) are highlighted to trigger discussion and validation by process teams.

   - Rule-driven validation
     
   All outputs are checked against explicit process rules to ensure structural consistency and reviewability.

   - Human-in-the-loop by design
     
   FlowMind supports human judgment rather than replacing it, positioning AI as an accelerator for collaborative process modeling.


# Output Format: Process DSL

FlowMind outputs a lightweight, text-based Process DSL designed for early-stage process modeling, clarification, and review.

The DSL serves as an intermediate representation between unstructured text (procedures, instructions, transcripts) and formal process models or diagrams.

# Core Concepts

The Process DSL follows an EPC-inspired structure with three node types:

- event — a state, trigger, or outcome (e.g. “Request received”, “Milk accepted”)

- activity — an action performed within the process (e.g. “Perform quality check”)
  
- decision — a branching point that splits the flow based on conditions
  
A valid process:

- starts with an event
- ends with an event
- may contain any combination of events, activities, and decisions in between
  
The model does not enforce strict alternation (e.g. event → activity → event).

Instead, structural patterns such as consecutive events are surfaced as open questions rather than being automatically corrected.

# Node Structure (v1)

Each node in the DSL contains the following fields:

```json
{
  "id": "string",
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

- responsible represents a position or team explicitly mentioned or clearly implied
  
- confidence is generated by the LLM and reflects the strength of the extraction, not process correctness
  
- reference always supports traceability back to the source text or document

# Example Output (Simplified)

```json
{
  "nodes": [
    {
      "id": "E1",
      "type": "event",
      "label": "Milk procurement request received",
      "responsible": "Quality Team",
      "confidence": "high",
      "reference": {
        "kind": "text",
        "value": ["Milk procurement request is received."]
      }
    },
    {
      "id": "A1",
      "type": "activity",
      "label": "Perform quality check",
      "responsible": "Quality Team",
      "confidence": "mid",
      "reference": {
        "kind": "doc_clause",
        "value": ["WI-3.1"]
      }
    },
    {
      "id": "D1",
      "type": "decision",
      "label": "Is the milk compliant?",
      "responsible": "Quality Team",
      "confidence": "high",
      "reference": {
        "kind": "text",
        "value": ["If the milk is compliant, it is accepted; otherwise rejected."]
      }
    }
  ],
  "edges": [
    { "from": "E1", "to": "A1" },
    { "from": "A1", "to": "D1" }
  ],
  "open_questions": [
    "What specific criteria define compliance?"
  ],
  "assumptions": [],
  "notes": [
    "Confidence values reflect extraction strength, not business correctness."
  ]
}
```

# Design Intent

The Process DSL is intentionally not:

- a BPMN replacement
  
- an execution or automation language
  
- a tool-specific modeling format
  
Its purpose is to provide a clear, reviewable first draft that helps process teams move from unstructured descriptions to structured discussion and validation.

# Limitations & Non-Goals

FlowMind is intentionally scoped as a process understanding and draft-generation tool, not as a fully automated modeling or execution system.

The following limitations are by design:

- FlowMind does not complete, optimize, or correct processes

Missing activities, roles, or rules are surfaced as open questions instead of being inferred.

- FlowMind does not guarantee process correctness

The output reflects how confidently the structure was extracted from the input, not whether the process itself is valid or compliant.

- FlowMind does not produce executable workflows or BPMN models

The Process DSL is an intermediate representation, not a runtime or automation format.

- FlowMind does not enforce strict modeling conventions

Structural patterns (e.g. consecutive events) are highlighted for discussion rather than automatically fixed.

- FlowMind does not replace human process expertise

It is designed to accelerate review and discussion, not to eliminate expert judgment.

# How to Run

## How to Run (Local)

```bash
cd backend
python app/main.py ../examples/input_sample.txt --out output.json
```
