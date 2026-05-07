from unittest.mock import MagicMock, patch

from schemas import ExtractedFields, Rule, RulesResponse


def _sample_fields() -> ExtractedFields:
    return ExtractedFields(
        buyer_name="John Doe",
        seller_name="ABC Developers LLC",
        property_value=8500000,
        deposit_percentage=10,
        balance_percentage=90,
        due_date="2025-06-15",
        jurisdiction="Dubai, UAE",
        effective_date="2025-01-10",
    )


def _sample_rules() -> list[Rule]:
    return [
        Rule(
            rule_id="RULE_001",
            rule_name="Late Payment Penalty",
            source_clause="Late payments incur 5% per annum.",
            condition="payment_status == LATE",
            action="calculate_fee",
            params={"rate": 0.05, "basis": "per_annum"},
            blockchain_event="TriggerPenaltyProvision",
            severity="WARNING",
            tags=["payment", "penalty"],
        )
    ]


@patch("agents.rule_generator._agent")
def test_generate_rules_returns_rules_when_agent_returns_pydantic(mock_agent):
    expected = _sample_rules()
    fake = MagicMock()
    fake.run.return_value = MagicMock(content=RulesResponse(rules=expected))
    mock_agent.return_value = fake

    from agents.rule_generator import generate_rules

    result = generate_rules(_sample_fields(), "raw deed text")
    assert result == expected


@patch("agents.rule_generator._agent")
def test_generate_rules_validates_dict_content(mock_agent):
    fake = MagicMock()
    fake.run.return_value = MagicMock(
        content={
            "rules": [
                {
                    "rule_id": "RULE_001",
                    "rule_name": "Deposit Obligation",
                    "source_clause": "Buyer shall pay 10% deposit.",
                    "condition": "deposit_paid == false",
                    "action": "flag_breach",
                    "params": {"party": "buyer"},
                    "blockchain_event": "DepositBreachDetected",
                    "severity": "CRITICAL",
                    "tags": ["deposit", "breach"],
                }
            ]
        }
    )
    mock_agent.return_value = fake

    from agents.rule_generator import generate_rules

    result = generate_rules(_sample_fields(), "raw deed text")
    assert len(result) == 1
    assert result[0].rule_id == "RULE_001"
    assert result[0].severity == "CRITICAL"


@patch("agents.rule_generator._agent")
def test_generate_rules_validates_json_string(mock_agent):
    fake = MagicMock()
    fake.run.return_value = MagicMock(
        content='{"rules": [{"rule_id": "RULE_001", "rule_name": "X", "source_clause": "c",'
        ' "condition": "true", "action": "noop", "params": {}, "severity": "INFO", "tags": []}]}'
    )
    mock_agent.return_value = fake

    from agents.rule_generator import generate_rules

    result = generate_rules(_sample_fields(), "raw deed text")
    assert len(result) == 1
    assert result[0].rule_id == "RULE_001"
