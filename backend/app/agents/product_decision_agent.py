
import json

from app.agents.schemas import DecisionDraft
from app.core.llm import get_llm
from app.prompts.decision import DECISION_PROMPT


# Turn verified data into product recommendations
def make_decision(state):

    question = state["question"]

    # Prepare retrieved customer feedback
    passages = "\n\n".join(
        f"Source {item['source_id']}: {item['text'][:1400]}"
        for item in state.get("evidence", [])[:15]
    )

    # Prepare the prompt
    prompt = DECISION_PROMPT.format(
        question=question,
        metrics=json.dumps(
            state.get("metrics", {}),
            default=str
        ),
        passages=passages
    )

    # Generate natural, structured analysis
    decision = get_llm(DecisionDraft).invoke(prompt)

    draft = decision.model_dump()

    # Show phases when the user requests a roadmap
    roadmap_words = (
        "roadmap",
        "90-day",
        "90 day",
        "30/60/90",
        "implementation plan"
    )

    if any(word in question.lower() for word in roadmap_words):

        phases = [
            "Days 1-30",
            "Days 31-60",
            "Days 61-90"
        ]

        for phase, proposal in zip(
            phases,
            draft["proposals"][:3]
        ):
            action = proposal["action"]

            if not action.startswith(phase):
                proposal["action"] = f"{phase} — {action}"

    return {"draft": draft}
