from app.forecasting.astram_model_wrapper import (
    ASTRaMForecastInput,
    ASTRaMModelWrapper,
)


model = ASTRaMModelWrapper()

sample = ASTRaMForecastInput(
    event_cause="construction",
    corridor="Hosur Road",
    zone="South Zone 1",
    junction="SilkBoardJunc",
    hour=7,
    day_of_week=1,
    month=3,
    is_planned=False,
    involves_heavy_vehicle=False,
    is_authenticated=True,
)

result = model.predict(sample)

print(result.model_dump())