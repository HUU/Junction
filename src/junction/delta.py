from abc import ABC, abstractmethod
from typing import List

from junction.confluence.api import Confluence
from junction.confluence.models import (
    UpdateContent,
    Body,
    ContentBody,
    CreateContent,
    Space,
    Content,
)
from junction.git import Modification, ModificationType
from junction.util import for_all


class PageAction(ABC):
    @abstractmethod
    def execute(self, api_client: Confluence, space_key: str):
        pass


class MovePage(PageAction):
    def __init__(self, title: str, ancestor_titles: List[str] = None):
        self.title = title
        self.ancestor_titles = ancestor_titles

    def execute(self, api_client: Confluence, space_key: str):
        query = api_client.content.get_content(
            type="page", space_key=space_key, title=self.title, expand="version"
        )
        if query.size != 1:
            raise RuntimeError(
                f"No page found with title {self.title} in space {space_key} to move."
            )

        parent = (
            EnsureAncestors(self.ancestor_titles).execute(api_client, space_key)
            if self.ancestor_titles
            else None
        )

        update_request = UpdateContent()
        update_request.title = self.new_title
        update_request.type = "page"
        update_request.version = {"number": query.results[0].version.number + 1}
        update_request.ancestors = {"id": parent.id} if parent else None

        api_client.content.update_content(query.results[0].id, update_request)


class CreatePage(PageAction):
    def __init__(self, title: str, new_body: str, ancestor_titles: List[str] = None):
        self.title = title
        self.new_body = new_body
        self.ancestor_titles = ancestor_titles

    def execute(self, api_client: Confluence, space_key: str):
        query = api_client.content.get_content(
            type="page", space_key=space_key, title=self.title, expand="version"
        )
        if query.size > 1:
            raise RuntimeError(
                f"More than one result when searching for {self.title} in space {space_key} to update."
            )
        elif query.size == 1:
            UpdatePage(self.title, self.new_body, self.ancestor_titles).execute(
                api_client, space_key
            )
        else:  # query.size == 0
            parent = (
                EnsureAncestors(self.ancestor_titles).execute(api_client, space_key)
                if self.ancestor_titles
                else None
            )

            create_request = CreateContent()
            create_request.title = self.title
            create_request.type = "page"
            create_request.space = Space()
            create_request.space.key = space_key
            create_request.ancestors = {"id": parent.id} if parent else None
            create_request.body = Body()
            create_request.body.storage = ContentBody()
            create_request.body.storage.value = self.new_body

            return api_client.content.add_content(create_request)


class EnsureAncestors(CreatePage):
    def __init__(self, ancestor_titles: List[str]):
        super().__init__(ancestor_titles[-1], "Index page, todo", ancestor_titles[:-1])

    def execute(self, api_client: Confluence, space_key: str) -> Content:
        query = api_client.content.get_content(
            type="page", space_key=space_key, title=self.title, expand="version"
        )
        if query.size > 1:
            raise RuntimeError(
                f"More than one result when searching for {self.title} in space {space_key} to create."
            )
        elif query.size == 1 or not self.ancestor_titles:
            # ancestor must already exist OR this is the root page of the space..good enough!
            return query.results[0]
        else:  # query.size == 0 and it isn't the root page
            return super().execute(api_client, space_key)


class UpdatePage(PageAction):
    def __init__(self, title: str, new_body: str, ancestor_titles: List[str] = None):
        self.title = title
        self.new_body = new_body
        self.ancestor_titles = ancestor_titles

    def execute(self, api_client: Confluence, space_key: str) -> Content:
        query = api_client.content.get_content(
            type="page",
            space_key=space_key,
            title=self.title,
            expand="version,ancestors",
        )
        if query.size > 1:
            raise RuntimeError(
                f"More than one result when searching for {self.title} in space {space_key} to update."
            )
        elif query.size == 1:
            current_ancestors = [x.title for x in query.results[0].ancestors]
            assert (
                self.ancestor_titles == current_ancestors
            ), "Cannot change ancestors during with UpdatePage, use MovePage instead.  {} != {}".format(
                self.ancestor_titles, current_ancestors
            )

            update_request = UpdateContent()
            update_request.title = self.title
            update_request.type = "page"
            update_request.version = {"number": query.results[0].version.number + 1}
            update_request.ancestors = (
                {"id": query.results[0].ancestors[-1].id}
                if query.results[0].ancestors
                else None
            )
            update_request.body = Body()
            update_request.body.storage = ContentBody()
            update_request.body.storage.value = self.new_body

            return api_client.content.update_content(
                query.results[0].id, update_request
            )
        else:  # query.size == 0
            return CreatePage(self.title, self.new_body, self.ancestor_titles)


class DeletePage(PageAction):
    def __init__(self, title: str):
        self.title = title

    def execute(self, api_client: Confluence, space_key: str):
        query = api_client.content.get_content(
            type="page", space_key=space_key, title=self.title
        )
        if query.size > 1:
            raise RuntimeError(
                f"More than one result when searching for {self.title} in space {space_key} to delete."
            )
        elif query.size == 0:
            # already gone, don't error
            return
        else:  # query.size == 1
            api_client.content.delete_content(query.results[0].id)


class Delta(object):
    def __init__(self):
        self.deletes: List[PageAction] = []
        self.start_renames: List[PageAction] = []
        self.updates: List[PageAction] = []
        self.adds: List[PageAction] = []
        self.finish_renames: List[PageAction] = []

    def execute(self, api_client: Confluence, space_key: str):
        for_all(self.deletes, lambda x: x.execute(api_client, space_key))
        for_all(self.start_renames, lambda x: x.execute(api_client, space_key))
        for_all(self.adds, lambda x: x.execute(api_client, space_key))
        for_all(self.finish_renames, lambda x: x.execute(api_client, space_key))
        for_all(self.updates, lambda x: x.execute(api_client, space_key))
        # TODO: cleanup empty indexes?

    @staticmethod
    def from_modifications(modifications: List[Modification]):
        me = Delta()
        for mod in modifications:
            if mod.change_type == ModificationType.ADD:
                pass
            elif mod.change_type == ModificationType.MODIFY:
                pass
            elif mod.change_type == ModificationType.DELETE:
                pass
            elif mod.change_type == ModificationType.RENAME:
                pass
            else:
                raise NotImplementedError(
                    "Cannot process delta for modification type {}".format(
                        mod.change_type
                    )
                )
        return me
