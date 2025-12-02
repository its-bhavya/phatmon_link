# MCP-Enhanced Agent Hooks Guide

This guide shows how to use MCP (Model Context Protocol) servers to supercharge your Phantom Link BBS agent hooks.

## What Are MCP Servers?

MCP servers provide external tools that Kiro agents can use during automated executions. Think of them as plugins that give your agent hooks superpowers like:
- File system operations
- API calls (fetch, GitHub, Slack)
- Database queries (PostgreSQL, SQLite)
- Cloud services (AWS, Google Cloud)

## Why Use MCP with Agent Hooks?

**Agent Hooks** = Automated triggers (on file save, message send, etc.)
**MCP Servers** = Tools available during those automated executions

Together, they enable sophisticated automation workflows.

## Setup: Your Current MCP Configuration

Your current MCP config at `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\Bhavya\\phantom-link-bbs"],
      "disabled": false
    }
  }
}
```

## Pattern 1: Auto-Test on Code Changes

**Use Case**: When you save a Python file, automatically run tests and report results.

### Hook Configuration
- **Trigger**: onFileSave
- **File Pattern**: `backend/**/*.py`
- **Action**: sendMessage

### Message Template
```
Use the filesystem MCP to:
1. Read the test file for this module
2. Check if tests exist for new functions
3. Report coverage gaps
```

### Why MCP Helps
The filesystem MCP can read test files, compare function signatures, and identify missing test coverage automatically.


## Pattern 2: Gemini Service Validation (Perfect for Your Project!)

**Use Case**: When you modify Gemini integration code, validate it against live API and test cases.

### Hook Configuration
- **Trigger**: onFileSave
- **File Pattern**: `backend/vecna/**/*.py`
- **Action**: sendMessage

### Message Template
```
Use MCP tools to validate this Gemini service change:
1. Use filesystem MCP to read backend/tests/test_gemini_service.py
2. Check if new test cases are needed for this change
3. Use fetch MCP to test a sample Gemini API call
4. Report any issues or missing test coverage
```

### Example Hook in Kiro UI
1. Open Command Palette → "Open Kiro Hook UI"
2. Create new hook:
   - Name: "Validate Gemini Changes"
   - Trigger: "On file save"
   - File pattern: `backend/vecna/**/*.py`
   - Action: "Send message to agent"
   - Message: (use template above)

### What Happens
When you save `backend/vecna/gemini_service.py`, Kiro automatically:
- Reads your test file using filesystem MCP
- Identifies missing test cases
- Tests actual API connectivity
- Reports back in chat

## Pattern 3: Database Integrity Checks

**Use Case**: When room models change, validate against actual database.

### Add SQLite MCP Server
Update your `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\Bhavya\\phantom-link-bbs"],
      "disabled": false
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "C:\\Users\\Bhavya\\phantom-link-bbs\\phantom_link.db"],
      "disabled": false
    }
  }
}
```

### Hook Configuration
- **Trigger**: onFileSave
- **File Pattern**: `backend/rooms/models.py`
- **Action**: sendMessage

### Message Template
```
Use MCP tools to validate room model changes:
1. Use filesystem MCP to read the updated models.py
2. Use sqlite MCP to query current room table schema
3. Check for schema mismatches
4. Suggest migration steps if needed
```


## Pattern 4: Auto-Routing Quality Assurance

**Use Case**: Monitor auto-routing decisions and flag potential issues.

### Hook Configuration
- **Trigger**: onMessage (or periodic)
- **Action**: sendMessage

### Message Template
```
Use MCP tools to analyze recent auto-routing decisions:
1. Use sqlite MCP to query last 20 routing decisions from database
2. Calculate routing accuracy metrics
3. Use filesystem MCP to append results to logs/routing_metrics.json
4. Alert if accuracy drops below 80%
```

