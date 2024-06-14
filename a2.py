# DO NOT modify or add any import statements
from a2_support import *
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional, Callable

# Name: Wilkinson John Chan
# Student Number: 47277610
# ----------------

# Write your classes and functions here

class Tile():
    """
    Abstract class from which all instantiated types of tile inherit.

    Provides default tile behavior,
    which can be inherited or overridden by specific types of tiles.
    """

    _name = TILE_NAME
    _id = TILE_SYMBOL
    _blocking = False

    def get_tile_name(self) -> str:
        """
        Returns the name of the type of the tile (i.e. the name 
        of the most specific class to which the tile belongs).
        """
        return self._name


    def is_blocking(self) -> bool:
        """
        Returns the character representing the type of the tile.
        """
        return self._blocking
    
    def __repr__ (self) -> str:
        """
        Returns a machine readable string that could be used 
        to construct an identical instance of the tile.
        """
        return f"{self.__class__.__name__}()"


    def __str__ (self) -> str:
        """
        Returns the character representing the type of the tile.
        """
        return self._id

class Ground(Tile):
    """
    Inhertits from class Tile.
    Ground represent simple, walkable ground with no special properties 
    and has no special properties.
    """

    def __init__(self) -> None:
        self._name = GROUND_NAME
        self._id = GROUND_SYMBOL
        self._blocking = False

        super().__init__()

class Mountain(Tile):
    """
    Inherits from class Tile.
    Mountain tiles represent unpassable terrain and is always blocking.
    """
    
    def __init__(self) -> None:
        self._name = MOUNTAIN_NAME
        self._id = MOUNTAIN_SYMBOL
        self._blocking = True
        super().__init__()

class Building(Tile):
    """
    Inherits from class Tile.
    Building tiles represent one or more buildings 
    that the player must protect from enemies.
    """
    _building_health = None

    def __init__(self, initial_health: int) -> None:
        """
        Instantiates a building with the specified health. 
        A precondition to this function is that the specified health 
        will be between 0 and 9 (inclusive).

        Parameter:
            initial_health: initial health of a building.
        """
        self._building_health = max(0, min(initial_health, MAX_BUILDING_HEALTH))
        # self._id = str(self._building_health)
        self._name = BUILDING_NAME
        self._blocking = True

        super().__init__()

    def is_destroyed(self) -> bool:
        """
        Returns True only when the building is destroyed.
        """
        if self._building_health:
            return False
        else:
            self._blocking = False
            return True
    
    def damage(self, damage: int) -> None:
        """
        Reduces the health of the building by the amount specified.
        If the building is destroyed, do nothing.

        Parameter:
            damage: amount of damage of a building about to receive.
        """
        if not self.is_destroyed():
            if damage >= 0:
                self._building_health = max(0, self._building_health - damage)
                
            else:
                self._building_health = min(MAX_BUILDING_HEALTH, 
                                            self._building_health - damage)
        else:
            self._building_health = self._building_health

        

    def __repr__(self) -> str:
        """
        Returns a machine readable string that could be used 
        to construct an identical instance of the tile.
        """
        return f"{self.__class__.__name__}({str(self._building_health)})"
    
    def __str__(self) -> str:

        return str(self._building_health)

class Board():
    """
    Board represents a structured set of tiles.
    A board organizes tiles in a rectangular grid, 
    where each tile has an associated (row, column) position.
    """

    def __init__(self, board: list[list[str]]) -> None:
        """
        Set up a new Board instance. Each list in board represents 
        a row of the board, from top to bottom.

        Parameters:
            board: list of list of string representing all instances.
        """
        self._game_board = []
        self._default_row = 0
        self._default_col = 0
        self._buildings_dict = {}
        tile_classes = {
        GROUND_SYMBOL: Ground,
        MOUNTAIN_SYMBOL: Mountain
    }


        for _, row in enumerate(board):
            board_row = []
            for _, tile_symbol in enumerate(row):
                tile_class = tile_classes.get(tile_symbol)
                if tile_class:
                    # Create an instance of the tile class
                    tile_inst = tile_class()
                    board_row.append(tile_inst)
                elif tile_symbol.isdigit():
                    # If the symbol is a digit, it represents a building
                    building_inst = Building(int(tile_symbol))
                    board_row.append(building_inst)
            self._game_board.append(board_row)
                    
    
    def get_dimensions(self) -> tuple[int, int]:
        """
        Return the (#rows, #columns) dimensions of the board.
        """
        if len(self._game_board) >= 1:
            return (len(self._game_board), len(self._game_board[0]))
        # return (self._default_row, self._default_col)
    
    def get_tile(self, position: tuple[int, int])-> Tile:
        """
        Returns the Tile instance located at the given position.

        Parameters:
            position: a tuple storing row and col index.
        """
        _coordinate_row, _coordinate_col = position
        return self._game_board[_coordinate_row][_coordinate_col]
        
        
    
    def get_buildings(self)-> dict[tuple[int, int], Building]:
        """
        Returns a dictionary mapping the positions of buildings 
        to the building instances at those positions.
        """
        for row_index, row in enumerate(self._game_board):
            for col_index, tile_inst in enumerate(row):
                if isinstance(tile_inst, Building):
                    self._buildings_dict[(row_index, col_index)] = tile_inst

        return self._buildings_dict
    
    def __repr__(self) -> str:
        """
        Returns a machine readable string that could be used to 
        construct an identical instance of the board.
        """
        _repr_board = []
        for _, row in enumerate(self._game_board):
            board_row = []
            for _, tile_instance in enumerate(row):
                board_row.append(str(tile_instance))
            _repr_board.append(board_row)

        return f"Board({_repr_board})"
    
    def __str__(self) -> str:
        """
        Return a string representation of the board.
        """
        _concat_str = None
        if len(self._game_board) <= 1:
            _concat_str = ''.join(str(char)
                                  for char in self._game_board)
        else:
            _concat_str = '\n'.join([''.join(str(char) for char in row) 
                                 for row in self._game_board])

        return _concat_str
    
