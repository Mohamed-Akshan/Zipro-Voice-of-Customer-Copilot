from langgraph.graph import StateGraph, START, END

from app.agents.state import VoiceOfCustomerState
from app.agents.domain_guard import domain_guard, route_domain
from app.agents.investigation_agent import investigate
from app.agents.product_decision_agent import make_decision
from app.agents.evidence_verification_agent import verify_evidence
from app.rag.corrective import check_retrieval, retry_search, insufficient_evidence


def build_graph(checkpointer):
    # Three business agents plus lightweight guardrail and correction nodes.
    workflow = StateGraph(VoiceOfCustomerState)

    workflow.add_node("guardrail", domain_guard)
    workflow.add_node("investigate", investigate)
    workflow.add_node("retry", retry_search)
    workflow.add_node("decision", make_decision)
    workflow.add_node("verify", verify_evidence)
    workflow.add_node("insufficient", insufficient_evidence)

    workflow.add_edge(START, "guardrail")

    workflow.add_conditional_edges("guardrail", route_domain, {
        "stop": END,
        "investigate": "investigate"
    })

    workflow.add_conditional_edges("investigate", check_retrieval, {
        "direct": END,
        "decision": "decision",
        "retry": "retry",
        "insufficient": "insufficient"
    })

    workflow.add_edge("retry", "investigate")
    workflow.add_edge("decision", "verify")
    workflow.add_edge("verify", END)
    workflow.add_edge("insufficient", END)

    return workflow.compile(checkpointer=checkpointer)
