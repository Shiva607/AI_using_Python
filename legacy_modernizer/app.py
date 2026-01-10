import os
import streamlit as st
from dotenv import load_dotenv

from core.language_detector import detect_language
from agents.documentation_agent import DocumentationAgent
from agents.modernization_agent import ModernizationAgent

# Load .env at startup
load_dotenv()

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Legacy Code Modernizer",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("🚀 Legacy Code Modernizer")
st.markdown("""
### AI-Powered Two-Stage Modernization with Schema Validation

**Stage 1:** Structured analysis with schema validation  
**Stage 2:** Modern, production-ready code generation

*Powered by OpenRouter AI*
""")

# -----------------------------
# Input
# -----------------------------
st.header("📝 Input Legacy Code")

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload legacy code",
        type=["py", "java", "js", "cpp", "c", "cs"]
    )

with col2:
    manual_language = st.selectbox(
        "Language (optional)",
        ["Auto-detect", "Python", "Java", "JavaScript", "C++", "C#"]
    )

code_input = st.text_area(
    "Or paste code here",
    height=300,
    placeholder="Paste legacy code..."
)

# -----------------------------
# Process
# -----------------------------
if st.button("🔍 Analyze & Modernize", type="primary", use_container_width=True):
    
    # Check API key
    if not os.getenv("OPEN_ROUTER_API_KEY"):
        st.error("❌ OPEN_ROUTER_API_KEY not found in .env file")
        st.stop()
    
    if not uploaded_file and not code_input.strip():
        st.warning("⚠️ Please provide code")
        st.stop()
    
    # Get code
    if uploaded_file:
        source_code = uploaded_file.read().decode("utf-8")
        filename = uploaded_file.name
    else:
        source_code = code_input
        filename = ""
    
    # Detect language
    if manual_language != "Auto-detect":
        language = manual_language.lower()
    else:
        language = detect_language(filename, source_code)
    
    st.info(f"📌 Language: **{language.upper()}**")
    
    # -----------------------------
    # STAGE 1: Structured Analysis
    # -----------------------------
    st.header("📚 Stage 1: Structured Analysis")
    
    try:
        with st.spinner("🤖 Analyzing code with schema validation..."):
            doc_agent = DocumentationAgent()
            project_ir = doc_agent.generate_structured_analysis(source_code, language)
        
        st.success("✅ Analysis complete - Schema validated")
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Structured IR",
            "📋 Code Skeleton",
            "📖 Documentation",
            "🔍 Raw JSON"
        ])
        
        with tab1:
            st.markdown("### Validated Intermediate Representation")
            
            # Summary
            st.markdown(f"**Summary:** {project_ir.summary}")
            st.markdown(f"**Language:** {project_ir.language}")
            st.markdown(f"**Modules:** {len(project_ir.modules)}")
            
            # Module breakdown
            for module in project_ir.modules:
                with st.expander(f"📦 {module.name} ({module.type})"):
                    st.markdown(f"**Description:** {module.description}")
                    st.markdown(f"**Functions:** {len(module.functions)}")
                    
                    if module.design_patterns:
                        st.markdown(f"**Patterns:** {', '.join(module.design_patterns)}")
                    
                    for func in module.functions:
                        st.markdown(f"##### {func.name}")
                        st.markdown(f"*{func.description}*")
                        
                        if func.inputs:
                            st.markdown("**Inputs:**")
                            for inp in func.inputs:
                                st.markdown(f"- `{inp.type} {inp.name}`: {inp.description or 'N/A'}")
                        
                        if func.side_effects:
                            st.warning(f"Side effects: {', '.join(func.side_effects)}")
            
            # Technical debt
            if project_ir.technical_debt:
                st.markdown("### ⚠️ Technical Debt")
                for debt in project_ir.technical_debt:
                    severity_color = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢"
                    }
                    st.markdown(f"{severity_color[debt.severity]} **{debt.category}** ({debt.severity}): {debt.description}")
                    st.caption(f"💡 {debt.recommendation}")
        
        with tab2:
            st.markdown("### Code Skeleton")
            skeleton = doc_agent.generate_code_skeleton(project_ir)
            st.code(skeleton, language=language)
            
            st.download_button(
                "⬇️ Download Skeleton",
                skeleton,
                f"skeleton.{language}",
                use_container_width=True
            )
        
        with tab3:
            st.markdown("### Comprehensive Documentation")
            docs = doc_agent.generate_markdown_from_ir(project_ir)
            st.markdown(docs)
            
            st.download_button(
                "⬇️ Download Documentation",
                docs,
                "documentation.md",
                use_container_width=True
            )
        
        with tab4:
            st.markdown("### Raw JSON (Validated)")
            json_output = project_ir.model_dump_json(indent=2)
            st.code(json_output, language="json")
            
            st.download_button(
                "⬇️ Download JSON",
                json_output,
                "analysis.json",
                use_container_width=True
            )
    
    except ValueError as e:
        st.error(f"""
        ❌ **Schema Validation Failed**
        
        The LLM output did not match the required schema.
        
        **Error:** {str(e)}
        
        **Troubleshooting:**
        - Try a different model in .env file
        - Simplify the input code
        - Check if code is syntactically valid
        """)
        st.stop()
    
    except Exception as e:
        st.error(f"""
        ❌ **Analysis Failed**
        
        **Error:** {str(e)}
        
        Check your .env configuration.
        """)
        st.stop()
    
    # -----------------------------
    # STAGE 2: Modernization
    # -----------------------------
    st.header("⚡ Stage 2: Code Modernization")
    
    try:
        with st.spinner("🤖 Generating modern code..."):
            mod_agent = ModernizationAgent()
            modern_code = mod_agent.modernize_code(source_code, language)
        
        st.success(f"✅ Modern {language.upper()} generated")
        
        st.code(modern_code, language=language)
        
        st.download_button(
            "⬇️ Download Modern Code",
            modern_code,
            f"modernized.{language}",
            use_container_width=True
        )
        
        # Comparison
        st.markdown("---")
        st.subheader("🔄 Before & After")
        
        col_old, col_new = st.columns(2)
        
        with col_old:
            st.markdown("#### Legacy")
            st.code(source_code[:1000], language=language)
        
        with col_new:
            st.markdown("#### Modern")
            st.code(modern_code[:1000], language=language)
    
    except Exception as e:
        st.error(f"""
        ❌ **Modernization Failed**
        
        **Error:** {str(e)}
        
        Documentation from Stage 1 is still available above.
        """)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("""
**Architecture:** Legacy Code → Schema-Validated IR → Documentation + Skeleton → Modernized Code  
**Powered by:** OpenRouter AI
""")