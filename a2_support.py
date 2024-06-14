import tkinter as tk
from typing import Union

# Model Constants
TANK_RANGE = 5
SCORPION_RANGE = 2
FIREFLY_RANGE = 5

MAX_BUILDING_HEALTH = 9

TILE_NAME = "Tile"
TILE_SYMBOL = "T"
GROUND_NAME = "Ground"
GROUND_SYMBOL = " "
MOUNTAIN_NAME = "Mountain"
MOUNTAIN_SYMBOL = "M"
BUILDING_NAME = "Building"

ENTITY_NAME = "Entity"
ENTITY_SYMBOL = "E"
MECH_NAME = "Mech"
MECH_SYMBOL = "M"
ENEMY_NAME = "Enemy"
ENEMY_SYMBOL = "N"
TANK_NAME = "TankMech"
TANK_SYMBOL = "T"
HEAL_NAME = "HealMech"
HEAL_SYMBOL = "H"
SCORPION_NAME = "Scorpion"
SCORPION_SYMBOL = "S"
FIREFLY_NAME = "Firefly"
FIREFLY_SYMBOL = "F"

TANK_DISPLAY = "\U000023F8"
HEAL_DISPLAY = "\U0001F6E1"
SCORPION_DISPLAY = "\U00010426"
FIREFLY_DISPLAY = "\U00000D9E"

# Used to get attack tiles for various entities
PLUS_OFFSETS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

# GUI Constants
GRID_SIZE = 450
SIDEBAR_WIDTH = 300
BANNER_HEIGHT = 75
CONTROL_BAR_HEIGHT = 100

BANNER_TEXT = "Into The Breach"
SIDEBAR_HEADINGS = ("Unit", "Coord", "Hp", "Dmg")

SAVE_TEXT = "Save Game"
LOAD_TEXT = "Load Game"
UNDO_TEXT = "Undo Move"
TURN_TEXT = "End Turn"

INVALID_SAVE_TITLE = "Cannot Save!"
INVALID_SAVE_MESSAGE = "You can only save at the beginning of your turn!"
IO_ERROR_TITLE = "File Error"
IO_ERROR_MESSAGE = "Cannot open specified file: "
PLAY_AGAIN_TEXT = "Would you like to play again?"

BANNER_FONT = ("Arial", 22, "bold")
ENTITY_FONT = ("Arial", 20, "bold")
SIDEBAR_FONT = ("Arial", 14, "bold")

ATTACK_COLOR = "Red"
MOVE_COLOR = "Lime"
GROUND_COLOR = "SandyBrown"
BUILDING_COLOR = "Turquoise"
DESTROYED_COLOR = "Teal"
MOUNTAIN_COLOR = "Olive"


