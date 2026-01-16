# Start.py for install requirements and loading into project

from GUI import App_interface
from subprocess import run

if __name__ == "__main__":

    run(["pip", "install", "-r", "requirements.txt"])

    menu= App_interface()

    try:
        menu.mainloop()
    except Exception as e:
        print(f"Error occurred: {e}")
5