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

# Custom CSS for better formatting
st.markdown("""
<style>
    /* Improve spacing */
    .stMarkdown {
        line-height: 1.6;
    }
    
    /* Better code blocks */
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid #333;
    }
    
    /* Improve metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Better expanders */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Improve headers */
    h1, h2, h3, h4 {
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Better spacing for sections */
    .element-container {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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


def extract_folder_from_path(file_path: str) -> str:
    """
    Extract folder structure from file path
    Examples:
        'src/utils/helper.py' -> 'src/utils'
        'Calculator.java' -> ''
    """
    path = Path(file_path)
    if path.parent and path.parent != Path('.'):
        return str(path.parent).replace('\\', '/')
    return ""


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


def generate_index_documentation(all_results: list) -> str:
    """
    Generate main INDEX.md with links to all files
    """
    lines = []
    
    lines.append("# 📚 Code Modernization Project Index\n")
    lines.append("## Overview\n")
    lines.append(f"**Total Files Processed:** {len(all_results)}")
    lines.append(f"**Status:** ✅ Modernization Complete\n")
    lines.append("---\n")
    
    # Group by folder
    by_folder = {}
    for result in all_results:
        folder = result['folder'] or 'root'
        if folder not in by_folder:
            by_folder[folder] = []
        by_folder[folder].append(result)
    
    lines.append("## 📂 Project Structure\n")
    lines.append("```")
    lines.append("project/")
    for folder in sorted(by_folder.keys()):
        if folder == 'root':
            for r in by_folder[folder]:
                lines.append(f"├── {r['original_filename']}")
        else:
            lines.append(f"├── {folder}/")
            for r in by_folder[folder]:
                lines.append(f"│   ├── {r['original_filename']}")
    lines.append("```\n")
    
    lines.append("---\n")
    lines.append("## 📄 Files Overview\n")
    
    for folder in sorted(by_folder.keys()):
        if folder != 'root':
            lines.append(f"\n### 📁 {folder}\n")
        else:
            lines.append(f"\n### 📁 Root Level\n")
        
        for result in by_folder[folder]:
            lines.append(f"#### {result['original_filename']} → {result['suggested_filename']}\n")
            lines.append(f"**Language:** {result['language'].upper()}")
            lines.append(f"**Summary:** {result['changes_summary']}\n")
            
            # Links to documentation
            doc_path = f"{result['folder']}/docs" if result['folder'] else "docs"
            lines.append("**Documentation:**")
            lines.append(f"- [📖 Master Documentation]({doc_path}/MASTER_DOCUMENTATION.md)")
            lines.append(f"- [📋 README]({doc_path}/README.md)")
            lines.append(f"- [🏗️ Architecture]({doc_path}/ARCHITECTURE.md)")
            lines.append(f"- [🔄 Migration Guide]({doc_path}/MIGRATION_GUIDE.md)")
            
            if result['ir'].technical_debt:
                lines.append(f"- [⚠️ Technical Debt]({doc_path}/TECHNICAL_DEBT.md)")
            
            lines.append(f"- [📚 API Reference]({doc_path}/API_REFERENCE.md)")
            lines.append(f"- [🧪 Testing Guide]({doc_path}/TESTING_GUIDE.md)")
            
            # Link to modernized code
            modern_path = f"{result['folder']}/modernized" if result['folder'] else "modernized"
            lines.append(f"\n**Modernized Code:** [{result['suggested_filename']}]({modern_path}/{result['suggested_filename']})\n")
            
            # Metrics
            total_functions = sum(len(m.functions) for m in result['ir'].modules)
            lines.append(f"**Metrics:** {len(result['ir'].modules)} modules, {total_functions} functions, {len(result['ir'].technical_debt)} debt items\n")
            
            lines.append("---\n")
    
    lines.append("\n## 🚀 Quick Start\n")
    lines.append("1. Navigate to the modernized code for each file")
    lines.append("2. Read the MIGRATION_GUIDE.md for setup instructions")
    lines.append("3. Review TECHNICAL_DEBT.md for resolved issues")
    lines.append("4. Check TESTING_GUIDE.md for validation\n")
    
    lines.append("## 📊 Summary Statistics\n")
    
    total_modules = sum(len(r['ir'].modules) for r in all_results)
    total_functions = sum(sum(len(m.functions) for m in r['ir'].modules) for r in all_results)
    total_debt = sum(len(r['ir'].technical_debt) for r in all_results)
    
    lines.append(f"- **Total Modules:** {total_modules}")
    lines.append(f"- **Total Functions:** {total_functions}")
    lines.append(f"- **Technical Debt Resolved:** {total_debt} items")
    
    # Language breakdown
    languages = {}
    for r in all_results:
        lang = r['language'].upper()
        languages[lang] = languages.get(lang, 0) + 1
    
    lines.append(f"\n**Languages:**")
    for lang, count in languages.items():
        lines.append(f"- {lang}: {count} files")
    
    return '\n'.join(lines)


# -----------------------------
# Title
# -----------------------------
st.title("🚀 Legacy Code Modernizer")
st.markdown("""
### AI-Powered Two-Stage Modernization with Interlinked Documentation

**Stage 1:** Structured analysis with schema validation  
**Stage 2:** Modern, production-ready code generation  
**Documentation:** Interlinked master + modular docs with project index

*Supports folder uploads with complete structure preservation*
""")

# -----------------------------
# Input Section
# -----------------------------
st.header("📝 Input Legacy Code")

upload_mode = st.radio(
    "Upload Mode",
    ["Single File", "Multiple Files / Folder"],
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
    # Multiple files / folder upload mode
    st.info("💡 **Tip:** You can upload entire folders by selecting all files inside. Folder structure will be preserved automatically.")
    
    uploaded_files = st.file_uploader(
        "Upload multiple legacy code files (supports folder structure)",
        type=["py", "java", "js", "cpp", "c", "cs", "ts", "go", "rs", "kt", "swift"],
        accept_multiple_files=True
    )
    
    files_to_process = []
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} files uploaded")
        
        # Show detected folder structure
        detected_folders = set()
        for uploaded_file in uploaded_files:
            folder = extract_folder_from_path(uploaded_file.name)
            if folder:
                detected_folders.add(folder)
        
        if detected_folders:
            st.success(f"✅ Detected folder structure: {', '.join(sorted(detected_folders))}")
        
        for uploaded_file in uploaded_files:
            # Extract folder structure from filename
            folder = extract_folder_from_path(uploaded_file.name)
            filename = Path(uploaded_file.name).name
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
        status_text.text(f"Processing {idx + 1}/{len(files_to_process)}: {folder + '/' if folder else ''}{filename}")
        
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
            
            # Add to ZIP collections - PRESERVE FOLDER STRUCTURE
            if folder:
                base_path = folder
            else:
                base_path = "root"
            
            # Modernized code (preserve original folder structure)
            modernized_files[f"{base_path}/modernized/{result['suggested_filename']}"] = result["modernized_code"]
            
            # Documentation (in docs subfolder)
            documentation_files[f"{base_path}/docs/MASTER_DOCUMENTATION.md"] = result["master_documentation"]
            
            # Modular documentation
            for doc_name, doc_content in result["modular_documentation"].items():
                documentation_files[f"{base_path}/docs/{doc_name}"] = doc_content
            
            # Skeleton (preserve original name)
            documentation_files[f"{base_path}/skeleton/{filename}"] = result["skeleton"]
            
            # Original code (for reference)
            documentation_files[f"{base_path}/original/{filename}"] = source_code
        
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
    
    # Generate project index
    index_doc = generate_index_documentation(all_results)
    documentation_files["INDEX.md"] = index_doc
    
    # Generate project README
    project_readme = f"""# Modernized Code Project

## Overview

This project contains the modernized versions of {len(all_results)} legacy code files.

## 📋 Quick Links

- [📚 Project Index](INDEX.md) - Complete overview with links to all files
- [📂 Folder Structure](#folder-structure)

## Folder Structure

See [INDEX.md](INDEX.md) for complete project structure and file navigation.

## Getting Started

1. Start with [INDEX.md](INDEX.md) to see all processed files
2. Navigate to each file's documentation folder for detailed migration guides
3. Review modernized code in the `modernized/` folders
4. Check `TECHNICAL_DEBT.md` files for resolved issues

## Status

✅ **Modernization Complete**  
📊 **Files Processed:** {len(all_results)}  
🚀 **Ready for Integration**
"""
    
    documentation_files["README.md"] = project_readme
    
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
            "complete_modernization.zip",
            "application/zip",
            use_container_width=True
        )
    
    # Show project index
    st.header("📚 Project Index")
    
    with st.expander("View Complete Project Index", expanded=True):
        st.markdown(index_doc)
        
        st.download_button(
            "⬇️ Download INDEX.md",
            index_doc,
            "INDEX.md",
            mime="text/markdown"
        )
    
    # -----------------------------
    # Display Individual Results
    # -----------------------------
    st.header("📊 Detailed Results by File")
    
    # Group by folder
    by_folder = {}
    for result in all_results:
        folder = result['folder'] or 'root'
        if folder not in by_folder:
            by_folder[folder] = []
        by_folder[folder].append(result)
    
    for folder in sorted(by_folder.keys()):
        folder_display = f"📁 {folder}" if folder != 'root' else "📁 Root Level"
        
        with st.expander(folder_display, expanded=False):
            for result in by_folder[folder]:
                # Header with better spacing
                st.markdown(f"## 📄 {result['original_filename']} → {result['suggested_filename']}")
                st.markdown("---")
                
                # Metadata in clean columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Language**")
                    st.info(result['language'].upper())
                
                with col2:
                    st.markdown("**Status**")
                    st.success("✅ Modernized")
                
                with col3:
                    st.markdown("**Folder**")
                    st.code(result['folder'] or '/', language="text")
                
                # Changes summary in a nice box
                st.markdown("### 📝 Changes Summary")
                st.markdown(f"> {result['changes_summary']}")
                
                st.markdown("---")
                
                # Tabs for different views
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📖 Master Doc",
                    "📚 Modular Docs",
                    "⚡ Modern Code",
                    "📋 Skeleton",
                    "🔍 Analysis"
                ])
                
                with tab1:
                    st.markdown("### 📖 Complete Migration Documentation")
                    st.markdown("")  # Add spacing
                    
                    # Display master doc with better formatting
                    st.markdown(result["master_documentation"])
                    
                    st.markdown("")
                    st.download_button(
                        "⬇️ Download Master Documentation",
                        result["master_documentation"],
                        f"{result['original_filename']}_MASTER_DOC.md",
                        mime="text/markdown",
                        key=f"master_doc_{folder}_{result['original_filename']}",
                        use_container_width=True
                    )
                
                with tab2:
                    st.markdown("### 📚 Modular Documentation Files")
                    st.markdown("")
                    
                    # Display modular docs with better organization
                    doc_categories = {
                        "README.md": "📋 Project Overview",
                        "ARCHITECTURE.md": "🏗️ Architecture Details",
                        "MIGRATION_GUIDE.md": "🔄 Migration Guide",
                        "TECHNICAL_DEBT.md": "⚠️ Technical Debt",
                        "API_REFERENCE.md": "📚 API Reference",
                        "TESTING_GUIDE.md": "🧪 Testing Guide"
                    }
                    
                    for doc_name, doc_content in result["modular_documentation"].items():
                        doc_display = doc_categories.get(doc_name, f"📄 {doc_name}")
                        
                        with st.expander(doc_display, expanded=False):
                            st.markdown(doc_content)
                            
                            st.markdown("")
                            st.download_button(
                                f"⬇️ Download {doc_name}",
                                doc_content,
                                doc_name,
                                mime="text/markdown",
                                key=f"{doc_name}_{folder}_{result['original_filename']}",
                                use_container_width=True
                            )
                
                with tab3:
                    st.markdown("### ⚡ Modernized Code")
                    st.markdown("")
                    
                    # Show code with proper formatting
                    st.code(result["modernized_code"], language=result["language"])
                    
                    st.markdown("")
                    st.download_button(
                        "⬇️ Download Modernized Code",
                        result["modernized_code"],
                        result["suggested_filename"],
                        mime="text/plain",
                        key=f"modern_{folder}_{result['original_filename']}",
                        use_container_width=True
                    )
                    
                    # Side-by-side comparison with better layout
                    st.markdown("---")
                    st.markdown("### 🔄 Side-by-Side Comparison")
                    st.markdown("")
                    
                    col_old, col_new = st.columns(2)
                    
                    # Find original code
                    original_code = next(
                        (content for name, content, fld in files_to_process 
                         if name == result['original_filename'] and fld == result['folder']),
                        ""
                    )
                    
                    with col_old:
                        st.markdown("#### 🔴 Legacy Code (Before)")
                        st.code(original_code[:1500] + ("..." if len(original_code) > 1500 else ""), 
                               language=result["language"])
                    
                    with col_new:
                        st.markdown("#### 🟢 Modern Code (After)")
                        st.code(result["modernized_code"][:1500] + ("..." if len(result["modernized_code"]) > 1500 else ""), 
                               language=result["language"])
                
                with tab4:
                    st.markdown("### 📋 Code Skeleton")
                    st.markdown("")
                    
                    st.code(result["skeleton"], language=result["language"])
                    
                    st.markdown("")
                    st.download_button(
                        "⬇️ Download Skeleton",
                        result["skeleton"],
                        f"skeleton_{result['original_filename']}",
                        mime="text/plain",
                        key=f"skeleton_{folder}_{result['original_filename']}",
                        use_container_width=True
                    )
                
                with tab5:
                    st.markdown("### 🔍 Intermediate Representation Analysis")
                    st.markdown("")
                    
                    # Key metrics in cards
                    st.markdown("#### 📊 Key Metrics")
                    
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    
                    with col_m1:
                        st.metric(
                            label="Modules",
                            value=len(result["ir"].modules),
                            delta=None
                        )
                    
                    with col_m2:
                        total_functions = sum(len(m.functions) for m in result["ir"].modules)
                        st.metric(
                            label="Functions",
                            value=total_functions,
                            delta=None
                        )
                    
                    with col_m3:
                        st.metric(
                            label="Technical Debt",
                            value=len(result["ir"].technical_debt),
                            delta="Resolved",
                            delta_color="off"
                        )
                    
                    with col_m4:
                        st.metric(
                            label="Dependencies",
                            value=len(result["ir"].dependencies),
                            delta=None
                        )
                    
                    # Technical debt breakdown
                    if result["ir"].technical_debt:
                        st.markdown("")
                        st.markdown("#### ⚠️ Technical Debt by Severity")
                        
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
                        
                        # Show debt details
                        st.markdown("")
                        with st.expander("📋 View Technical Debt Details"):
                            for debt in result["ir"].technical_debt:
                                severity_emoji = {
                                    "critical": "🔴",
                                    "high": "🟠",
                                    "medium": "🟡",
                                    "low": "🟢"
                                }
                                
                                st.markdown(f"**{severity_emoji[debt.severity]} {debt.category.title()}** ({debt.severity})")
                                st.markdown(f"- **Issue:** {debt.description}")
                                st.markdown(f"- **Solution:** {debt.recommendation}")
                                st.markdown("")
                    
                    # Full IR JSON (collapsible)
                    st.markdown("")
                    with st.expander("🔍 View Complete IR (JSON)", expanded=False):
                        st.json(result["ir"].model_dump())
                
                # Separator between files
                st.markdown("---")
                st.markdown("")