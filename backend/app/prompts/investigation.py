REWRITE_PROMPT = """
Rewrite the following ride-hailing customer-feedback search request to retrieve
more relevant ORIGINAL SOURCE EVIDENCE. Do not answer the question.
Preserve the same customer issue, time range, and meaning. Use alternative
concrete terms a customer might write in an app review or support ticket.
Keep it one concise search sentence, with no new assumptions or instructions.

Original question: {question}
"""
