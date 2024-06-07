from typing import Optional
from pymemri.data.schema import EdgeList, Item

class Reporter(Item):
    description = """A person (alive, dead, undead, or fictional)."""
    properties = Item.properties + [
        "userKey",
        "username",
        "email",
        "fullName",
        "title",
        "role",
        "information",
        "starred",
    ]
    edges = Item.edges + [
        "hasPhoneNumber",
        "medicalCondition",
        "profilePicture",
        "division",
    ]

    def __init__(
        self,
        userKey: str = None,
        username: str = None,
        email: str = None,
        fullName: str = None,
        title: str = None,
        role: str = None,
        information: str = None,
        starred: bool = None,
        hasPhoneNumber: EdgeList["PhoneNumber"] = None,
        medicalCondition: EdgeList["MedicalCondition"] = None,
        profilePicture: EdgeList["Photo"] = None,
        division: EdgeList["Division"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Properties
        self.userKey: Optional[str] = userKey
        self.username: Optional[str] = username
        self.email: Optional[str] = email
        self.fullName: Optional[str] = fullName
        self.title: Optional[str] = title
        self.role: Optional[str] = role
        self.information: Optional[str] = information
        self.starred: Optional[bool] = starred

        # Edges
        self.hasPhoneNumber: EdgeList["PhoneNumber"] = EdgeList(
            "hasPhoneNumber", "PhoneNumber", hasPhoneNumber
        )
        self.medicalCondition: EdgeList["MedicalCondition"] = EdgeList(
            "medicalCondition", "MedicalCondition", medicalCondition
        )
        self.profilePicture: EdgeList["Photo"] = EdgeList(
            "profilePicture", "Photo", profilePicture
        )
        self.division: EdgeList["Division"] = EdgeList("division", "Division", division)


class Report(Item):
    description = """A report"""
    properties = Item.properties + [
        "category",
        "subtype",
        "size",
        "importance", # in a scale between 0-10
        "status",
        "text"
    ]
    edges = Item.edges + ["reporter", "photo", "location"]

    def __init__(
        self,
        category: str = None,
        subtype: str = None,
        size: int = None,
        importance: int = None,
        status: str = None,
        text: str = None,
        reporter: EdgeList["Reporter"] = None,
        photo: EdgeList["Photo"] = None,
        location: EdgeList["Location"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Properties
        self.category: Optional[str] = category
        self.subtype: Optional[str] = subtype
        self.size: Optional[int] = size
        self.importance: Optional[int] = importance
        self.status: Optional[str] = status
        self.text: Optional[str] = text
        self.reporter: EdgeList["Reporter"] = EdgeList("reporter", "Reporter", reporter)
        self.photo: EdgeList["Photo"] = EdgeList("photo", "Photo", photo)
        self.location: EdgeList["Location"] = EdgeList("location", "Location", location)