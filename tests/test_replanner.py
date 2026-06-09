from agent.replanner import build_safe_fallback_plan


def test_build_safe_fallback_plan_returns_hover_and_land():
    fallback = build_safe_fallback_plan("target_not_found:red")

    assert fallback == [
        {"action": "hover", "duration": 1.0, "fallback_reason": "target_not_found:red"},
        {"action": "land", "fallback_reason": "target_not_found:red"},
    ]