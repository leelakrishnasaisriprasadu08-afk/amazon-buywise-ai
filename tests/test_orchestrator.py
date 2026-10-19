"""Unit and integration tests for AgentDecisionOrchestrator and SSE streaming."""

import json
import pytest

from buywise.core.orchestrator import AgentDecisionOrchestrator
from buywise.models.report import DecisionVerdict
from buywise.providers.mock_provider import MockFixtureProvider
from buywise.storage.sqlite_store import SQLiteAuditStore


@pytest.fixture
def orchestrator() -> AgentDecisionOrchestrator:
    provider = MockFixtureProvider()
    store = SQLiteAuditStore(db_path=":memory:")
    return AgentDecisionOrchestrator(provider=provider, store=store)


class TestAgentDecisionOrchestrator:
    """Test suite evaluating end-to-end decision intelligence across primary domain scenarios."""

    def test_genuine_deal_yields_buy(self, orchestrator: AgentDecisionOrchestrator):
        # B08N5WRWNW: MacBook Air M1 - $749.00 vs $899 median
        report = orchestrator.run_pipeline("B08N5WRWNW")
        assert report.asin == "B08N5WRWNW"
        assert report.verdict == DecisionVerdict.BUY
        assert report.confidence >= 0.85
        assert any("all-time low" in reason.lower() for reason in report.key_reasons)
        assert report.price_metrics is not None
        assert report.price_metrics.is_all_time_low is True

    def test_artificial_deal_yields_wait(self, orchestrator: AgentDecisionOrchestrator):
        # B09V3K3EXP: Smartphone with pre-sale inflated MSRP
        report = orchestrator.run_pipeline("B09V3K3EXP")
        assert report.asin == "B09V3K3EXP"
        assert report.verdict == DecisionVerdict.WAIT
        assert report.confidence >= 0.80
        assert report.price_metrics is not None
        assert report.price_metrics.is_artificial_discount is True
        assert any("artificial" in reason.lower() for reason in report.key_reasons)

    def test_hardware_defect_yields_dont_buy(self, orchestrator: AgentDecisionOrchestrator):
        # B07DEFECT0: TurboClick Gaming Mouse with scroll-wheel breakage
        report = orchestrator.run_pipeline("B07DEFECT0")
        assert report.asin == "B07DEFECT0"
        assert report.verdict == DecisionVerdict.DONT_BUY
        assert report.confidence >= 0.80
        assert report.aspect_analysis is not None
        assert report.aspect_analysis.defect_rate >= 0.20
        assert any("defect" in reason.lower() for reason in report.key_reasons)

    def test_college_laptop_yields_switch_dont_buy(self, orchestrator: AgentDecisionOrchestrator):
        # B0COLLEGE1: VendorX SlimBook 14 with soldered RAM vs BenchmarkPro 14 (B0COLLEGE2)
        report = orchestrator.run_pipeline("B0COLLEGE1")
        assert report.asin == "B0COLLEGE1"
        assert report.verdict == DecisionVerdict.DONT_BUY
        assert report.alternative is not None
        assert report.alternative.alternative_asin == "B0COLLEGE2"
        assert report.alternative.is_strictly_better is True
        assert any("strictly superior alternative" in reason.lower() for reason in report.key_reasons)

    def test_new_listing_yields_insufficient_evidence(self, orchestrator: AgentDecisionOrchestrator):
        # B0NEWITEM0: Brand new hub with 1 review and 1 price snapshot
        report = orchestrator.run_pipeline("B0NEWITEM0")
        assert report.asin == "B0NEWITEM0"
        assert report.verdict == DecisionVerdict.INSUFFICIENT_EVIDENCE
        assert report.confidence < 0.50
        assert len(report.missing_evidence) >= 1

    @pytest.mark.asyncio
    async def test_stream_pipeline_emits_sse_milestones(self, orchestrator: AgentDecisionOrchestrator):
        events = []
        async for sse_chunk in orchestrator.stream_pipeline("B08N5WRWNW"):
            events.append(sse_chunk)

        assert len(events) >= 5
        # Verify event format
        assert any("event: milestone" in e for e in events)
        assert any("event: complete" in e for e in events)

        # Verify final event carries complete report
        complete_event = [e for e in events if "event: complete" in e][0]
        data_line = [line for line in complete_event.split("\n") if line.startswith("data: ")][0]
        payload = json.loads(data_line[6:])
        assert payload["stage"] == "COMPLETE"
        assert payload["report"]["asin"] == "B08N5WRWNW"
        assert payload["report"]["verdict"] == "BUY"
