import json
import sys
from pathlib import Path
import os

def merge_mcp_config(review_gate_dir: str):
    mcp_file_path = Path(os.path.expanduser("~/.cursor/mcp.json"))
    
    # Ensure paths use forward slashes for JSON
    review_gate_dir_json = review_gate_dir.replace("\\", "/") 
    python_path_json = f"{review_gate_dir_json}/venv/Scripts/python.exe"
    mcp_script_path_json = f"{review_gate_dir_json}/review_gate_v2_mcp.py"
    mcp_script_path_fixed_json = f"{review_gate_dir_json}/review_gate_v2_mcp_fixed.py"

    # Define the Review Gate specific MCP server configurations
    review_gate_servers = {
        "review-gate-v2": {
            "command": python_path_json,
            "args": [mcp_script_path_json],
            "env": {
                "PYTHONPATH": review_gate_dir_json,
                "PYTHONUNBUFFERED": "1",
                "REVIEW_GATE_MODE": "cursor_integration",
                "PYTHONIOENCODING": "utf-8"
            }
        },
        "review-gate-v2-fixed": {
            "command": python_path_json,
            "args": [mcp_script_path_fixed_json],
            "env": {
                "PYTHONPATH": review_gate_dir_json,
                "PYTHONUNBUFFERED": "1",
                "REVIEW_GATE_MODE": "cursor_integration",
                "PYTHONIOENCODING": "utf-8"
            }
        }
    }

    current_config = {"mcpServers": {}}

    # Read existing mcp.json if it exists
    if mcp_file_path.exists():
        try:
            with open(mcp_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip(): # Check if file is not empty
                    current_config = json.loads(content)
                else:
                    print(f"Info: Existing {mcp_file_path} is empty. Starting with new configuration.", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Warning: Existing {mcp_file_path} is not valid JSON. Creating new configuration.", file=sys.stderr)
            current_config = {"mcpServers": {}} # Start fresh if invalid
        except Exception as e:
            print(f"Error reading existing {mcp_file_path}: {e}. Creating new configuration.", file=sys.stderr)
            current_config = {"mcpServers": {}} # Start fresh on other read errors
    
    # Ensure mcpServers key exists and is a dictionary
    if "mcpServers" not in current_config or not isinstance(current_config["mcpServers"], dict):
        current_config["mcpServers"] = {}

    # Merge Review Gate servers into current config
    current_config["mcpServers"].update(review_gate_servers)

    # Write back the merged configuration
    try:
        mcp_file_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
        with open(mcp_file_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=2)
        print(f"✅ MCP configuration successfully updated at {mcp_file_path}")
    except Exception as e:
        print(f"❌ Error writing merged MCP configuration to {mcp_file_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python merge_mcp_config.py <REVIEW_GATE_DIR>", file=sys.stderr)
        sys.exit(1)
    
    review_gate_directory = sys.argv[1]
    merge_mcp_config(review_gate_directory) 