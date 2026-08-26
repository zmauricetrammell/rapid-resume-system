from uuid import UUID

import pytest

from rrs.infrastructure.runtime.id_generator import (
    DeterministicIdGenerator,
    UuidIdGenerator,
)
from rrs.ports.id_generator import IdGenerator


def accepts_id_generator(generator: IdGenerator) -> IdGenerator:
    return generator


def assert_prefixed_uuid(value: str, prefix: str) -> None:
    expected_prefix = f"{prefix}-"
    assert value.startswith(expected_prefix)
    identifier = UUID(value.removeprefix(expected_prefix))
    assert identifier.version == 4


def test_uuid_generator_produces_prefixed_uuid4_ids() -> None:
    generator = accepts_id_generator(UuidIdGenerator())

    generated = (
        (str(generator.new_job_id()), "job"),
        (str(generator.new_execution_id()), "execution"),
        (str(generator.new_command_id()), "command"),
        (str(generator.new_event_id()), "event"),
        (str(generator.new_interaction_id()), "interaction"),
        (str(generator.new_message_id()), "message"),
        (str(generator.new_failure_id()), "failure"),
    )

    for value, prefix in generated:
        assert_prefixed_uuid(value, prefix)


def test_uuid_generator_produces_unique_ids() -> None:
    generator = UuidIdGenerator()

    assert generator.new_job_id() != generator.new_job_id()


def test_deterministic_generator_produces_repeatable_sequence() -> None:
    first = accepts_id_generator(DeterministicIdGenerator())
    second = accepts_id_generator(DeterministicIdGenerator())

    first_sequence = (
        str(first.new_job_id()),
        str(first.new_event_id()),
        str(first.new_command_id()),
        str(first.new_execution_id()),
        str(first.new_interaction_id()),
        str(first.new_message_id()),
        str(first.new_failure_id()),
    )
    second_sequence = (
        str(second.new_job_id()),
        str(second.new_event_id()),
        str(second.new_command_id()),
        str(second.new_execution_id()),
        str(second.new_interaction_id()),
        str(second.new_message_id()),
        str(second.new_failure_id()),
    )

    assert first_sequence == second_sequence
    assert first_sequence == (
        "job-000001",
        "event-000002",
        "command-000003",
        "execution-000004",
        "interaction-000005",
        "message-000006",
        "failure-000007",
    )


def test_deterministic_generator_can_start_from_explicit_value() -> None:
    generator = DeterministicIdGenerator(next_value=42)

    assert generator.new_job_id() == "job-000042"


def test_deterministic_generator_rejects_invalid_start() -> None:
    with pytest.raises(ValueError, match="next_value must be >= 1"):
        DeterministicIdGenerator(next_value=0)
