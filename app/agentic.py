"""Constrained model-directed research with an allowlisted tool.

The model chooses a tool call; only company_lookup is executable. The
server enforces company_id binding, tool-call count, response schema,
and fail-closed behavior. No arbitrary URLs or outreach actions.
"""
import os
from app.tools import company_lookup, ToolFailure

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "company_lookup",
        "description": "Look up the synthetic company record by exact ID",
        "parameters": {
            "type": "object",
            "properties": {"company_id": {"type": "string"}},
            "required": ["company_id"],
            "additionalProperties": False,
        },
    },
}

def model_research(company_id: str, model=None) -> dict:
    """Execute exactly one allowlisted model-requested tool call.

    No API key is needed when injecting a fake model for automated tests.
    Real execution requires an OpenAI API key and may incur charges.
    """
    if model is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY required for agentic research")
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                           temperature=0, timeout=20, max_retries=1)
    model_with_tools = model.bind_tools([TOOL_SPEC], tool_choice="required")
    response = model_with_tools.invoke([
        ("system", "You are an agent that can only request company_lookup. "
                   "Look up the exact company ID provided. Do not infer facts or "
                   "make other tool calls. Return one tool call."),
        ("human", "Look up company_id: " + company_id),
    ])
    calls = getattr(response, "tool_calls", None) or []
    if len(calls) != 1:
        raise ToolFailure("Expected exactly one tool call")
    call = calls[0]
    if call.get("name") != "company_lookup":
        raise ToolFailure("Tool not permitted")
    args = call.get("args")
    if not isinstance(args, dict) or set(args) != {"company_id"}:
        raise ToolFailure("Tool arguments invalid")
    if args["company_id"] != company_id:
        raise ToolFailure("Cross-record tool request refused")
    result = company_lookup(company_id)
    result["metadata"]["mode"] = "model_directed"
    result["metadata"]["tool_calls"] = 1
    return result