class AbstractGrid(tk.Canvas):
    """A type of tkinter Canvas that provides support for using the canvas as a
    grid (i.e. a collection of rows and columns)."""

    def __init__(
        self,
        master: Union[tk.Tk, tk.Widget],
        dimensions: tuple[int, int],
        size: tuple[int, int],
        **kwargs
    ) -> None:
        """Constructor for AbstractGrid.

        Parameters:
            master: The master frame for this Canvas.
            dimensions: (#rows, #columns)
            size: (width in pixels, height in pixels)
        """
        super().__init__(
            master,
            width=size[0] + 1,
            height=size[1] + 1,
            highlightthickness=0,
            **kwargs
        )
        self._size = size
        self.set_dimensions(dimensions)

    def set_dimensions(self, dimensions: tuple[int, int]) -> None:
        """Sets the dimensions of the grid.

        Parameters:
            dimensions: Dimensions of this grid as (#rows, #columns)
        """
        self._dimensions = dimensions

    def _get_cell_size(self) -> tuple[int, int]:
        """Returns the size of the cells (width, height) in pixels."""
        rows, cols = self._dimensions
        width, height = self._size
        return width // cols, height // rows

    def pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        """Converts a pixel position to a cell position.

        Parameters:
            x: The x pixel position.
            y: The y pixel position.

        Returns:
            The (row, col) cell position.
        """
        cell_width, cell_height = self._get_cell_size()
        return y // cell_height, x // cell_width

    def _get_bbox(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
        """Returns the bounding box of the given (row, col) position.

        Parameters:
            position: The (row, col) cell position.

        Returns:
            Bounding box for this position as (x_min, y_min, x_max, y_max).
        """
        row, col = position
        cell_width, cell_height = self._get_cell_size()
        x_min, y_min = col * cell_width, row * cell_height
        x_max, y_max = x_min + cell_width, y_min + cell_height
        return x_min, y_min, x_max, y_max

    def _get_midpoint(self, position: tuple[int, int]) -> tuple[int, int]:
        """Gets the graphics coordinates for the center of the cell at the
            given (row, col) position.

        Parameters:
            position: The (row, col) cell position.

        Returns:
            The x, y pixel position of the center of the cell.
        """
        row, col = position
        cell_width, cell_height = self._get_cell_size()
        x_pos = col * cell_width + cell_width // 2
        y_pos = row * cell_height + cell_height // 2
        return x_pos, y_pos

    def annotate_position(
        self, position: tuple[int, int], text: str, font=None
    ) -> None:
        """Annotates the cell at the given (row, col) position with the
            provided text.

        Parameters:
            position: The (row, col) cell position.
            text: The text to draw.
        """
        self.create_text(self._get_midpoint(position), text=text, font=font)

    def color_cell(self, position: tuple[int, int], color: str) -> None:
        """
        Colors the cell at the given (row, col) position with the specified
        color

        Parameters:
            position: The (row, col) cell position.
            color: The tkInter string corresponding to the desired color
        """
        self.create_rectangle(*self._get_bbox(position), fill=color)

    def clear(self):
        """Clears all child widgets off the canvas."""
        self.delete("all")


# Note: "" just allows type hint despite BreachModel not being defined in file.
def get_distance(
    game_state: "BreachModel", origin: tuple[int, int], destination: tuple[int, int]
) -> int:
    """
    Computes the minimum taxicab distance between two points on a given board,
    from all paths that avoid blocking tiles and other entities. The method may
    begin on an entity or blocking tile, but will avoid all such tiles while
    searching possible paths. This method requires you to have gotten up to the
    BreachModel class, with correct get_board, get_entity, and entity_position
    methods.

    Args:
        game_state (BreachModel): Model representing gamestate
        origin (tuple[int,int]): starting position.
        destination (tuple[int,int]): ending position. Precondition: will not be
                                      a blocking tile according to game_state,
                                      and will not posess an entity according to
                                      game_state

    Returns:
        int: taxicab distance of shortest path within the given game board
             between origin and destination such that blocking tiles and entities
             are avoided, or -1 if no such path exists.
    """
    # Implements A* search algorithm.
    # NOTE: YOU DO NOT NEED TO UNDERSTAND THIS ALGORITHM
    entity_tiles = set(game_state.entity_positions().keys())
    # Initialise
    searched = set()
    frontier = {origin: 0}

    while len(frontier) > 0:
        # get minimum frontier node
        min = float("inf")
        node = None
        for key, val in frontier.items():
            if val < min:
                node = key
                min = val
        # Move node to searched pile
        value = frontier.pop(node)
        searched.add(node)

        if node == destination:
            return value
        else:
            # Add children to frontier
            new_val = value + 1
            for delta in PLUS_OFFSETS:
                new_node = (node[0] + delta[0], node[1] + delta[1])
                if (
                    (new_node not in searched)
                    and (new_node not in entity_tiles)
                    and not (game_state.get_board().get_tile(new_node).is_blocking())
                    and not (frontier.get(new_node, float("inf")) <= new_val)
                ):
                    frontier[new_node] = new_val
                    

    # We have run out of paths
    return -1
