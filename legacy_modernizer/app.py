import os
import streamlit as st
from dotenv import load_dotenv
import zipfile
from io import BytesIO
from pathlib import Path

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
# Helper Functions
# -----------------------------
def get_file_extension(language: str) -> str:
    """Get proper file extension for language"""
    extension_map = {
        "python": "py",
        "java": "java",
        "javascript": "js",
        "cpp": "cpp",
        "c": "c",
        "csharp": "cs",
        "c#": "cs",
        "typescript": "ts",
        "go": "go",
        "rust": "rs",
        "kotlin": "kt",
        "swift": "swift"
    }
    return extension_map.get(language.lower(), "txt")


def create_download_zip(files_dict: dict) -> bytes:
    """
    Create a ZIP file from dictionary of files
    
    Args:
        files_dict: {"folder/filename.ext": "content", ...}
    
    Returns:
        bytes: ZIP file content
    """
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filepath, content in files_dict.items():
            zip_file.writestr(filepath, content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# -----------------------------
# Title
# -----------------------------
st.title("🚀 Legacy Code Modernizer")
st.markdown("""
### AI-Powered Two-Stage Modernization with Comprehensive Documentation

**Stage 1:** Structured analysis with schema validation  
**Stage 2:** Modern, production-ready code generation  
**Documentation:** Master document + modular focused docs

*Supports single files and bulk uploads with folder structure preservation*
""")

# -----------------------------
# Input Section
# -----------------------------
st.header("📝 Input Legacy Code")

upload_mode = st.radio(
    "Upload Mode",
    ["Single File", "Multiple Files (Bulk)"],
    horizontal=True
)

if upload_mode == "Single File":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload legacy code file",
            type=["py", "java", "js", "cpp", "c", "cs", "ts", "go", "rs", "kt", "swift"]
        )
    
    with col2:
        manual_language = st.selectbox(
            "Language (optional)",
            ["Auto-detect", "Python", "Java", "JavaScript", "C++", "C#", "TypeScript"]
        )
    
    code_input = st.text_area(
        "Or paste code here",
        height=300,
        placeholder="Paste legacy code..."
    )
    
    files_to_process = []
    
    if uploaded_file:
        files_to_process = [(uploaded_file.name, uploaded_file.read().decode("utf-8"), "")]
    elif code_input.strip():
        files_to_process = [("pasted_code.txt", code_input, "")]

else:
    # Bulk upload mode
    uploaded_files = st.file_uploader(
        "Upload multiple legacy code files",
        type=["py", "java", "js", "cpp", "c", "cs", "ts", "go", "rs", "kt", "swift"],
        accept_multiple_files=True
    )
    
    files_to_process = []
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} files uploaded")
        
        for uploaded_file in uploaded_files:
            # Extract folder structure from filename if present
            file_path = Path(uploaded_file.name)
            folder = str(file_path.parent) if file_path.parent != Path('.') else ""
            filename = file_path.name
            content = uploaded_file.read().decode("utf-8")
            
            files_to_process.append((filename, content, folder))

