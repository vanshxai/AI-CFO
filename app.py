"""
AI CFO - Streamlit UI
Clean interface for the finance AI system.
"""

import streamlit as st
from orchestrator import AICFOOrchestrator, check_ollama_status
from finance_tools import get_available_tools
import json


st.set_page_config(
    page_title="AI CFO",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI CFO - Financial Analysis Assistant")
st.markdown("---")

# Initialize orchestrator
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = AICFOOrchestrator()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # Check Ollama status
    ollama_status = check_ollama_status()
    
    if ollama_status.get("ollama_available"):
        st.success("✅ Ollama is running")
        if ollama_status.get("phi3_available"):
            st.success("✅ Phi-3 model available")
        else:
            st.warning("⚠️ Phi-3 model not found. Run: `ollama pull phi3:mini`")
    else:
        st.error("❌ Ollama not running")
        st.info("Start Ollama with: `ollama serve`")
    
    st.markdown("---")
    
    st.header("Available Tools")
    tools = get_available_tools()
    for tool_name, tool_info in tools.items():
        with st.expander(f"`{tool_name}`"):
            st.write(f"**Description:** {tool_info['description']}")
            st.write("**Parameters:**")
            for param, desc in tool_info["parameters"].items():
                st.write(f"- `{param}`: {desc}")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Main chat area
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "details" in message and message["details"]:
            with st.expander("🔍 View Details"):
                if message["details"].get("tool_used"):
                    st.write("**Tool Used:**")
                    st.code(json.dumps(message["details"]["tool_used"], indent=2))
                if message["details"].get("tool_result"):
                    st.write("**Tool Result:**")
                    st.json(message["details"]["tool_result"])
                if message["details"].get("reasoning"):
                    st.write("**Model Reasoning:**")
                    st.write(message["details"]["reasoning"])

# User input
if prompt := st.chat_input("Ask about NPV, IRR, ROI, break-even analysis, or financial ratios..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Process with AI CFO
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            result = st.session_state.orchestrator.process_query(prompt)
            
            # Show final answer
            st.write(result["final_answer"])
            
            # Store details for expander
            details = {
                "tool_used": result["tool_used"],
                "tool_result": result["tool_result"],
                "reasoning": result["reasoning"]
            }
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["final_answer"],
                "details": details
            })

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "AI CFO powered by Phi-3 Mini • Local & Offline • No calculations by LLM"
    "</div>",
    unsafe_allow_html=True
)
