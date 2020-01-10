import json
from typing import Dict, TypeVar, List, Union


class ApiModel(object):

    def encode_json(self):
        return self.__dict__


class OperationCheckResult(ApiModel):

    operation: str = None
    targetType: str = None


class MenusLookAndFeel(ApiModel):

    hoverOrFocus = None
    color: str = None


class ButtonLookAndFeel(ApiModel):

    backgroundColor: str = None
    color: str = None

class NavigationLookAndFeel(ApiModel):

    color: str = None
    hoverOrFocus = None


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


class LookAndFeel(ApiModel):

    headings = None
    links = None
    menus: MenusLookAndFeel = None
    header: HeaderLookAndFeel = None
    content: ContentLookAndFeel = None
    bordersAndDividers = None


class Icon(ApiModel):

    path: str = None
    width: int = None
    height: int = None
    isDefault: bool = None


class SpacePermission(ApiModel):

    subjects = None
    operation: OperationCheckResult = None
    anonymousAccess: bool = None
    unlicensedAccess: bool = None


class SpaceSettings(ApiModel):

    routeOverrideEnabled: bool = None
    _links: Dict[str,str] = None


class Space(ApiModel):

    id: int = None
    key: str = None
    name: str = None
    icon: Icon = None
    description = None
    homepage: 'Content' = None
    type: str = None
    metadata = None
    operations: List[OperationCheckResult] = None
    permissions: List[SpacePermission] = None
    status: str = None
    settings: SpaceSettings = None
    theme = None
    lookAndFeel: LookAndFeel = None
    history = None
    _expandable = None
    _links: Dict[str,str] = None


class EmbeddedContent(ApiModel):

    entityId: int = None
    entity = None


class SuperBatchWebResources(ApiModel):

    uris = None
    tags = None
    metatags: str = None


class WebResourceDependencies(ApiModel):

    keys: List[str] = None
    contexts: List[str] = None
    uris = None
    tags = None
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
    _expandable = None


class Content(ApiModel):

    id = None
    type = None
    status = None
    space: Space = None
    history = None
    version = None
    ancestors: List['Content'] = None
    operations: List[OperationCheckResult] = None
    children = None
    childTypes = None
    descendants = None
    containers: Union[Space, 'Content'] = None
    body: Body = None
    restrictions = None
    _expandable = None
    _links: Dict[str,str] = None


class ContentArray(ApiModel):

    results: List[Content] = None
    start: int = None
    limit: int = None
    size: int = None
    _links: Dict[str,str] = None