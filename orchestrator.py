"""
AI CFO Orchestration System
Handles model interaction, tool calling, and response generation.
"""

import json
import re
import requests
from typing import Dict, Any, Optional, List, Tuple
from finance_tools import execute_tool, get_available_tools


# System prompt with strict rules
SYSTEM_PROMPT = """You are an AI Financial Analyst. You have access to financial calculation tools.

CRITICAL RULES:
1. NEVER perform manual calculations - always use tools for numerical tasks
2. ALWAYS call tools for: NPV, IRR, ROI, break-even, financial ratios
3. Ask for missing inputs before calling tools (e.g., "What is the discount rate?")
4. Be concise and structured in your responses
5. Act as a professional financial analyst

AVAILABLE TOOLS:
- npv(cashflows, rate): Calculate Net Present Value
- irr(cashflows): Calculate Internal Rate of Return  
- roi(gain, cost): Calculate Return on Investment
- break_even(fixed_cost, price, variable_cost): Calculate Break-Even Point
- financial_ratios(balance_sheet, income_statement): Calculate Financial Ratios

TOOL CALLING FORMAT:
When you need to calculate something, output ONLY this JSON format:
{"tool": "function_name", "inputs": {"param1": value1, "param2": value2}}

EXAMPLES:
User: "Calculate NPV with cashflows [-1000, 300, 400, 500] at 10% rate"
Assistant: {"tool": "npv", "inputs": {"cashflows": [-1000, 300, 400, 500], "rate": 0.1}}

User: "What's the ROI if gain is 15000 and cost is 10000?"
Assistant: {"tool": "roi", "inputs": {"gain": 15000, "cost": 10000}}

User: "I need break-even analysis"
Assistant: I can help with break-even analysis. Please provide:
- Fixed costs
- Selling price per unit
- Variable cost per unit

After receiving tool results, explain the findings clearly as a financial analyst."""


class AICFOOrchestrator:
    """Orchestrates the AI CFO system with Ollama and finance tools."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "phi3:mini"):
        self.ollama_url = ollama_url
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        self.tools = get_available_tools()
        
    def _call_ollama(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Send prompt to Ollama and get response."""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 500
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.ConnectionError:
            return "ERROR: Cannot connect to Ollama. Please ensure Ollama is running."
        except requests.exceptions.Timeout:
            return "ERROR: Request timed out."
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def _extract_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract tool call JSON from model response."""
        # Try to find JSON pattern in the response
        json_pattern = r'\{[^{}]*"tool"[^{}]*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            try:
                tool_call = json.loads(match.group())
                if "tool" in tool_call and "inputs" in tool_call:
                    return tool_call
            except json.JSONDecodeError:
                pass
        
        # Also check if the entire response is JSON
        try:
            tool_call = json.loads(text.strip())
            if "tool" in tool_call and "inputs" in tool_call:
                return tool_call
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _format_tool_result(self, tool_name: str, result: Dict[str, Any]) -> str:
        """Format tool result for the model."""
        if result.get("status") == "error":
            return f"Tool '{tool_name}' returned error: {result.get('error', 'Unknown error')}"
        
        # Format based on tool type
        if tool_name == "npv":
            return f"NPV Result: ${result['npv']:,.2f} (Rate: {result['rate']*100:.1f}%, Cashflows: {result['cashflows']})"
        
        elif tool_name == "irr":
            return f"IRR Result: {result['irr_percentage']:.2f}% (Cashflows: {result['cashflows']})"
        
        elif tool_name == "roi":
            return f"ROI Result: {result['roi_percentage']:.2f}% (Net Profit: ${result['net_profit']:,.2f})"
        
        elif tool_name == "break_even":
            return (f"Break-Even Result: {result['break_even_units']:.2f} units "
                    f"or ${result['break_even_revenue']:,.2f} revenue "
                    f"(Contribution Margin: ${result['contribution_margin']:.2f}/unit)")
        
        elif tool_name == "financial_ratios":
            ratios = result.get("ratios", {})
            formatted = "Financial Ratios:\n"
            for key, value in ratios.items():
                if value is not None:
                    if "ratio" in key or "margin" in key:
                        formatted += f"  - {key.replace('_', ' ').title()}: {value:.4f}\n"
                    elif "turnover" in key:
                        formatted += f"  - {key.replace('_', ' ').title()}: {value:.2f}x\n"
                    else:
                        formatted += f"  - {key.replace('_', ' ').title()}: {value:.4f}\n"
            return formatted.strip()
        
        return f"Tool '{tool_name}' result: {json.dumps(result, indent=2)}"
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user query through the full orchestration cycle.
        
        Returns:
            Dictionary with reasoning, tool_used, and final_answer
        """
        result = {
            "user_input": user_input,
            "reasoning": "",
            "tool_used": None,
            "tool_result": None,
            "final_answer": ""
        }
        
        # Step 1: Get model's initial response
        model_response = self._call_ollama(user_input)
        result["reasoning"] = model_response
        
        # Step 2: Check if model wants to call a tool
        tool_call = self._extract_tool_call(model_response)
        
        if tool_call:
            tool_name = tool_call["tool"]
            inputs = tool_call["inputs"]
            result["tool_used"] = tool_name
            
            # Step 3: Execute the tool
            tool_result = execute_tool(tool_name, inputs)
            result["tool_result"] = tool_result
            
            # Step 4: Format tool result and send back to model
            formatted_result = self._format_tool_result(tool_name, tool_result)
            
            follow_up_prompt = (
                f"User query: {user_input}\n\n"
                f"Your tool call: {json.dumps(tool_call)}\n\n"
                f"Tool result: {formatted_result}\n\n"
                f"Now provide a clear, concise final answer as a financial analyst. "
                f"Explain what the result means and any implications."
            )
            
            final_response = self._call_ollama(follow_up_prompt, system_prompt="")
            result["final_answer"] = final_response
        else:
            # No tool needed - model provided direct answer
            result["final_answer"] = model_response
        
        return result
    
    def chat(self, user_input: str) -> str:
        """Simple chat interface that returns the final answer."""
        result = self.process_query(user_input)
        return result["final_answer"]
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []


def check_ollama_status(ollama_url: str = "http://localhost:11434") -> Dict[str, Any]:
    """Check if Ollama is running and model is available."""
    try:
        # Check if Ollama is running
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        
        model_names = [m.get("name", "") for m in models]
        phi3_available = any("phi3" in name.lower() for name in model_names)
        
        return {
            "status": "running",
            "ollama_available": True,
            "models": model_names,
            "phi3_available": phi3_available
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "not_running",
            "ollama_available": False,
            "message": "Ollama is not running. Start it with: ollama serve"
        }
    except Exception as e:
        return {
            "status": "error",
            "ollama_available": False,
            "message": str(e)
        }
