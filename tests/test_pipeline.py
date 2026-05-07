from unittest.mock import patch

from schemas import ExtractedFields, Rule


@patch("core.pipeline.generate_rules")
@patch("core.pipeline.extract_fields")
def test_analyze_deed_chains_extractor_then_rule_generator(mock_extract, mock_rules):
    fields = ExtractedFields(buyer_name="A", seller_name="B")
    rules = [
        Rule(
            rule_id="RULE_001",
            rule_name="X",
            source_clause="c",
            condition="true",
            action="noop",
            params={},
            severity="INFO",
            tags=[],
        )
    ]
    mock_extract.return_value = fields
    mock_rules.return_value = rules

    from core.pipeline import analyze_deed

    out_fields, out_rules = analyze_deed("some raw text")

    mock_extract.assert_called_once_with("some raw text")
    mock_rules.assert_called_once_with(fields, "some raw text")
    assert out_fields is fields
    assert out_rules is rules
