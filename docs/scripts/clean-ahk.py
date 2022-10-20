from pathlib import Path
import shutil

addon_name = "MyAddon"


classic_link = Path(
    Rf"C:\Program Files (x86)\World of Warcraft\_classic_\Interface\AddOns\{addon_name}"
)
if classic_link.exists():
    classic_link.unlink()
    print(f"deleted {classic_link}")

retail_link = Path(
    Rf"C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\{addon_name}"
)
if retail_link.exists():
    retail_link.unlink()
    print(f"deleted {retail_link}")

addon_dir = Path() / addon_name
if addon_dir.exists():
    shutil.rmtree(addon_dir)
    print(f"deleted {addon_dir}")
