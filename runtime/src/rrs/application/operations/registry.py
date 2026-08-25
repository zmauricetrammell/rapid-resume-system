"""Validated Operation Specification registry and semantic hashing."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, replace
from hashlib import sha256
from types import MappingProxyType

from rrs.domain.enums import OperationType, RetrievalRequirement
from rrs.domain.operations import OperationSpecification


class OperationRegistryValidationError(ValueError):
    """Raised when the effective operation registry is invalid."""


@dataclass(frozen=True)
class RegistryValidationContext:
    handler_keys: frozenset[str]
    resource_paths: frozenset[str]
    schema_paths: frozenset[str]
    professional_roles: frozenset[str]
    reconciliation_keys: frozenset[str]
    retry_policy_refs: frozenset[str]
    evidence_source_keys: frozenset[str]
    dependency_names: frozenset[str]


def _canonical_payload(spec: OperationSpecification) -> dict[str, object]:
    binding = spec.professional_binding
    output = spec.output_contract
    return {
        "operation_type": spec.operation_type.value,
        "handler_key": spec.handler_key,
        "allowed_lifecycle_phases": sorted(x.value for x in spec.allowed_lifecycle_phases),
        "professional_binding": {
            "professional_role": binding.professional_role,
            "contract": {
                "path": binding.contract.path, 
                "content_hash": binding.contract.content_hash
            },
            "task": {"path": binding.task.path, "content_hash": binding.task.content_hash},
        },
        "required_inputs": list(spec.required_inputs),
        "optional_inputs": list(spec.optional_inputs),
        "identity_dependencies": list(spec.identity_dependencies),
        "freshness_dependencies": list(spec.freshness_dependencies),
        "retrieval": {
            "requirement": spec.retrieval.requirement.value,
            "evidence_source_key": spec.retrieval.evidence_source_key,
        },
        "output_contract": {
            "required_artifact_types": [x.value for x in output.required_artifact_types],
            "coupled_groups": [[x.value for x in group] for group in output.coupled_groups],
            "schemas": [{"path": x.path, "content_hash": x.content_hash} for x in output.schemas],
        },
        "pointer_authority": sorted(
            [{"target": x.target.value, "mutation_type": x.mutation_type.value}
             for x in spec.pointer_authority],
            key=lambda x: (str(x["target"]), str(x["mutation_type"])),
        ),
        "deterministic_reconciliation": list(spec.deterministic_reconciliation),
        "retry_policy_ref": spec.retry_policy_ref,
    }


class OperationSpecificationHasher:
    @staticmethod
    def hash(spec: OperationSpecification) -> str:
        payload = json.dumps(_canonical_payload(spec), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode()).hexdigest()

    @classmethod
    def finalize(cls, spec: OperationSpecification) -> OperationSpecification:
        return replace(spec, specification_hash=cls.hash(spec))


class OperationRegistryHasher:
    @staticmethod
    def hash(specifications: tuple[OperationSpecification, ...]) -> str:
        rows = sorted(
            ((x.operation_type.value, x.specification_hash) for x in specifications),
            key=lambda x: x[0],
        )
        return sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


class RegistryValidator:
    @staticmethod
    def validate(
        specifications: tuple[OperationSpecification, ...],
        context: RegistryValidationContext,
    ) -> None:
        if not specifications:
            raise OperationRegistryValidationError("operation registry must not be empty")
        types = [x.operation_type for x in specifications]
        if len(set(types)) != len(types):
            raise OperationRegistryValidationError("duplicate operation_type")
        for spec in specifications:
            RegistryValidator._validate_spec(spec, context)

    @staticmethod
    def _validate_spec(
        spec: OperationSpecification,
        context: RegistryValidationContext,
    ) -> None:
        prefix = spec.operation_type.value
        if spec.handler_key not in context.handler_keys:
            raise OperationRegistryValidationError(f"{prefix}: missing handler")
        binding = spec.professional_binding
        if binding.contract.path not in context.resource_paths:
            raise OperationRegistryValidationError(f"{prefix}: missing contract resource")
        if binding.task.path not in context.resource_paths:
            raise OperationRegistryValidationError(f"{prefix}: missing task resource")
        if binding.professional_role not in context.professional_roles:
            raise OperationRegistryValidationError(f"{prefix}: unknown professional role")
        if any(x.path not in context.schema_paths for x in spec.output_contract.schemas):
            raise OperationRegistryValidationError(f"{prefix}: missing schema resource")
        if set(spec.deterministic_reconciliation) - context.reconciliation_keys:
            raise OperationRegistryValidationError(
                f"{prefix}: unknown deterministic reconciliation"
            )
        if spec.retry_policy_ref not in context.retry_policy_refs:
            raise OperationRegistryValidationError(f"{prefix}: unknown retry policy")
        if (
            spec.retrieval.requirement is not RetrievalRequirement.NONE
            and spec.retrieval.evidence_source_key not in context.evidence_source_keys
        ):
            raise OperationRegistryValidationError(f"{prefix}: unresolved evidence source")
        authorized = ( 
            set(spec.required_inputs)
            | set(spec.optional_inputs)
            | set(context.dependency_names)
        )
        if not set(spec.identity_dependencies).issubset(authorized):
            raise OperationRegistryValidationError(f"{prefix}: invalid identity dependency")
        if not set(spec.freshness_dependencies).issubset(authorized):
            raise OperationRegistryValidationError(f"{prefix}: invalid freshness dependency")


class OperationSpecificationRegistry:
    def __init__(self, specifications: tuple[OperationSpecification, ...]) -> None:
        if not specifications:
            raise OperationRegistryValidationError("operation registry must not be empty")
        by_type = {x.operation_type: x for x in specifications}
        if len(by_type) != len(specifications):
            raise OperationRegistryValidationError("duplicate operation_type")
        if any(
            x.specification_hash != OperationSpecificationHasher.hash(x)
            for x in specifications
        ):
            raise OperationRegistryValidationError(
                "registry requires finalized specification hashes"
            )
        self._specifications = tuple(sorted(specifications, key=lambda x: x.operation_type.value))
        self._by_type: Mapping[OperationType, OperationSpecification] = MappingProxyType(by_type)
        self._registry_hash = OperationRegistryHasher.hash(self._specifications)

    @classmethod
    def build(
        cls,
        specifications: tuple[OperationSpecification, ...],
        context: RegistryValidationContext,
    ) -> OperationSpecificationRegistry:
        RegistryValidator.validate(specifications, context)
        return cls(tuple(OperationSpecificationHasher.finalize(x) for x in specifications))

    @property
    def registry_hash(self) -> str:
        return self._registry_hash

    def all(self) -> tuple[OperationSpecification, ...]:
        return self._specifications

    def get(self, operation_type: OperationType) -> OperationSpecification:
        try:
            return self._by_type[operation_type]
        except KeyError as exc:
            raise KeyError(f"unknown operation_type: {operation_type.value}") from exc


__all__ = [
    "OperationRegistryHasher",
    "OperationRegistryValidationError",
    "OperationSpecificationHasher",
    "OperationSpecificationRegistry",
    "RegistryValidationContext",
    "RegistryValidator",
]
