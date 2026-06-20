from pydantic import BaseModel, Field
import networkx as nx


class DiversionInput(BaseModel):
    source: str
    destination: str
    blocked_roads: list[str] = Field(default_factory=list)


class RouteOption(BaseModel):
    route: list[str]
    total_delay_minutes: float
    explanation: str


class DiversionPlan(BaseModel):
    source: str
    destination: str
    blocked_roads: list[str]
    recommended_route: RouteOption
    alternate_routes: list[RouteOption]


class DiversionPlanner:
    def __init__(self):
        self.graph = self._build_demo_network()

    def _build_demo_network(self) -> nx.Graph:
        graph = nx.Graph()

        roads = [
            ("Central Stadium Road", "Ring Road", 8),
            ("Central Stadium Road", "Market Junction", 12),
            ("Market Junction", "Lake Road", 10),
            ("Lake Road", "City Hospital Road", 7),
            ("Ring Road", "City Hospital Road", 11),
            ("Ring Road", "Airport Connector", 15),
            ("Airport Connector", "City Exit Road", 10),
            ("City Hospital Road", "City Exit Road", 9),
            ("Market Junction", "Old Town Road", 14),
            ("Old Town Road", "City Exit Road", 13),
        ]

        for start, end, delay in roads:
            graph.add_edge(start, end, weight=delay)

        return graph

    def plan(self, data: DiversionInput) -> DiversionPlan:
        graph = self.graph.copy()

        for road in data.blocked_roads:
            if road in graph:
                graph.remove_node(road)

        if data.source not in graph:
            raise ValueError(f"Source '{data.source}' is unavailable or blocked.")

        if data.destination not in graph:
            raise ValueError(f"Destination '{data.destination}' is unavailable or blocked.")

        simple_routes = list(
            nx.shortest_simple_paths(
                graph,
                source=data.source,
                target=data.destination,
                weight="weight",
            )
        )

        route_options = []

        for route in simple_routes[:3]:
            delay = self._calculate_delay(graph, route)
            route_options.append(
                RouteOption(
                    route=route,
                    total_delay_minutes=delay,
                    explanation=f"Route avoids blocked roads: {data.blocked_roads}",
                )
            )

        if not route_options:
            raise ValueError("No valid diversion route found.")

        return DiversionPlan(
            source=data.source,
            destination=data.destination,
            blocked_roads=data.blocked_roads,
            recommended_route=route_options[0],
            alternate_routes=route_options[1:],
        )

    def _calculate_delay(self, graph: nx.Graph, route: list[str]) -> float:
        delay = 0.0

        for index in range(len(route) - 1):
            start = route[index]
            end = route[index + 1]
            delay += graph[start][end]["weight"]

        return delay