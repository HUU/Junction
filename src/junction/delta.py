"""The Junction Delta API

The Delta API uses sets of Modification's to build lists of API calls to execute against Confluence in order
to reconcile it with the pages in the local filesystem.

It assumes the wiki space is managed by Junction in its entirety and no other modifications are performed
manually.  The Delta API works well for large wiki spaces because it minimizes the amount of data that needs
to be fetched from Confluence, as well as the number of API calls needed to update the wiki.

The downside of the Delta API is certain errors will leave the wiki either in an unreconcilable state or it
will "leak" some pages, usually index pages, that need to be cleaned up by hand.

The Delta API breaks up modifications into several different actions and executes them in this order:
    * Page Deletes (and cleaning up any indexes without children after those deletes)
    * Starting Page Moves, by moving them to the root of the space with a randomly generated name (and cleaning up any indexes without children after those moves)
    * Page Creates (and making any index pages that do not already exist)
    * Finishing Page Moves, by moving them to their final destinations with the desired name (and making any index pages that do not already exist)
    * Page Updates

This ordering was chosen very specifically, along with the choice to split page moves in this seemingly peculiar way, to deal with various potential edge cases
that can occur based on the type of modifications, some examples:
    * A Page "A.md" gets moved into a folder with the same name and gets a new name "A/Foobar.md"
    * A Folder "Foobar" gets deleted and replaced with a file by the same name "Foobar.md"
These edge cases even occur in Confluence naturally, with users having to rename pages/move them around as they shuffle the page hierarchy.  This was the most sane, generic
way to replicate that procedure.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Iterable, Any
from uuid import uuid4

from junction.markdown import markdown_to_storage
from junction.confluence import Confluence
from junction.confluence.models import (
    UpdateContent,
    Body,
    ContentBody,
    CreateContent,
    Space,
    Content,
    ContentArray,
    ContentPage,
    Version,
)
from junction.git import Modification, ModificationType
from junction.util import for_all, JunctionError


logger = logging.getLogger(__name__)


class DeltaError(JunctionError):
    pass


class PageAction(ABC):
    """Base class for all actions against individual pages.  A page action should target an individual page in Confluence,
    though it may also trigger additional actions affecting other pages as needed to successfully complete the requested action,
    for example generating index pages for new folders.

    Page actions should attempt to be somewhat replayable.  This ensures if Junction fails while executing a Delta that it can simply
    be re-run.  This isn't quite full idempotency as some actions are inherently un-idempotent.  This could be changed to full idempotency
    if index pages were made explicit (via the git/Modification API) rather than implicit as needed by a particular page action."""

    def __init__(self, title: str):
        self.title = title

    @abstractmethod
    def execute(self, api_client: Confluence) -> Any:
        pass

    def fetch_target_page(self, api_client: Confluence) -> ContentArray[ContentPage]:
        query = api_client.content.get_page(
            title=self.title, expand="version,ancestors,childTypes.page"
        )
        if query.size and query.size > 1:
            raise RuntimeError(
                f"More than one result when searching for {self.title} to update; this should never happen, something strange is happening."
            )
        return query


class MovePage(PageAction):
    """Move a page to under a different parent, or to a different name, or both simultaneously.  Although Confluence supports it,
    you cannot change th content of the page while executing a move."""

    def __init__(self, title: str, new_title: str, ancestor_titles: List[str] = []):
        """Initializes an instance of MovePage.

        Arguments:
            title {str} -- The title of the page to move.
            new_title {str} -- The new title of the page (can be the same as the old title if you just want to change the parent).

        Keyword Arguments:
            ancestor_titles {List[str]} -- The names of the parents to move the page under from root to leaf, excluding the space homepage. (default: {[]})
        """
        super().__init__(title)
        self.new_title = new_title
        self.ancestor_titles = ancestor_titles if ancestor_titles else []

    def execute(self, api_client: Confluence) -> None:
        """Moves a page by (optionally) changing its title and (optionally) changing its parent.  If the targeted page does not
        exist, and the new page is already in place then returns successfully without doing anything.  This ensures this action
        can be replayed in the event of failure somewhere else in the Delta.  If the targeted page and the new page do not exist,
        then the operation aborts with an error as the wiki and git are in an unreconcilable state.

        Automatically created any ancestor pages that do not already exist for the moved page.
        Automatically deletes any ancestors pages without children after the old page is moved away.

        Arguments:
            api_client {Confluence} -- Confluence API client to use for all API actions.

        Raises:
            RuntimeError: If the targeted page cannot be found AND the new page is not present we cannot determine if
            the operation succeeded and fail out.
        """

        query = self.fetch_target_page(api_client)
        if query.size == 0:
            logger.warn(
                "%s does not exist, checking if the move to %s was previously completed...",
                self.title,
                self.new_title,
            )
            new_query = api_client.content.get_page(title=self.new_title)
            if new_query.size == 1:
                # new page already exists, move must have been done previously.
                logger.info(
                    "Trying to move %s, but it was already moved to %s",
                    self.title,
                    self.new_title,
                )
                return
            else:
                raise RuntimeError(f"No page found with title {self.title} to move.")
        else:
            old_page = query.results[0]

            parent = (
                EnsureAncestors(self.ancestor_titles).execute(api_client)
                if self.ancestor_titles
                else None
            )

            update_request = UpdateContent(
                title=self.new_title,
                type="page",
                version=Version(
                    number=old_page.version.number + 1
                    if old_page.version and old_page.version.number
                    else 2
                ),
                ancestors=[Content(id=parent.id)] if parent else None,
            )

            if old_page.id:
                logger.info(
                    "Moving %s to %s.",
                    (
                        [x.title for x in old_page.ancestors[1:]]
                        if old_page.ancestors
                        else []
                    )
                    + [self.title],
                    (self.ancestor_titles if self.ancestor_titles else [])
                    + [self.new_title],
                )
                api_client.content.update_content(old_page.id, update_request)
            else:
                raise JunctionError(
                    "Fatal error: unable to move page because its ID was unexpectedly empty.  This indicates Junction has a bug and hence has aborted the current operation."
                )

            if old_page.ancestors and old_page.ancestors[-1].title:
                # the last entry in ancestors will be the immediate parent
                CleanupEmptyAncestors(old_page.ancestors[-1].title).execute(api_client)


class CreatePage(PageAction):
    """Create a new page under a particular parent (or the space homepage if no parents specified)"""

    def __init__(self, title: str, new_body: str, ancestor_titles: List[str] = []):
        """Initializes an instance of CreatePage.

        Arguments:
            title {str} -- The title of the page to create.
            new_body {str} -- The body of the new page in Confluence storage representation.

        Keyword Arguments:
            ancestor_titles {List[str]} -- The names of the parents of the new page from root to leaf, excluding the space homepage. (default: {[]})
        """
        super().__init__(title)
        self.new_body = new_body
        self.ancestor_titles = ancestor_titles if ancestor_titles else []

    def execute(self, api_client: Confluence) -> Content:
        """Creates a brand new page under a particular parent.  If no parents are specified, Confluence makes the page under the space homepage.
        If the requested page already exists, this will instead update the existing page.  This ensures this action can be replayed in the event
        of a failure somewhere else in the Delta.

        Automatically created any ancestor pages that do not already exist.

        Arguments:
            api_client {Confluence} -- Confluence API client to use for all API actions.

        Returns:
            Content -- The created page.
        """

        query = self.fetch_target_page(api_client)
        if query.size == 1:
            logger.info(
                "Trying to create %s but it already exists, updating instead.",
                self.title,
            )
            return UpdatePage(self.title, self.new_body, self.ancestor_titles).execute(
                api_client
            )
        else:  # query.size == 0
            parent = (
                EnsureAncestors(self.ancestor_titles).execute(api_client)
                if self.ancestor_titles
                else None
            )

            create_request = CreateContent(
                title=self.title,
                type="page",
                space=Space(key=api_client.space_key),
                ancestors=[Content(id=parent.id)] if parent else None,
                body=Body(
                    storage=ContentBody(value=self.new_body, representation="storage")
                ),
            )

            logger.info(
                "Creating %s",
                (self.ancestor_titles if self.ancestor_titles else []) + [self.title],
            )
            return api_client.content.create_content(create_request)


class EnsureAncestors(CreatePage):
    """Creates index pages (which correspond to folders in the file system) recursively ensuring all parents up to the root (space homepage) exist."""

    PAGE_BODY_LIST_CHILDREN = '<p><ac:structured-macro ac:name="children" ac:schema-version="2" ac:macro-id="92c7a2c4-5cca-4ecf-81a2-946ef7388c71" /></p>'

    def __init__(self, ancestor_titles: List[str]):
        """Initializes an instance of EnsureAncestors.  This class should not be used for pages with no parents AKA pages
        whose parent is the space homepage.  The space homepage is assumed to exist and there is no handling for this not being
        the case.

        Arguments:
            ancestor_titles {List[str]} -- The names of each parent page in order, excluding the root (space homepage).
                                           Must not be empty, therefore at least one parent must be specified.
        """
        super().__init__(
            ancestor_titles[-1], self.PAGE_BODY_LIST_CHILDREN, ancestor_titles[:-1]
        )

    def execute(self, api_client: Confluence) -> Content:
        """Attempts to create the requested ancestor pages.  Begin by looking for the immediate parent (leaf page).
        If the leaf already exists, then the process ends.  Otherwise, attempt to create the leaf page, with the page
        content set to the Child Display macro in Confluence.  Page is created using CreatePage which will end up
        recursively calling EnsureAncestors.  Hence, this action will recursively create all missing parent pages from
        root to leaf in this order Child --> Grandchild --> Great Grandchild --> ... --> Leaf.

        Arguments:
            api_client {Confluence} -- Confluence API client to use for all API actions.

        Returns:
            Content -- The leaf ancestor (whose ID can be specified in ancestors[0].id for a create/update page request)
        """

        query = self.fetch_target_page(api_client)
        if query.size == 1:
            # ancestor must already exist
            logger.info(
                "Ancestor page %s already exists with ID %s.",
                self.title,
                query.results[0].id,
            )
            return query.results[0]
        else:  # query.size == 0
            logger.info("Ancestor page %s doesn't exist, creating it...")
            return super().execute(api_client)


class UpdatePage(PageAction):
    """Updates the content of a page.  Cannot move (change the title or parent) of a page even though Confluence supports this.  Use
    MovePage if you want to do that."""

    def __init__(self, title: str, new_body: str, ancestor_titles: List[str] = []):
        """Initializes an instance of UpdatePage.  This class should not be used for moving a page, it is only for changing the content
        of an existing page.

        Arguments:
            title {str} -- The title of the page to update.
            new_body {str} -- The body to assign to the page.  Should be in Confluence storage representation.

        Keyword Arguments:
            ancestor_titles {List[str]} -- The parents of the targeted page from root to leaf (excluding space homepage).
                                           Must match current parents in Confluence (default: {[]})
        """
        super().__init__(title)
        self.new_body = new_body
        self.ancestor_titles = ancestor_titles if ancestor_titles else []

    def execute(self, api_client: Confluence) -> Content:
        """Updates the content of an already existing page.  If the page does not exist, this operation silently switches to creating
        the page instead.  This ensures the action can be replayed in the event of failure somewhere else in the Delta.

        Fails if the ancestors are different from those found in Confluence; this is a sanity check that detects if the wiki is in an
        unreconcilable state with the file system (as otherwise update does not care what you put for ancestors).

        api_client {Confluence} -- Confluence API client to use for all API actions.

        Returns:
            Content -- The updated page.
        """

        query = self.fetch_target_page(api_client)
        if query.size == 1:
            existing = query.results[0]
            # skip the first ancestor, it's the space home page
            current_ancestors = (
                [x.title for x in existing.ancestors[1:]] if existing.ancestors else []
            )
            assert (
                self.ancestor_titles == current_ancestors
            ), "Cannot change ancestors with UpdatePage, use MovePage instead.  {} != {}.".format(
                self.ancestor_titles, current_ancestors
            )

            update_request = UpdateContent(
                title=self.title,
                type="page",
                version=Version(
                    number=existing.version.number + 1
                    if existing.version and existing.version.number
                    else 2
                ),
                ancestors=[Content(id=existing.ancestors[-1].id)]
                if existing.ancestors
                else [],
                body=Body(
                    storage=ContentBody(value=self.new_body, representation="storage")
                ),
            )

            if existing.id:
                logger.info(
                    "Updating %s with new content.",
                    (self.ancestor_titles if self.ancestor_titles else [])
                    + [self.title],
                )
                return api_client.content.update_content(existing.id, update_request)
            else:
                raise JunctionError(
                    "Fatal error: unable to update page because its ID was unexpectedly empty.  This indicates Junction has a bug and hence has aborted the current operation."
                )
        else:  # query.size == 0
            logger.info(
                "Trying to update %s but it doesn't exist, creating instead.",
                self.title,
            )
            return CreatePage(self.title, self.new_body, self.ancestor_titles).execute(
                api_client
            )


class DeletePage(PageAction):
    """Deletes an existing page."""

    def execute(self, api_client: Confluence) -> None:
        """Deletes the page from Confluence.  If the page does not exist then the operation reports success without doing
        anything.  This ensures that the action can be replayed in the event of failure elsewhere in the delta.

        Automatically cleans up any ancestor pages that no longer have children after the delete.

        Arguments:
            api_client {Confluence} -- Confluence API client to use for all API actions.
        """
        query = self.fetch_target_page(api_client)
        if query.size == 0:
            # already gone, don't error
            logger.info("Trying to delete %s but it's already gone.", self.title)
            return
        else:  # query.size == 1
            page = query.results[0]
            if page.id:
                logger.info(
                    "Deleting %s",
                    ([x.title for x in page.ancestors[1:]] if page.ancestors else [])
                    + [self.title],
                )
                api_client.content.delete_content(page.id)
            if page.ancestors and page.ancestors[-1].title:
                # try to cleanup any parents as they might now be empty..however skip
                # this step if there aren't any parents, or only 1 parent (that is always the
                # space homepage, and we don't want to delete that).
                # (the last entry in ancestors will be the immediate parent)
                CleanupEmptyAncestors(page.ancestors[-1].title).execute(api_client)


class CleanupEmptyAncestors(DeletePage):
    """Recursively cleans up ancestor pages that no longer have any children.  Should be used after any operations that may "empty out"
    an ancestor such as a move or a delete."""

    def execute(self, api_client: Confluence) -> None:
        """Removes the page if it has no more child pages.  It uses DeletePage for this operation
        which will end up recursively calling this action.  The result is that ancestors will be
        cleaned up all the way to the root if they become empty in this order: Leaf --> ... -> Great Grandchild
        --> Grandchild --> Child.

        Arguments:
            api_client {Confluence} -- Confluence API client to use for all API actions.
        """
        query = self.fetch_target_page(api_client)
        if query.size == 0:
            # already gone, don't error
            logger.info(
                "Cleaning up empty ancestor page %s but it's already gone.", self.title
            )
            return
        else:  # query.size == 1
            page = query.results[0]
            if (
                not page.childTypes
                or not page.childTypes.page
                or not page.childTypes.page.value
            ):
                # no children, delete self!  this will recursively delete all parents as they empty out too
                logger.info("Cleaning up empty ancestor page %s...", self.title)
                super().execute(api_client)
            else:
                logger.info(
                    "Cleaning up empty ancestor page %s but it still has children.",
                    self.title,
                )


class Delta(object):
    """A set of changes to be made to Confluence."""

    def __init__(self) -> None:
        self.deletes: List[PageAction] = []
        self.start_renames: List[PageAction] = []
        self.updates: List[PageAction] = []
        self.adds: List[PageAction] = []
        self.finish_renames: List[PageAction] = []

    def execute(self, api_client: Confluence) -> None:
        """Executes all of the changes to Confluence that this delta represents.  Operations
        are applied in a very particular order to ensure correctness in as many situations as possible.
        Deltas generically cannot be replayed but some tolerance for this has been added to support re-running
        if Junction fails for any reason (code bug, Confluence failure, network issue, etc).  In cases where
        Junction detects the wiki in an unreconcilable state the entire Delta will report with a more detailed error.

        In these cases, manual cleanup of the wiki may be necessary to restore service.  This is the key weakness of
        the Delta API.  On the otherhand, this API avoids reading/downloading more of the wiki than strictly necessary
        thus making it work well for large wiki spaces.

        Arguments:
            api_client {Confluence} -- Confluence API client to use for all API actions.
        """
        for_all(self.deletes, lambda x: x.execute(api_client))
        for_all(self.start_renames, lambda x: x.execute(api_client))
        for_all(self.adds, lambda x: x.execute(api_client))
        for_all(self.finish_renames, lambda x: x.execute(api_client))
        for_all(self.updates, lambda x: x.execute(api_client))

    @staticmethod
    def from_modifications(modifications: Iterable[Modification]) -> "Delta":
        """Builds a Delta from a list of (git) modifications.  Resulting Delta will work against
        wikis that have been updated and maintained exclusively with Junction, no other guarantees
        are provided.

        Arguments:
            modifications {List[Modification]} -- A list of modifications to a filesystem to be realized against Confluence

        Raises:
            NotImplementedError: A modification that is not supported by the Delta API will report failure.

        Returns:
            Delta -- A ready-to-execute Delta.
        """
        me = Delta()
        for mod in modifications:
            if not mod.path:
                continue

            title = mod.path.stem
            ancestors = list(mod.path.parts[:-1])

            if mod.change_type == ModificationType.ADD:
                me.adds.append(
                    CreatePage(title, markdown_to_storage(mod.source_code), ancestors)
                )
            elif mod.change_type == ModificationType.MODIFY:
                me.updates.append(
                    UpdatePage(title, markdown_to_storage(mod.source_code), ancestors)
                )
            elif mod.change_type == ModificationType.DELETE:
                me.deletes.append(DeletePage(title))
            elif mod.change_type == ModificationType.RENAME and mod.previous_path:
                old_title = mod.previous_path.stem
                temporary_title = f"{uuid4()}_{old_title}"
                me.start_renames.append(MovePage(old_title, temporary_title))
                me.finish_renames.append(MovePage(temporary_title, title, ancestors))
                me.finish_renames.append(
                    UpdatePage(title, markdown_to_storage(mod.source_code), ancestors)
                )
            else:
                raise NotImplementedError(
                    "Cannot process delta for modification type {}".format(
                        mod.change_type
                    )
                )
        return me
