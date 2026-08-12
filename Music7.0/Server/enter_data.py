import dbname
import psycopg2
import os
import psycopg2.extras
import re

TIME_MAP = {
    "ln":[0,1,2,3],
    "em":[4,5,6],
    "m":[7,8,9],
    "lm":[10,11,12],
    "ea":[13,14,15],
    "la":[16,17,18],
    "en":[19,20,21],
    "n":[22,23],
}

def enter():
    sql_select = """
        SELECT id,type,path_audio,name,full_name,cover,original,vocal,hour from public.tracks where hour is null
        order by id asc
    """

    unregistered_rows = []
    try:
        with dbname.connect_db(dbname.CONFIG["dbname"]) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql_select)
                unregistered_rows = cur.fetchall()

    except Exception as e:
        print(f"DB Error:{e}")

    if unregistered_rows:
        type = input("bgm/Music\n>>")
        for i,track in enumerate(unregistered_rows,1):
            
            process_metadata_entry(track,i,len(unregistered_rows),type)

def process_metadata_entry(db_track,index,total,type):

    if type == "music":

        print(f"\n-- [{index}/{total}] {db_track['full_name']}")

        if os.path.exists(db_track["path_audio"]):
            os.startfile(db_track["path_audio"])

        type_input = type

        time_input = input(f"[{index}/{total}]曲を再生する時間帯は？\",\"で区切る\n>>")
        time_list = [
            hour
            for t in time_input.split(",")
            for hour in TIME_MAP.get(t.strip().lower(), [t.strip()])
        ]
        weather = input("Weather(Clear,Clouds,Rain,Snow)\n>>").split(",")

        s_name,s_original = name_suggestion(db_track["full_name"],db_track["cover"])

        name = input(f"Name of the music\n[{s_name}]\n>>") or s_name
        original = input(f"Original of the music\n[{s_original}]\n>>") or s_original

        hour = 25

        track_data = {
            "id":db_track["id"],
            "type":type_input,
            "name":name,
            "original":original,
            "hour":hour,
            "time":time_list,
            "weather":weather
            
        }

    elif type == "bgm":
        print(f"\n-- [{index}/{total}] {db_track["name"]}")

        hour = input("bgm hour\n>>")

        type_input = type
        track_data = {
            "id":db_track["id"],
            "type":type_input,
            "name":"",
            "original":"",
            "hour":hour,
            "time":[],
            "weather":[]
            
        }

    save_track_to_db(track_data)

def save_track_to_db(track_data):
    try:
        sql_update = """
        UPDATE tracks
        SET
            type = %s,
            name = %s,
            original = %s,
            hour = %s
        WHERE id = %s
        """

        values = (
            track_data["type"],
            track_data["name"],
            [track_data["original"]],
            track_data["hour"],
            track_data["id"]
        )

        with dbname.connect_db(dbname.CONFIG["dbname"]) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_update, values)

                if cur.rowcount == 0:
                    print(f"Track not found: id={track_data['id']}")
                else:
                    print(f"DB updated: id={track_data['id']}")

    
        sql_insert = """
        INSERT INTO playback_presets (
            track_id,
            name,
            time,
            weather
        )
        VALUES (%s, %s, %s, %s)
        """

        values = (
            track_data["id"],
            track_data["name"],
            track_data["time"],
            track_data["weather"]
        )

        with dbname.connect_db(dbname.CONFIG["dbname"]) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_insert, values)

    except Exception as e:
        print(f"DB Error: {e}")


def name_suggestion(fullname,cover):

    name = "None"
    original = cover
    try:

        if cover[0] == "DECO*27":
            original = cover
            name = fullname.split(" ")[2]

        elif cover[0] == "MIMI":
            original = cover
            name = fullname.split(" ")[2]
            
        elif cover[0] == "Official髭男dism":
            original = cover
            name = " ".join(fullname.split(" ")[2:]).split(" [")[0].split("［")[0]
            
        elif cover[0] == "YOASOBI":
            original = cover
            name = re.search(r"「(.*?)」",fullname).group(1) if re.search(r"「(.*?)」",fullname) else fullname
            
        elif cover[0] == "ロクデナシ":
            original = cover
            name = re.search(r"「(.*?)」",fullname).group(1) if re.search(r"「(.*?)」",fullname) else fullname

        elif cover[0] == "幾田りら":
            original = cover
            name = "".join(fullname.split("「")[1]).split("」")[0]
            
        elif cover[0] == "Guiano":
            original = cover
            name = fullname.split(" ")[2]
            
        elif cover[0] == "Orangestar":
            original = cover
            name = " ".join(fullname.split(" ")[2:]).split(" (")[0]
            
        elif cover[0] == "はるまきごはん / Harumaki Gohan Official":
            original = cover
            name = fullname.split()[0]

        return name,original

    except Exception as e:
        print(f"Error has occured:{e}")
        return name,original