# FeedbinMCP

> This project was generated almost entirely by [Claude Code](https://claude.ai/claude-code), Anthropic's AI coding assistant, with only minor human editing.

An [MCP](https://modelcontextprotocol.io) server that connects Claude to your [Feedbin](https://feedbin.com) RSS account. Read articles, manage read/unread state, and star or unstar entries — all from a Claude conversation.

## Tools

| Tool | Description |
|------|-------------|
| `get_subscriptions` | List all subscribed feeds |
| `get_feed` | Get details for a specific feed |
| `get_unread_entries` | Paginated unread articles |
| `get_read_entries` | Paginated read articles |
| `get_starred_entries` | Paginated starred articles |
| `get_entries` | Entries with filters (feed, date, IDs) |
| `get_entry` | Full content for a single entry |
| `get_unread_entry_ids` | Flat list of all unread IDs |
| `get_starred_entry_ids` | Flat list of all starred IDs |
| `mark_entries_read` | Mark one or more entries as read |
| `mark_entries_unread` | Mark one or more entries as unread |
| `star_entries` | Star (bookmark) entries |
| `unstar_entries` | Remove star from entries |
| `get_tags` | List all tags |
| `get_taggings` | Feed-to-tag mappings |

## Requirements

- Python 3.11+
- A [Feedbin](https://feedbin.com) account
- [pip](https://pip.pypa.io) (ships with Python)

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/hypermoose/FeedbinMCP.git
cd FeedbinMCP

# 2. Install the package and its dependencies
pip install -e .
```

This installs a `feedbin-mcp` command and all required dependencies (`mcp`, `httpx`).

To confirm the install worked:

```bash
feedbin-mcp --help
```

## Adding to Claude Code

Run this once, substituting your real Feedbin credentials:

```bash
claude mcp add feedbin \
  --env FEEDBIN_EMAIL=you@example.com \
  --env FEEDBIN_PASSWORD=your_password \
  -- feedbin-mcp
```

Verify it's registered:

```bash
claude mcp list
```

The server will be available in all Claude Code sessions. Type `/mcp` inside a session to confirm it's connected.

## Credentials

Feedbin uses HTTP Basic Auth (email + password). The server reads credentials from two environment variables:

| Variable | Description |
|----------|-------------|
| `FEEDBIN_EMAIL` | Your Feedbin account email |
| `FEEDBIN_PASSWORD` | Your Feedbin account password |

These are passed via `--env` in the `claude mcp add` command above and are never stored in the repository.

## Running directly (without installing)

If you prefer not to install the package, you can run the server directly with Python after installing dependencies:

```bash
pip install mcp[cli] httpx

FEEDBIN_EMAIL=you@example.com \
FEEDBIN_PASSWORD=your_password \
python feedbin_mcp/server.py
```

And reference it in Claude Code as:

```bash
claude mcp add feedbin \
  --env FEEDBIN_EMAIL=you@example.com \
  --env FEEDBIN_PASSWORD=your_password \
  -- python /path/to/FeedbinMCP/feedbin_mcp/server.py
```