### Advanced: Add Fetch MCP for External Monitoring

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "disabled": false
    }
  }
}
```

Then your hook can POST metrics to external monitoring services.

## Pattern 5: Documentation Sync

**Use Case**: When code changes, check if documentation needs updates.

### Hook Configuration
- **Trigger**: onFileSave
- **File Pattern**: `backend/**/*.py`
- **Action**: sendMessage

### Message Template
```
Use filesystem MCP to:
1. Read the changed Python file
2. Read related .md files in backend/vecna/
3. Check if docstrings match documentation
4. Suggest documentation updates if needed
```

## Recommended MCP Servers for Phantom Link BBS

### Essential (Add These)

**fetch** - For API testing and webhooks
```json
"fetch": {
  "command": "uvx",
  "args": ["mcp-server-fetch"],
  "disabled": false
}
```

**sqlite** - For database validation
```json
"sqlite": {
  "command": "uvx",
  "args": ["mcp-server-sqlite", "--db-path", "C:\\Users\\Bhavya\\phantom-link-bbs\\phantom_link.db"],
  "disabled": false
}
```

### Optional (Nice to Have)

**git** - For version control automation
```json
"git": {
  "command": "uvx",
  "args": ["mcp-server-git", "--repository", "C:\\Users\\Bhavya\\phantom-link-bbs"],
  "disabled": false
}
```


## Complete Example: Smart Test Runner Hook

Here's a complete, production-ready hook that uses multiple MCP servers:

### 1. Install Required MCP Servers

Update `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\Bhavya\\phantom-link-bbs"],
      "disabled": false,
      "autoApprove": ["read_file", "list_directory"]
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "C:\\Users\\Bhavya\\phantom-link-bbs\\phantom_link.db"],
      "disabled": false,
      "autoApprove": ["read_query"]
    }
  }
}
```

### 2. Create the Hook

Open Command Palette → "Open Kiro Hook UI"

**Hook Name**: Smart Test Runner
**Trigger**: On file save
**File Pattern**: `backend/**/*.py` (exclude test files: `!backend/tests/**`)
**Action**: Send message to agent

**Message**:
```
I just saved a Python file. Use MCP tools to run smart tests:

1. Use filesystem MCP to:
   - Read the saved file and identify changed functions
   - Find corresponding test file in backend/tests/
   - Check if tests exist for changed functions

2. If tests exist:
   - Run pytest on the specific test file
   - Report pass/fail status

3. If tests are missing:
   - List which functions need tests
   - Suggest test cases based on function signatures

4. Use sqlite MCP to:
   - Check if any database models were changed
   - Validate schema consistency

Report findings concisely.
```

### 3. What This Hook Does

When you save `backend/vecna/gemini_service.py`:
- Reads the file using filesystem MCP
- Finds `backend/tests/test_gemini_service.py`
- Identifies which functions changed
- Runs relevant tests
- Reports results in chat
- Flags missing test coverage

## Best Practices

### 1. Auto-Approve Safe Operations
In your MCP config, auto-approve read-only operations:

```json
"autoApprove": ["read_file", "list_directory", "read_query"]
```

This prevents approval prompts during automated hook executions.

### 2. Keep Hook Messages Focused
Bad: "Check everything and fix all issues"
Good: "Use filesystem MCP to read test file and report coverage for changed functions"

### 3. Use Conditional Logic
Structure your hook messages with clear steps:
```
1. If X, then do Y
2. Otherwise, do Z
3. Report results
```

### 4. Combine Multiple MCP Servers
Use filesystem + sqlite + fetch together for comprehensive checks.


## Troubleshooting

### MCP Server Not Found
If you get "uvx: command not found":
1. Install uv: `pip install uv` or use Homebrew/Chocolatey
2. Restart Kiro
3. Check MCP Server view in Kiro sidebar

### Hook Not Triggering
1. Check file pattern matches your saved file
2. Verify hook is enabled in Agent Hooks view
3. Check Kiro output panel for errors

### MCP Tools Not Available
1. Open MCP Server view in Kiro sidebar
2. Check server status (should be green/running)
3. Click "Reconnect" if needed
4. Check server logs for errors

### Approval Prompts During Hooks
Add operations to `autoApprove` list in MCP config:
```json
"autoApprove": ["read_file", "list_directory", "read_query"]
```

## Next Steps

1. **Start Simple**: Create one hook with filesystem MCP
2. **Test It**: Save a file and watch the hook execute
3. **Iterate**: Add more MCP servers as needed
4. **Monitor**: Check hook execution logs in Kiro

## Resources

- MCP Server Registry: https://github.com/modelcontextprotocol/servers
- Kiro Agent Hooks: Command Palette → "Open Kiro Hook UI"
- Your existing guide: `backend/vecna/AGENT_HOOKS_GUIDE.md`

## Quick Reference

### Common MCP Servers

| Server | Use Case | Install Command |
|--------|----------|-----------------|
| filesystem | Read/write files | `npx -y @modelcontextprotocol/server-filesystem` |
| sqlite | Database queries | `uvx mcp-server-sqlite --db-path <path>` |
| fetch | HTTP requests | `uvx mcp-server-fetch` |
| git | Version control | `uvx mcp-server-git --repository <path>` |
| github | GitHub API | `uvx mcp-server-github` |

### Hook Trigger Types

- **onFileSave**: When any file is saved
- **onMessage**: When you send a message to Kiro
- **onExecutionComplete**: After agent finishes a task
- **onSessionCreate**: When you start a new chat
- **manual**: Button in UI to trigger manually

### File Pattern Examples

- `**/*.py` - All Python files
- `backend/**/*.py` - Python files in backend/
- `!backend/tests/**` - Exclude test files
- `*.{js,ts}` - JavaScript and TypeScript files

---

**Pro Tip**: Start with the "Smart Test Runner" example above. It's immediately useful and demonstrates the power of MCP + Agent Hooks.
