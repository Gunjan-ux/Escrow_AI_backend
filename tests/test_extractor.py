from unittest.mock import MagicMock, patch

from schemas import ExtractedFields


@patch("agents.extractor._agent")
def test_extract_fields_returns_pydantic_when_agent_does(mock_agent):
    expected = ExtractedFields(
        buyer_name="John Doe",
        seller_name="ABC Developers LLC",
        property_address="Unit 4B, Marina Tower, Dubai, UAE",
        property_value=8500000,
        deposit_percentage=10,
        balance_percentage=90,
        due_date="2025-06-15",
        jurisdiction="Dubai, UAE",
        effective_date="2025-01-10",
    )
    fake = MagicMock()
    fake.run.return_value = MagicMock(content=expected)
    mock_agent.return_value = fake

    from agents.extractor import extract_fields

    result = extract_fields("any raw text")
    assert result == expected


@patch("agents.extractor._agent")
def test_extract_fields_validates_dict_content(mock_agent):
    fake = MagicMock()
    fake.run.return_value = MagicMock(
        content={
            "buyer_name": "John Doe",
            "seller_name": "ABC Developers LLC",
            "property_address": "Unit 4B, Marina Tower, Dubai, UAE",
            "property_value": 8500000,
            "deposit_percentage": 10,
            "balance_percentage": 90,
            "due_date": "2025-06-15",
            "jurisdiction": "Dubai, UAE",
            "effective_date": "2025-01-10",
            "additional_clauses": None,
        }
    )
    mock_agent.return_value = fake

    from agents.extractor import extract_fields

    result = extract_fields("any raw text")
    assert result.buyer_name == "John Doe"
    assert result.property_value == 8500000
    assert result.deposit_percentage == 10
    assert result.balance_percentage == 90


@patch("agents.extractor._agent")
def test_extract_fields_validates_json_string(mock_agent):
    fake = MagicMock()
    fake.run.return_value = MagicMock(
        content='{"buyer_name": "Jane", "seller_name": "Acme", "property_value": 1000000}'
    )
    mock_agent.return_value = fake

    from agents.extractor import extract_fields

    result = extract_fields("any raw text")
    assert result.buyer_name == "Jane"
    assert result.property_value == 1000000