# -----------------------------
# Process Button
# -----------------------------
if st.button("🔍 Analyze & Modernize All", type="primary", use_container_width=True):
    
    # Check API key
    if not os.getenv("OPEN_ROUTER_API_KEY"):
        st.error("❌ OPEN_ROUTER_API_KEY not found in .env file")
        st.stop()
    
    if not files_to_process:
        st.warning("⚠️ Please provide code file(s)")
        st.stop()
    
    # Storage for results
    all_results = []
    modernized_files = {}  # For ZIP: {path: content}
    documentation_files = {}  # For ZIP: {path: content}
    
    # Process each file
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, (filename, source_code, folder) in enumerate(files_to_process):
        status_text.text(f"Processing {idx + 1}/{len(files_to_process)}: {filename}")
        
        # Detect language
        if upload_mode == "Single File" and manual_language != "Auto-detect":
            language = manual_language.lower()
        else:
            language = detect_language(filename, source_code)
        
        try:
            # -----------------------------
            # STAGE 1: Analysis
            # -----------------------------
            with st.spinner(f"🤖 Analyzing {filename}..."):
                doc_agent = DocumentationAgent()
                project_ir = doc_agent.generate_structured_analysis(source_code, language, filename)
            
            # Generate skeleton
            skeleton = doc_agent.generate_code_skeleton(project_ir)
            
            # -----------------------------
            # STAGE 2: Modernization
            # -----------------------------
            with st.spinner(f"⚡ Modernizing {filename}..."):
                mod_agent = ModernizationAgent()
                modernization_result = mod_agent.modernize_code(
                    source_code,
                    language,
                    project_ir.original_filename,
                    project_ir.suggested_filename
                )
            
            # -----------------------------
            # STAGE 3: Comprehensive Documentation
            # -----------------------------
            with st.spinner(f"📝 Generating documentation for {filename}..."):
                comprehensive_docs = doc_agent.generate_comprehensive_documentation(
                    project_ir,
                    source_code,
                    modernization_result["modernized_code"],
                    modernization_result["changes_summary"]
                )
            
            # Store results
            result = {
                "original_filename": filename,
                "folder": folder,
                "language": language,
                "ir": project_ir,
                "master_documentation": comprehensive_docs["master_doc"],
                "modular_documentation": comprehensive_docs["modular_docs"],
                "skeleton": skeleton,
                "modernized_code": modernization_result["modernized_code"],
                "suggested_filename": modernization_result["filename"],
                "changes_summary": modernization_result["changes_summary"]
            }
            
            all_results.append(result)
            
            # Add to ZIP collections
            # Preserve folder structure
            base_path = folder if folder else "output"
            
            # Modernized code
            modernized_files[f"{base_path}/modernized/{result['suggested_filename']}"] = result["modernized_code"]
            
            # Master documentation
            documentation_files[f"{base_path}/docs/MASTER_DOCUMENTATION.md"] = result["master_documentation"]
            
            # Modular documentation
            for doc_name, doc_content in result["modular_documentation"].items():
                documentation_files[f"{base_path}/docs/{doc_name}"] = doc_content
            
            # Skeleton
            documentation_files[f"{base_path}/skeleton/{filename}"] = result["skeleton"]
        
        except ValueError as e:
            st.error(f"❌ Schema validation failed for {filename}: {str(e)}")
            continue
        except Exception as e:
            st.error(f"❌ Failed to process {filename}: {str(e)}")
            continue
        
        # Update progress
        progress_bar.progress((idx + 1) / len(files_to_process))
    
    status_text.text("✅ All files processed!")
    progress_bar.empty()
    
    # -----------------------------
    # Display Results Summary
    # -----------------------------
    if not all_results:
        st.error("No files were successfully processed")
        st.stop()
    
    st.success(f"✅ Successfully processed {len(all_results)}/{len(files_to_process)} files")
    
    # -----------------------------
    # Download Options
    # -----------------------------
    st.header("📥 Download Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download all modernized code as ZIP
        modernized_zip = create_download_zip(modernized_files)
        st.download_button(
            "⬇️ Download Modernized Code (ZIP)",
            modernized_zip,
            "modernized_code.zip",
            "application/zip",
            use_container_width=True
        )
    
    with col2:
        # Download all documentation as ZIP
        docs_zip = create_download_zip(documentation_files)
        st.download_button(
            "⬇️ Download Documentation (ZIP)",
            docs_zip,
            "documentation.zip",
            "application/zip",
            use_container_width=True
        )
    
    with col3:
        # Download everything combined
        all_files = {**modernized_files, **documentation_files}
        all_zip = create_download_zip(all_files)
        st.download_button(
            "⬇️ Download Everything (ZIP)",
            all_zip,
            "complete_output.zip",
            "application/zip",
            use_container_width=True
        )
    
    # -----------------------------
    # Display Individual Results
    # -----------------------------
    st.header("📊 Detailed Results")
    
    for result in all_results:
        with st.expander(f"📄 {result['original_filename']} → {result['suggested_filename']}", expanded=False):
            
            st.markdown(f"**Language:** {result['language'].upper()}")
            st.markdown(f"**Folder:** `{result['folder'] or 'root'}`")
            st.markdown(f"**Summary:** {result['changes_summary']}")
            
            st.markdown("---")
            
            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📖 Master Documentation",
                "📚 Modular Docs",
                "⚡ Modernized Code",
                "📋 Skeleton",
                "🔍 IR Analysis"
            ])
            
            with tab1:
                st.markdown("### Complete Migration Documentation")
                st.markdown(result["master_documentation"])
                
                st.download_button(
                    "⬇️ Download Master Doc",
                    result["master_documentation"],
                    f"{result['original_filename']}_MASTER_DOC.md",
                    mime="text/markdown",
                    key=f"master_doc_{result['original_filename']}"
                )
            
            with tab2:
                st.markdown("### Modular Documentation Files")
                
                for doc_name, doc_content in result["modular_documentation"].items():
                    with st.expander(f"📄 {doc_name}"):
                        st.markdown(doc_content)
                        
                        st.download_button(
                            f"⬇️ Download {doc_name}",
                            doc_content,
                            doc_name,
                            mime="text/markdown",
                            key=f"{doc_name}_{result['original_filename']}"
                        )
            
            with tab3:
                st.markdown("### Modernized Code")
                st.code(result["modernized_code"], language=result["language"])
                
                st.download_button(
                    "⬇️ Download Modern Code",
                    result["modernized_code"],
                    result["suggested_filename"],
                    mime="text/plain",
                    key=f"modern_{result['original_filename']}"
                )
                
                # Side-by-side comparison
                st.markdown("---")
                st.markdown("### 🔄 Before & After Comparison")
                
                col_old, col_new = st.columns(2)
                
                with col_old:
                    st.markdown("#### Legacy Code")
                    st.code(files_to_process[all_results.index(result)][1][:1500], language=result["language"])
                
                with col_new:
                    st.markdown("#### Modern Code")
                    st.code(result["modernized_code"][:1500], language=result["language"])
            
            with tab4:
                st.markdown("### Code Skeleton")
                st.code(result["skeleton"], language=result["language"])
                
                st.download_button(
                    "⬇️ Download Skeleton",
                    result["skeleton"],
                    f"skeleton_{result['original_filename']}",
                    mime="text/plain",
                    key=f"skeleton_{result['original_filename']}"
                )
            
            with tab5:
                st.markdown("### Intermediate Representation (IR)")
                
                st.json(result["ir"].model_dump())
                
                # Key metrics
                col_m1, col_m2, col_m3 = st.columns(3)
                
                with col_m1:
                    st.metric("Modules", len(result["ir"].modules))
                
                with col_m2:
                    total_functions = sum(len(m.functions) for m in result["ir"].modules)
                    st.metric("Functions", total_functions)
                
                with col_m3:
                    st.metric("Technical Debt", len(result["ir"].technical_debt))
                
                # Technical debt breakdown
                if result["ir"].technical_debt:
                    st.markdown("#### Technical Debt by Severity")
                    
                    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
                    for debt in result["ir"].technical_debt:
                        severity_counts[debt.severity] += 1
                    
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    
                    with col_s1:
                        st.metric("🔴 Critical", severity_counts["critical"])
                    with col_s2:
                        st.metric("🟠 High", severity_counts["high"])
                    with col_s3:
                        st.metric("🟡 Medium", severity_counts["medium"])
                    with col_s4:
                        st.metric("🟢 Low", severity_counts["low"])