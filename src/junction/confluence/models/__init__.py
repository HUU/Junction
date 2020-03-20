"""All the models used on the Confluence API.

Models must meet the following criteria:
    * Inherit from ApiModel to ensure proper serialization
    * Define all class attributes with a default value (of None usually)
    * All attributes should be type hinted except in extreme circumstances; for "unknown" types use DotDict
    * Reference only primitive types or other ApiModels

Basic type discrimination is supported for class hierarchies with the @discriminator annotation.

Dumped into one giant file to avoid circular references.  None of the solutions to circular imports in
Python appealed to me and models are unchanging, uncomplicated, and often used together so not worth splitting out
into different modules.  Also makes adding new models easier as there is only one module it can possibly go!

Reference model definitions at https://developer.atlassian.com/cloud/confluence/rest/
"""

from typing import List, Union, Any, Optional, Generic, TypeVar

from junction.util import DotDict
from junction.confluence.models.subclassing import discriminator


class ApiModel(object):
    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            assert hasattr(self, key), "{} not a valid attribute of {}".format(
                key, self.__class__
            )
            setattr(self, key, value)

    def __repr__(self) -> str:
        return "<class {}({})>".format(
            self.__class__.__name__,
            {
                k: getattr(self, k, None)
                for k in dir(self)
                if not k.startswith("_") and k != "encode_json"
            },
        )

    def __str__(self) -> str:
        return self.__repr__()

    def encode_json(self) -> dict:
        return self.__dict__


class Label(ApiModel):

    prefix: Optional[str] = None
    name: Optional[str] = None
    id: Optional[str] = None
    label: Optional[str] = None


class LabelArray(ApiModel):

    results: Optional[List[Label]] = None
    start: Optional[int] = None
    limit: Optional[int] = None
    size: Optional[int] = None
    _links: Optional[DotDict]


class OperationCheckResult(ApiModel):

    operation: Optional[str] = None
    targetType: Optional[str] = None


class LookAndFeelColorAndBackground(ApiModel):

    backgroundColor: Optional[str] = None
    color: Optional[str] = None


class MenusLookAndFeel(ApiModel):

    hoverOrFocus: Optional[LookAndFeelColorAndBackground] = None
    color: Optional[str] = None


class ButtonLookAndFeel(ApiModel):

    backgroundColor: Optional[str] = None
    color: Optional[str] = None


class NavigationLookAndFeel(ApiModel):

    color: Optional[str] = None
    hoverOrFocus: Optional[LookAndFeelColorAndBackground] = None


class SearchFieldLookAndFeel(ApiModel):

    backgroundColor: Optional[str] = None
    color: Optional[str] = None


class HeaderLookAndFeel(ApiModel):

    backgroundColor: Optional[str] = None
    button: Optional[ButtonLookAndFeel] = None
    primaryNavigation: Optional[NavigationLookAndFeel] = None
    secondaryNavigation: Optional[NavigationLookAndFeel] = None
    search: Optional[SearchFieldLookAndFeel] = None


class ScreenLookAndFeel(ApiModel):

    background: Optional[str] = None
    backgroundColor: Optional[str] = None
    backgroundImage: Optional[str] = None
    backgroundSize: Optional[str] = None
    gutterTop: Optional[str] = None
    gutterRight: Optional[str] = None
    gutterBottom: Optional[str] = None
    gutterLeft: Optional[str] = None


class ContainerLookAndFeel(ApiModel):

    background: Optional[str] = None
    backgroundColor: Optional[str] = None
    backgroundImage: Optional[str] = None
    backgroundSize: Optional[str] = None
    padding: Optional[str] = None
    borderRadius: Optional[str] = None


class ContentLookAndFeel(ApiModel):

    screen: Optional[ScreenLookAndFeel] = None
    container: Optional[ContainerLookAndFeel] = None
    header: Optional[ContainerLookAndFeel] = None
    body: Optional[ContainerLookAndFeel] = None


class LookAndFeelColor(ApiModel):

    color: Optional[str] = None


class LookAndFeel(ApiModel):

    headings: Optional[LookAndFeelColor] = None
    links: Optional[LookAndFeelColor] = None
    menus: Optional[MenusLookAndFeel] = None
    header: Optional[HeaderLookAndFeel] = None
    content: Optional[ContentLookAndFeel] = None
    bordersAndDividers: Optional[LookAndFeelColor] = None


class Icon(ApiModel):

    path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    isDefault: Optional[bool] = None


class SpacePermissionUser(ApiModel):

    results: Optional[List["User"]] = None
    size: Optional[int] = None


