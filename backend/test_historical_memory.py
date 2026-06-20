from app.knowledge.historical_memory import HistoricalMemory


memory = HistoricalMemory()

memory.add_event(
    event_id="event_001",
    event_text=(
        "Football final near Central Stadium Road with 18000 crowd, rain, "
        "arterial road congestion, 24 officers, 12 barricades, diversion via Ring Road."
    ),
    metadata={
        "event_type": "sports",
        "location": "Central Stadium Road",
        "crowd_size": 18000,
        "weather": "rain",
        "manpower_used": 24,
        "barricades_used": 12,
        "diversion_effectiveness": "good",
    },
)

memory.add_event(
    event_id="event_002",
    event_text=(
        "Music concert near City Arena with 12000 crowd, clear weather, "
        "collector road congestion, 16 officers, 8 barricades, diversion via Lake Road."
    ),
    metadata={
        "event_type": "concert",
        "location": "City Arena",
        "crowd_size": 12000,
        "weather": "clear",
        "manpower_used": 16,
        "barricades_used": 8,
        "diversion_effectiveness": "moderate",
    },
)

matches = memory.find_similar_events(
    query_text="Large sports event near stadium during rain with crowd congestion",
    top_k=2,
)

for match in matches:
    print(match)
    