from __future__ import annotations

from typing import Any

import re

ID_PATTERN = re.compile(r"^(EV|AC|DE)\d{2}$")

ALLOWED_NODE_TYPES = {"event", "activity", "decision"}
ALLOWED_CONFIDENCE = {"low", "mid", "high"}
ALLOWED_REFERENCE_KINDS = {"text", "doc_clause", "transcript", "inferred_boundary"}

TYPE_TO_PREFIX = {
    "event": "EV",
    "activity": "AC",
    "decision": "DE",
}

def _err(
    *,
    entity: str,
    entity_id: str | None,
    field: str,
    code: str,
    message: str,
    expected: Any | None = None,
    received: Any | None = None,
) -> dict[str, Any]:
    e: dict[str, Any] = {
        "entity": entity,
        "entity_id": entity_id,
        "field": field,
        "code": code,
        "message": message,
    }
    if expected is not None:
        e["expected"] = expected
    if received is not None:
        e["received"] = received
    return e



def validate_dsl_v1(payload: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    """
    Minimal validator for FlowMind Process DSL v1.

    Returns:
        (is_valid, errors)
    """
    errors: list[dict[str, Any]] = []

    # Top-level keys
    nodes = payload.get("nodes")
    edges = payload.get("edges")

    if not isinstance(nodes, list):
        errors.append(
            _err(
                entity="payload",
                entity_id=None,
                field="nodes",
                code="invalid_type",
                message="Top-level field 'nodes' must be a list.",
                expected="list",
                received=type(nodes).__name__,
            )
        )
        nodes = []

    if not isinstance(edges, list):
        errors.append(
            _err(
                entity="payload",
                entity_id=None,
                field="edges",
                code="invalid_type",
                message="Top-level field 'edges' must be a list.",
                expected="list",
                received=type(nodes).__name__,
            )
        )
        edges = []
        

    # Node validation
    required_node_fields = {"id", "type", "label", "responsible", "confidence", "reference"}

    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(
                _err(
                    entity="node",
                    entity_id=None,
                    field="*",
                    code="invalid_structure",
                    message="Each item in 'nodes' must be an object/dict.",
                    expected="dict",
                    received=type(node).__name__,
                )
            )
            continue

        missing = required_node_fields - set(node.keys())
        if missing:
            # If id is present and valid, we can attach entity_id; otherwise keep None
            node_id_for_error = node_id if (isinstance(node.get("id"), str) and node_id is not None and ID_PATTERN.match(node_id)) else None

            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id_for_error,
                    field="*",
                    code="missing_required_field",
                    message="Node is missing required fields.",
                    expected=sorted(required_node_fields),
                    received=sorted(set(node.keys())),
                )
            )


        node_id_raw = node.get("id")
        node_id: str | None = None

        if not isinstance(node_id_raw, str) or not node_id_raw.strip():
            errors.append(
                _err(
                    entity="node",
                    entity_id=None,
                    field="id",
                    code="invalid_type",
                    message="Node id must be a non-empty string.",
                    expected="string (non-empty)",
                    received=node_id_raw,
                )
            )
        else:
            node_id = node_id_raw.strip()
            if not ID_PATTERN.match(node_id):
                errors.append(
                    _err(
                        entity="node",
                        entity_id=None,  # don't trust invalid ids
                        field="id",
                        code="invalid_value",
                        message="Node id must match pattern ^(EV|AC|DE)\d{2}$ (e.g., EV1, AC12, DE3).",
                        expected="^(EV|AC|DE)\d{2}$",
                        received=node_id,
                    )
                )

        node_type = node.get("type")
        if node_type not in ALLOWED_NODE_TYPES:
            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id if (node_id is not None and ID_PATTERN.match(node_id)) else None,
                    field="type",
                    code="invalid_value",
                    message=f"Node type must be one of {sorted(ALLOWED_NODE_TYPES)}.",
                    expected=sorted(ALLOWED_NODE_TYPES),
                    received=node_type,
                )
            )

        expected_prefix = TYPE_TO_PREFIX.get(node_type)

        if expected_prefix is not None and not node_id.startswith(expected_prefix):
            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id,
                    field="id",
                    code="invalid_value",
                    message=f"Node id prefix must match node.type. For type '{node_type}', id must start with '{expected_prefix}'.",
                    expected=f"{expected_prefix}00..{expected_prefix}99",
                    received=node_id,
                )
            )

        label = node.get("label")
        if not isinstance(label, str) or not label.strip():
            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id if (node_id is not None and ID_PATTERN.match(node_id)) else None,
                    field="label",
                    code="invalid_type",
                    message="Node label must be a non-empty string.",
                    expected="string (non-empty)",
                    received=label,
                )
            )

        responsible = node.get("responsible")
        if not isinstance(responsible, str) or not responsible.strip():
            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id if (node_id is not None and ID_PATTERN.match(node_id)) else None,
                    field="responsible",
                    code="invalid_type",
                    message="Node responsible must be a non-empty string (position or team).",
                    expected="string (non-empty)",
                    received=responsible,
                )
            )

        confidence = node.get("confidence")
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id if (node_id is not None and ID_PATTERN.match(node_id)) else None,
                    field="confidence",
                    code="invalid_value",
                    message=f"Node confidence must be one of {sorted(ALLOWED_CONFIDENCE)}.",
                    expected=sorted(ALLOWED_CONFIDENCE),
                    received=confidence,
                )
            )

        reference = node.get("reference")
        if not isinstance(reference, dict):
            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id if (node_id is not None and ID_PATTERN.match(node_id)) else None,
                    field="reference",
                    code="invalid_structure",
                    message="Node reference must be an object with 'kind' and 'value'.",
                    expected="dict with keys: kind, value",
                    received=type(reference).__name__ if reference is not None else None,
                )
            )
            continue

        kind = reference.get("kind")
        if kind not in ALLOWED_REFERENCE_KINDS:
            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id if (node_id is not None and ID_PATTERN.match(node_id)) else None,
                    field="reference.kind",
                    code="invalid_value",
                    message=f"reference.kind must be one of {sorted(ALLOWED_REFERENCE_KINDS)}.",
                    expected=sorted(ALLOWED_REFERENCE_KINDS),
                    received=kind,
                )
            )

        value = reference.get("value")
        if not isinstance(value, list) or len(value) == 0:
            errors.append(
                _err(
                    entity="node",
                    entity_id=node_id if (node_id is not None and ID_PATTERN.match(node_id)) else None,
                    field="reference.value",
                    code="invalid_type",
                    message="reference.value must be a non-empty list of strings.",
                    expected="list[string] (non-empty)",
                    received=value,
                )
            )
        else:
            for j, v in enumerate(value):
                if not isinstance(v, str) or not v.strip():
                    errors.append(
                        _err(
                            entity="node",
                            entity_id=node_id if (node_id is not None and ID_PATTERN.match(node_id)) else None,
                            field=f"reference.value[{j}]",
                            code="invalid_type",
                            message="Each item in reference.value must be a non-empty string.",
                            expected="string (non-empty)",
                            received=v,
                        )
                    )

    # Edge validation (strict shape for v1)
    allowed_edge_fields = {"from", "to", "condition"}

    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(
                _err(
                    entity="edge",
                    entity_id=None,
                    field="*",
                    code="invalid_structure",
                    message="Each item in 'edges' must be an object/dict.",
                    expected="dict",
                    received=type(edge).__name__,
                )
            )
            continue

        extra = set(edge.keys()) - allowed_edge_fields
        if extra:
            errors.append(
                _err(
                    entity="edge",
                    entity_id=None,
                    field="*",
                    code="unknown_field",
                    message="Edge has unknown fields.",
                    expected=sorted(allowed_edge_fields),
                    received=sorted(extra),
                )
            )

        if "from" not in edge or "to" not in edge:
            errors.append(
                _err(
                    entity="edge",
                    entity_id=None,
                    field="*",
                    code="missing_required_field",
                    message="Edge must include 'from' and 'to' fields.",
                    expected=["from", "to"],
                    received=sorted(edge.keys()),
                )
            )
            continue

        edge_from = edge.get("from")
        edge_to = edge.get("to")

        if not isinstance(edge_from, str) or not edge_from.strip():
            errors.append(
                _err(
                    entity="edge",
                    entity_id=None,
                    field="from",
                    code="invalid_type",
                    message="Edge 'from' must be a non-empty string.",
                    expected="string (non-empty)",
                    received=edge_from,
                )
            )

        if not isinstance(edge_to, str) or not edge_to.strip():
            errors.append(
                _err(
                    entity="edge",
                    entity_id=None,
                    field="to",
                    code="invalid_type",
                    message="Edge 'to' must be a non-empty string.",
                    expected="string (non-empty)",
                    received=edge_to,
                )
            )

        if "condition" in edge:
            cond = edge.get("condition")
            if not (isinstance(cond, str) and cond.strip()):
                errors.append(
                    _err(
                        entity="edge",
                        entity_id=None,
                        field="condition",
                        code="invalid_type",
                        message="Edge 'condition' must be a non-empty string when provided.",
                        expected="string (non-empty)",
                        received=cond,
                    )
                )


    return (len(errors) == 0), errors
