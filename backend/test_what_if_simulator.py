from app.simulation.what_if_simulator import (
    ScenarioInput,
    ScenarioModification,
    WhatIfInput,
    WhatIfSimulator,
)


simulator = WhatIfSimulator()

input_data = WhatIfInput(
    original_scenario=ScenarioInput(
        impact_score=55,
        closure_probability=0.45,
        priority="medium",
        expected_crowd_size=8000,
        event_duration_hours=3,
        peak_hour=False,
        nearby_sensitive_zone=False,
    ),
    modifications=ScenarioModification(
        expected_crowd_size=18000,
        event_duration_hours=5,
        peak_hour=True,
        priority="critical",
        closure_probability=0.78,
        impact_score=82,
    ),
)

result = simulator.run(input_data)

print(result.model_dump())