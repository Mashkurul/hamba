# Verify all dialogs render fields correctly (dark mode, screenshot check)
import os, time
os.environ.setdefault("TCL_LIBRARY", "")
import customtkinter as ctk
from PIL import ImageGrab

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
from database import initialize_database
initialize_database()

admin = {"id": 1, "username": "admin", "role": "admin",
         "full_name": "System Administrator", "is_active": 1}

root = ctk.CTk()
root.withdraw()
import gui.pages as P

def count_input_bg(name):
    from PIL import Image
    img = Image.open(name).convert("RGB")
    w, h = img.size
    t = (30, 45, 64)
    return sum(1 for y in range(0, h) for x in range(0, w)
               if all(abs(img.getpixel((x, y))[i] - t[i]) < 6 for i in range(3)))

def check(name, factory):
    d = factory()
    d.update()
    d.deiconify()
    d.lift()
    d.attributes("-topmost", True)
    for _ in range(6):
        d.update()
        time.sleep(0.1)
    x, y = d.winfo_rootx(), d.winfo_rooty()
    w, h = d.winfo_width(), d.winfo_height()
    fn = f"_v_{name}.png"
    ImageGrab.grab(bbox=(x, y, x+w, y+h)).save(fn)
    n = count_input_bg(fn)
    print(f"{name}: {n} input-bg px", "OK" if n > 2000 else "BROKEN")
    d.destroy()

check("Cow",        lambda: P.CowDialog(root, on_save=lambda m: None))
check("Milk",       lambda: P.MilkDialog(root, on_save=lambda m: None))
check("Food",       lambda: P.FoodDialog(root, on_save=lambda m: None))
check("Health",     lambda: P.HealthDialog(root, on_save=lambda m: None))
check("Emp",        lambda: P.EmpDialog(root, on_save=lambda m: None))
check("Att",        lambda: P.AttDialog(root, on_save=lambda m: None))
check("Exp",        lambda: P.ExpDialog(root, on_save=lambda m: None))
check("Sale",       lambda: P.SaleDialog(root, on_save=lambda m: None))
check("CreateUser", lambda: P.CreateUserDialog(root, current_user=admin, on_save=lambda m: None))

root.destroy()
print("DONE")
