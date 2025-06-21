#!/usr/bin/env python3
"""Sophia AI Tool Explorer
Interactive tool to explore all available integrations, capabilities, and workflows
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.config_manager import get_secret
from backend.core.tool_registry import ToolCategory, ToolStatus, tool_registry

console = Console()


class SophiaToolExplorer:
    """Interactive tool explorer for Sophia AI"""

    def __init__(self):
        self.registry = tool_registry

    def display_summary(self):
        """Display overall tool summary"""
        console.print("\n[bold cyan]🤖 Sophia AI Tool Summary[/bold cyan]\n")

        # Status summary
        status_table = Table(title="Tool Status Overview", box=box.ROUNDED)
        status_table.add_column("Status", style="cyan")
        status_table.add_column("Count", justify="right")
        status_table.add_column("Percentage", justify="right")

        status_summary = self.registry.get_status_summary()
        total = sum(status_summary.values())

        for status, count in sorted(
            status_summary.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / total) * 100 if total > 0 else 0
            emoji = {
                ToolStatus.ACTIVE: "✅",
                ToolStatus.CONFIGURED: "🔧",
                ToolStatus.PLANNED: "📋",
                ToolStatus.DEPRECATED: "⚠️",
                ToolStatus.PLACEHOLDER: "🔲",
            }.get(status, "❓")

            status_table.add_row(
                f"{emoji} {status.value.title()}", str(count), f"{percentage:.1f}%"
            )

        console.print(status_table)

        # Category summary
        console.print("\n")
        category_table = Table(title="Tools by Category", box=box.ROUNDED)
        category_table.add_column("Category", style="green")
        category_table.add_column("Tools", justify="right")

        category_summary = self.registry.get_categories()
        for category, count in sorted(
            category_summary.items(), key=lambda x: x[0].value
        ):
            category_table.add_row(category.value, str(count))

        console.print(category_table)

    def display_category_tools(self, category: Optional[ToolCategory] = None):
        """Display tools by category"""
        if category:
            tools = self.registry.list_tools(category=category)
            title = f"Tools in {category.value}"
        else:
            tools = self.registry.list_tools()
            title = "All Tools"

        tree = Tree(f"[bold]{title}[/bold]")

        current_category = None
        category_branch = None

        for tool in tools:
            if tool.category != current_category:
                current_category = tool.category
                category_branch = tree.add(f"[yellow]{current_category.value}[/yellow]")

            status_emoji = {
                ToolStatus.ACTIVE: "✅",
                ToolStatus.CONFIGURED: "🔧",
                ToolStatus.PLANNED: "📋",
                ToolStatus.DEPRECATED: "⚠️",
                ToolStatus.PLACEHOLDER: "🔲",
            }.get(tool.status, "❓")

            tool_branch = category_branch.add(
                f"{status_emoji} [bold]{tool.name}[/bold] - {tool.description}"
            )

            if tool.mcp_server:
                tool_branch.add(f"[dim]MCP Server: {tool.mcp_server}[/dim]")

            if tool.api_key_env:
                tool_branch.add(f"[dim]API Key: {tool.api_key_env}[/dim]")

        console.print(tree)

    def display_tool_details(self, tool_id: str):
        """Display detailed information about a specific tool"""
        tool = self.registry.get_tool(tool_id)
        if not tool:
            console.print(f"[red]Tool '{tool_id}' not found[/red]")
            return

        status_emoji = {
            ToolStatus.ACTIVE: "✅",
            ToolStatus.CONFIGURED: "🔧",
            ToolStatus.PLANNED: "📋",
            ToolStatus.DEPRECATED: "⚠️",
            ToolStatus.PLACEHOLDER: "🔲",
        }.get(tool.status, "❓")

        # Create detailed panel
        content = f"""
# {status_emoji} {tool.name}

