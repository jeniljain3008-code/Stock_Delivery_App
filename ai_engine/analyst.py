def answer_question(
    question: str, symbol: str | None, stocks: list[dict], gold_stocks: list[dict]
) -> dict:
    q = question.lower()
    universe = gold_stocks if "gold" in q or "highest" in q else stocks
    if symbol:
        matches = [row for row in stocks if row["symbol"] == symbol.upper()]
    else:
        matches = universe[:5]
    if not matches:
        return {
            "answer": "No matching stock was found in the current analytics universe.",
            "supporting_symbols": [],
        }
    lead = matches[0]
    answer = (
        f"{lead['symbol']} is notable because delivery quantity is running at "
        f"{lead.get('delivery_surge', 1):.2f}x its recent average while the accumulation score is "
        f"{lead.get('accumulation_score', 0):.1f}. The platform prioritizes delivery expansion first, "
        "then confirms with price trend, volume participation, and breakout readiness. "
        f"Current swing action is {lead.get('swing_signal', 'WATCH')} with {lead.get('risk_rating', 'Medium')} risk."
    )
    return {"answer": answer, "supporting_symbols": [row["symbol"] for row in matches]}
