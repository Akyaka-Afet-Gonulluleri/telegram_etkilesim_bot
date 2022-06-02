from typing import Optional
from pymemri.data.schema import Location, Person, Edge, EdgeList


class Fire(Location):
    description = """A potential wildfire"""
    properties = Location.properties + [
        "semptom",
        "degree", # in a scale between 0-10
        "status"
    ]
    edges = Location.edges + ["reporter"]

    def __init__(
        self,
        semptom: str = None,
        degree: int = None,
        status: str = None,
        reporter: EdgeList["Person"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Properties
        self.semptom: Optional[str] = semptom
        self.degree: Optional[int] = degree
        self.status: Optional[str] = status
        self.reporter: EdgeList["Person"] = reporter if reporter is not None else EdgeList()

class Risk(Location):
    description = """A potential wildfire risk"""
    properties = Location.properties + [
        "riskType",
        "degree", # in a scale between 0-10
        "status"
    ]
    edges = Location.edges + ["reporter"]

    def __init__(
        self,
        riskType: str = None,
        degree: int = None,
        status: str = None,
        reporter: EdgeList["Person"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Properties
        self.riskType: Optional[str] = riskType
        self.degree: Optional[int] = degree
        self.status: Optional[str] = status
        self.reporter: EdgeList["Person"] = reporter if reporter is not None else EdgeList()

class WaterSource(Location):
    description = """A water source"""
    properties = Location.properties + [
        "sourceType",
        "volume",
        "status"
    ]
    edges = Location.edges + ["reporter"]

    def __init__(
        self,
        sourceType: str = None,
        volume: int = None,
        status: str = None,
        reporter: EdgeList["Person"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Properties
        self.sourceType: Optional[str] = sourceType
        self.volume: Optional[int] = volume
        self.status: Optional[str] = status
        self.reporter: EdgeList["Person"] = reporter if reporter is not None else EdgeList()

class Tank(Location):
    description = """A mobile water tank"""
    properties = Location.properties + [
        "tankType",
        "volume",
        "status"
    ]
    edges = Location.edges + ["reporter"]

    def __init__(
        self,
        tankType: str = None,
        volume: int = None,
        status: str = None,
        reporter: EdgeList["Person"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Properties
        self.tankType: Optional[str] = tankType
        self.volume: Optional[int] = volume
        self.status: Optional[str] = status
        self.reporter: EdgeList["Person"] = reporter if reporter is not None else EdgeList()