class SpacePermissionGroup(ApiModel):

    results: Optional[List["Group"]] = None
    size: Optional[int] = None


class SpacePermissionSubjects(ApiModel):

    user: Optional[SpacePermissionUser] = None
    group: Optional[SpacePermissionGroup] = None
    _expandable: Optional[DotDict] = None


class SpacePermission(ApiModel):

    subjects: Optional[SpacePermissionSubjects] = None
    operation: Optional[OperationCheckResult] = None
    anonymousAccess: Optional[bool] = None
    unlicensedAccess: Optional[bool] = None


class SpaceSettings(ApiModel):

    routeOverrideEnabled: Optional[bool] = None
    _links: Optional[DotDict] = None


class SpaceDescription(ApiModel):

    value: Optional[str] = None
    representation: Optional[str] = None
    embeddedContent: Optional[List[DotDict]] = None


class Description(ApiModel):

    plain: Optional[SpaceDescription] = None
    view: Optional[SpaceDescription] = None


class SpaceMetadata(ApiModel):

    labels: Optional["LabelArray"] = None


class SpaceHistory(ApiModel):

    createdDate: Optional[str] = None


class SpaceTheme(ApiModel):

    themeKey: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[Icon] = None
    _links: Optional[DotDict] = None


class Space(ApiModel):

    id: Optional[int] = None
    key: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[Icon] = None
    description: Optional[Description] = None
    homepage: Optional["Content"] = None
    type: Optional[str] = None
    metadata: Optional[SpaceMetadata] = None
    operations: Optional[List[OperationCheckResult]] = None
    permissions: Optional[List[SpacePermission]] = None
    status: Optional[str] = None
    settings: Optional[SpaceSettings] = None
    theme: Optional[SpaceTheme] = None
    lookAndFeel: Optional[LookAndFeel] = None
    history: Optional[SpaceHistory] = None
    _expandable: Optional[DotDict] = None
    _links: Optional[DotDict] = None


class EmbeddedContent(ApiModel):

    entityId: Optional[int] = None
    entity: Optional[DotDict] = None


class SuperBatchWebResources(ApiModel):

    uris: Optional[DotDict] = None
    tags: Optional[DotDict] = None
    metatags: Optional[str] = None


class WebResourceDependencies(ApiModel):

    keys: Optional[List[str]] = None
    contexts: Optional[List[str]] = None
    uris: Optional[DotDict] = None
    tags: Optional[DotDict] = None
    superbatch: Optional[SuperBatchWebResources] = None


class ContentBody(ApiModel):

    value: Optional[str] = None
    representation: Optional[str] = None
    embeddedContent: Optional[List[EmbeddedContent]] = None
    webResource: Optional[WebResourceDependencies] = None
    _exapndable = None


class Body(ApiModel):

    view: Optional[ContentBody] = None
    export_view: Optional[ContentBody] = None
    styled_view: Optional[ContentBody] = None
    storage: Optional[ContentBody] = None
    editor2: Optional[ContentBody] = None
    anonymous_export_view: Optional[ContentBody] = None
    _expandable: Optional[DotDict] = None


class ContentExtensions(ApiModel):

    position: Optional[int] = None


class Favourited(ApiModel):

    isFavourite: Optional[bool] = None
    favouritedDate: Optional[str] = None


class LastModified(ApiModel):

    version: Optional["Version"] = None
    friendlyLastModified: Optional[str] = None


class LastContributed(ApiModel):

    status: Optional[str] = None
    when: Optional[str] = None


class Viewed(ApiModel):

    lastSeen: Optional[str] = None
    friendlyLastSeen: Optional[str] = None


class CurrentUserMetadata(ApiModel):

    favourited: Optional[Favourited] = None
    lastModified: Optional[LastModified] = None
    lastContributed: Optional[LastContributed] = None
    viewed: Optional[Viewed] = None


class ContentMetadata(ApiModel):

    currentUser: Optional[CurrentUserMetadata] = None
    properties: Optional[DotDict] = None
    frontend: Optional[DotDict] = None
    labels: Optional[LabelArray] = None


class Content(ApiModel):

    id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    space: Optional[Space] = None
    history: Optional["ContentHistory"] = None
    version: Optional["Version"] = None
    ancestors: Optional[
        List["ContentPage"]
    ] = None  # this really isn't the right type, but in 99% cases it is and it makes the type checker quiet down
    operations: Optional[List[OperationCheckResult]] = None
    children: Optional["ContentChildren"] = None
    childTypes: Optional["ContentChildType"] = None
    descendants: Optional["ContentChildren"] = None
    containers: Optional[Union[Space, "Content"]] = None
    body: Optional[Body] = None
    restrictions: Optional["ContentRestrictions"] = None
    _expandable: Optional[DotDict] = None
    _links: Optional[DotDict] = None


