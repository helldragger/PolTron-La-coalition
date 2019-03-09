import sqlite3

DB_PATH = ""


def create_table(table_name: str, args: str) -> None:
    global DB
    cursor = DB.cursor()
    command = f"CREATE TABLE {table_name} ({args})"
    try:
        cursor.execute(command)
    except Exception as e:
        # alreadyExists
        pass

def prepare_db_tables() -> None:
    global DB
    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    create_table("game", "game_id INTEGER PRIMARY KEY, "
                         "Size TEXT NOT NULL,"
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
                                 "player_order INTEGER NOT NULL, "
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
        ORDER BY game_id ASC
        """)

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS game_players_initial_data AS
        SELECT game_id, player_id, player_order, x, y
        FROM player_order 
            INNER JOIN initial_positions 
                ON player_order.game_id = initial_positions.game_id
        ORDER BY game_id ASC, player_id ASC
        """)

        cursor.execute("""
                CREATE VIEW IF NOT EXISTS last_game_id AS
                SELECT max(game_id) 
                FROM game
                """)

    except Exception as e:
        # already exists
        pass
    DB.commit()
    DB.close()


def insert_important_moment(game_id: int, tick: int, nb_walls: int,
                            c_deaths: int) -> None:
    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO important_moments (game_id, tick , nb_walls , c_deaths ) 
    VALUES ('{game_id}', '{tick}', '{nb_walls}', '{c_deaths}')""")
    DB.commit()
    DB.close()
    return


def insert_deaths(game_id: int, tick: int, player_ids: [int]) -> None:
    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    for player_id in player_ids:
        cursor.execute(f"""INSERT INTO deaths (game_id, tick , player_id) 
    VALUES ('{game_id}', '{tick}', '{player_id}')""")
    DB.commit()
    DB.close()
    return


def insert_game_result(game_id: int, last_tick: int, victory: bool) -> None:
    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO game_result (game_id, last_tick , victory) 
    VALUES ('{game_id}', '{last_tick}', '{victory}')""")
    DB.commit()
    DB.close()
    return


def insert_player_order(game_id: int, player_id: int,
                        player_order: int) -> None:
    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO player_order (game_id, player_order , player_id) 
    VALUES ('{game_id}', '{player_order}', '{player_id}')""")
    DB.commit()
    DB.close()
    return


def insert_initial_positions(game_id: int, player_id: int, x: int,
                             y: int) -> None:
    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO initial_positions (game_id, player_id , x, y) 
    VALUES ('{game_id}', '{player_id}', '{x}', '{y}')""")
    DB.commit()
    DB.close()
    return


def insert_game_info(game_id: int, size: str, m: int, n: int, ds: int, dc: int,
                     c: int) -> None:
    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    cursor.execute(f"""INSERT INTO game (game_id, Size, M, N, Ds, Dc, C) 
    VALUES ('{game_id}', '{size}', '{m}', '{n}', '{ds}', '{dc}', '{c}')""")
    DB.commit()
    DB.close()
    return


def get_last_game_id() -> int:
    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    cursor.execute(f"""SELECT * FROM last_game_id""")
    game_id = cursor.fetchone()[0]
    if game_id == None:
        game_id = 0
    DB.close()
    return int(game_id)


def prepare_db_path(args):
    import datetime

    param_string = ""
    if args.model:
        param_string += "model_"
    else:
        param_string += "ai_"
    now = str(datetime.datetime.now())[:19]
    now = now.replace(":", "-").replace(" ", "_")
    param_string += now + "_"
    param_string += f"{args.iter}iter"
    param_string += f".db"

    global DB_PATH
    DB_PATH = "../resources/" + param_string
    return None