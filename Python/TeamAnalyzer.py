import sqlite3  # This is the package for all sqlite3 access in Python
import sys      # This helps with command-line parameters

# All the "against" column suffixes:
types_list = ["bug","dark","dragon","electric","fairy","fight",
    "fire","flying","ghost","grass","ground","ice","normal",
    "poison","psychic","rock","steel","water"]

# Handle the conversion from Pokemon names to Pokedex numbers 
def get_pokemon_id(pokemon, cursor):
    if pokemon.isdigit():
        return int(pokemon)
    else:
        cursor.execute("SELECT id FROM pokemon WHERE name=?", (pokemon,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(f"Invalid Pokemon name: {pokemon}")

# Analyze the strengths and weaknesses of the Pokemon
# Accept either Pokedex numbers or Pokemon names 
def analyze_pokemon(pokemon_id, cursor):
    cursor.execute("SELECT name, type1, type2 FROM pokemon WHERE id=?", (pokemon_id,))
    pokemon = cursor.fetchone()
    name, type1, type2 = pokemon
    types = [type1]
    if type2:
        types.append(type2)
    strengths = []
    weaknesses = []

    for t in types:
        for against_type in types_list:
            against_value = cursor.execute(f"SELECT {t} FROM pokemon WHERE id=?", (pokemon_id,)).fetchone()[0]
            if against_value > 1:
                strengths.append(against_type)
            elif against_value < 1:
                weaknesses.append(against_type)

    strengths = list(set(strengths))
    weaknesses = list(set(weaknesses))
    return name, types, strengths, weaknesses


# Take six parameters on the command-line
if len(sys.argv) != 7:
    print("You must give me six Pokemon to analyze!")
    sys.exit()

conn = sqlite3.connect('pokemon.db')
cursor = conn.cursor()

team = []
for i, arg in enumerate(sys.argv):
    if i == 0:
        continue

    try:
        pokemon_id = get_pokemon_id(arg, cursor)
    except ValueError as e:
        print(e)
        exit(1)

    # Analyze the pokemon whose pokedex_number is in "arg"
    name, types, strengths, weaknesses = analyze_pokemon(pokemon_id, cursor)
    team.append((name, types, strengths, weaknesses))
    print(f"Analyzing {arg}")
    print(f"{name} ({' '.join(types)}) is strong against {strengths} but weak against {weaknesses}")

    # You will need to write the SQL, extract the results, and compare
    # Remember to look at those "against_NNN" column values; greater than 1
    # means the Pokemon is strong against that type, and less than 1 means
    # the Pokemon is weak against that type

answer = input("Would you like to save this team? (Y)es or (N)o: ")
if answer.upper() == "Y" or answer.upper() == "YES":
    team_name = input("Enter the team name: ")
    # Write the pokemon team to the "teams" table
    cursor.execute("INSERT INTO teams (name) VALUES (?)", (team_name,))
    team_id = cursor.lastrowid
    for arg in sys.argv[1:]:
        pokemon_id = get_pokemon_id(arg, cursor)
        cursor.execute("INSERT INTO team_members (team_id, pokemon_id) VALUES (?, ?)", (team_id, int(pokemon_id)))
    conn.commit()
    print("Saving " + teamName + " ...")
else:
    print("Bye for now!")

conn.close()

