from typing import List, Union, Any

from junction.util import DotDict
from junction.confluence.models.subclassing import discriminator


class ApiModel(object):
    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            assert hasattr(self, key), "{} not a valid attribute of {}".format(
                key, self.__class__
            )
            setattr(self, key, value)

    def __repr__(self):
        return "<class {}({})>".format(
            self.__class__.__name__,
            {k: getattr(self, k, None) for k in dir(self) if not k.startswith("_")},
        )

    def __str__(self):
        return self.__repr__()

    def encode_json(self):
        return self.__dict__


class Label(ApiModel):

    prefix: str = None
    name: str = None
    id: str = None
    label: str = None


class LabelArray(ApiModel):

    results: List[Label] = None
    start: int = None
    limit: int = None
    size: int = None
    _links: DotDict


class OperationCheckResult(ApiModel):

    operation: str = None
    targetType: str = None


class LookAndFeelColorAndBackground(ApiModel):

    backgroundColor: str = None
    color: str = None


class MenusLookAndFeel(ApiModel):

    hoverOrFocus: LookAndFeelColorAndBackground = None
    color: str = None


class ButtonLookAndFeel(ApiModel):

    backgroundColor: str = None
    color: str = None


class NavigationLookAndFeel(ApiModel):

    color: str = None
    hoverOrFocus: LookAndFeelColorAndBackground = None


class SearchFieldLookAndFeel(ApiModel):

    backgroundColor: str = None
    color: str = None


class HeaderLookAndFeel(ApiModel):

    backgroundColor: str = None
    button: ButtonLookAndFeel = None
    primaryNavigation: NavigationLookAndFeel = None
    secondaryNavigation: NavigationLookAndFeel = None
    search: SearchFieldLookAndFeel = None


class ScreenLookAndFeel(ApiModel):

    background: str = None
    backgroundColor: str = None
    backgroundImage: str = None
    backgroundSize: str = None
    gutterTop: str = None
    gutterRight: str = None
    gutterBottom: str = None
    gutterLeft: str = None


class ContainerLookAndFeel(ApiModel):

    background: str = None
    backgroundColor: str = None
    backgroundImage: str = None
    backgroundSize: str = None
    padding: str = None
    borderRadius: str = None


class ContentLookAndFeel(ApiModel):

    screen: ScreenLookAndFeel = None
    container: ContainerLookAndFeel = None
    header: ContainerLookAndFeel = None
    body: ContainerLookAndFeel = None


class LookAndFeelColor(ApiModel):

    color: str = None


class LookAndFeel(ApiModel):

    headings: LookAndFeelColor = None
    links: LookAndFeelColor = None
    menus: MenusLookAndFeel = None
    header: HeaderLookAndFeel = None
    content: ContentLookAndFeel = None
    bordersAndDividers: LookAndFeelColor = None


class Icon(ApiModel):

    path: str = None
    width: int = None
    height: int = None
    isDefault: bool = None


class SpacePermissionUser(ApiModel):

    results: List["User"] = None
    size: int = None


class SpacePermissionGroup(ApiModel):

    results: List["Group"] = None
    size: int = None


class SpacePermissionSubjects(ApiModel):

    user: SpacePermissionUser = None
    group: SpacePermissionGroup = None
    _expandable: DotDict = None


class SpacePermission(ApiModel):

    subjects: SpacePermissionSubjects = None
    operation: OperationCheckResult = None
    anonymousAccess: bool = None
    unlicensedAccess: bool = None


class SpaceSettings(ApiModel):

    routeOverrideEnabled: bool = None
    _links: DotDict = None


class SpaceDescription(ApiModel):

    value: str = None
    representation: str = None
    embeddedContent: List[DotDict] = None


class Description(ApiModel):

    plain: SpaceDescription = None
    view: SpaceDescription = None


class SpaceMetadata(ApiModel):

    labels: "LabelArray" = None


class SpaceHistory(ApiModel):

    createdDate: str = None


class SpaceTheme(ApiModel):

    themeKey: str = None
    name: str = None
    description: str = None
    icon: Icon = None
    _links: DotDict = None


class Space(ApiModel):

    id: int = None
    key: str = None
    name: str = None
    icon: Icon = None
    description: Description = None
    homepage: "Content" = None
    type: str = None
    metadata: SpaceMetadata = None
    operations: List[OperationCheckResult] = None
    permissions: List[SpacePermission] = None
    status: str = None
    settings: SpaceSettings = None
    theme: SpaceTheme = None
    lookAndFeel: LookAndFeel = None
    history: SpaceHistory = None
    _expandable: DotDict = None
    _links: DotDict = None


class EmbeddedContent(ApiModel):

    entityId: int = None
    entity: DotDict = None


class SuperBatchWebResources(ApiModel):

    uris: DotDict = None
    tags: DotDict = None
    metatags: str = None


class WebResourceDependencies(ApiModel):

    keys: List[str] = None
    contexts: List[str] = None
    uris: DotDict = None
    tags: DotDict = None
    superbatch: SuperBatchWebResources = None


class ContentBody(ApiModel):

    value: str = None
    representation: str = None
    embeddedContent: List[EmbeddedContent] = None
    webResource: WebResourceDependencies = None
    _exapndable = None