@discriminator(lambda json: json.get("type") == "page")
class ContentPage(Content):

    title: Optional[str] = None
    metadata: Optional[ContentMetadata] = None
    extensions: Optional[ContentExtensions] = None


class UpdateVersion(ApiModel):

    number: Optional[int] = None


class UpdateContent(ApiModel):

    version: Optional[UpdateVersion] = None
    title: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    ancestors: Optional[List["Content"]] = None
    body: Optional[Body] = None


class CreateContent(ApiModel):

    id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    space: Optional[Space] = None
    status: Optional[str] = None
    ancestors: Optional[List["Content"]] = None
    body: Optional[Body] = None


TContent = TypeVar("TContent", bound=Content)


class ContentArray(Generic[TContent], ApiModel):

    results: List[TContent] = []
    start: Optional[int] = None
    limit: Optional[int] = None
    size: Optional[int] = None
    _links: Optional[DotDict] = None


class ContentChildren(ApiModel):

    attachment: Optional[ContentArray[Content]] = None
    comment: Optional[ContentArray[Content]] = None
    page: Optional[ContentArray[ContentPage]] = None
    _expandable: Optional[DotDict] = None
    _links: Optional[DotDict] = None


class ContentChildTypeValue(ApiModel):

    value: Optional[bool] = None
    _links: Optional[DotDict] = None


class ContentChildType(ApiModel):

    attachment: Optional[ContentChildTypeValue] = None
    comment: Optional[ContentChildTypeValue] = None
    page: Optional[ContentChildTypeValue] = None
    _expandable: Optional[DotDict] = None


class ContentRestriction(ApiModel):

    operation: Optional[str] = None
    restrictions: Optional["Restrictions"] = None
    content: Optional[Content] = None
    _expandable: Optional[DotDict] = None
    _links: Optional[DotDict] = None


class ContentRestrictions(ApiModel):

    read: Optional[ContentRestriction] = None
    update: Optional[ContentRestriction] = None
    _links: Optional[DotDict] = None


class Restrictions(ApiModel):

    user: Optional["UserArray"] = None
    group: Optional["GroupArray"] = None
    _exapndable = None


class Contributors(ApiModel):

    publishers: Optional["UsersUserKeys"] = None


class ContentHistory(ApiModel):

    latest: Optional[bool] = None
    createdBy: Optional["User"] = None
    createdDate: Optional[str] = None
    lastUpdated: Optional["Version"] = None
    previousVersion: Optional["Version"] = None
    contributors: Optional[Contributors] = None
    nextVersion: Optional["Version"] = None
    _expandable: Optional[DotDict] = None
    _links: Optional[DotDict] = None


class Business(ApiModel):

    position: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None


class Personal(ApiModel):

    phone: Optional[str] = None
    im: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None


class UserDetails(ApiModel):

    business: Optional[Business] = None
    personal: Optional[Personal] = None


class User(ApiModel):

    type: Optional[str] = None
    username: Optional[str] = None
    userKey: Optional[str] = None
    accountId: Optional[str] = None
    accountType: Optional[str] = None
    email: Optional[str] = None
    publicName: Optional[str] = None
    profilePicture: Optional[Icon] = None
    displayName: Optional[str] = None
    operations: Optional[OperationCheckResult] = None
    details: Optional[UserDetails] = None
    personalSpace: Optional[Space] = None
    _expandable: Optional[DotDict] = None
    _links: Optional[DotDict]


class UsersUserKeys(ApiModel):

    users: Optional[List[User]] = None
    userKeys: Optional[List[str]] = None
    _links: Optional[DotDict] = None


class UserArray(ApiModel):

    results: Optional[List[User]] = None
    start: Optional[int] = None
    limit: Optional[int] = None
    size: Optional[int] = None


class Group(ApiModel):

    type: Optional[str] = None
    name: Optional[str] = None
    _links: Optional[DotDict] = None


class GroupArray(ApiModel):

    results: Optional[List[Group]] = None
    start: Optional[int] = None
    limit: Optional[int] = None
    size: Optional[int] = None


class Version(ApiModel):

    by: Optional[User] = None
    when: Optional[str] = None
    friendlyWhen: Optional[str] = None
    message: Optional[str] = None
    number: Optional[int] = None
    minorEdit: Optional[bool] = None
    content: Optional[Content] = None
    collaborators: Optional[UsersUserKeys] = None
    _expandable: Optional[DotDict] = None
    _links: Optional[DotDict] = None
