from pathlib import Path
from datetime import datetime
import zipfile
import shutil
import tempfile


# ============================================================
# PROJECT SETTINGS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "db.sqlite3"
MEDIA_FOLDER = BASE_DIR / "media"
BACKUP_FOLDER = BASE_DIR / "backups"


# ============================================================
# CREATE BACKUP
# ============================================================

def create_backup():

    if not DATABASE_FILE.exists():
        print("ERROR: Database file not found.")
        return None

    BACKUP_FOLDER.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    backup_filename = (
        f"HR_Backup_{timestamp}.zip"
    )

    backup_path = (
        BACKUP_FOLDER / backup_filename
    )

    try:

        with zipfile.ZipFile(
            backup_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as backup_zip:

            # -------------------------
            # Database
            # -------------------------

            backup_zip.write(
                DATABASE_FILE,
                arcname="db.sqlite3"
            )

            # -------------------------
            # Media
            # -------------------------

            if MEDIA_FOLDER.exists():

                for file_path in MEDIA_FOLDER.rglob("*"):

                    if file_path.is_file():

                        relative_path = (
                            file_path.relative_to(BASE_DIR)
                        )

                        backup_zip.write(
                            file_path,
                            arcname=str(relative_path)
                        )

        print()
        print("======================================")
        print("BACKUP CREATED SUCCESSFULLY")
        print("======================================")
        print(f"Backup file:")
        print(backup_path)
        print()

        return backup_path

    except Exception as error:

        print()
        print("ERROR: Backup failed.")
        print(error)

        if backup_path.exists():
            backup_path.unlink()

        return None


# ============================================================
# VALIDATE BACKUP
# ============================================================

def validate_backup(backup_path):

    backup_path = Path(backup_path)

    if not backup_path.exists():

        print("ERROR: Backup file not found.")
        return False

    if not zipfile.is_zipfile(backup_path):

        print("ERROR: This is not a valid ZIP backup.")
        return False

    try:

        with zipfile.ZipFile(
            backup_path,
            "r"
        ) as backup_zip:

            file_list = backup_zip.namelist()

            # Database must exist
            if "db.sqlite3" not in file_list:

                print(
                    "ERROR: db.sqlite3 is missing from backup."
                )

                return False

            # -------------------------
            # Security check
            # -------------------------

            base_resolved = BASE_DIR.resolve()

            for file_name in file_list:

                target_path = (
                    BASE_DIR / file_name
                ).resolve()

                if not str(target_path).startswith(
                    str(base_resolved)
                ):

                    print(
                        "ERROR: Unsafe file detected in backup."
                    )

                    return False

            # -------------------------
            # Test ZIP integrity
            # -------------------------

            bad_file = backup_zip.testzip()

            if bad_file is not None:

                print(
                    f"ERROR: Corrupt file in backup: {bad_file}"
                )

                return False

        print("Backup verified successfully.")

        return True

    except Exception as error:

        print("ERROR: Could not validate backup.")
        print(error)

        return False


# ============================================================
# RESTORE BACKUP
# ============================================================

def restore_backup(backup_path):

    backup_path = Path(backup_path)

    print()
    print("Checking backup...")

    # --------------------------------------------------------
    # STEP 1: Validate backup
    # --------------------------------------------------------

    if not validate_backup(backup_path):

        print()
        print("RESTORE CANCELLED.")

        return

    # --------------------------------------------------------
    # STEP 2: Confirmation
    # --------------------------------------------------------

    print()
    print("WARNING!")
    print("--------------------------------------")
    print("Restoring this backup will replace:")
    print("1. Current database")
    print("2. Current employee photos")
    print("--------------------------------------")

    confirmation = input(
        "Type RESTORE to continue: "
    ).strip()

    if confirmation != "RESTORE":

        print()
        print("Restore cancelled.")

        return

    # --------------------------------------------------------
    # STEP 3: Emergency backup
    # --------------------------------------------------------

    print()
    print("Creating emergency backup of current system...")

    emergency_backup = create_backup()

    if emergency_backup is None:

        print()
        print(
            "Restore cancelled because "
            "emergency backup failed."
        )

        return

    print(
        f"Emergency backup created:\n"
        f"{emergency_backup}"
    )

    # --------------------------------------------------------
    # STEP 4: Extract backup to temporary folder
    # --------------------------------------------------------

    try:

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            print()
            print("Extracting backup...")

            with zipfile.ZipFile(
                backup_path,
                "r"
            ) as backup_zip:

                backup_zip.extractall(temp_path)

            restored_database = (
                temp_path / "db.sqlite3"
            )

            if not restored_database.exists():

                print(
                    "ERROR: Database not found "
                    "after extraction."
                )

                return

            # ------------------------------------------------
            # STEP 5: Restore database
            # ------------------------------------------------

            print("Restoring database...")

            shutil.copy2(
                restored_database,
                DATABASE_FILE
            )

            # ------------------------------------------------
            # STEP 6: Restore media
            # ------------------------------------------------

            restored_media = (
                temp_path / "media"
            )

            if restored_media.exists():

                print("Restoring media folder...")

                if MEDIA_FOLDER.exists():

                    shutil.rmtree(
                        MEDIA_FOLDER
                    )

                shutil.copytree(
                    restored_media,
                    MEDIA_FOLDER
                )

            else:

                print(
                    "No media folder found in backup."
                )

        print()
        print("======================================")
        print("RESTORE COMPLETED SUCCESSFULLY")
        print("======================================")
        print()
        print(
            "Emergency backup is available at:"
        )
        print(emergency_backup)
        print()

    except Exception as error:

        print()
        print("======================================")
        print("RESTORE FAILED")
        print("======================================")
        print()
        print(error)
        print()
        print(
            "Your emergency backup should still be "
            "available in the backups folder."
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("     HR MANAGEMENT SYSTEM")
    print("     BACKUP AND RESTORE")
    print("======================================")
    print()

    print("1. Create Backup")
    print("2. Restore Backup")
    print("3. Exit")
    print()

    choice = input(
        "Enter your choice (1/2/3): "
    ).strip()

    # --------------------------------------------------------
    # CREATE BACKUP
    # --------------------------------------------------------

    if choice == "1":

        create_backup()

    # --------------------------------------------------------
    # RESTORE BACKUP
    # --------------------------------------------------------

    elif choice == "2":

        backup_file = input(
            "Enter the full path of the backup ZIP file: "
        ).strip().strip('"')

        restore_backup(
            backup_file
        )

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    elif choice == "3":

        print("Program closed.")

    else:

        print("Invalid choice.")