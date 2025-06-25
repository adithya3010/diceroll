import random
import time

def roll_dice():
    input("\nPress Enter to roll the dice...")

    print("Rolling", end="")
    for _ in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
        
    print("\n")
    result = random.randint(1, 6)

    dice_faces = {
        1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"
    }

    print(f"You rolled: {result} {dice_faces[result]}")

def main():
    while True:
        roll_dice()
        again = input("Do you want to roll , Press enter to roll again or enter q to quit  ").strip().lower()
        if again == "q":
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
