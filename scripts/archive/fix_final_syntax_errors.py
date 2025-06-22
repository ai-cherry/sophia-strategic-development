#!/usr/bin/env python3
"""Fix final syntax errors in pulumi_agent.py"""

import re


def fix_syntax_errors():
    """Fix syntax errors in pulumi_agent.py"""
    with open("backend/agents/pulumi_agent.py", "r") as f:
        content = f.read()

    # Fix line 57: command_lower = command.lower().
    content = content.replace(
        "command_lower = command.lower().\n", "command_lower = command.lower()\n"
    )

    # Fix line 144: stack_name = await self._get_stack_from_command_or_context(command, session_id).
    content = content.replace(
        "stack_name = await self._get_stack_from_command_or_context(command, session_id).\n",
        "stack_name = await self._get_stack_from_command_or_context(command, session_id)\n",
    )

    # Fix line 229: stack_name = await self._get_stack_from_command_or_context(command, session_id).
    content = content.replace(
        "stack_name = await self._get_stack_from_command_or_context(command, session_id).\n",
        "stack_name = await self._get_stack_from_command_or_context(command, session_id)\n",
    )

    # Fix line 239: try:.
    content = content.replace("        try:.\n", "        try:\n")

    # Fix line 269: stack_name = await self._get_stack_from_command_or_context(command, session_id).
    content = content.replace(
        "stack_name = await self._get_stack_from_command_or_context(command, session_id).\n",
        "stack_name = await self._get_stack_from_command_or_context(command, session_id)\n",
    )

    # Fix line 280: stack_name = await self._get_stack_from_command_or_context(command, session_id).
    content = content.replace(
        "stack_name = await self._get_stack_from_command_or_context(command, session_id).\n",
        "stack_name = await self._get_stack_from_command_or_context(command, session_id)\n",
    )

    # Fix the multi-line string issues (remove trailing commas after triple quotes)
    content = re.sub(r'""",(\.)?$', '"""', content, flags=re.MULTILINE)

    # Fix the specific issue on line 361 - remove comma after closing triple quotes
    content = content.replace(
        'pulumi.export("bucket_name", bucket.id)""",',
        'pulumi.export("bucket_name", bucket.id)"""',
    )
    content = content.replace(
        'pulumi.export("public_ip", instance.public_ip)""",',
        'pulumi.export("public_ip", instance.public_ip)"""',
    )
    content = content.replace(
        'pulumi.export("deployment_name", deployment.metadata.name)""",',
        'pulumi.export("deployment_name", deployment.metadata.name)"""',
    )

    # Write back
    with open("backend/agents/pulumi_agent.py", "w") as f:
        f.write(content)

    print("Fixed syntax errors in backend/agents/pulumi_agent.py")


if __name__ == "__main__":
    fix_syntax_errors()
