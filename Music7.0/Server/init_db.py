import dbname


class InitDB:

    def __init__(self):
        self.create_functions()
        self.create_tables()

    def create_tables(self):
        command = """
        create table if not exists tracks (
            id SERIAL PRIMARY KEY,
            type VARCHAR(5),

            path_original TEXT,
            path_480p TEXT,
            path_audio TEXT,





            name TEXT,
            full_name TEXT NOT NULL,
            cover TEXT[],
            original TEXT[],
            vocal TEXT[],

            registered CHAR(8),
            published CHAR(8),
            volume_offset real,
            duration INTEGER,
            source TEXT[],
            hour INTEGER,
            selection TEXT[] DEFAULT '{}',

            CONSTRAINT source_no_duplicates
                CHECK(array_has_no_duplicates(source))
        );

        CREATE TABLE IF NOT EXISTS sources (
        id SERIAL PRIMARY KEY,
        track_id INTEGER NOT NULL REFERENCES tracks(id),
        url TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS playback_presets (
        id SERIAL PRIMARY KEY,
        track_id INTEGER NOT NULL REFERENCES tracks(id),

        name TEXT NOT NULL,
        time TEXT NOT NULL,
        signal_time_clear CHAR(4),
        signal_time_clouds CHAR(4),
        signal_time_rain CHAR(4),
        signal_time_snow CHAR(4),
        signal_time_else CHAR(4),
        weather TEXT[]
        );


        """
        self.process_command(command)


    def create_functions(self):
        command = """
            create or replace function array_has_no_duplicates(arr TEXT[])
            returns boolean
            language sql
            immutable
            as $$
                select
                    arr is null
                    or cardinality(arr) = 
                        cardinality(array(
                            select distinct unnest(arr)
                        ));
            $$;
            """

        self.process_command(command)



    def process_command(self,command):
        conn = None

        try:
            conn = dbname.connect_db(dbname.CONFIG["dbname"])
            cur = conn.cursor()
            cur.execute(command)
            conn.commit()
            cur.close()

        except Exception as e:
            print(f"Error has occured:{e}")

        finally:
            if conn is not None:
                conn.close()



