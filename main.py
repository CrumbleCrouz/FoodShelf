import msvcrt
import os
import random
import sys
import time
import keyboard as kb

running = True


class FoodShelf:
    digits_key_hashmap = {
        79: 1,
        80: 2,
        81: 3,
        75: 4,
        76: 5,
        77: 6,
        71: 7,
        72: 8,
        73: 9,
        82: 0
    }

    def __init__(self, file: str):
        self.menu = ["Manger", "Stock", "Fermer"]
        self.pressing = False
        self.file_path = file
        self.food_list = []
        self.values_list = []
        self.inv = {}

        self.load_db()
        self.refresh_list()
        self.cli()

    def load_db(self):
        try:
            f = open(file=self.file_path, encoding="UTF-8")
            brut_data = [v.rstrip("\n").split(',') for v in f.readlines()]
            self.inv = {v[0]: int(v[1]) for v in brut_data if v[0] != ''}
            f.close()
            self.save_db(self.file_path, speak=False)
        except FileNotFoundError:
            self.inv = {"vide": 0}
            print("Une erreur est survenue : le fichier de base de données n'a pas été trouvé. Un nouveau a été créé.")
            input()
            self.save_db(self.file_path, speak=False)
        except Exception as err:
            print(f"Une erreur est survenue avec la base de données : {err}")
            print("Appuyez sur backspace pour continuer...")
            kb.wait("backspace")

    def refresh_list(self):
        self.food_list = [v for v in self.inv.keys()]
        self.values_list = [v for v in self.inv.values()]

    def stock_menu(self):
        self.pressing = False

        i = 0
        editing_flag = False

        self.two_cols_table(i)
        # Stock menu loop
        while True:
            key = kb.read_event()
            if key.event_type == "up":
                self.pressing = False
                continue
            if key.scan_code == 72 and not key.is_keypad:  # UP ARROW
                if not self.pressing:
                    self.pressing = True
                    i = i - 1 if i > 0 else len(self.food_list)
                    self.two_cols_table(i)
                    editing_flag = False
            elif key.scan_code == 80 and not key.is_keypad:  # DOWN ARROW
                if not self.pressing:
                    self.pressing = True
                    i = i + 1 if i < len(self.food_list) else 0
                    self.two_cols_table(i)
                    editing_flag = False
            elif key.scan_code == 75 and not key.is_keypad:  # LEFT ARROW
                if not self.pressing and i != len(self.food_list):
                    self.pressing = True
                    if self.values_list[i] > 0:
                        self.values_list[i] -= 1
                        self.two_cols_table(i)
                        self.inv = {self.food_list[i]: self.values_list[i] for i in range(len(self.food_list))}
                        self.save_db(self.file_path, speak=False)
                        editing_flag = False
            elif key.scan_code == 77 and not key.is_keypad:  # RIGHT ARROW
                if not self.pressing and i != len(self.food_list):
                    self.pressing = True
                    self.values_list[i] += 1
                    self.two_cols_table(i)
                    self.inv = {self.food_list[i]: self.values_list[i] for i in range(len(self.food_list))}
                    self.save_db(self.file_path, speak=False)
                    editing_flag = False
            elif key.scan_code == 14:  # BACKSPACE
                if not self.pressing and i != len(self.food_list):
                    self.pressing = True
                    self.values_list[i] = 0
                    self.two_cols_table(i)
                    self.inv = {self.food_list[i]: self.values_list[i] for i in range(len(self.food_list))}
                    self.save_db(self.file_path, speak=False)
                    editing_flag = False
            # Supports direct number input
            if key.scan_code in self.digits_key_hashmap.keys():
                if not self.pressing and i != len(self.food_list):
                    self.pressing = True
                    self.values_list[i] = self.values_list[i] * 10 + self.digits_key_hashmap[
                        key.scan_code] if editing_flag else \
                        self.digits_key_hashmap[key.scan_code]
                    editing_flag = True
                    self.two_cols_table(i)
                    self.inv = {self.food_list[i]: self.values_list[i] for i in range(len(self.food_list))}
                    self.save_db(self.file_path, speak=False)
            elif key.scan_code == 28:  # ENTER
                if not self.pressing:
                    self.pressing = True
                    editing_flag = False
                    while kb.is_pressed("enter"):
                        continue
                    clear_stdin()
                    if i == len(self.food_list):
                        self.add_food()
                        self.two_cols_table(i)
            elif key.scan_code == 1:  # ESCAPE
                if not self.pressing:
                    self.pressing = True
                    self.save_db(self.file_path, speak=False)
                    break
            else:
                self.pressing = False

    def hungry(self):
        # Initial display
        self.pressing = False
        if len(self.inv) == 1 and 'vide' in list(self.inv.keys()):  # If the inventory is empty
            print("\033[H\033[J", end="")
            print("Il n'y a rien à manger !")
            print("Appuyez sur backspace pour continuer...")
            kb.wait("backspace")
            msvcrt.getch()
            clear_stdin()
            return
        # Arrow speed
        speed = 2 + random.uniform(0, 1)
        slowing_down_rate = random.uniform(0.05, 0.1)

        # Arrow position
        ind = random.uniform(0, len(self.food_list) - 1)

        # Arrow animation
        while speed > slowing_down_rate:
            if kb.is_pressed("esc"):
                if not self.pressing:
                    self.pressing = True
                    break
            else:
                self.pressing = False

            if int(ind) >= len(self.food_list) - 1:
                ind = 0
            else:
                ind += speed

            speed = speed - slowing_down_rate if speed > slowing_down_rate else slowing_down_rate
            self.two_cols_table(int(ind), add_btn=False)

            # Sleep for 50ms
            time.sleep(0.05)

        # Food selection
        ind = int(ind)
        food = self.food_list[ind]
        time.sleep(0.5)
        print("\033[H\033[J", end="")
        a = str(input(f"Voulez vous manger {food} ? (y/n) "))
        if a.lower() in ["y", "yes"]:
            self.inv[food] -= 1
            self.save_db(self.file_path)
            print(f"Vous avez mangé {food}")
        else:
            print("Une prochaine fois !")

        msvcrt.getch()
        clear_stdin()
        self.pressing = True

    def add_food(self):
        new_food = str(input("Que voulez-vous ajouter ? ")).lower()
        while True:
            c = str(input("Combien en stock ? "))
            try:
                c = int(c)
                if new_food in list(self.inv.keys()):
                    self.inv[new_food] += c
                else:
                    self.inv[new_food] = c
                self.save_db(self.file_path)
                break
            except ValueError:
                print("Entrez un nombre entier !")
                continue

    def save_db(self, filename: str, speak=True):
        f = open(filename, 'w', encoding="UTF-8")

        for k in list(self.inv.keys()):
            if self.inv[k] < 1:
                self.inv.pop(k)

        for k in self.inv.keys():
            if k == 'vide':
                if len(self.inv) == 1:
                    self.inv[k] = 0
                else:
                    self.inv.pop(k)


        if len(self.inv) == 0:
            self.inv["vide"] = 0

        for i in range(len(self.inv)):
            f.write(
                f"{[list(self.inv.keys())[i], list(self.inv.values())[i]]}"
                .translate(str.maketrans("", "", "[]'\""))
                + "\n"
            )
        f.close()
        self.refresh_list()
        if speak:
            print("\033[H\033[J", end="")
            print(f"Le stock a été actualisé")

    def one_col_table(self, select=0):
        max_value_l1 = max(*([len(str(val)) for val in self.menu])) + 2

        print(f"/{'-' * max_value_l1}\\")  # Header
        for i in range(len(self.menu)):  # Content
            print(f"|{self.menu[i].center(max_value_l1)}|" + (" <-" if i == select else ""))
        print(f"\\{'-' * max_value_l1}/")  # Footer

    def two_cols_table(self, select=0, add_btn=True):
        max_value_l1 = (max(*([len(str(val)) for val in self.food_list])) + 2) if len(self.food_list) > 1 else (len(str(self.food_list[0])) + 2)
        max_value_l2 = (max(*([len(str(val)) for val in self.values_list])) + 1) if len(self.food_list) > 1 else (len(str(self.values_list[0])) + 1)

        print("\033[H\033[J", end="")
        width = (max_value_l1 + max_value_l2 + 1) if (max_value_l1 + max_value_l2 + 1) >= 9 else 9

        print(f"/{'-' * width }\\")  # Header
        for i in range(len(self.food_list)):  # Content
            print(f"|{str(self.food_list[i]).center(width - max_value_l2 - 1)}|{str(self.values_list[i]).rjust(max_value_l2)}|" + (
                " <-" if i == select else ""))
        if add_btn:
            print(f"|{'-' * width}|")
            print(f"|{'Ajouter'.center(width)}|" + (" <-" if select == len(self.food_list) else ""))
        print(f"\\{'-' * width}/")  # Footer

    def cli(self):
        ind = 0

        # Initial display
        # print("\033[H\033[J", end="")
        self.one_col_table(ind)

        while True:
            global running
            if kb.is_pressed("up arrow"):
                if not self.pressing:
                    self.pressing = True
                    if ind > 0:
                        ind -= 1
                        print("\033[H\033[J", end="")
                        self.one_col_table(ind)
            elif kb.is_pressed("down arrow"):
                if not self.pressing:
                    self.pressing = True
                    if ind < len(self.menu) - 1:
                        ind += 1
                        print("\033[H\033[J", end="")
                        self.one_col_table(ind)
            elif kb.is_pressed("esc"):
                if not self.pressing:
                    self.pressing = True
                    running = False
                    break
            elif kb.is_pressed("enter"):
                if not self.pressing:
                    # Input safety
                    while kb.is_pressed("enter"):
                        continue
                    clear_stdin()
                    match ind:
                        case 0:
                            self.hungry()
                        case 1:
                            self.stock_menu()
                        case 2:
                            running = False
                            break
                    print("\033[H\033[J", end="")
                    self.one_col_table(ind)
            else:
                self.pressing = False


def clear_stdin():
    while msvcrt.kbhit():
        msvcrt.getch()
    sys.stdin.flush()


def start():
    while running:
         try:
             clear_stdin()
             FoodShelf(os.path.realpath(os.path.dirname(sys.argv[0])) + "\\food_db.csv")

         except Exception as err:
            print(f"Une erreur est survenue : {err}")
            print("Appuyez sur backspace pour redémarrer le programme...")
            kb.wait("backspace")
            continue


if __name__ == "__main__":
    start()
