from typing import Optional
from pymemri.data.schema import EdgeList, Item

class Report(Item):
    description = """A report"""
    properties = Item.properties + [
        "type",
        "subtype",
        "size",
        "importance", # in a scale between 0-10
        "status"
    ]
    edges = Item.edges + ["reporter", "photo", "location"]

    def __init__(
        self,
        type: str = None,
        subtype: str = None,
        size: int = None,
        importance: int = None,
        status: str = None,
        reporter: EdgeList["Person"] = None,
        photo: EdgeList["Photo"] = None,
        location: EdgeList["Location"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Properties
        self.type: Optional[str] = type
        self.subtype: Optional[str] = subtype
        self.size: Optional[int] = size
        self.importance: Optional[int] = importance
        self.status: Optional[str] = status
        self.reporter: EdgeList["Person"] = reporter if reporter is not None else EdgeList()
        self.photo: EdgeList["Photo"] = photo if photo is not None else EdgeList()
        self.location: EdgeList["Location"] = location if location is not None else EdgeList()