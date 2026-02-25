"""Feedbin MCP Server — exposes Feedbin RSS API as MCP tools."""

import os
import json
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = "https://api.feedbin.com/v2"

mcp = FastMCP("feedbin")


def _client() -> httpx.AsyncClient:
    email = os.environ.get("FEEDBIN_EMAIL")
    password = os.environ.get("FEEDBIN_PASSWORD")
    if not email or not password:
        raise RuntimeError(
            "FEEDBIN_EMAIL and FEEDBIN_PASSWORD environment variables must be set."
        )
    return httpx.AsyncClient(
        auth=(email, password),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=30.0,
    )


def _fmt(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Subscriptions / Feeds
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_subscriptions() -> str:
    """List all feed subscriptions in the Feedbin account.

    Returns a list of subscriptions, each with:
    - id: subscription id
    - feed_id: the associated feed id
    - title: feed title
    - feed_url: the RSS/Atom feed URL
    - site_url: the website URL
    - created_at: when the subscription was added
    """
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/subscriptions.json")
        r.raise_for_status()
        return _fmt(r.json())


@mcp.tool()
async def get_feed(feed_id: int) -> str:
    """Get details for a specific feed by its feed_id.

    Args:
        feed_id: The numeric feed ID.
    """
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/feeds/{feed_id}.json")
        r.raise_for_status()
        return _fmt(r.json())


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_unread_entries(page: int = 1, per_page: int = 50) -> str:
    """Get unread article entries from Feedbin.

    Returns a page of unread entries, each with fields like:
    id, feed_id, title, author, summary, url, published, created_at.

    Args:
        page: Page number (default 1).
        per_page: Number of entries per page, max 100 (default 50).
    """
    params: dict[str, Any] = {"read": "false", "page": page, "per_page": min(per_page, 100)}
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/entries.json", params=params)
        r.raise_for_status()
        return _fmt(r.json())


@mcp.tool()
async def get_read_entries(page: int = 1, per_page: int = 50) -> str:
    """Get read (already-read) article entries from Feedbin.

    Returns a page of read entries. Useful for reviewing recently-read articles.

    Args:
        page: Page number (default 1).
        per_page: Number of entries per page, max 100 (default 50).
    """
    params: dict[str, Any] = {"read": "true", "page": page, "per_page": min(per_page, 100)}
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/entries.json", params=params)
        r.raise_for_status()
        return _fmt(r.json())


@mcp.tool()
async def get_starred_entries(page: int = 1, per_page: int = 50) -> str:
    """Get starred (bookmarked) article entries from Feedbin.

    Starred entries are articles the user has explicitly saved/bookmarked.

    Args:
        page: Page number (default 1).
        per_page: Number of entries per page, max 100 (default 50).
    """
    params: dict[str, Any] = {"starred": "true", "page": page, "per_page": min(per_page, 100)}
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/entries.json", params=params)
        r.raise_for_status()
        return _fmt(r.json())


@mcp.tool()
async def get_entries(
    page: int = 1,
    per_page: int = 50,
    since: str = "",
    feed_id: int = 0,
    ids: str = "",
) -> str:
    """Get article entries with optional filters.

    Returns entries matching the provided filters.

    Args:
        page: Page number (default 1).
        per_page: Number of entries per page, max 100 (default 50).
        since: Only return entries created after this ISO 8601 datetime,
               e.g. "2024-01-01T00:00:00.000000Z".
        feed_id: If non-zero, only return entries from this specific feed.
        ids: Comma-separated list of specific entry IDs to retrieve (max 100).
    """
    params: dict[str, Any] = {"page": page, "per_page": min(per_page, 100)}
    if since:
        params["since"] = since
    if ids:
        params["ids"] = ids

    async with _client() as client:
        if feed_id:
            url = f"{BASE_URL}/feeds/{feed_id}/entries.json"
        else:
            url = f"{BASE_URL}/entries.json"
        r = await client.get(url, params=params)
        r.raise_for_status()
        return _fmt(r.json())


@mcp.tool()
async def get_entry(entry_id: int) -> str:
    """Get the full details of a single entry by its ID.

    Returns complete entry data including content (full HTML body).

    Args:
        entry_id: The numeric entry ID.
    """
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/entries/{entry_id}.json")
        r.raise_for_status()
        return _fmt(r.json())


# ---------------------------------------------------------------------------
# Unread state management
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_unread_entry_ids() -> str:
    """Get the list of all unread entry IDs.

    Returns a flat array of integer entry IDs that are currently unread.
    More efficient than fetching full entries when you just need counts or IDs.
    """
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/unread_entries.json")
        r.raise_for_status()
        return _fmt(r.json())


@mcp.tool()
async def mark_entries_read(entry_ids: list[int]) -> str:
    """Mark one or more entries as read.

    Args:
        entry_ids: List of entry IDs to mark as read.
    """
    async with _client() as client:
        r = await client.request(
            "DELETE",
            f"{BASE_URL}/unread_entries.json",
            content=json.dumps({"unread_entries": entry_ids}),
        )
        r.raise_for_status()
        return json.dumps({"status": "ok", "marked_read": entry_ids})


@mcp.tool()
async def mark_entries_unread(entry_ids: list[int]) -> str:
    """Mark one or more entries as unread.

    Args:
        entry_ids: List of entry IDs to mark as unread.
    """
    async with _client() as client:
        r = await client.post(
            f"{BASE_URL}/unread_entries.json",
            content=json.dumps({"unread_entries": entry_ids}),
        )
        r.raise_for_status()
        return json.dumps({"status": "ok", "marked_unread": entry_ids})


# ---------------------------------------------------------------------------
# Starred / bookmark management
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_starred_entry_ids() -> str:
    """Get the list of all starred entry IDs.

    Returns a flat array of integer entry IDs that are currently starred.
    More efficient than fetching full entries when you just need counts or IDs.
    """
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/starred_entries.json")
        r.raise_for_status()
        return _fmt(r.json())


@mcp.tool()
async def star_entries(entry_ids: list[int]) -> str:
    """Star (bookmark) one or more entries.

    Args:
        entry_ids: List of entry IDs to star.
    """
    async with _client() as client:
        r = await client.post(
            f"{BASE_URL}/starred_entries.json",
            content=json.dumps({"starred_entries": entry_ids}),
        )
        r.raise_for_status()
        return json.dumps({"status": "ok", "starred": entry_ids})


@mcp.tool()
async def unstar_entries(entry_ids: list[int]) -> str:
    """Unstar (remove bookmark from) one or more entries.

    Args:
        entry_ids: List of entry IDs to unstar.
    """
    async with _client() as client:
        r = await client.request(
            "DELETE",
            f"{BASE_URL}/starred_entries.json",
            content=json.dumps({"starred_entries": entry_ids}),
        )
        r.raise_for_status()
        return json.dumps({"status": "ok", "unstarred": entry_ids})


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_tags() -> str:
    """Get all tags used to organise subscriptions in the Feedbin account."""
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/tags.json")
        r.raise_for_status()
        return _fmt(r.json())


@mcp.tool()
async def get_taggings() -> str:
    """Get all taggings — the mapping of which feeds belong to which tags."""
    async with _client() as client:
        r = await client.get(f"{BASE_URL}/taggings.json")
        r.raise_for_status()
        return _fmt(r.json())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
