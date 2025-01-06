import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
# https://chatgpt.com/share/677c1371-29e0-8010-9ea3-ffea5e57840f
# manual changes:
# lines 158-159:
#            else:
#                output_widget.insert(tk.END, f"No change needed: {filepath}\n")


ENCODINGS_TO_TRY = [
    'utf-8',
    'utf-16',
    'cp1252',
    'iso-8859-1'
]

def try_open_text_file(filepath):
    """
    Attempt to open and read the file using multiple encodings.
    Returns (content, encoding) if successful, or (None, None) if not.
    """
    for enc in ENCODINGS_TO_TRY:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read(), enc
        except UnicodeDecodeError:
            pass
        except FileNotFoundError:
            return None, None
        except PermissionError:
            return None, None
        except Exception as e:
            print(f"Unexpected error while reading '{filepath}' with encoding '{enc}': {e}")
            return None, None
    return None, None

def regex_replace_and_store(content, compiled_pattern, mode, replace_pattern=None):
    """
    Depending on the selected mode:
    
    1. 'match':
       - Detect all matches. No modifications.
       - Returns (None, list_of_matches).

    2. 'invert':
       - Treat all non-matching text as if it matched,
         and keep the actual matches unchanged.
       - If replace_pattern is provided, replace the non-matching segments with it,
         otherwise remove them.
       - Returns (updated_content, None).

    3. 'replace':
       - Standard search-and-replace for the matched text.
       - Returns (updated_content, None).
    """
    try:
        if mode == 'match':
            all_matches = compiled_pattern.findall(content)
            return None, all_matches

        elif mode == 'invert':
            parts = compiled_pattern.split(content)
            updated_segments = []
            for i, segment in enumerate(parts):
                if i % 2 == 1:  # matched text
                    updated_segments.append(segment)
                else:           # non-matching text
                    if replace_pattern is not None:
                        updated_segments.append(replace_pattern)
                    else:
                        updated_segments.append('')
            updated_content = ''.join(updated_segments)
            return updated_content, None

        elif mode == 'replace':
            updated_content = compiled_pattern.sub(
                replace_pattern if replace_pattern else '',
                content
            )
            return updated_content, None

        else:
            return None, None

    except re.error as e:
        print(f"Regex error: {e}")
        return None, None

def process_files(file_paths, match_pattern, mode, replace_pattern, output_widget):
    """
    Process each file in file_paths according to the chosen mode:
      - 'match': Log matches, no modifications
      - 'invert': Remove or replace non-matching parts
      - 'replace': Replace matched text

    Attempts multiple encodings. Skips files that cannot be read.
    """
    try:
        compiled_pattern = re.compile(f'({match_pattern})')
    except re.error as e:
        output_widget.insert(tk.END, f"Invalid Regex: {e}\n")
        output_widget.see(tk.END)
        return

    processed_count = 0
    skipped_count = 0
    matched_files = 0  # Only used in 'match' mode

    for filepath in file_paths:
        if not os.path.isfile(filepath):
            continue

        content, used_encoding = try_open_text_file(filepath)
        if content is None:
            skipped_count += 1
            output_widget.insert(tk.END, f"Skipping (unreadable or missing permissions): {filepath}\n")
            output_widget.see(tk.END)
            continue

        updated_content, matches = regex_replace_and_store(
            content=content,
            compiled_pattern=compiled_pattern,
            mode=mode,
            replace_pattern=replace_pattern
        )

        if mode != 'match' and updated_content is None and matches is None:
            # Means a regex error or some unexpected error
            skipped_count += 1
            output_widget.insert(tk.END, f"Skipping (regex error): {filepath}\n")
            output_widget.see(tk.END)
            continue

        if mode == 'match':
            if matches is None:
                skipped_count += 1
                output_widget.insert(tk.END, f"Skipping (regex error): {filepath}\n")
                output_widget.see(tk.END)
                continue
            if matches:
                matched_files += 1
                output_widget.insert(
                    tk.END,
                    f"[MATCH FOUND] {filepath} [Encoding: {used_encoding}] -> Matches: {matches}\n"
                )
        else:  # 'invert' or 'replace'
            if updated_content is not None and updated_content != content:
                try:
                    with open(filepath, 'w', encoding=used_encoding) as out_file:
                        out_file.write(updated_content)
                    output_widget.insert(
                        tk.END, f"Processed file: {filepath} [Encoding: {used_encoding}]\n"
                    )
                except PermissionError:
                    output_widget.insert(
                        tk.END, f"Skipping (no permission to write): {filepath}\n"
                    )
                except Exception as e:
                    output_widget.insert(
                        tk.END, f"Skipping (error writing to file {filepath}): {e}\n"
                    )

        processed_count += 1
        output_widget.see(tk.END)

    # Summaries
    output_widget.insert(tk.END, "\n--- Summary ---\n")
    output_widget.insert(tk.END, f"Processed files: {processed_count}\n")
    output_widget.insert(tk.END, f"Skipped files:   {skipped_count}\n")
    if mode == 'match':
        output_widget.insert(tk.END, f"Files with matches: {matched_files}\n")
    output_widget.insert(tk.END, "-----------------\n\n")
    output_widget.see(tk.END)