class Body(ApiModel):

    view: ContentBody = None
    export_view: ContentBody = None
    styled_view: ContentBody = None
    storage: ContentBody = None
    editor2: ContentBody = None
    anonymous_export_view: ContentBody = None
    _expandable: DotDict = None


class ContentExtensions(ApiModel):

    position: int = None


class Favourited(ApiModel):

    isFavourite: bool = None
    favouritedDate: str = None


class LastModified(ApiModel):

    version: "Version" = None
    friendlyLastModified: str = None


class LastContributed(ApiModel):

    status: str = None
    when: str = None


class Viewed(ApiModel):

    lastSeen: str = None
    friendlyLastSeen: str = None


class CurrentUserMetadata(ApiModel):

    favourited: Favourited = None
    lastModified: LastModified = None
    lastContributed: LastContributed = None
    viewed: Viewed = None


class ContentMetadata(ApiModel):

    currentUser: CurrentUserMetadata = None
    properties: DotDict = None
    frontend: DotDict = None
    labels: LabelArray = None


class Content(ApiModel):

    id: str = None
    type: str = None
    status: str = None
    space: Space = None
    history: "ContentHistory" = None
    version: "Version" = None
    ancestors: List["Content"] = None
    operations: List[OperationCheckResult] = None
    children: "ContentChildren" = None
    childTypes: "ContentChildType" = None
    descendants: "ContentChildren" = None
    containers: Union[Space, "Content"] = None
    body: Body = None
    restrictions: "ContentRestrictions" = None
    _expandable: DotDict = None
    _links: DotDict = None


@discriminator(lambda json: json.get("type") == "page")
class ContentPage(Content):

    title: str = None
    metadata: ContentMetadata = None
    extensions: ContentExtensions = None


class UpdateVersion(ApiModel):

    number: int = None


class UpdateContent(ApiModel):
    @classmethod
    def from_content(cls, content):
        me = cls()
        me.version = DotDict({"number": content.version.number + 1})
        me.title = content.title
        me.type = content.type
        me.status = content.status
        me.ancestors = (
            [DotDict({"id": content.ancestors[-1].id})] if content.ancestors else None
        )
        me.body = content.body
        return me

    version: UpdateVersion = None
    title: str = None
    type: str = None
    status: str = None
    ancestors: List["Content"] = None
    body: Body = None


class CreateContent(ApiModel):

    id: str = None
    title: str = None
    type: str = None
    space: Space
    status: str = None
    ancestors: List["Content"] = None
    body: Body = None


class ContentArray(ApiModel):

    results: List[Content] = None
    start: int = None
    limit: int = None
    size: int = None
    _links: DotDict = None


class ContentChildren(ApiModel):

    attachment: ContentArray = None
    comment: ContentArray = None
    page: ContentArray = None
    page: ContentArray = None
    _expandable: DotDict = None
    _links: DotDict = None


class ContentChildTypeValue(ApiModel):

    value: bool = None
    _links: DotDict = None


class ContentChildType(ApiModel):

    attachment: ContentChildTypeValue = None
    comment: ContentChildTypeValue = None
    page: ContentChildTypeValue = None
    _expandable: DotDict = None


class ContentRestriction(ApiModel):

    operation: str = None
    restrictions: "Restrictions" = None
    content: Content = None
    _expandable: DotDict = None
    _links: DotDict = None


class ContentRestrictions(ApiModel):

    read: ContentRestriction = None
    update: ContentRestriction = None
    _links: DotDict = None


class Restrictions(ApiModel):

    user: "UserArray" = None
    group: "GroupArray" = None
    _exapndable = None


class Contributors(ApiModel):

    publishers: "UsersUserKeys" = None


class ContentHistory(ApiModel):

    latest: bool = None
    createdBy: "User" = None
    createdDate: str = None
    lastUpdated: "Version" = None
    previousVersion: "Version" = None
    contributors: Contributors = None
    nextVersion: "Version" = None
    _expandable: DotDict = None
    _links: DotDict = None


class Business(ApiModel):

    position: str = None
    department: str = None
    location: str = None


class Personal(ApiModel):

    phone: str = None
    im: str = None
    website: str = None
    email: str = None


class UserDetails(ApiModel):

    business: Business = None
    personal: Personal = None


class User(ApiModel):

    type: str = None
    username: str = None
    userKey: str = None
    accountId: str = None
    accountType: str = None
    email: str = None
    publicName: str = None
    profilePicture: Icon = None
    displayName: str = None
    operations: OperationCheckResult = None
    details: UserDetails = None
    personalSpace: Space = None
    _expandable: DotDict = None
    _links: DotDict


class UsersUserKeys(ApiModel):

    users: List[User] = None
    userKeys: List[str] = None
    _links: DotDict = None


class UserArray(ApiModel):

    results: List[User] = None
    start: int = None
    limit: int = None
    size: int = None


class Group(ApiModel):

    type: str = None
    name: str = None
    _links: DotDict = None


class GroupArray(ApiModel):

    results: List[Group] = None
    start: int = None
    limit: int = None
    size: int = None


class Version(ApiModel):

    by: User = None
    when: str = None
    friendlyWhen: str = None
    message: str = None
    number: int = None
    minorEdit: bool = None
    content: Content = None
    collaborators: UsersUserKeys = None
    _expandable: DotDict = None
    _links: DotDict = None
