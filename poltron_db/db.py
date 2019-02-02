import sqlite3


def create_table(table_name: str, args: str) -> None:
    global DB
    cursor = DB.cursor()
    command = f"CREATE TABLE {table_name} ({args})"
    try:
        cursor.execute(command)
        print("O)   TABLE " + table_name + " has been created".upper())
    except Exception as e:
        # alreadyExists
        print("X)   TABLE " + table_name + " could not be created:".upper(), e)


def prepare_db_tables() -> None:
    global DB
    DB = sqlite3.connect("resources/data.db")
    cursor = DB.cursor()
    create_table("game", "game_id INTEGER PRIMARY KEY, "
                         "M INTEGER NOT NULL, "
                         "N INTEGER NOT NULL, "
                         "Ds INTEGER NOT NULL, "
                         "Dc INTEGER NOT NULL, "
                         "C INTEGER NOT NULL")

    create_table("initial_positions", "game_id INTEGER NOT NULL, "
                                      "x INTEGER NOT NULL, "
                                      "y INTEGER NOT NULL, "
                                      "player_id INTEGER NOT NULL,"
                                      "FOREIGN KEY(game_id) REFERENCES game(game_id)")

    create_table("player_order", "game_id INTEGER NOT NULL, "
                                 "order INTEGER NOT NULL, "
                                 "player_id INTEGER NOT NULL,"
                                 "FOREIGN KEY(game_id) REFERENCES game(game_id)")

    create_table("game_result", "game_id INTEGER NOT NULL, "
                                "last_tick INTEGER NOT NULL, "
                                "victory BOOLEAN NOT NULL,"
                                "FOREIGN KEY(game_id) REFERENCES game(game_id)")

    create_table("important_moments", "game_id INTEGER NOT NULL, "
                                      "tick INTEGER NOT NULL, "
                                      "nb_walls INTEGER NOT NULL, "
                                      "c_deaths INTEGER NOT NULL, "
                                      "map_string text NOT NULL,"
                                      "FOREIGN KEY(game_id) REFERENCES game(game_id)")

    create_table("deaths", "game_id INTEGER NOT NULL, "
                           "tick INTEGER NOT NULL, "
                           "player_id INTEGER NOT NULL,"
                           "FOREIGN KEY(game_id) REFERENCES game(game_id)")
    # TODO Add cache loading and saving
    try:
        cursor.execute("""
        CREATE VIEW IF NOT EXISTS moment_analysis AS
        SELECT 
            game_id, 
            tick, 
            nb_walls, 
            c_deaths, 
            map_string, 
            (c_deaths/C) AS c_remaining, 
            ((C-c_deaths)/C) AS overwhelm_factor, 
            (((nb_walls+(C-c_deaths)+1)/(M*N))) AS encumberment_factor
        FROM important_moments 
            INNER JOIN game 
                ON important_moments.game_id = game.game_id
        GROUP BY game_id, tick
        ORDER BY game_id ASC, tick ASC
        """)

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS result_analysis AS
        SELECT game.* ,  game_result.*
        FROM game_result 
            INNER JOIN game 
                ON game_result.game_id = game.game_id
        ORDER BY game_id ASC, tick ASC
        """)

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS game_players_initial_data AS
        SELECT game_id, player_id, order, x, y
        FROM player_order 
            INNER JOIN initial_positions 
                ON player_order.game_id = initial_positions.game_id
        ORDER BY game_id ASC, player_id ASC
        """)

        cursor.execute("""
                CREATE VIEW IF NOT EXISTS next_game_id AS
                SELECT max(game_id) + 1 
                FROM game
                """)

        cursor.execute("""
                CREATE VIEW IF NOT EXISTS games_without_results AS
                SELECT game_id
                FROM game
                    OUTER JOIN initial_positions 
                        ON game.game_id = game_result.game_id
                """)

        print("O)   CREATED OVERVIEW VIEWS")
    except Exception as e:
        print("X)   FAILED TO CREATE THE VIEWS: ", e)

    DB.commit()


def insert_important_moment(game_id: int, tick: int, nb_walls: int,
                            c_deaths: int, map_string: str) -> None:
    DB = sqlite3.connect("resources/data.db")
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO important_moments (game_id, tick , nb_walls , c_deaths , map_string) 
    VALUES ('{game_id}', '{tick}', '{nb_walls}', '{c_deaths}', {map_string})""")
    DB.commit()
    return


def insert_deaths(game_id: int, tick: int, player_ids: [int]) -> None:
    DB = sqlite3.connect("resources/data.db")
    cursor = DB.cursor()
    for player_id in player_ids:
        cursor.execute(f"""INSERT INTO deaths (game_id, tick , player_id) 
    VALUES ('{game_id}', '{tick}', '{player_id}')""")
    DB.commit()
    return


def insert_game_result(game_id: int, last_tick: int, victory: bool) -> None:
    DB = sqlite3.connect("resources/data.db")
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO game_result (game_id, last_tick , victory) 
    VALUES ('{game_id}', '{last_tick}', '{victory}')""")
    DB.commit()
    return


def insert_player_order(game_id: int, order: int, player_id: int) -> None:
    DB = sqlite3.connect("resources/data.db")
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO player_order (game_id, order , player_id) 
    VALUES ('{game_id}', '{order}', '{player_id}')""")
    DB.commit()
    return


def insert_initial_positions(game_id: int, player_id: int, x: int,
                             y: int) -> None:
    DB = sqlite3.connect("resources/data.db")
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO player_order (game_id, player_id , x, y) 
    VALUES ('{game_id}', '{player_id}', '{x}', '{y}')""")
    DB.commit()
    return


def insert_game_info(game_id: int, m: int, n: int, ds: int, dc: int,
                     c: int) -> None:
    DB = sqlite3.connect("resources/data.db")
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO game (game_id, M, N, Ds, Dc, C) 
    VALUES ('{game_id}', '{m}', '{n}', '{ds}', '{dc}', '{c}')""")
    DB.commit()
    return
