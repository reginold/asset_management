#!/usr/bin/env python3
"""
MCP Server for Asset Management
Provides tools for billing analysis and category management
"""

import asyncio
import json
import sys
from typing import Any, Sequence
from pathlib import Path

# Add agents directory to path
sys.path.append(str(Path(__file__).parent / "agents"))

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from billing_agent import BillingAgent, get_tools, handle_tool_call

# Create server instance
server = Server("asset-management")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    tools_config = get_tools()
    tools = []
    
    for tool_config in tools_config:
        tools.append(
            Tool(
                name=tool_config["name"],
                description=tool_config["description"],
                inputSchema=tool_config["inputSchema"]
            )
        )
    
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}
    
    try:
        result = handle_tool_call(name, arguments)
        
        if isinstance(result, dict) and "error" in result:
            return [
                TextContent(
                    type="text",
                    text=f"Error: {result['error']}"
                )
            ]
        
        # Format the result nicely
        if name == "process_billing":
            output = format_billing_report(result)
        elif name == "review_unknown_categories":
            output = format_unknown_categories(result)
        elif name == "update_category":
            output = f"✅ {result.get('message', 'Category updated successfully')}"
        else:
            output = json.dumps(result, indent=2, default=str)
            
        return [
            TextContent(
                type="text", 
                text=output
            )
        ]
        
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )
        ]

def format_billing_report(result):
    """Format billing report for display."""
    if "error" in result:
        return f"❌ Error: {result['error']}"
    
    summary = result.get("summary", {})
    output = f"""
📊 BILLING ANALYSIS REPORT
{'='*50}

📈 Summary:
  • Total Transactions: {summary.get('total_transactions', 0):,}
  • Total Amount: ¥{summary.get('total_amount', 0):,.0f}
  • Date Range: {summary.get('date_range', 'N/A')}
  • Files Processed: {result.get('files_processed', 0)}

💰 By Category:
"""
    
    by_category = result.get("by_category", {})
    if by_category:
        for category in by_category.get("sum", {}):
            amount = by_category["sum"][category]
            count = by_category["count"][category]
            output += f"  • {category}: ¥{amount:,.0f} ({count} transactions)\n"
    
    output += "\n📅 By Month:\n"
    by_month = result.get("by_month", {})
    for month, amount in by_month.items():
        output += f"  • {month}: ¥{amount:,.0f}\n"
    
    output += "\n✅ Analysis complete! Check 'billing_analysis.png' for visualizations."
    
    return output

def format_unknown_categories(result):
    """Format unknown categories for review."""
    unreviewed = result.get("unreviewed_merchants", {})
    
    if not unreviewed:
        return "✅ All merchants have been categorized!"
    
    output = f"""
📋 MERCHANTS REQUIRING CATEGORIZATION
{'='*50}

Found {len(unreviewed)} merchants needing review:

"""
    
    for merchant, info in list(unreviewed.items())[:10]:  # Show first 10
        date_added = info.get("date_added", "Unknown")[:10]  # Just date part
        output += f"  • {merchant} (added: {date_added})\n"
    
    if len(unreviewed) > 10:
        output += f"  ... and {len(unreviewed) - 10} more\n"
    
    output += """
To categorize a merchant, use:
  update_category(merchant="merchant_name", category="category_name")

Available categories:
  Shopping, Utilities, Transportation, Food & Dining, 
  Entertainment, Digital Services, Healthcare, Education, 
  Clothing, Other
"""
    
    return output

async def main():
    """Run the MCP server."""
    # Server can be configured here
    options = InitializationOptions(
        server_name="asset-management",
        server_version="1.0.0",
        capabilities={
            "tools": {},
            "resources": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    asyncio.run(main())