class Entity():
    def __init__( self, position: tuple[int, int], 
                 initial_health: int, 
                 speed: int, 
                 strength: int ) -> None:
        """
        Instantiates a new entity with the specified position, 
        health, speed, and strength.

        Parameters:
            position: initial position of entity in the format of (col, row).
            initial_health: initial health of the entity.
            speed: initial speed of the entity.
            strength: initial strength of the entity.
        """
        self._position_row, self._position_col = position
        self._health = initial_health
        self._speed = speed
        self._strength = strength
        self._is_friendly = False

    def get_symbol(self) -> str:
        """
        Returns the character that represents the entity type.
        """
        return ENTITY_SYMBOL
    
    def get_name(self) -> str:
        """
        Returns the name of the type of the entity 
        (the name of the most specific class to which this entity belongs).
        """
        return ENTITY_NAME
    
    def get_position(self) -> tuple[int, int]:
        """
        Returns the (row, column) position currently occupied by the entity.
        """
        return (self._position_row, self._position_col)
    
    def set_position(self, position: tuple[int, int])-> None:
        """
        Moves the entity to the specified position.

        Parameters:
            position: new position of the entity in the format of (row, col).
        """
        self._position_row, self._position_col = position

    def get_health(self) -> int:
        """
        Returns the current health of the entity
        """
        return self._health
    
    def get_speed(self) -> int:
        """
        Returns the current health of the entity
        """
        return self._speed
    
    def get_strength(self) -> int:
        """
        Returns the strength of the entity
        """
        return self._strength
    
    def damage(self, damage: int)-> None:
        """
        Reduces the health of the entity by the amount specified.
        The damage is effective only if the entity is alive
        and the affected health cannot go below 0.

        Parameters:
            damage: the current entity is being targeted and is about to
                    receive the amount of damage being passed in.
        """
        if self.is_alive():
            if (self.get_health() - damage > 0):
                self._health = self.get_health() - damage
            else:
                self._health = 0

    def is_alive(self) -> bool:
        """
        Returns True if and only if the entity is not destroyed.
        """
        return self.get_health() > 0
    
    def is_friendly(self) -> bool:
        """
        Returns True if and only if the entity is friendly. 
        By default, entities are not friendly.
        """
        return self._is_friendly
    
    def get_targets(self) -> list[tuple[int, int]]:
        """
        Returns the positions that would be attacked 
        by the entity during a combat phase. 
        By default, entities target vertically and horizontally adjacent tiles.
        """
        targets = []
        for directions in PLUS_OFFSETS:
            target = (self._position_row + directions[0], 
                      self._position_col + directions[1])
            targets.append(target)
        
        return targets
        

    def attack(self, entity: "Entity")-> None:
        """
        Applies this entity's effect to the given entity. 
        By default, entities deal damage equal to the strength of the entity.

        Parameters:
            entity: an entity instance being attacked (or healed).
        """
    
        entity.damage(self.get_strength())
    
    def __repr__(self) -> str:
        """
        
        Returns a machine readable string that could be used to 
        construct an identical instance of the entity."""
        
        return (f"{self.__class__.__name__}(({self._position_row}, "
                f"{self._position_col}), {self.get_health()}, "
                f"{self.get_speed()}, {self.get_strength()})")
    
    def __str__(self) -> str:
        """
        Returns the string representation of the entity.
        The format is as following:
            character representing the type of the entity;
            row currently occupied by the entity;
            col currently occupied by the entity;
            current health of the entity; 
            the speed of the entity; and
            the strength of the entity

        """
        return (f"{self.get_symbol()},{self._position_row},"
                f"{self._position_col},{self.get_health()},"
                f"{self.get_speed()},{self.get_strength()}")  


class Mech(Entity):
    """
    Inherits from Entity.
    This class provides default mech behavior, 
    which can be inherited or overridden by specific types of 13 mechs.
    Mechs are always active upon instantiation. 
    Additionally, all mechs also keep track of their previous position, 
    that is, the position they were at before the most recent call to 
    set_position. Mechs of any type are always friendly. 
    Abstract mechs are represented by the character M.
    """
    _enabled = True

    def __init__(self, position: tuple[int, int], 
                 initial_health: int, 
                 speed: int, 
                 strength: int,
                 is_friendly: bool = True) -> None:
        """
        Initializes a Mech instance with the specified attributes.
        By default, mechs are always friendly.

        Parameters:
            position: initial position of Mech in the format of (col, row).
            initial_health: initial health of the Mech.
            speed: initial speed of the Mech.
            strength: initial strength of the mech.
            is_friendly: by default Mechs are Mech.
        """
        super().__init__(position, initial_health, speed, strength)
        self._previous_pos = None
        self._next_pos = None
        self._is_friendly = is_friendly

    def get_name(self) -> str:
        """
        Returns the name of the type of the entity ('Mech').
        """
        return MECH_NAME

    def get_symbol(self) -> str:
        """
        Returns the character that represents the entity type ('TM).
        """
        return MECH_SYMBOL

    def enable(self) -> None:
        """
        Enables the current Mech.
        """
        self._enabled = True

    def disable(self) -> None:
        """
        Disables the current Mech.
        """
        self._enabled = False

    def is_active(self) -> bool:
        """
        Checks if the current Mech is active.
        """
        return self._enabled == True


class TankMech(Mech):
    """
    TankMech inherits from Mech. 
    TankMech represents a type of mech that attacks 
    at a long range horizontally. 
    Tank mechs are represented by the character T.
    """

    def __init__(self, position: tuple[int, int], 
                 initial_health: int, 
                 speed: int, 
                 strength: int,
                 is_friendly: bool = True) -> None:
        """
        Initializes a Mech instance with the specified attributes.
        By default, mechs are always friendly.

        Parameters:
            position: initial position of entity in the format of (col, row).
            initial_health: initial health of the HealMech.
            speed: initial speed of the HealMech.
            strength: by default set strength of HealMech to negative to heal.
            is_friendly: by default HealMechs are friendly.
        """
        super().__init__(position, initial_health, speed, strength)
    
    def get_name(self) -> str:
        """
        Returns the name of the type of the entity ('TankMech').
        """
        return TANK_NAME
    
    def get_symbol(self) -> str:
        """
        Returns the character that represents the entity type ('T').
        """
        return TANK_SYMBOL
    
    def get_targets(self) -> list[tuple[int, int]]:
        """
        Returns the positions that would be attacked by 
        the TankMech during a combat phase.
        Excludes self position.
        """
        targets = []
        for tank_attack_range in range((-TANK_RANGE), (TANK_RANGE + 1)):
            if tank_attack_range != 0:
                target = (self.get_position()[0], 
                      self.get_position()[1] + tank_attack_range)
                targets.append(target)
        
        return targets


