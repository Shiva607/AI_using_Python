## Explanation of CMD Commands (Python Virtual Environment)

### 1. Check Python Version

```cmd
python --version
```

This command displays the **installed Python version** on the system, helping confirm that Python is correctly installed and accessible from the command line.

---

### 2. List Global Python Packages

```cmd
python -m pip list
```

This shows all **packages installed globally** in the system Python environment (outside any virtual environment).

---

### 3. Create a Virtual Environment

```cmd
python -m venv venv
```

This creates a **virtual environment named `venv`** using the currently active Python version, allowing project-specific package isolation.

---

### 4. Activate the Virtual Environment

```cmd
venv\Scripts\activate
```

This activates the virtual environment, updating the command prompt and ensuring that Python and pip commands now use the **isolated environment** instead of the global one.

---

### 5. List Packages Inside Virtual Environment

```cmd
pip list
```

This displays packages installed **inside the virtual environment**, which is usually minimal (like `pip` and `setuptools`) at first.

---

### 6. Deactivate the Virtual Environment

```cmd
deactivate
```

This exits the virtual environment and returns the terminal to the **global Python environment**.

---

## Summary

These commands demonstrate how to **check Python installation, view global packages, create and activate a virtual environment, manage isolated dependencies, and return to the system environment**.

---