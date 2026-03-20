#!/usr/bin/env python3
"""
AI CFO - CLI Interface
Command-line interface for the finance AI system.
"""

import sys
import json
from orchestrator import AICFOOrchestrator, check_ollama_status
from finance_tools import get_available_tools


def print_colored(text: str, color: str = "white"):
    """Print colored text in terminal."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def show_banner():
    """Display ASCII banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                    📊 AI CFO v1.0                        ║
║         Local Offline Financial Analysis Assistant       ║
║              Powered by Phi-3 Mini + Ollama              ║
╚══════════════════════════════════════════════════════════╝
    """
    print_colored(banner, "cyan")


def show_tools():
    """Display available tools."""
    print_colored("\n📋 Available Tools:", "green")
    tools = get_available_tools()
    for tool_name, tool_info in tools.items():
        print_colored(f"  • {tool_name}: {tool_info['description']}", "cyan")
        for param, desc in tool_info["parameters"].items():
            print(f"      - {param}: {desc}")


def check_system():
    """Check system status."""
    print_colored("\n🔍 System Status:", "green")
    status = check_ollama_status()
    
    if status.get("ollama_available"):
        print_colored("  ✓ Ollama is running", "green")
        if status.get("phi3_available"):
            print_colored("  ✓ Phi-3 model available", "green")
        else:
            print_colored("  ⚠ Phi-3 model not found. Run: ollama pull phi3:mini", "yellow")
    else:
        print_colored("  ✗ Ollama not running", "red")
        print_colored("    Start with: ollama serve", "yellow")
    
    return status.get("ollama_available", False)


def interactive_mode(orchestrator: AICFOOrchestrator):
    """Run interactive chat mode."""
    print_colored("\n💬 Interactive Mode (type 'quit' to exit, 'tools' to show tools)\n", "green")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print_colored("\nGoodbye!", "cyan")
                break
            
            if user_input.lower() == 'tools':
                show_tools()
                continue
            
            if user_input.lower() == 'status':
                check_system()
                continue
            
            # Process query
            print_colored("\nAI CFO:", "magenta")
            result = orchestrator.process_query(user_input)
            
            # Show reasoning if tool was used
            if result["tool_used"]:
                print_colored(f"  [Tool: {result['tool_used']}]", "yellow")
                if result["tool_result"]:
                    print_colored(f"  [Result: {json.dumps(result['tool_result'], indent=2)}]", "blue")
            
            print(f"\n{result['final_answer']}\n")
            
        except KeyboardInterrupt:
            print_colored("\n\nGoodbye!", "cyan")
            break
        except EOFError:
            break


def single_query_mode(orchestrator: AICFOOrchestrator, query: str, verbose: bool = False):
    """Process a single query and exit."""
    result = orchestrator.process_query(query)
    
    if verbose:
        print_colored("\n=== Reasoning ===", "yellow")
        print(result["reasoning"])
        
        if result["tool_used"]:
            print_colored("\n=== Tool Used ===", "yellow")
            print(f"Tool: {result['tool_used']}")
            print(f"Result: {json.dumps(result['tool_result'], indent=2)}")
        
        print_colored("\n=== Final Answer ===", "green")
    
    print(result["final_answer"])


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI CFO - Local Financial Analysis Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive mode
  %(prog)s -q "Calculate NPV..."    # Single query
  %(prog)s --tools                  # Show available tools
  %(prog)s --status                 # Check system status
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Single query to process"
    )
    parser.add_argument(
        "--tools",
        action="store_true",
        help="Show available tools"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check system status"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output with reasoning and tool details"
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama API URL (default: http://localhost:11434)"
    )
    
    args = parser.parse_args()
    
    show_banner()
    
    # Handle special flags
    if args.tools:
        show_tools()
        return
    
    if args.status:
        check_system()
        return
    
    # Initialize orchestrator
    orchestrator = AICFOOrchestrator(ollama_url=args.ollama_url)
    
    # Check system
    if not check_system():
        print_colored("\n⚠️  Ollama is not running. Some features may not work.", "yellow")
        print_colored("   Start Ollama with: ollama serve\n", "yellow")
    
    # Process query or start interactive mode
    if args.query:
        single_query_mode(orchestrator, args.query, args.verbose)
    else:
        interactive_mode(orchestrator)


if __name__ == "__main__":
    main()
