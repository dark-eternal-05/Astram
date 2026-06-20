from app.routing.diversion_planner import DiversionInput, DiversionPlanner


planner = DiversionPlanner()

input_data = DiversionInput(
    source="Central Stadium Road",
    destination="City Exit Road",
    blocked_roads=["Market Junction"],
)

plan = planner.plan(input_data)

print(plan.model_dump())