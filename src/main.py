import arcade
from src.app.game_app import GameApp
from src.app.window import GameWindow

def main():
    app = GameApp()
    GameWindow(app)
    arcade.run()

if __name__ == "__main__":
    main()