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
        "rust": "rs"
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
### AI-Powered Two-Stage Modernization

**Stage 1:** Structured analysis with schema validation  
**Stage 2:** Modern, production-ready code generation

*Supports single files and bulk uploads with folder structure preservation*
""")

# -----------------------------
# Input
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
            type=["py", "java", "js", "cpp", "c", "cs", "ts", "go", "rs"]
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
    
    files_to_process = []
    
    if uploaded_file:
        files_to_process = [(uploaded_file.name, uploaded_file.read().decode("utf-8"), "")]
    elif code_input.strip():
        files_to_process = [("pasted_code.txt", code_input, "")]

else:
    # Bulk upload mode
    uploaded_files = st.file_uploader(
        "Upload multiple legacy code files",
        type=["py", "java", "js", "cpp", "c", "cs", "ts", "go", "rs"],
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
            doc_agent = DocumentationAgent()
            project_ir = doc_agent.generate_structured_analysis(source_code, language, filename)
            
            # Generate documentation
            docs = doc_agent.generate_markdown_from_ir(project_ir)
            skeleton = doc_agent.generate_code_skeleton(project_ir)
            
            # -----------------------------
            # STAGE 2: Modernization
            # -----------------------------
            mod_agent = ModernizationAgent()
            modernization_result = mod_agent.modernize_code(
                source_code,
                language,
                project_ir.original_filename,
                project_ir.suggested_filename
            )
            
            # Store results
            result = {
                "original_filename": filename,
                "folder": folder,
                "language": language,
                "ir": project_ir,
                "documentation": docs,
                "skeleton": skeleton,
                "modernized_code": modernization_result["modernized_code"],
                "suggested_filename": modernization_result["filename"],
                "changes_summary": modernization_result["changes_summary"]
            }
            
            all_results.append(result)
            
            # Add to ZIP collections
            # Preserve folder structure
            base_path = folder if folder else "output"
            
            modernized_files[f"{base_path}/modernized/{result['suggested_filename']}"] = result["modernized_code"]
            documentation_files[f"{base_path}/docs/{filename}.md"] = result["documentation"]
            documentation_files[f"{base_path}/skeleton/{filename}"] = result["skeleton"]
        
        except Exception as e:
            st.error(f"❌ Failed to process {filename}: {str(e)}")
            continue
        
        # Update progress
        progress_bar.progress((idx + 1) / len(files_to_process))
    
    status_text.text("✅ All files processed!")
    progress_bar.empty()
    
    # -----------------------------
    # Display Results
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
            "⬇️ Download All Modernized Code (ZIP)",
            modernized_zip,
            "modernized_code.zip",
            "application/zip",
            use_container_width=True
        )
    
    with col2:
        # Download all documentation as ZIP
        docs_zip = create_download_zip(documentation_files)
        st.download_button(
            "⬇️ Download All Documentation (ZIP)",
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
        with st.expander(f"📄 {result['original_filename']} → {result['suggested_filename']}"):
            
            st.markdown(f"**Language:** {result['language'].upper()}")
            st.markdown(f"**Folder:** `{result['folder'] or 'root'}`")
            st.markdown(f"**Changes:** {result['changes_summary']}")
            
            tab1, tab2, tab3, tab4 = st.tabs(["Modernized Code", "Documentation", "Skeleton", "IR Analysis"])
            
            with tab1:
                st.code(result["modernized_code"], language=result["language"])
            
            with tab2:
                st.markdown(result["documentation"])
            
            with tab3:
                st.code(result["skeleton"], language=result["language"])
            
            with tab4:
                st.json(result["ir"].model_dump())