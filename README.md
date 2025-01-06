# **Summary of All GUI Options**

| **Option**                       | **Purpose**                                                 | **Visibility**                                                               |
|---------------------------------|-------------------------------------------------------------|------------------------------------------------------------------------------|
| **Input Source**                | Choose _Directory_, _Single File_, or _Multiline String_.   | Always visible.                                                              |
| **Path**                        | Select or type the path to the directory or file.           | Shown if _Directory_ or _Single File_ is selected.                           |
| **File Extension Filter**       | Limit files in a directory by extension (e.g., `.txt`).     | Shown **only** if _Directory_ is selected.                                   |
| **Multiline String Text Box**   | Type or paste text directly.                                | Shown **only** if _Multiline String_ is selected.                            |
| **Regex Pattern**               | Enter your regex (e.g., `\d+`, `[A-Z]`, etc.).              | Always visible.                                                              |
| **Operation Mode**              | - **Just Match**: logs matches<br>- **Invert Match**: remove/replace non-matches<br>- **Replace**: remove/replace matches | Always visible.                                                              |
| **Replacement Pattern**         | If “Invert Match” or “Replace,” text to replace with.       | Enabled only if _Invert Match_ or _Replace_. Disabled for _Just Match_.      |
| **Process** (Button)            | Runs the operation.                                         | Always visible.                                                              |
| **Console Output** (Text Area)  | Logs messages, errors, matches, etc.                        | Always shown at bottom of the window.                                        |

---

**That’s it!** You now have a comprehensive overview of all the GUI options and how to use them.

Disclaimer: this was originally developed for personal use, created using AI assistance, and licensed under the GPL-3.0 license.
