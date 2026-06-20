from app.optimization.resource_optimizer import OptimizationInput, ResourceOptimizer


optimizer = ResourceOptimizer()

input_data = OptimizationInput(
    impact_score=82,
    closure_probability=0.78,
    priority="critical",
    expected_crowd_size=18000,
    event_duration_hours=5,
    peak_hour=True,
    nearby_sensitive_zone=True,
)

plan = optimizer.optimize(input_data)

print(plan.model_dump())