def process_multiline_string(text_input, match_pattern, mode, replace_pattern, output_widget):
    """
    Process a user-provided multiline string instead of files.
    Logs results to the output widget.
    """
    try:
        compiled_pattern = re.compile(f'({match_pattern})')
    except re.error as e:
        output_widget.insert(tk.END, f"Invalid Regex: {e}\n")
        output_widget.see(tk.END)
        return text_input

    try:
        updated_content, matches = regex_replace_and_store(
            content=text_input,
            compiled_pattern=compiled_pattern,
            mode=mode,
            replace_pattern=replace_pattern
        )
    except Exception as e:
        output_widget.insert(tk.END, f"Error processing string with regex: {e}\n")
        output_widget.see(tk.END)
        return text_input

    if updated_content is None and matches is None:
        output_widget.insert(tk.END, "Skipping due to regex error.\n")
        output_widget.see(tk.END)
        return text_input

    if mode == 'match':
        if matches:
            output_widget.insert(tk.END, f"Matches found: {matches}\n")
        else:
            output_widget.insert(tk.END, "No matches found.\n")
        return text_input
    else:
        # 'invert' or 'replace'
        if updated_content != text_input:
            output_widget.insert(tk.END, "The text was modified.\n")
            output_widget.insert(tk.END, "--- Updated Text Below ---\n")
            output_widget.insert(tk.END, updated_content + "\n\n")
        else:
            output_widget.insert(tk.END, "No change needed.\n")
        return updated_content

def gather_file_paths(input_type, path, extension_filter=None):
    """
    Return a list of file paths for 'single' or 'directory'.
    If extension_filter is provided (non-empty), only files matching that extension
    will be included. Otherwise, all files are included.
    """
    # Normalize extension_filter for easier checking
    if extension_filter:
        # If the user typed "txt" instead of ".txt", add the leading dot
        extension_filter = extension_filter.strip()
        if not extension_filter.startswith('.'):
            extension_filter = '.' + extension_filter
        extension_filter = extension_filter.lower()

    try:
        if input_type == 'single':
            # Single file input -> ignore extension filter here
            return [path] if os.path.isfile(path) else []
        else:
            file_paths = []
            for root, _, files in os.walk(path):
                for filename in files:
                    # If filter is specified, check extension
                    if extension_filter:
                        # Compare end of filename with extension filter
                        if not filename.lower().endswith(extension_filter):
                            continue
                    file_paths.append(os.path.join(root, filename))
            return file_paths
    except Exception as e:
        print(f"Error gathering file paths: {e}")
        return []

class RegexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Regex Utility")

        # 1) Frame: Input Source (directory vs. single file vs. multiline string)
        input_src_frame = tk.Frame(root, padx=10, pady=5)
        input_src_frame.pack(fill=tk.X)

        tk.Label(input_src_frame, text="Input Source:").pack(side=tk.LEFT)
        self.input_type_var = tk.StringVar(value='directory')

        tk.Radiobutton(
            input_src_frame, text="Directory", variable=self.input_type_var,
            value='directory', command=self.update_ui_for_input_type
        ).pack(side=tk.LEFT, padx=5)

        tk.Radiobutton(
            input_src_frame, text="Single File", variable=self.input_type_var,
            value='single', command=self.update_ui_for_input_type
        ).pack(side=tk.LEFT, padx=5)

        tk.Radiobutton(
            input_src_frame, text="Multiline String", variable=self.input_type_var,
            value='string', command=self.update_ui_for_input_type
        ).pack(side=tk.LEFT, padx=5)

        # 2) Frame that will contain either path_frame or text_frame
        self.input_details_frame = tk.Frame(root, padx=10, pady=5)
        self.input_details_frame.pack(fill=tk.X)

        # 2a) Path frame (for directory/single-file)
        self.path_frame = tk.Frame(self.input_details_frame)
        tk.Label(self.path_frame, text="Path:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(self.path_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        self.browse_button = tk.Button(self.path_frame, text="Browse", command=self.on_browse)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # 2b) Extension filter frame (only applies to 'directory')
        self.ext_filter_frame = tk.Frame(self.input_details_frame, pady=2)
        tk.Label(self.ext_filter_frame, text="File Extension Filter (optional):").pack(side=tk.LEFT)
        self.extension_var = tk.StringVar()
        self.ext_entry = tk.Entry(self.ext_filter_frame, textvariable=self.extension_var, width=8)
        self.ext_entry.pack(side=tk.LEFT, padx=5)

        # 2c) Text frame (for multiline string)
        self.text_frame = tk.Frame(self.input_details_frame)
        tk.Label(self.text_frame, text="Enter/paste your text below:").pack(anchor='w')

        # Set default (minimum) height to 1
        self.text_widget = tk.Text(self.text_frame, height=1, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.X, expand=True)
        self.text_widget.bind("<KeyRelease>", self.auto_resize_text)

        # 3) Frame: Regex pattern
        regex_frame = tk.Frame(root, padx=10, pady=5)
        regex_frame.pack(fill=tk.X)
        tk.Label(regex_frame, text="Regex pattern:").pack(side=tk.LEFT)
        self.regex_var = tk.StringVar()
        self.regex_entry = tk.Entry(regex_frame, textvariable=self.regex_var, width=50)
        self.regex_entry.pack(side=tk.LEFT, padx=5)

        # 4) Frame: Operation mode
        mode_frame = tk.Frame(root, padx=10, pady=5)
        mode_frame.pack(fill=tk.X)
        tk.Label(mode_frame, text="Operation Mode:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value='match')

        tk.Radiobutton(
            mode_frame, text="Just Match",
            variable=self.mode_var, value='match',
            command=self.update_replacement_state
        ).pack(side=tk.LEFT, padx=5)

        tk.Radiobutton(
            mode_frame, text="Invert Match",
            variable=self.mode_var, value='invert',
            command=self.update_replacement_state
        ).pack(side=tk.LEFT, padx=5)

        tk.Radiobutton(
            mode_frame, text="Replace",
            variable=self.mode_var, value='replace',
            command=self.update_replacement_state
        ).pack(side=tk.LEFT, padx=5)

        # 5) Frame: Replacement pattern
        replace_frame = tk.Frame(root, padx=10, pady=5)
        replace_frame.pack(fill=tk.X)
        tk.Label(replace_frame, text="Replacement pattern:").pack(side=tk.LEFT)
        self.replace_var = tk.StringVar()
        self.replace_entry = tk.Entry(replace_frame, textvariable=self.replace_var, width=50)
        self.replace_entry.pack(side=tk.LEFT, padx=5)

        # 6) Frame: Process button
        button_frame = tk.Frame(root, padx=10, pady=5)
        button_frame.pack(fill=tk.X)
        tk.Button(button_frame, text="Process", command=self.on_process).pack(side=tk.LEFT)

        # 7) Frame: Output (log)
        output_frame = tk.Frame(root, padx=10, pady=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(output_frame, text="Console Output:").pack(anchor="w")
        self.output_text = tk.Text(output_frame, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Initialize UI
        self.update_ui_for_input_type()
        self.update_replacement_state()

    def update_ui_for_input_type(self):
        """ Show path_frame + extension filter if directory, or just path_frame if single file, or text_frame if string. """
        input_type = self.input_type_var.get()

        # Hide all relevant frames first
        self.path_frame.pack_forget()
        self.ext_filter_frame.pack_forget()
        self.text_frame.pack_forget()

        if input_type == 'directory':
            # Show path frame and the extension filter frame
            self.path_frame.pack(fill=tk.X)
            self.ext_filter_frame.pack(fill=tk.X, padx=5)
        elif input_type == 'single':
            # Show path frame, hide extension filter
            self.path_frame.pack(fill=tk.X)
        else:  # 'string'
            # Show text frame
            self.text_frame.pack(fill=tk.X, expand=True)

    def on_browse(self):
        """Handle the Browse button for file/directory modes."""
        input_type = self.input_type_var.get()
        try:
            if input_type == 'single':
                filepath = filedialog.askopenfilename(
                    title="Select a single file",
                    filetypes=[("All files", "*.*")]
                )
                if filepath:
                    self.path_var.set(filepath)
            elif input_type == 'directory':
                directory = filedialog.askdirectory(title="Select a directory containing files")
                if directory:
                    self.path_var.set(directory)
        except Exception as e:
            messagebox.showerror("Error", f"Error during file/directory selection: {e}")

    def update_replacement_state(self):
        """Enable or disable the replacement pattern entry based on selected mode."""
        mode = self.mode_var.get()
        if mode == 'match':
            self.replace_entry.configure(state=tk.DISABLED)
            self.replace_var.set('')
        else:
            self.replace_entry.configure(state=tk.NORMAL)

    def on_process(self):
        """Collect user inputs and run the process."""
        input_type = self.input_type_var.get()  # 'single', 'directory', or 'string'
        path = self.path_var.get().strip()
        match_regex = self.regex_var.get().strip()
        mode = self.mode_var.get()
        replace_pattern = self.replace_var.get().strip() or None

        # Only applies if user selected directory
        extension_filter = None
        if input_type == 'directory':
            extension_filter = self.extension_var.get().strip() or None

        if not match_regex:
            messagebox.showwarning("Missing Regex", "Please provide a regex pattern.")
            return

        # Warn if we're about to modify files
        if mode in ('invert', 'replace') and input_type != 'string':
            proceed = messagebox.askyesno(
                "Warning",
                "This operation may permanently modify files. Do you want to continue?"
            )
            if not proceed:
                return

        # Clear the output
        self.output_text.delete("1.0", tk.END)

        try:
            if input_type == 'string':
                # Handle multiline string
                text_input = self.text_widget.get("1.0", tk.END).rstrip('\n')
                if not text_input:
                    messagebox.showwarning("Empty Text", "Please enter or paste some text.")
                    return

                self.output_text.insert(tk.END, f"Starting processing in '{mode}' mode (Multiline String)...\n\n")
                process_multiline_string(
                    text_input=text_input,
                    match_pattern=match_regex,
                    mode=mode,
                    replace_pattern=replace_pattern,
                    output_widget=self.output_text
                )
                self.output_text.insert(tk.END, "Processing complete.\n")
                self.output_text.see(tk.END)
                messagebox.showinfo("Done", "Processing completed!")

            elif input_type == 'single':
                # Single file
                if not os.path.isfile(path):
                    messagebox.showerror("Invalid File", "The selected path is not a valid file.")
                    return
                file_paths = [path]

                self.output_text.insert(tk.END, f"Starting processing in '{mode}' mode...\n\n")
                process_files(
                    file_paths=file_paths,
                    match_pattern=match_regex,
                    mode=mode,
                    replace_pattern=replace_pattern,
                    output_widget=self.output_text
                )
                self.output_text.insert(tk.END, "Processing complete.\n")
                self.output_text.see(tk.END)
                messagebox.showinfo("Done", "Processing completed!")

            else:
                # Directory
                if not os.path.isdir(path):
                    messagebox.showerror("Invalid Directory", "The selected path is not a valid directory.")
                    return

                file_paths = gather_file_paths(
                    input_type='directory',
                    path=path,
                    extension_filter=extension_filter
                )

                if not file_paths:
                    messagebox.showwarning("No Files", "No files found to process.")
                    return

                self.output_text.insert(tk.END, f"Starting processing in '{mode}' mode...\n\n")
                process_files(
                    file_paths=file_paths,
                    match_pattern=match_regex,
                    mode=mode,
                    replace_pattern=replace_pattern,
                    output_widget=self.output_text
                )
                self.output_text.insert(tk.END, "Processing complete.\n")
                self.output_text.see(tk.END)
                messagebox.showinfo("Done", "Processing completed!")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def auto_resize_text(self, event):
        """
        Dynamically adjust the text widget height based on the line count.
        """
        try:
            line_count = int(self.text_widget.index("end-1c").split('.')[0])
            min_height = 1
            max_height = 20
            new_height = max(min_height, min(line_count, max_height))
            self.text_widget.config(height=new_height)
        except Exception as e:
            print(f"Error resizing text widget: {e}")

def main():
    try:
        root = tk.Tk()
        app = RegexApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
