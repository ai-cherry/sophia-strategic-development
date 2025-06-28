#!/usr/bin/env python3
"""
Sophia AI Prompt and Rule Management CLI
Similar to cursor-companion but integrated with Sophia AI
"""

import json
import argparse
from pathlib import Path

class SophiaPromptManager:
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.sophia_dir = self.workspace_root / ".sophia"
        self.prompts_dir = self.sophia_dir / "prompts"
        self.rules_dir = self.sophia_dir / "rules"
    
    def list_prompts(self):
        """List available prompts"""
        if not self.prompts_dir.exists():
            print("No prompts directory found. Run 'sophia init' first.")
            return
        
        prompts = list(self.prompts_dir.glob("*.json"))
        if not prompts:
            print("No prompts installed.")
            return
        
        print("📝 Installed Prompts:")
        for prompt_file in prompts:
            with open(prompt_file, 'r') as f:
                data = json.load(f)
            print(f"  • {prompt_file.stem}: {data.get('description', 'No description')}")
    
    def list_rules(self):
        """List available rules"""
        if not self.rules_dir.exists():
            print("No rules directory found. Run 'sophia init' first.")
            return
        
        rules = list(self.rules_dir.glob("*.json"))
        if not rules:
            print("No rules installed.")
            return
        
        print("📋 Installed Rules:")
        for rule_file in rules:
            with open(rule_file, 'r') as f:
                data = json.load(f)
            print(f"  • {rule_file.stem}: {data.get('description', 'No description')}")
    
    def show_prompt(self, name):
        """Show prompt details"""
        prompt_file = self.prompts_dir / f"{name}.json"
        if not prompt_file.exists():
            print(f"Prompt '{name}' not found.")
            return
        
        with open(prompt_file, 'r') as f:
            data = json.load(f)
        
        print(f"📝 Prompt: {name}")
        print(f"Description: {data.get('description', 'No description')}")
        print("\nTemplate:")
        print(data.get('template', 'No template'))
    
    def create_prompt(self, name, description, template):
        """Create a new prompt"""
        prompt_data = {
            "name": name,
            "description": description,
            "template": template,
            "created": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
        
        prompt_file = self.prompts_dir / f"{name}.json"
        with open(prompt_file, 'w') as f:
            json.dump(prompt_data, f, indent=2)
        
        print(f"✅ Created prompt: {name}")

def main():
    parser = argparse.ArgumentParser(description="Sophia AI Prompt Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List commands
    list_parser = subparsers.add_parser("list", help="List prompts or rules")
    list_parser.add_argument("type", choices=["prompts", "rules"], help="What to list")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show prompt details")
    show_parser.add_argument("name", help="Prompt name")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new prompt")
    create_parser.add_argument("name", help="Prompt name")
    create_parser.add_argument("description", help="Prompt description")
    create_parser.add_argument("template", help="Prompt template")
    
    args = parser.parse_args()
    manager = SophiaPromptManager()
    
    if args.command == "list":
        if args.type == "prompts":
            manager.list_prompts()
        else:
            manager.list_rules()
    elif args.command == "show":
        manager.show_prompt(args.name)
    elif args.command == "create":
        manager.create_prompt(args.name, args.description, args.template)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