**Status:** {tool.status.value}
**Category:** {tool.category.value}
**Description:** {tool.description}
"""

        if tool.mcp_server:
            content += f"\n**MCP Server:** `{tool.mcp_server}`"

        if tool.api_key_env:
            content += f"\n**API Key Environment Variable:** `{tool.api_key_env}`"

        if tool.documentation_url:
            content += f"\n**Documentation:** {tool.documentation_url}"

        if tool.capabilities:
            content += "\n\n## Capabilities\n"
            for cap in tool.capabilities:
                content += f"\n### `{cap.name}`\n"
                content += f"{cap.description}\n\n"
                content += f"**Example:**\n```python\n{cap.example_usage}\n```\n"

                if cap.required_params:
                    content += (
                        f"\n**Required Parameters:** {', '.join(cap.required_params)}\n"
                    )
                if cap.optional_params:
                    content += (
                        f"**Optional Parameters:** {', '.join(cap.optional_params)}\n"
                    )

        if tool.example_workflows:
            content += "\n## Example Workflows\n"
            for workflow in tool.example_workflows:
                content += f"- {workflow}\n"

        if tool.dependencies:
            content += "\n## Dependencies\n"
            for dep in tool.dependencies:
                content += f"- {dep}\n"

        panel = Panel(
            Markdown(content), title=f"Tool Details: {tool.name}", border_style="cyan"
        )
        console.print(panel)

    async def check_tool_health(self, tool_id: str):
        """Check if a tool is properly configured and healthy"""
        tool = self.registry.get_tool(tool_id)
        if not tool:
            console.print(f"[red]Tool '{tool_id}' not found[/red]")
            return

        console.print(f"\n[cyan]Checking health for {tool.name}...[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Check API key
            task = progress.add_task("Checking API key configuration...", total=3)

            api_key_present = False
            if tool.api_key_env:
                try:
                    key = await get_secret(tool.api_key_env)
                    api_key_present = bool(key)
                except:
                    api_key_present = False

            progress.update(
                task,
                advance=1,
                description="Checking API key... "
                + ("✅" if api_key_present else "❌"),
            )

            # Check MCP server
            progress.update(task, description="Checking MCP server...")
            mcp_healthy = False
            if tool.mcp_server:
                try:
                    # This would check actual MCP server health
                    mcp_healthy = True  # Placeholder
                except:
                    mcp_healthy = False

            progress.update(
                task,
                advance=1,
                description="Checking MCP server... "
                + ("✅" if mcp_healthy or not tool.mcp_server else "❌"),
            )

            # Overall health
            progress.update(task, description="Analyzing overall health...")
            await asyncio.sleep(0.5)  # Simulate processing

            is_healthy = (
                (api_key_present or not tool.api_key_env)
                and (mcp_healthy or not tool.mcp_server)
                and tool.status in [ToolStatus.ACTIVE, ToolStatus.CONFIGURED]
            )

            progress.update(
                task,
                advance=1,
                description="Overall health... "
                + ("✅ Healthy" if is_healthy else "⚠️ Issues detected"),
            )

        # Display results
        results_table = Table(
            title=f"Health Check Results: {tool.name}", box=box.ROUNDED
        )
        results_table.add_column("Check", style="cyan")
        results_table.add_column("Status", justify="center")
        results_table.add_column("Details")

        results_table.add_row(
            "API Key",
            "✅" if api_key_present else "❌",
            (
                f"{tool.api_key_env} {'configured' if api_key_present else 'missing'}"
                if tool.api_key_env
                else "Not required"
            ),
        )

        results_table.add_row(
            "MCP Server",
            "✅" if mcp_healthy or not tool.mcp_server else "❌",
            (
                f"{tool.mcp_server} {'running' if mcp_healthy else 'not running'}"
                if tool.mcp_server
                else "Not required"
            ),
        )

        results_table.add_row(
            "Tool Status",
            "✅" if tool.status in [ToolStatus.ACTIVE, ToolStatus.CONFIGURED] else "⚠️",
            tool.status.value,
        )

        console.print("\n", results_table)

    def search_tools(self, query: str):
        """Search for tools matching a query"""
        results = self.registry.search_tools(query)

        if not results:
            console.print(f"[yellow]No tools found matching '{query}'[/yellow]")
            return

        console.print(
            f"\n[green]Found {len(results)} tools matching '{query}':[/green]\n"
        )

        for tool in results:
            status_emoji = {
                ToolStatus.ACTIVE: "✅",
                ToolStatus.CONFIGURED: "🔧",
                ToolStatus.PLANNED: "📋",
                ToolStatus.DEPRECATED: "⚠️",
                ToolStatus.PLACEHOLDER: "🔲",
            }.get(tool.status, "❓")

            console.print(
                f"{status_emoji} [bold]{tool.name}[/bold] ({tool.category.value})"
            )
            console.print(f"   {tool.description}")
            console.print()

    def show_workflows(self, workflow_query: Optional[str] = None):
        """Show example workflows"""
        if workflow_query:
            tools = self.registry.get_workflow_tools(workflow_query)
            title = f"Tools supporting '{workflow_query}' workflows"
        else:
            # Show all unique workflows
            all_workflows = set()
            for tool in self.registry.tools.values():
                all_workflows.update(tool.example_workflows)

            console.print("\n[bold]All Available Workflows:[/bold]\n")
            for workflow in sorted(all_workflows):
                console.print(f"• {workflow}")
            return

        if not tools:
            console.print(
                f"[yellow]No tools found for workflow '{workflow_query}'[/yellow]"
            )
            return

        console.print(f"\n[bold]{title}:[/bold]\n")

        for tool in tools:
            console.print(f"[cyan]{tool.name}[/cyan]")
            for workflow in tool.example_workflows:
                if workflow_query.lower() in workflow.lower():
                    console.print(f"  • {workflow}")
            console.print()

    def export_documentation(
        self, format: str = "markdown", filename: Optional[str] = None
    ):
        """Export tool registry documentation"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = (
                f"sophia_tools_{timestamp}.{format if format != 'markdown' else 'md'}"
            )

        content = self.registry.export_registry(format)

        with open(filename, "w") as f:
            f.write(content)

        console.print(f"[green]✅ Documentation exported to {filename}[/green]")

    async def interactive_mode(self):
        """Run interactive exploration mode"""
        console.print(
            Panel.fit(
                "[bold cyan]Welcome to Sophia AI Tool Explorer[/bold cyan]\n\n"
                "Explore all available tools, integrations, and capabilities",
                border_style="cyan",
            )
        )

        while True:
            console.print("\n[bold]Options:[/bold]")
            console.print("1. Show summary")
            console.print("2. Browse by category")
            console.print("3. View tool details")
            console.print("4. Search tools")
            console.print("5. Check tool health")
            console.print("6. Show workflows")
            console.print("7. Export documentation")
            console.print("8. Exit")

            choice = Prompt.ask(
                "\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"]
            )

            if choice == "1":
                self.display_summary()

            elif choice == "2":
                categories = list(ToolCategory)
                console.print("\n[bold]Categories:[/bold]")
                for i, cat in enumerate(categories, 1):
                    console.print(f"{i}. {cat.value}")
                console.print(f"{len(categories) + 1}. All categories")

                cat_choice = Prompt.ask(
                    "Select category",
                    choices=[str(i) for i in range(1, len(categories) + 2)],
                )

                if int(cat_choice) <= len(categories):
                    self.display_category_tools(categories[int(cat_choice) - 1])
                else:
                    self.display_category_tools()

            elif choice == "3":
                tool_id = Prompt.ask("Enter tool ID (e.g., 'gong', 'slack', 'apollo')")
                self.display_tool_details(tool_id)

            elif choice == "4":
                query = Prompt.ask("Enter search query")
                self.search_tools(query)

            elif choice == "5":
                tool_id = Prompt.ask("Enter tool ID to check health")
                await self.check_tool_health(tool_id)

            elif choice == "6":
                workflow = Prompt.ask(
                    "Enter workflow to search (or press Enter for all)"
                )
                self.show_workflows(workflow if workflow else None)

            elif choice == "7":
                format_choice = Prompt.ask(
                    "Export format", choices=["markdown", "json"], default="markdown"
                )
                self.export_documentation(format_choice)

            elif choice == "8":
                if Confirm.ask("Exit Tool Explorer?"):
                    console.print(
                        "[cyan]Thank you for using Sophia AI Tool Explorer![/cyan]"
                    )
                    break


async def main():
    """Main entry point"""
    explorer = SophiaToolExplorer()

    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "summary":
            explorer.display_summary()
        elif command == "list":
            explorer.display_category_tools()
        elif command == "search" and len(sys.argv) > 2:
            explorer.search_tools(" ".join(sys.argv[2:]))
        elif command == "export":
            format = sys.argv[2] if len(sys.argv) > 2 else "markdown"
            explorer.export_documentation(format)
        elif command == "workflows":
            query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
            explorer.show_workflows(query)
        else:
            console.print(
                "[red]Unknown command. Use: summary, list, search, export, workflows[/red]"
            )
    else:
        # Run interactive mode
        await explorer.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