class HealMech(Mech):
    def __init__(self, position: tuple[int, int], 
                 initial_health: int, 
                 speed: int, 
                 strength: int,
                 is_friendly: bool = True) -> None:
        """
        Initializes a Mech instance with the specified attributes.
        By default, mechs are always friendly.

        Parameters:
            position: initial position of entity in the format of (col, row).
            initial_health: initial health of the HealMech.
            speed: initial speed of the HealMech.
            strength: by default set strength of HealMech to negative to heal.
            is_friendly: by default HealMechs are friendly.
        """
        super().__init__(position, initial_health, speed, strength)
        self._strength = -strength

    def get_name(self) -> str:
        """
        Returns the name of the type of the entity (HealMech).
        """
        return HEAL_NAME
    
    def get_symbol(self) -> str:
        """
        Returns the character that represents the entity type ('H').
        """
        return HEAL_SYMBOL
    
    def get_strength(self) -> int:
        """
        Return a value equal to the negative of the heal mech's strength.
        """
        return self._strength
    
    def attack(self, entity: "Entity")-> None:
        """
        While the entity being attacked is not friendly,
        the heal mech does nothing.

        Parameters:
            entity: targeted entity being healed.
        """
        
        if isinstance(entity, Building):
            entity.damage(self.get_strength())
        else:
            if entity.is_friendly():
                # entity._health = entity.get_health() - self.get_strength()
                entity.damage(self.get_strength())
            else:
                entity._health = entity._health

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(({self._position_row}, "
                f"{self._position_col}), {self.get_health()}, "
                f"{self.get_speed()}, {-self.get_strength()})")
    
    def __str__(self) -> str:
        return (f"{self.get_symbol()},{self._position_row},"
                f"{self._position_col},{self.get_health()},"
                f"{self.get_speed()},{-self.get_strength()}")


class Enemy(Entity):
    """
    Inherits from Entity.
    All enemies have an objective, 
    which is a position that the entity wants to move towards. 
    The objective of all enemies upon instantiation is the enemy's 
    current position. 
    Enemies of any type are never friendly. 
    Abstract enemies are represented by the character N.
    """
    def __init__(self, position: tuple[int, int], 
                 initial_health: int, 
                 speed: int, 
                 strength: int,
                 is_friendly: bool = False) -> None:
        """
        Initializes an Enemy instance with the specified attributes.
        By default, enemies are never friendly.

        Parameters:
            position: initial position of enemy in the format of (col, row).
            initial_health: initial health of the enemy.
            speed: initial speed of the enemy.
            strength: initial strength of the enemy.
            is_friendly: by default an enemy is never friendly.
        """
        super().__init__(position, initial_health, speed, strength)
        self._is_friendly = is_friendly
        self._position = position
        self._objective = self._position

    def get_objective(self)-> tuple[int, int]:
        """
        Returns the current objective of the enemy 
        which is the position of the entity wants to move towards.
        """
        return self._objective
    
    def update_objective(self, entities: list[Entity], 
                         buildings: dict[tuple[int, int], Building])-> None:
        """
        Updates the enemy's objective.
        This is like an interface (in Java) and is bound to be 
        overwritten by child classes.
        Precondition: 
            entities (list of Entity)is sorted in descending priority order.
            The first entity in the list being the highest priority.

        Parameters:
            entities: all entity instances.
            buildings: all buildings from get_buildings() method 
                        from Board class.
        """
        self._objective = self.get_position()

    def get_name(self) -> str:
        """
        Returns the name of the type of the entity ('Enemy').
        """
        return ENEMY_NAME
    
    def get_symbol(self) -> str:
        """
        Returns the character that represents the entity type ('E').
        """
        return ENEMY_SYMBOL
    
    def __str__(self) -> str:
        return super().__str__()


class Scorpion(Enemy):
    """
    Inherits from Enemy, under Entity.
    Scorpion represents a type of enemy that attacks at 
    a moderate range in all directions, 
    and targets mechs with the highest health.
    Scorpions are represented by the character S.
    """

    def __init__(self, position: tuple[int, int], 
                 initial_health: int, 
                 speed: int, 
                 strength: int,
                 is_friendly: bool = False) -> None:
        """
        Initializes a Scorpion instance with the specified attributes.
        By default, enemies are never friendly.

        Parameters:
            position: initial position of Scorpion in the format of (col, row).
            initial_health: initial health of the Scorpion.
            speed: initial speed of the Scorpion.
            strength: initial strength of the Scorpion.
            is_friendly: by default an Scorpion is never friendly.
        """
        super().__init__(position, initial_health, speed, strength)
        self._is_friendly = is_friendly
        self._objective = position

    def get_name(self) -> str:
        """
        Returns the name of the type of the entity ('Scorpion').
        """
        return SCORPION_NAME
    
    def get_symbol(self) -> str:
        """
        Returns the character that represents the entity type ('S').
        """
        return SCORPION_SYMBOL
    
    def get_targets(self) -> list[tuple[int, int]]:
        """
        Returns the positions that would be attacked by 
        the Scorpion during a combat phase.
        Excludes self position.
        """
        targets = []
        for scorpion_attack_range in range((-SCORPION_RANGE), 
                                           (SCORPION_RANGE + 1)):
            if scorpion_attack_range != 0:
                targets.append((self.get_position()[0] + scorpion_attack_range, 
                                self.get_position()[1]))
                targets.append((self.get_position()[0], 
                                self.get_position()[1] + scorpion_attack_range))
        
        return targets
    
    def update_objective(self, 
                         entities: list[Entity], 
                         buildings: dict[tuple[int, int], Building]) -> None:
        """
        Updates the objective of the Scorpion based on 
        a list of entities and dictionary of buildings.
        Since a Scorpion only attacks mechs, this method is only using 
        the entities list.

        Precondition: 
            entities (list of Entity) is sorted in descending priority order.
            The first entity in the list being the highest priority.

        Parameters:
            entities: all entity instances.
            buildings: all buildings from get_buildings() method 
                        from Board class.
        """
        _dummy_entity_health = 0
        _dummy_entity_pos = ()
        for entity in entities:
            if (entity.is_friendly() == True 
                and entity.get_health() >= _dummy_entity_health):
                _dummy_entity_health = entity.get_health()
                _dummy_entity_pos = entity.get_position()
        self._objective = _dummy_entity_pos


class Firefly(Enemy):
    """
    Inherits from Enemy, under Entity.
    Firefly represents a type of enemy that attacks at a long range vertically, 
    and targets buildings with the lowest health. 
    Fireflies are represented by the character F. 
    """

    def __init__(self, position: tuple[int, int], 
                 initial_health: int, 
                 speed: int, 
                 strength: int,
                 is_friendly: bool = False) -> None:
        """
        Initializes a Scorpion instance with the specified attributes.
        By default, enemies are never friendly.

        Parameters:
            position: initial position of Scorpion in the format of (col, row).
            initial_health: initial health of the Scorpion.
            speed: initial speed of the Scorpion.
            strength: initial strength of the Scorpion.
            is_friendly: by default an Scorpion is never friendly.
        """
        super().__init__(position, initial_health, speed, strength)
        self._is_friendly = is_friendly
        self._objective = position

    def get_name(self) -> str:
        """
        Returns the name of the type of the entity ('Firefly').
        """
        return FIREFLY_NAME
    
    def get_symbol(self) -> str:
        """
        Returns the character that represents the entity type ('F').
        """
        return FIREFLY_SYMBOL
    
    def get_targets(self) -> list[tuple[int, int]]:
        """
        Returns the positions that would be attacked by 
        the Scorpion during a combat phase.
        Excludes self position.
        """
        targets = []
        for firefly_attack_range in range((-FIREFLY_RANGE), 
                                           (FIREFLY_RANGE + 1)):
            if firefly_attack_range != 0:
                targets.append((self.get_position()[0] + firefly_attack_range, 
                                self.get_position()[1]))
        return targets

    def update_objective(self, 
                         entities: list[Entity], 
                         buildings: dict[tuple[int, int], Building]) -> None:
        """
        Updates the objective of the Scorpion based on 
        a list of entities and dictionary of buildings.
        Since a firefly only attacks buildings, this method is only using 
        the buildings dictionary.

        Parameters:
            entities: all entity instances.
            buildings: all buildings from get_buildings() method 
                        from Board class.
        """
        _targeted_health = float('inf')
        lowest_hp_pos_list = []

        # check for lowest health
        for building in buildings.values():
            current_building_health = int(str(building))
            if current_building_health <= _targeted_health:
                _targeted_health = current_building_health

        for building_pos, building in buildings.items():
            current_building_health = int(str(building))
            if current_building_health == _targeted_health:
                if building_pos not in lowest_hp_pos_list:
                    lowest_hp_pos_list.append(building_pos)
        
        if len(lowest_hp_pos_list) == 1:
            self._objective = lowest_hp_pos_list[0]
        elif len(lowest_hp_pos_list) > 1:
            self._objective = max(lowest_hp_pos_list, key=lambda x: x)
        else:
            self._objective = self.get_position()    
        
        
class BreachModel():
    """
    BreachModel models the logical state of a game of Into The Breach.
    """
    _any_moved_made = False


    def __init__(self, board: Board, entities: list[Entity]) -> None:
        """
        Instantiates a new model class with the given board and entities.

        Parameter:
            board: the board instance. It is the current status of the board.
            entities: the list of entity instances.
        """
        self._board = board
        self._entities = entities

    def __str__(self) -> str:
        """
        Returns the string representation of the model.
        The string representation of a model is:
            the string representation of the game board, 
            followed by a blank line, 
            followed by the string representation of all game entities 
            in descending priority order, 
            separated by newline characters.
        """
        str_entities = [str(entity) for entity in self.get_entities()]
        str_entities_concat = '\n\n' + '\n'.join(str_entities)
        str_board = str(self.get_board())
        return str_board + str_entities_concat
    
    def get_board(self) -> Board:
        """
        Returns the current board instance.
        """
        return self._board
    
    def get_entities(self) -> list[Entity]:
        """
        Returns the list of all entities in descending priority order, 
        with the highest priority entity being the first element of the list.
        """
        return self._entities
    
    def has_won(self) -> bool:
        """
        Returns True iff at the end of an attack phase:
            ALL enemies are destroyed, and
            At least 1 Mech is not destroyed, and
            At least 1 Building is not destroyed.
        """
        current_board = self.get_board()
        current_building_dict = current_board.get_buildings()

        current_entities_list = self.get_entities()

        # use is_destroyed method under Building/Mechs to check 
        _buildings_destroyed = 0
        _mechs_destroyed = 0

        _enemies_counter = 0
        _enemies_destroyed = 0

        # check for number of destroyed buildings
        for building in current_building_dict.values():
            if not building.is_destroyed():
                _buildings_destroyed += 1

        # check for number of destroyed Mechs aka friendly entities
        for entity in current_entities_list:
            if (entity.is_friendly() and entity.is_alive()):
                _mechs_destroyed += 1

        # count for enemies
        for entity in current_entities_list:
            if not entity.is_friendly():
                _enemies_counter += 1

        # count for destroyed enemies
        for entity in current_entities_list:
            if not entity.is_friendly():
                if not entity.is_alive():
                    _enemies_destroyed += 1
                
        # return True only when:
        # ALL enemies are dead, AND
        # at least 1 building is alive, AND
        # at least 1 mech is alive
        return ((_enemies_counter == _enemies_destroyed) 
                and ( _buildings_destroyed > 0)
                and (_mechs_destroyed > 0))
    
    def has_lost(self) -> bool:
        """
        Returns True iff at the end of an attack phase:
            ALL buildings are destroyed, or
            ALL Mechs are destroyed.
        """
        current_board = self.get_board()
        current_building_dict = current_board.get_buildings()
        current_entities_list = self.get_entities()

        # check total numbers of buildings and mechs
        _buildings_counter = 0
        _mechs_counter = 0

        # use is_destroyed method under Building/Mechs to check 
        _buildings_destroyed = 0
        _mechs_destroyed = 0

        # check for total number of buildings
        for building in current_building_dict.values():
            _buildings_counter += 1

        # check for total number of mechs
        for entity in current_entities_list:
            if entity.is_friendly() == True:
                _mechs_counter += 1

        # check for number of destroyed buildings
        for building in current_building_dict.values():
            if building.is_destroyed() == True:
                _buildings_destroyed += 1

        # check for number of destroyed Mechs
        for entity in current_entities_list:
            if entity.is_alive() == False:
                _mechs_destroyed += 1
        
        # return True only when:
        # ALL buildings are destroyed, OR
        # ALL mechs are destroyed
        return ((_buildings_counter == _buildings_destroyed) 
                or (_mechs_counter == _mechs_destroyed))
    
    def entity_positions(self) -> dict[tuple[int, int], Entity]:
        """
        Returns a dictionary containing all entities, 
        indexed by entity position.
        """
        current_entites = self.get_entities()
        dict_entities = {}
        for entity in current_entites:
            dict_entities[entity.get_position()] = entity

        return dict_entities
    
    def get_valid_movement_positions(self, 
                                     entity: Entity) -> list[tuple[int, int]]:
        """
        Returns the list of positions that the given entity could move to during
         the relevant movement phase. This function does not check if the entity
         has already moved during a given movement phase.
        """
        valid_positions = []
        board_dimensions = self.get_board().get_dimensions()
        entity_position = entity.get_position()
        entity_speed = entity.get_speed()

        # Iterate over all possible positions on the board
        for row in range(board_dimensions[0]):
            for col in range(board_dimensions[1]):
                new_position = (row, col)

                # Skip the current position of the entity
                if new_position == entity_position:
                    continue
                
                # Check if the new position is within the board dimensions
                if ((0 <= new_position[0] < board_dimensions[0]) 
                    and (0 <= new_position[1] < board_dimensions[1])):
                    # Check if the new position is valid
                    tile = self.get_board().get_tile(new_position)
                    if (not tile.is_blocking() 
                        and new_position not in self.entity_positions().keys()):
                        # Calculate the distance 
                        # from the entity's current position to the new position
                        distance = get_distance(self, 
                                                entity_position, 
                                                new_position)
                        
                        # If the distance is within the entity's speed, 
                        # add the new position to the list
                        if distance != -1 and distance <= entity_speed:
                            valid_positions.append(new_position)
        
        # Sort the valid positions based on the specified order
        valid_positions.sort(key=lambda pos: (pos[0], pos[1]))
        
        return valid_positions
    
    def attempt_move(self, entity: Entity, position: tuple[int, int]) -> None:
        """
        Moves the given entity to the specified position only if 
        the entity is friendly, active, and can move to that position 
        according to the game rules. Does nothing otherwise. 
        Disables entity if a successful move is made.

        Parameter:
            entity: the selected entity for moving.
            position: a destination selectable for moving.
        """
        if entity.is_friendly():
            if entity.is_active():
                if position in self.get_valid_movement_positions(entity):
                    entity.set_position(position)
                    entity.disable()
                    self._any_moved_made = True
        else:
            if position in self.get_valid_movement_positions(entity):
                entity.set_position(position)
                self._any_moved_made = True

    def ready_to_save(self) -> bool:
        """
        Returns true only when no move has been made 
        since the last call to end_turn.
        """
        return (not self._any_moved_made)
    
    def assign_objectives(self) -> None:
        """
        Updates the objectives of all enemies based on the current game state.
        """

        entities_list = self.get_entities()
        buildings_dict = self.get_board().get_buildings()

        for entity in entities_list:
            if not entity.is_friendly():
                entity.update_objective(entities_list, buildings_dict)
     
    def move_enemies(self) -> None:
        """
        Moves each enemy to the valid movement position that minimizes 
        the distance of the shortest valid path between the position 
        and the enemy's objective.

        If there is a tie for shortest distance (Priority):
            -> Move to the position in the bottom-most row
            -> Move to the position in the right-most column
        
        If there is no valid path from an enemy to its objective, 
        the enemy does not move. 
        Enemies move in descending priority order starting with 
        the highest priority enemy.
        """
        entities_list = self.get_entities()
        
        for entity in entities_list:
            # check for enemy
            if not entity.is_friendly():
                all_valid_pos = self.get_valid_movement_positions(entity)
                enemy_obj = entity.get_objective()
                # check for valid movements exist and the enemy has an obj
                if all_valid_pos and enemy_obj:
                    potential_move = all_valid_pos[0]
                    same_dist_pos_list = []
                    no_route_found_pos_list = []
                    shortest_dist = float('inf')
                    for valid_pos in all_valid_pos:
                        cal_dist = get_distance(self, enemy_obj, valid_pos)
                        if cal_dist < shortest_dist and cal_dist != -1:
                            shortest_dist = cal_dist
                            potential_move = valid_pos
                        elif cal_dist == shortest_dist and cal_dist != -1:
                            if potential_move not in same_dist_pos_list:
                                same_dist_pos_list.append(potential_move)
                            same_dist_pos_list.append(valid_pos)
                        elif cal_dist == -1:
                            no_route_found_pos_list.append(valid_pos)
                    
                    # if the enemy has no possible movement at all
                    if no_route_found_pos_list == all_valid_pos:
                        continue
                    
                    # if there are not positions with same distance to target
                    if not same_dist_pos_list:
                        self.attempt_move(entity, potential_move)
                    else:
                        if entity.get_position() in same_dist_pos_list:
                            same_dist_pos_list.remove(entity.get_position())
                        self.attempt_move(entity,sorted(same_dist_pos_list, 
                                                        key=lambda x: x,
                                                        reverse=True)[0])

    def make_attack(self, entity: Entity) -> None:
        """
        Makes given entity perform an attack against every tile that 
        is currently a target of the entity.

        Parameter:
            entity: an entity instance, can be a mech or an enemy.
        """
        _attack_range = entity.get_targets()
        _entity_strength = entity.get_strength()
        _all_buildings = self.get_board().get_buildings()
        _all_buildings_key = _all_buildings.keys()
        _entity_pos_dict = self.entity_positions()
        _entity_positions = _entity_pos_dict.keys()

        for target_pos in _attack_range:
            if target_pos in _entity_positions:
                entity.attack(_entity_pos_dict[target_pos])
            elif target_pos in _all_buildings_key:
                self.get_board().get_tile(target_pos).damage(_entity_strength)


    def end_turn(self) -> None:
        """
        Executes the attack and enemy movement phases, 
        then sets all mechs to be active.

        Attack phase:
            All entities attack in descending priority.
            Note: assign_objectives is in descending order, where the item 
            has the highest priority is the first item.
        After attacked:
            If entity is dead, remove from entity list.
        
        Enemy movement phase:
            All enemies are assigned an objective.
            In descending order, each enemy moves to the shortest path
            to the objective.
                (Enemy can only move to tiles reachable 
                via valid paths of length 
                no greater than it's speed)
            If no valid path, enemy does not move.

        """
        entities_list = self.get_entities()

        # attack phase
        for entity in entities_list:
            if entity.is_alive():
                self.make_attack(entity)
            else:
                entities_list.remove(entity)
        
        # double check to delete dead entities
        for entity in entities_list:
            if not entity.is_alive():
                entities_list.remove(entity)
        
        # enemy movement phase
                
        self.assign_objectives()
        self.move_enemies()

        # set mech to active
        for entity in entities_list:
            if entity.is_friendly():
                entity.enable()

        self._any_moved_made = False


# GUI COMPONENTS BELOW
                
# GameGrid
class GameGrid(AbstractGrid):
    """
    GameGrid class inherits from AbstractGrid class from a2 support file
    (which inherits tk.Canvas).

    This displays:
        1. Basic tile display.
        2. Highlighting tiles.
        3. Entities display on top of tiles. 
            Annotating building health on top of buildings.
        4. Do not bind any commands to mouse buttons at this stage. 
            This will be done when working on the controller.
    """

    def redraw(self, 
               board: Board, 
               entities: list[Entity], 
               highlighted: list[tuple[int, int]] = None, 
               movement: bool = False ) -> None:
        """
        Clears the game grid, then redraws it 
        according to the provided information.
        Draw on gamegrid instance itself, not directly onto master or others.
        
        If a list of highlighted cells are provided, then the color of 
        those cells are overridden to be one of two highlight colors based on 
        if movement is 
        True (refer to MOVE_COLOR from support file) or
        False (refer to ATTACK_COLOR from support file).
        If highlighted is None then no highlighting occurs 
        and the movement parameter is ignored.

        The health of every building that is not destroyed is annotated 
        on top of their respective building tiles.

        The special Unicode character associated with each entity is 
        annotated on top of the tiles located at the position of 
        each respective entity.

        All annotations appear in the center of their respective cells.

        Parameter:
            board: instanced board.
            entities: a list of instanced entities. 
                        NOT the string representation.
            highlighted: coordinates of hightlighed grids.
            movement: False for next display being movement display,
                      True for next display being range of attack display.
        """
        self._board = board
        
        self._entities = entities
        #possible move or target
        self._highlighted = highlighted
        # False for movement display, True for target display
        self._movement = movement 

        # retrieve the dimensions and store (row, col) separately
        board_rows, board_cols = self._board.get_dimensions()

        # Clear the grid
        self.clear()

        # set dimensions
        self.set_dimensions((board_rows, board_cols))

        # Draw tiles
        for row in range(board_rows):
            for col in range(board_cols):
                tile = self._board.get_tile((row, col))
                # tile is highlighted for possible movement display
                if not self._movement and (row, col) in self._highlighted:
                    # is the tile a building?
                    if isinstance(tile, Building):
                        # is the Building destroyed? set color accordingly
                        if tile.is_destroyed():
                            color = DESTROYED_COLOR
                        else:
                            color = MOVE_COLOR
                        self.color_cell((row, col), color)
                        if not tile.is_destroyed():
                            self.annotate_position((row, col),
                                                   str(tile),
                                                   ENTITY_FONT)
                    # is the tile either a Mountain or a Ground?
                    if isinstance(tile, Mountain) or isinstance(tile, Ground):
                        self.color_cell((row, col), MOVE_COLOR)
                # tile is highlighted for attack range
                elif self._movement and (row, col) in self._highlighted:
                    # is the tile a Building?
                    if isinstance(tile, Building):
                        # is the Building destroyed? set color accordingly
                        if tile.is_destroyed():
                            color = DESTROYED_COLOR
                        else:
                            color = ATTACK_COLOR
                        self.color_cell((row, col), color)
                        if not tile.is_destroyed():
                            self.annotate_position((row, col),
                                                   str(tile),
                                                   ENTITY_FONT)
                    # is the tile either a Mountain or a Ground?
                    if isinstance(tile, Mountain) or isinstance(tile, Ground):
                        self.color_cell((row, col), ATTACK_COLOR)
                # tile is not highlighted
                elif (row, col) not in self._highlighted:
                    # is the tile a Building?
                    if isinstance(tile, Building):
                        if tile.is_destroyed():
                            color = DESTROYED_COLOR
                        else:
                            color = BUILDING_COLOR
                        self.color_cell((row, col), color)
                        if not tile.is_destroyed():
                            self.annotate_position((row, col),
                                                   str(tile),
                                                   ENTITY_FONT)
                    # is the tile either a Mountain?
                    elif isinstance(tile, Mountain):
                        self.color_cell((row, col), MOUNTAIN_COLOR)
                    # is the tile either a Ground?
                    elif isinstance(tile, Ground):
                        self.color_cell((row, col), GROUND_COLOR)
        
        # Draw entities
        for entity in self._entities:
            pos = entity.get_position()
            # entity highlighted for target
            if self._movement and pos in self._highlighted:
                self.color_cell(pos, ATTACK_COLOR)
            if isinstance(entity, TankMech):
                self.annotate_position(pos, 
                                        TANK_DISPLAY, 
                                        ENTITY_FONT)
            if isinstance(entity, HealMech):
                self.annotate_position(pos, 
                                        HEAL_DISPLAY, 
                                        ENTITY_FONT)
            if isinstance(entity, Scorpion):
                self.annotate_position(pos, 
                                        SCORPION_DISPLAY, 
                                        ENTITY_FONT)
            if isinstance(entity, Firefly):
                self.annotate_position(pos, 
                                        FIREFLY_DISPLAY, 
                                        ENTITY_FONT)

    def bind_click_callback(self, 
                            click_callback: 
                            Callable[[tuple[int, int]], None]) -> None:
        """
        Binds the <Button-1> and <Button-2> events on itself to a function 
        that calls the provided click handler at the correct position. 
        
        Note: We bind both <Button-1> and <Button-2> to account for differences 
        between Windows and Mac operating systems. These callbacks will be 
        created within the controller, as this is the only place where you have 
        access to the required modelling information. Integrate GameGrid 
        into the game before attempting this method.

        Parameter:
            click_callback: a callable function/method takes 
                            position (#rows, #cols) as argument.
                            Entity selection 
                            and targeted tile movement selection.
        """
        # lambda function to convert pixels being passed in by 
        # event (event.x, event.y) with user click to a position
        self.bind("<Button-1>", lambda event: click_callback(self.pixel_to_cell
                                                            (event.x, event.y)))
        
        self.bind("<Button-2>", lambda event: click_callback(self.pixel_to_cell
                                                            (event.x, event.y)))     
        
                
# SideBar
class SideBar(AbstractGrid):
    
    def __init__(self, 
                 master: tk.Widget, 
                 dimensions: tuple[int, int], 
                 size: tuple[int, int]) -> None:
        """
        Constructor of SideBar class, 
        inherits from AbstractGrid from a2 support file.

        Parameters:
            master: The master frame for this Canvas.
            dimensions: (#of entities, # of headers)
            size: (width in pixels, height in pixels)
        """
        super().__init__(master, dimensions, size)
        
    def display(self, entities: list[Entity]) -> None:
        """
        Clears the side bar, then redraws the header followed 
        by the relevant properties of the given entities on 
        the SideBar instance itself.

        Parameter:
            entities: list of entity instances.
        """
        #clear sidebar before displaying info
        self.clear()

        #rows and cols variables
        num_of_entities = len(entities)
        numb_of_headers = len(SIDEBAR_HEADINGS)

        self.set_dimensions((num_of_entities+1, numb_of_headers))
        
        #printing headers
        for i in range(numb_of_headers):
            self.annotate_position((0,i), 
                               SIDEBAR_HEADINGS[i], 
                               SIDEBAR_FONT)

        # printing entity infos            
        for entity_index, entity in enumerate(entities):
            entityCoord = entity.get_position()
            entityHealth = entity.get_health()
            entityDmg = entity.get_strength()
            # check entity type
            if isinstance(entity, TankMech):
                self.annotate_position((entity_index + 1, 0),
                                       TANK_DISPLAY,
                                       SIDEBAR_FONT)
            if isinstance(entity, HealMech):
                self.annotate_position((entity_index + 1, 0),
                                       HEAL_DISPLAY,
                                       SIDEBAR_FONT)
            if isinstance(entity, Scorpion):
                self.annotate_position((entity_index + 1, 0),
                                       SCORPION_DISPLAY,
                                       SIDEBAR_FONT)
            if isinstance(entity, Firefly):
                self.annotate_position((entity_index + 1, 0),
                                       FIREFLY_DISPLAY,
                                       SIDEBAR_FONT)
            # create coord text
            self.annotate_position((entity_index + 1, 1),
                                       f"({entityCoord[0]}, {entityCoord[1]})",
                                       SIDEBAR_FONT)
            #create hp text
            self.annotate_position((entity_index + 1, 2),
                                       entityHealth,
                                       SIDEBAR_FONT)
            #create dmg text
            self.annotate_position((entity_index + 1, 3),
                                       entityDmg,
                                       SIDEBAR_FONT)


# ControlBar
class ControlBar(tk.Frame):
    """
    Tkinter Frame Class

    Contains three buttons 
    that allow the user to perform administration actions.
    """
    def __init__(self, master: tk.Widget, **kwargs):
        """
        Constructor of the ControlBar class, inherits from tk.Frame.
        
        Parameters:
            master: The master frame for this Canvas.
            **kwargs: keyword arguments.
        """
        super().__init__(master, **kwargs)

        # create save game button  
        self.save_game_btn = tk.Button(
            self,
            text = SAVE_TEXT
        )
        self.save_game_btn.pack(
            side = tk.LEFT,
            expand = tk.TRUE
        )
        # create load game button
        self.load_game_btn = tk.Button(
            self,
            text = LOAD_TEXT
        )
        self.load_game_btn.pack(
            side = tk.LEFT,
            expand = tk.TRUE
        )
        # create end turn button
        self.end_turn_btn = tk.Button(
            self,
            text = TURN_TEXT
        )
        self.end_turn_btn.pack(
            side = tk.LEFT,
            expand = tk.TRUE
        )


# View class
class BreachView():
    def __init__(self, 
                 root: tk.Tk, 
                 board_dims: tuple[int, int], 
                 save_callback: Optional[Callable[[], None]] = None,
                 load_callback: Optional[Callable[[], None]] = None, 
                 turn_callback: Optional[Callable[[], None]] = None ) -> None:
        """
        Constructor of BreachView class.

        Parameters:
            root: The root frame of this Canvas.
            board_dims: #rows, #cols of the current game board.
            save_callback: save command method name as a reference.
            load_callback: load command method name as a reference.
            turn_callback: end turn command method name as a reference.

        """
        self.root = root
        self.board_dims = board_dims
        self._num_rows, self.num_cols = self.board_dims #change this later
        self._save_callback = save_callback
        self._load_callback = load_callback
        self._turn_callback = turn_callback

        # check if player made a move
        self.moved = False

        # window title
        self.root.title(BANNER_TEXT)

        # create game banner frame, TOP OF CANVAS
        bannerFrame = tk.Frame(
            root,
            height=BANNER_HEIGHT, # 75            
        )
        bannerFrame.pack(
            side=tk.TOP
        )
        # banner text
        banner = tk.Label(
            bannerFrame,
            text = BANNER_TEXT, # "Into The Breach"
            font = BANNER_FONT, # "Arial", 22, "bold"
        )
        banner.pack(
        )
        #MIDDLE FRAMAE
        midFrame = tk.Frame(
            root
        )
        midFrame.pack()
        # MIDDLE OF CANVAS (gamegrid)
        gameFrame = tk.Frame(
            midFrame,
            width=GRID_SIZE,
            # height=GRID_SIZE
        )
        gameFrame.pack(
            side = tk.LEFT,
            expand=tk.TRUE, 
            fill=tk.BOTH
        )
        
        # create gamegrid instance
        self._gamegrid = GameGrid(gameFrame,
                                 self.board_dims,
                                 (GRID_SIZE,
                                  GRID_SIZE))
        self._gamegrid.pack(
            side = tk.TOP,
            expand = tk.TRUE,
            fill=tk.BOTH
        )

        # MIDDLE OF THE CANVAS (sidebar)
        self.sidebarFrame = tk.Frame(
            midFrame,
            width=SIDEBAR_WIDTH
        )
        self.sidebarFrame.pack(
            side = tk.LEFT,
            expand=tk.TRUE, 
            fill=tk.BOTH
        )
        # create sidebar instance
        self._sidebar = SideBar(self.sidebarFrame,
                            (self.board_dims[0], 4), 
                            #dims is going to change anyways by display()
                            (SIDEBAR_WIDTH,
                            GRID_SIZE))
        self._sidebar.pack(
            side=tk.LEFT,
            expand=tk.TRUE,
            fill=tk.BOTH
        )

        # BOTTOM OF CANVAS (controlbar)
        self._controlbar = ControlBar(
            root,
            width = GRID_SIZE + SIDEBAR_WIDTH,
            height = CONTROL_BAR_HEIGHT,
        )
        self._controlbar.pack(
            side=tk.TOP,
            expand=tk.TRUE,
            fill=tk.BOTH
        )
        #configurate the buttons in ControllerBar with correct callbacks
        self._controlbar.save_game_btn.config(command=self._save_callback)
        self._controlbar.load_game_btn.config(command=self._load_callback)
        self._controlbar.end_turn_btn.config(command=self._turn_callback)
        
    def bind_click_callback(self, 
                            click_callback: 
                            Callable[[tuple[int, int]], None]) -> None:
        """
        Binds a click event handler to the instantiated GameGrid 
        based on click callback.
        Call the bind_click_callback() in gamegrid to bind events to
        "<button-1>" and "<button-2>"

        Parameter:
            click_callback: a callable method. Position (#row, #cols)
                            of user click is also being passed.
        """
        self._gamegrid.bind_click_callback(click_callback)
    
    def redraw(self, board: Board, 
               entities: list[Entity], 
               highlighted: list[tuple[int,int]] = None, 
               movement: bool = False ) -> None:
        """
        Redraws the instantiated GameGrid and SideBar 
        based on the given board, list of entities, 
        and tile highlight information.

        Takes the board, list of entities, and tile highlight information
        from the controller class (IntoTheBreach) and pass them to 
        child classes (gamegrid, sidebar).

        Parameters:
            board: instanced board passed from controller class.
            entities: instanced list of entities passed from controller class.
            highlighted: list of coordinates in tuples, storing coordinates of 
                        highlighted grids.
            movement: False for next display being movement display,
                      True for next display being range of attack display.
        """
        # the highlighted argument contains the selected entity

        # redraw gamegrid
        self._gamegrid.redraw(board,
                              entities,
                              highlighted,
                              movement)
        # display sidebar
        self._sidebar.display(entities)


# Controller class
class IntoTheBreach():
    """
    This is the Controller class.

    This is responsible for creating and maintaining instances of the model 
    and view classes, event handling, and facilitating communication between 
    the model and view classes.
    The controller will need to track which entity occupied 
    the tile last clicked on by the user in order to correctly highlight tiles 
    on the board, using the set_focussed_entity method.
    """

    def __init__(self, root: tk.Tk, game_file: str) -> None:
        """
        Constructor of controller class IntoTheBreach.
        Instantiates the controller. 
        Creates instances of BreachModel and BreachView, 
        and redraws display to show the initial game state.

        Parameters:
            root: The root frame of this Canvas.
            game_file: 1 out of the 3 pre-set game file.
        """
        # Store a reference to the root window
        self.root = root

        # get the desired game txt file directory
        self.game_file = game_file 
        
        # board related variables
        self.game_board = []
        self.game_board_width = 0
        self.game_board_height = 0

        # entities related variablesload
        self.game_entities = []
        self.coord_highlighted_entity = []
        self.number_of_entities = None

        # load game file path and content, 
        # load data to variables (board and entity)
        self.load_model(self.game_file)

        #movement?
        # False for moving, True for attacking
        self.moving_attacking = False

        # create instance of BreachModel class (Model)
        # self.breachModel = BreachModel(self.game_board, 
        #                               self.game_entities)
        # create instance of BreachView class (View)
        self.breachView = BreachView(self.root,
                                     self.game_board_dims,
                                      self._save_game,
                                      self._load_game,
                                      self._end_turn
                                      )
        self.breachView.bind_click_callback(self._handle_click)
        # mouse click passing event.x and event.y as pixels
        # self.breachView._gamegrid.bind('<Button-1>', self._handle_click)

        # redraw the gamegrid and sidebar
        self.redraw() 
        
    def redraw(self) -> None:
        """
        Redraws the instantiated GameGrid and SideBar based on 
        the given board, list of entities, and tile highlight information.
        """
        # call breachView to call gamegrid.redraw() and sidebar.display()

        # self.coord_highlighted_entity is the pos of focussed_entity

        if self.coord_highlighted_entity:
            entity_pos = self.coord_highlighted_entity[0]
            selected_entity = (self.breachModel.entity_positions()
                             [entity_pos])
            # entity is friendly and is going to move
            if selected_entity.is_friendly() and not self.moving_attacking:
                possible_move_of_selected_entity = (self.breachModel.
                                                 get_valid_movement_positions
                                                 (selected_entity))
                self.breachView.redraw(self.game_board,
                                       self.game_entities,
                                       possible_move_of_selected_entity)
            # entity is friendly and is going to attack or
            # entity is not friendly
            elif not selected_entity.is_friendly():
                attack_range = selected_entity.get_targets()
                self.breachView.redraw(self.game_board,
                                       self.game_entities,
                                       attack_range,
                                       self.moving_attacking)
            elif selected_entity.is_friendly() and self.moving_attacking:
                attack_range = selected_entity.get_targets()
                self.breachView.redraw(self.game_board,
                                       self.game_entities,
                                       attack_range,
                                       self.moving_attacking)
        else:
            # deselect - passing an empty list to clear the highlighting tile
            # looks very hardcoding
            self.breachView.redraw(self.game_board,
                                   self.game_entities,
                                   [],
                                   self.moving_attacking)
       
    def set_focussed_entity(self, 
                            entity: Optional[Entity]) -> None:
        """
        Sets the given entity to be the one on which to base highlighting. 
        Or clears the focussed entity if None is given.

        This method sets selected entity, disregards it being friendly or not.

        Parameter:
            entity: position (row, col) of a selected entity instance. 
                    If None is being passed in, no entity on the board 
                    is selected.
        """
        if entity is None:
            self.coord_highlighted_entity = []
        else:
            self.coord_highlighted_entity.append(entity.get_position())

    def make_move(self, 
                  position: tuple[int, int]) -> None:
        """
        Attempts to move the focussed entity to the given position, 
        and then clears the focussed entity. 
        Note that you have implemented a method in BreachModel 
        that enforces the validity of a move according 
        to the game rules already. (get_valid_movement_positions())

        Parameter:
            position: target position (#rows, #cols) 
                        the user wants to move the entity to.
        """
        focussed_entity = (self.breachModel.entity_positions()
                           [self.coord_highlighted_entity[0]])
        focussedEntityValidPos = (self.breachModel.get_valid_movement_positions
                                     (focussed_entity))
        # ensure Mech can only move to possible move
        if position in focussedEntityValidPos and focussed_entity.is_friendly():
            self.breachModel.attempt_move(focussed_entity, position)
            self.moving_attacking = True
        # clear the entity selection
        self.coord_highlighted_entity = self.set_focussed_entity(None)


    def load_model(self, 
                   file_path: str) -> None:
        """
        Replaces the current game state 
        with a new state based on the provided file.
        If the file is opened successfully, the string representation of 
        BreachModel will be returned.

        Parameters:
            file_path: a file path targetting at 1 of the 3 
                        string represented game files.

        Caution: 
            this method needs to process IOError. If such error occurs,
            an error messagebox should be displayed to the user 
            explaining the error that occurred, 
            and the game state should not change.
        """
        game_board = []
        game_str_entities = []
        # check for new line character for separating board and entities
        separate_line_check = False

        with open(file_path, "r") as game_file:
            for line in game_file:
                if not separate_line_check:
                    if line == '\n':
                        separate_line_check = True
                        continue
                    board_row = []
                    for char in line.strip():
                        board_row.append(char)
                    game_board.append(board_row)
                else:
                    entity_row = []
                    for char in line.strip():
                        if char != ',':
                            entity_row.append(char)
                    game_str_entities.append(entity_row)
        
        # assign read lines to game board status
        board_instance = Board(game_board)
        self.game_board = board_instance
        self.game_board_width = board_instance.get_dimensions()[1]
        self.game_board_height = board_instance.get_dimensions()[0]
        self.game_board_dims = (self.game_board_height, self.game_board_width)
        self.number_of_entities = len(game_str_entities)

        # Convert read lines of str entities to a list of entity instances
        # and load them
        game_entity_instances = []
        for entity_info in game_str_entities:
            if entity_info[0] == TANK_SYMBOL:
                tankmech_inst = TankMech((int(entity_info[1]), 
                                          int(entity_info[2])),
                                         int(entity_info[3]),
                                         int(entity_info[4]),
                                         int(entity_info[5]))
                game_entity_instances.append(tankmech_inst)
            if entity_info[0] == HEAL_SYMBOL:
                healmech_inst = HealMech((int(entity_info[1]), 
                                          int(entity_info[2])),
                                         int(entity_info[3]),
                                         int(entity_info[4]),
                                         int(entity_info[5]))
                game_entity_instances.append(healmech_inst)
            if entity_info[0] == SCORPION_SYMBOL:
                scorpion_inst = Scorpion((int(entity_info[1]), 
                                          int(entity_info[2])),
                                         int(entity_info[3]),
                                         int(entity_info[4]),
                                         int(entity_info[5]))
                game_entity_instances.append(scorpion_inst)
            if entity_info[0] == FIREFLY_SYMBOL:
                firefly_inst = Firefly((int(entity_info[1]), 
                                          int(entity_info[2])),
                                         int(entity_info[3]),
                                         int(entity_info[4]),
                                         int(entity_info[5]))
                game_entity_instances.append(firefly_inst)
        self.game_entities = game_entity_instances
        self.breachModel = BreachModel(self.game_board, 
                                       self.game_entities)
        # good practice to close file, but this is unnecessary when I am using
        # with open() as var:
        game_file.close()

    def _save_game(self) -> None:
        """
        If the the user has made no moves since the last time they clicked 
        the end turn button, opens a asksaveasfilename file dialog 
        to ask the user to specify a file, and then saves 
        the current game state to that file.

        If the user has made at least one move since the last time 
        they clicked the end turn button, shows an error message box 
        explaining to the user that they can only save at the beginning 
        of their turn.

        Caution:
            You do not need to handle IOErrors for this operation.
        """   
        if self.breachModel.ready_to_save():
            save_file_name = filedialog.asksaveasfilename()
            with open(save_file_name, "w") as new_save:
                # writelines game_board
                new_save.writelines(str(self.game_board))
                #writeline a new line \n
                new_save.write("\n\n")

                #writelines game_entities
                for entity in self.game_entities:
                    new_save.write(str(entity) + "\n")

            # good practice to close file, but this is unnecessary 
            # when I am using with open() as var:   
            new_save.close()
        else:
            messagebox.showerror(INVALID_SAVE_TITLE, INVALID_SAVE_MESSAGE)

    def _load_game(self) -> None:
        """
        Opens a askopenfilename file dialog to ask the user to specify a file, 
        and then loads in a new game state from that file.

        Caution:
            If an IO error occurs when loading in a new game state, 
            then a messagebox should be shown to the user explaining the error 
            as described in load model.
        """
        try:
            load_game_file = filedialog.askopenfilename()
            if load_game_file:
                self.load_model(load_game_file)
                self.set_focussed_entity(None)
                self.game_file = load_game_file

            self.redraw()
        except IOError:
            messagebox.showerror(IO_ERROR_TITLE, IO_ERROR_MESSAGE)
    
    def _end_turn(self) -> None:
        """
        Executes the attack phase, enemy movement phase, 
        and termination checking using messagebox.

        Note: attack phase and enemy movement phase is implemented with the
                end_turn() under model class (BreachModel).
        """
        # end_turn() under Model sets Mech to active
        self.breachModel.end_turn()
        if self.coord_highlighted_entity:
            self.set_focussed_entity(None)
        self.redraw()

        # player won the game
        if self.breachModel.has_won():
            if messagebox.askyesno('End game', 
                                       "You Win! " + PLAY_AGAIN_TEXT):
                    # yes - play again
                    self.load_model(self.game_file)
                    self.redraw()
            else:
                #no - end game
                self.root.destroy()
        #player lost the game
        if self.breachModel.has_lost():
            if messagebox.askyesno('End game', 
                                       "You Lost! " + PLAY_AGAIN_TEXT):
                    # yes - play again
                    self.load_model(self.game_file)
                    self.redraw()
            else:
                #no - end game
                self.root.destroy()
        
    def _handle_click(self, position: tuple[int, int]) -> None:
        """
        Handler for a click from the user at the given (row, column) position.
        Game rules apply.

        Parameter:
            position: position (row, col) of user click on the list of board.         
        """

        entity_positions = self.breachModel.entity_positions().keys()
        
        # is there an entity set to be focussed = ready to move?
        # does not matter if I check the length or if the variable exists
        # the coord is always storing either 1 or 0 tuple
        if len(self.coord_highlighted_entity) == 1:
            focussed_entity = (self.breachModel.entity_positions()
                             [self.coord_highlighted_entity[0]])
            if focussed_entity.is_friendly():
                self.make_move(position)
                self.redraw()

        # is clicked position containing an entity?
        if position in entity_positions:
            clicked_entity = self.breachModel.entity_positions()[position]
            # is the selected entity a Mech that the user can move?
            if clicked_entity.is_friendly():
                # has the Mech moved? Yes means it is deactivated (go to else)
                if clicked_entity.is_active():
                    # mech has not moved - display movable tiles of the mech
                    self.set_focussed_entity(None)
                    self.set_focussed_entity(clicked_entity)
                    self.moving_attacking = False
                    self.redraw()
                else:
                    # mech has moved - display attack range of the mech
                    self.set_focussed_entity(None)
                    self.set_focussed_entity(clicked_entity)
                    self.moving_attacking = True
                    self.redraw()
            else:
                # display attack range of selected enemy
                self.set_focussed_entity(None)
                self.set_focussed_entity(clicked_entity)
                self.moving_attacking = True
                self.redraw()

        # is clicked position not an entity? Yes then clear the highlights
        if position not in entity_positions:
            self.set_focussed_entity(None)
            self.redraw()


# Functions calling classes, since these are not under any classes, 
# they are not methods
def play_game(root: tk.Tk, file_path: str) -> None:
    """
    The function only do the following two tasks:
    1. Construct the controller instance using the given file path 
        and the root tk.Tk parameter.
    2. Ensure the root window stays opening listening 
        for events (using mainloop).

    Parameter:
        root: root frame of tkinter.
        file_path: game file directory of different levels (level 1 ~ 3).
    """
    # Pass as "master", and the game file in the class, __init__ method
    game = IntoTheBreach(root, file_path)
    root.mainloop()

def main() -> None:
    """The main function"""
    root = tk.Tk() #Display a window to the user
    
    level_1_file = 'levels/level1.txt' # level 1 txt file directory
    level_2_file = 'levels/level2.txt' # level 2 txt file directory
    level_3_file = 'levels/level3.txt' # level 3 txt file directory
    
    play_game(root, level_1_file)

if __name__ == "__main__":
    main()