from app.agents.schemas import DomainDecision
from app.core.guardrails import simple_domain_check
from app.core.llm import get_llm
from app.prompts.domain import DOMAIN_PROMPT


def domain_guard(state):
    # Gemini checks unusual questions; clear product requests pass quickly.
    question = state["question"].strip()

    if not simple_domain_check(question):
        allowed = False
    elif state.get("current_issue") and len(question.split()) <= 18:
        allowed = True
    else:
        prompt = DOMAIN_PROMPT + "\nQUESTION: " + question
        allowed = get_llm(DomainDecision).invoke(prompt).allowed

    if not allowed:
        return {"answer": {
            "status": "out_of_domain",
            "message": "Ask about customer feedback, insights or product decisions."
        }}

    return {}


def route_domain(state):
    return "stop" if state.get("answer") else "investigate"
