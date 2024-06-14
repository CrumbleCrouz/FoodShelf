# Internal modules
import os
import sys
import time
import random

# External modules
import msvcrt
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
        self.menu = ["Manger", "Boire", "Stock nourriture", "Stock boisson", "Fermer"]
        self.pressing = False
        self.file_path = file
        self.food_list = []
        self.drink_list = []
        self.food_values_list = []
        self.drink_values_list = []

        self.load_db()
        self.cli()

    def load_db(self):
        try:
            f = open(file=self.file_path, encoding="UTF-8")
            brut_data = [v.rstrip("\n").split(',') for v in f.readlines()]
            for v in brut_data:
                if v[0] != '':
                    if v[2].strip(' ') == "food":
                        self.food_list += [[v[0].strip(' '), int(v[1]), v[2].strip(' ')]]
                    if v[2].strip(' ') == "drink":
                        self.drink_list += [[v[0].strip(' '), int(v[1]), v[2].strip(' ')]]
            f.close()
            self.save_db(self.file_path, speak=False)
        except FileNotFoundError:
            self.food_list = [["vide", 0, "food"]]
            self.drink_list = [["vide", 0, "drink"]]
            print("Une erreur est survenue : le fichier de base de données n'a pas été trouvé. Un nouveau a été créé.")
            print("Appuyez sur backspace pour continuer...")
            kb.wait("backspace")
            self.save_db(self.file_path, speak=False)
        except Exception as err:
            print(f"Une erreur est survenue avec la base de données : {err}")
            print("Appuyez sur backspace pour continuer...")
            kb.wait("backspace")

    def stock_menu(self, type: str):
        self.pressing = False

        current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
        i = 0
        editing_flag = False
        self.two_cols_table(i, type=type)
        # Stock menu loop
        while True:
            key = kb.read_event()
            if key.event_type == "up":
                self.pressing = False
                continue
            if key.scan_code == 72 and not key.is_keypad:  # UP ARROW
                if not self.pressing:
                    self.pressing = True
                    i = i - 1 if i > 0 else len(current_elm_list)
                    self.save_db(self.file_path, speak=False)
                    current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
                    self.two_cols_table(i, type=type)
                    editing_flag = False

            elif key.scan_code == 80 and not key.is_keypad:  # DOWN ARROW
                if not self.pressing:
                    self.pressing = True
                    i = i + 1 if i < len(current_elm_list) else 0
                    self.save_db(self.file_path, speak=False)
                    current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
                    self.two_cols_table(i, type=type)
                    editing_flag = False

            elif key.scan_code == 75 and not key.is_keypad:  # LEFT ARROW
                if not self.pressing and i != len(current_elm_list):
                    self.pressing = True
                    if current_elm_list[i][1] > 0:
                        current_elm_list[i][1] -= 1
                        self.save_db(self.file_path, speak=False)
                        current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
                        self.two_cols_table(i, type=type)
                        editing_flag = False

            elif key.scan_code == 77 and not key.is_keypad:  # RIGHT ARROW
                if not self.pressing and i != len(current_elm_list):
                    self.pressing = True
                    current_elm_list[i][1] += 1
                    self.save_db(self.file_path, speak=False)
                    current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
                    self.two_cols_table(i, type=type)
                    editing_flag = False

            elif key.scan_code == 14:  # BACKSPACE
                if not self.pressing and i != len(current_elm_list):
                    self.pressing = True
                    current_elm_list[i][1] = int(current_elm_list[i][1] / 10)
                    self.save_db(self.file_path, speak=False)
                    current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
                    self.two_cols_table(i, type=type)
                    editing_flag = False

            # Supports direct number input
            if key.scan_code in self.digits_key_hashmap.keys():
                if not self.pressing and i != len(current_elm_list):
                    self.pressing = True
                    current_elm_list[i][1] = current_elm_list[i][1] * 10 + self.digits_key_hashmap[
                        key.scan_code] if editing_flag else self.digits_key_hashmap[key.scan_code]
                    editing_flag = True
                    self.save_db(self.file_path, speak=False)
                    current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
                    self.two_cols_table(i, type=type)

            elif key.scan_code == 28:  # ENTER
                if not self.pressing:
                    self.pressing = True
                    editing_flag = False
                    while kb.is_pressed("enter"):
                        continue
                    clear_stdin()
                    if i == len(current_elm_list):
                        self.add_food(type)
                        current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
                        self.two_cols_table(i, type=type)
            elif key.scan_code == 1:  # ESCAPE
                if not self.pressing:
                    self.pressing = True
                    self.save_db(self.file_path, speak=False)
                    break
            else:
                self.pressing = False
            if type == "food":
                self.food_list = current_elm_list.copy()
            else:
                self.drink_list = current_elm_list.copy()

    def hungry(self, type: str):
        current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()

        # Initial display
        self.pressing = False
        if len(current_elm_list) == 1 and current_elm_list[0][0] == "vide":  # If the inventory is empty
            print("\033[H\033[J", end="")
            print(f"Il n'y a rien à {'manger' if type == 'food' else 'boire'} !")
            print("Appuyez sur backspace pour continuer...")
            kb.wait("backspace")
            msvcrt.getch()
            clear_stdin()
            return
        # Arrow speed
        speed = 2 + random.uniform(0, 1)
        slowing_down_rate = random.uniform(0.05, 0.1)

        # Arrow position
        ind = random.uniform(0, len(current_elm_list) - 1)

        # Arrow animation
        while speed > slowing_down_rate:
            if kb.is_pressed("esc"):
                if not self.pressing:
                    self.pressing = True
                    break
            else:
                self.pressing = False

            if int(ind) >= len(current_elm_list) - 1:
                ind = 0
            else:
                ind += speed

            speed = speed - slowing_down_rate if speed > slowing_down_rate else slowing_down_rate
            self.two_cols_table(int(ind), type, add_btn=False)

            # Sleep for 50ms
            time.sleep(0.05)

        # Food selection
        ind = int(ind)
        food = current_elm_list[ind][0]
        time.sleep(0.5)
        print("\033[H\033[J", end="")
        a = str(input(f"Voulez vous {'manger' if type == 'food' else 'boire'} {food} ? (y/n)"))
        if a.lower() in ["y", "yes", "o" "oui"]:
            current_elm_list[ind][1] -= 1
            self.save_db(self.file_path)
            print(f"Vous avez {'mangé' if type == 'food' else 'bu'} {food}")
            if type == "food":
                self.food_list = current_elm_list.copy()
            else:
                self.drink_list = current_elm_list.copy()
        else:
            print("Une prochaine fois !")

        msvcrt.getch()
        clear_stdin()
        self.pressing = True

    def add_food(self, type: str):
        current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()
        new_food = str(input("Que voulez-vous ajouter ? ")).lower().strip(' ')
        while True:
            try:
                c = str(input("Combien en stock ? "))
                c = int(c)
                added = False
                for i in range(len(current_elm_list)):
                    if current_elm_list[i][0] == new_food:
                        current_elm_list[i][1] += c
                        added = True
                if not added:
                    current_elm_list.append([new_food, c, type])

                if type == "food":
                    self.food_list = current_elm_list.copy()
                else:
                    self.drink_list = current_elm_list.copy()
                self.save_db(self.file_path)
                return
            except ValueError:
                print("Entrez un nombre entier !")
                continue

    def save_db(self, filename: str, speak=True):
        f = open(filename, 'w', encoding="UTF-8")

        # Delete food if is empty
        ind = 0
        for _ in range(len(self.food_list)):
            if int(self.food_list[ind][1]) < 1:
                self.food_list.pop(ind)
            else:
                ind += 1
        ind = 0
        for _ in range(len(self.drink_list)):
            if int(self.drink_list[ind][1]) < 1:
                self.drink_list.pop(ind)
            else:
                ind += 1

        # Delete the default value if the db is not enough empty
        for i in range(len(self.food_list)):
            if self.food_list[i][0] == "vide":
                if len(self.food_list) == 1:
                    self.food_list.pop(i)
                else:
                    self.food_list[i][1] = 0
        for i in range(len(self.drink_list)):
            if self.drink_list[i][0] == "vide":
                if len(self.drink_list) == 1:
                    self.drink_list.pop(i)
                else:
                    self.drink_list[i][0] = 0

        # Creating the default value if the db is empty
        if len(self.food_list) == 0:
            self.food_list = [["vide", 0, "food"]]
        if len(self.drink_list) == 0:
            self.drink_list = [["vide", 0, "drink"]]

        f_elements_list = self.food_list + self.drink_list
        for i in range(len(f_elements_list)):
            f.write(
                f"{[f_elements_list[i][0], f_elements_list[i][1], f_elements_list[i][2]]}"
                .translate(str.maketrans("", "", "[]'\""))
                + "\n"
            )
        f.close()
        if speak:
            print("\033[H\033[J", end="")
            print(f"Le stock a été actualisé")

    def one_col_table(self, select=0):
        max_value_l1 = max(*([len(str(val)) for val in self.menu])) + 2

        print(f"/{'-' * max_value_l1}\\")  # Header
        for i in range(len(self.menu)):  # Content
            print(f"|{self.menu[i].center(max_value_l1)}|" + (" <-" if i == select else ""))
        print(f"\\{'-' * max_value_l1}/")  # Footer

    def two_cols_table(self, select: int, type: str, add_btn: bool = True):
        current_elm_list = self.food_list.copy() if type == "food" else self.drink_list.copy()

        max_value_c1 = (max(*([len(str(val[0])) for val in current_elm_list])) + 2) if len(current_elm_list) > 1 else (
                    len(str(current_elm_list[0][0])) + 2)
        max_value_c2 = (max(*([len(str(val[1])) for val in current_elm_list])) + 1) if len(current_elm_list) > 1 else (
                    len(str(current_elm_list[0][1])) + 1)

        print("\033[H\033[J", end="")
        width = (max_value_c1 + max_value_c2 + 1) if (max_value_c1 + max_value_c2 + 1) >= 9 else 9

        print(f"/{'-' * width}\\")  # Header
        for i in range(len(current_elm_list)):  # Content
            print(
                f"|{str(current_elm_list[i][0]).center(width - max_value_c2 - 1)}|{str(current_elm_list[i][1]).rjust(max_value_c2)}|" + (
                    " <-" if i == select else ""))
        if add_btn:
            print(f"|{'-' * width}|")
            print(f"|{'Ajouter'.center(width)}|" + (" <-" if select == len(current_elm_list) else ""))
        print(f"\\{'-' * width}/")  # Footer

    def cli(self):
        ind = 0

        # Initial display
        print("\033[H\033[J", end="")
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
                            self.hungry("food")
                        case 1:
                            self.hungry("drink")
                        case 2:
                            self.stock_menu("food")
                        case 3:
                            self.stock_menu("drink")
                        case 4:
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
