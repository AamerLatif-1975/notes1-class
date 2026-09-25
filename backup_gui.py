
import tkinter as tk
from tkinter import filedialog, messagebox

from backup_system import create_backup, restore_backup


# ============================================================
# BACKUP GUI
# ============================================================

def open_backup_window():

    # ========================================================
    # MAIN WINDOW
    # ========================================================

    root = tk.Tk()

    root.title("HR Management System - Backup & Restore")
    root.geometry("500x350")
    root.resizable(False, False)

    # ========================================================
    # TITLE
    # ========================================================

    title_label = tk.Label(
        root,
        text="HR MANAGEMENT SYSTEM",
        font=("Arial", 20, "bold")
    )

    title_label.pack(pady=(30, 5))

    subtitle_label = tk.Label(
        root,
        text="Backup & Restore",
        font=("Arial", 14)
    )

    subtitle_label.pack(pady=(0, 25))

    # ========================================================
    # CREATE BACKUP
    # ========================================================

    def backup_button():

        backup_file = create_backup()

        if backup_file:

            messagebox.showinfo(
                "Backup Successful",
                f"Backup created successfully.\n\n"
                f"File:\n{backup_file}"
            )

        else:

            messagebox.showerror(
                "Backup Failed",
                "Backup could not be created."
            )

    # ========================================================
    # RESTORE BACKUP
    # ========================================================

    def restore_button():

        backup_file = filedialog.askopenfilename(
            title="Select HR Backup",
            filetypes=[
                ("Backup ZIP files", "*.zip"),
                ("All files", "*.*")
            ]
        )

        if not backup_file:
            return

        confirmation = messagebox.askyesno(
            "Confirm Restore",
            "WARNING!\n\n"
            "Restoring this backup will replace the "
            "current database and employee photos.\n\n"
            "Do you want to continue?"
        )

        if not confirmation:
            return

        final_confirmation = messagebox.askyesno(
            "Final Confirmation",
            "A backup of the current system will be created "
            "before restoration.\n\n"
            "Continue with RESTORE?"
        )

        if not final_confirmation:
            return

        restore_backup(backup_file)

        messagebox.showinfo(
            "Restore Process",
            "Restore process has been completed.\n\n"
            "Please restart the HR Management System."
        )

    # ========================================================
    # BUTTONS
    # ========================================================

    backup_button_widget = tk.Button(
        root,
        text="Create Backup",
        command=backup_button,
        width=25,
        height=2,
        font=("Arial", 12)
    )

    backup_button_widget.pack(pady=10)

    restore_button_widget = tk.Button(
        root,
        text="Restore Backup",
        command=restore_button,
        width=25,
        height=2,
        font=("Arial", 12)
    )

    restore_button_widget.pack(pady=10)

    exit_button = tk.Button(
        root,
        text="Exit",
        command=root.destroy,
        width=25,
        height=2,
        font=("Arial", 12)
    )

    exit_button.pack(pady=10)

    # ========================================================
    # START GUI
    # ========================================================

    root.mainloop()


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":
    open_backup_window()
