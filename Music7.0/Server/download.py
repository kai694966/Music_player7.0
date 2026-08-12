import subprocess
import os
import re
import glob
import psycopg2
import shutil
import time
import dbname
import requests
from datetime import datetime
import xml.etree.ElementTree as ET


node_path = "C:\Program Files\nodejs\node.exe"

class download:
    def __init__(self,output_base,txt_path):
        self.txt_path = txt_path
        self.output_base = output_base
        if not os.path.exists(self.txt_path):
            print(f"File not found:{self.txt_path}")
            print(1/0)

        self.start_download(output_base)

    def start_download(self,path):
        self.download_orig = input("download best quality t/f\n>>")
        if self.download_orig == "t":
            self.download_orig = True
        else:
            self.download_orig = False

        self.download_p480 = input("download 480p t/f\n>>")
        if self.download_p480 == "t":
            self.download_p480 = True
        else:
            self.download_p480 = False

        self.download_audio = input("download audio t/f\n>>")
        if self.download_audio == "t":
            self.download_audio = True
        else:
            self.download_audio = False

        check = input("check if there is NO downloading file\n>>")

        check = input(f"check if DB is correct\n[{dbname.CONFIG['dbname']}]\n>>")

        check = input("check if disk was connected\n>>")

        self.read_urls()
        length = len(self.urls)
        i = 1
        for url in self.urls:
            print(f"[{i}/{length}]",end="")

            if url:
                self.download_urls(url,i,length)
                time.sleep(5)

            i += 1

    def read_urls(self):
        with open(self.txt_path,"r",encoding="utf-8") as f:
            self.urls = [line.strip() for line in f if line.strip()]
            if not self.urls:
                print("NO url found")
                print(1/0)

    def download_urls(self,url,i,length):

        command = (
            f'C:\\yt-dlp\\yt-dlp.exe --rm-cache-dir --cookies-from-browser firefox '
            f'--js-runtimes node --get-filename -o "%(title)s" {url}'
        )

        result = subprocess.run(command,
            capture_output=True,
            text=False,
            shell=True
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode("cp932",errors="replace")
            print(f"\n\nyt-dlp Error:\n{error_msg}\n\n")
            return

        raw_title_bytes = result.stdout.strip()
        raw_title = raw_title_bytes.decode("cp932",errors="replace").replace("?","？")
        clean_title = re.sub(r'[\\/:*?"<>|]', "", raw_title).replace("＊","")

        

        print(f"\n[開始] {clean_title}")

        command = (
            f'C:\\yt-dlp\\yt-dlp.exe --rm-cache-dir --cookies-from-browser firefox '
            f'--js-runtimes node --quiet --no-warnings '
            f'-f "bestvideo+bestaudio/best" --merge-output-format mp4 '
            f'-o "temp_%(id)s.%(ext)s" {url}'
        )

        subprocess.run(command,shell=True)

        paths = {
            "orig": os.path.join(self.output_base, "original"),
            "p480": os.path.join(self.output_base, "compressed_480p"),
            "audio": os.path.join(self.output_base, "audio_only")
        }

        for p in paths.values():
            os.makedirs(p,exist_ok=True)

        found_files = glob.glob(f"temp_*")
        if not found_files:
            print(f"ファイルが見つかりませんでした:(")
            return
        
        downloaded_file = found_files[0]
        temp_ext = os.path.splitext(downloaded_file)[1]

        orig_filename = f"{clean_title}{temp_ext}"
        p480_filename = f"{clean_title}.mp4"
        audio_filename = f"{clean_title}.m4a"

        final_file_paths = {
            "orig": os.path.join(paths["orig"], orig_filename),
            "p480": os.path.join(paths["p480"], p480_filename),
            "audio": os.path.join(paths["audio"], audio_filename)
        }


        if self.download_p480:
            subprocess.run([
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "info",
                "-stats",
                "-i",
                downloaded_file,
                "-vf",
                "scale=-2:480",
                "-c:v",
                "libx264",
                "-crf",
                "28",
                "-preset",
                "faster",
                "-c:a",
                "aac",
                "-b:a",
                "320k",
                os.path.join(paths["p480"],f"{clean_title}.mp4")
            ])
        else:
            final_file_paths["p480"] = None
        
        if self.download_audio:
            subprocess.run([
                "ffmpeg", 
                "-y", 
                "-hide_banner",
                "-loglevel",
                "info",
                "-stats",
                "-i", 
                downloaded_file, 
                "-vn", 
                "-c:a",
                "aac",
                "-b:a",
                "320k",
                os.path.join(paths["audio"], f"{clean_title}.m4a")
            ])
        else:
            final_file_paths["audio"] = None


        if self.download_orig:
            shutil.move(downloaded_file,final_file_paths["orig"])
        else:
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
            final_file_paths["orig"] = None

        self.register_to_db(url,clean_title,final_file_paths)

        print(f"\n\n###################################################################################################\n{i}/{length} [完了] {clean_title}\n###################################################################################################\n\n")

    def get_metadata(self,id):
        if "sm" in id or "nm" in id:

            url = f"https://nicovideo.jp/api/getthumbinfo/{id}"
            response = requests.get(url)
            response.raise_for_status()


            root = ET.fromstring(response.text)
            thumb = root.find("thumb")

            return {
                "title":thumb.findtext("title"),
                "channel":thumb.findtext("user_nickname"),
                "published":str(thumb.findtext("first_retrieve"))[0]+str(thumb.findtext("first_retrieve"))[1]+str(thumb.findtext("first_retrieve"))[2]+str(thumb.findtext("first_retrieve"))[3]+str(thumb.findtext("first_retrieve"))[5]+str(thumb.findtext("first_retrieve"))[6]+str(thumb.findtext("first_retrieve"))[8]+str(thumb.findtext("first_retrieve"))[9]
            }

        
        else:
            key = os.environ.get("YoutubeAPI")

            url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={id}&key={key}"

            result = requests.get(url)
            data = result.json()

            print(data)

            title = data["items"][0]["snippet"]["title"]
            channel = data["items"][0]["snippet"]["channelTitle"]
            published = data["items"][0]["snippet"]["publishedAt"]
            return {"title":title,"channel":channel,"published":datetime.fromisoformat(published.replace("Z","+00:00")).strftime("%Y%m%d")}



    def get_duration(self,path):
        try:
            cmd = [
                "ffprobe",
                "-v","error",
                "-show_entries","format=duration",
                "-of","default=noprint_wrappers=1:nokey=1",
                path
            ]
            result = subprocess.run(cmd,capture_output=True,text=True,check=True)
            duration = float(result.stdout.strip())
            return int(duration*1000)

        except Exception as e:
            print(f"Error has occured:{e}")
            return 0

    def get_lufs(self,path):
        try:
            cmd = [
                "ffmpeg",
                "-i",path,
                "-filter_complex","ebur128=framelog=verbose",
                "-f","null","-"
            ]

            print(
                cmd,
                subprocess.PIPE,subprocess.PIPE)

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            stderr = result.stderr.decode("utf-8",errors="replace")
            print(result.returncode,stderr,sep="\n")

            matches = re.findall(
                r"I:\s*(-?\d+(?:\.\d+)?)\s*LUFS",
                stderr
            )

            return float(matches[-1])
            
        except Exception as e:
            print(f"Error has occured:{e}")
            return 0


    def register_to_db(self, url, clean_title, file_paths):

        duration_path = (
            file_paths["audio"]
            or file_paths["p480"]
            or file_paths["orig"]
        )

        if duration_path and os.path.exists(duration_path):
            duration = self.get_duration(duration_path)
            lufs = self.get_lufs(duration_path)
        else:
            duration = 0
            lufs = None

        print(f"############ duration:{duration},lufs:{lufs}")

        # -------------------------
        # DBに接続
        # -------------------------


        if "youtube" in url:
            id = url[32:]
        elif "nicovideo" in url:
            id = url[31:]


        data = self.get_metadata(id)
        print(url,url[32:],data)

        conn = dbname.connect_db(dbname.CONFIG["dbname"])

        try:
            cur = conn.cursor()

            registered = time.strftime("%Y%m%d")

            source = [url]

            command = """
                INSERT INTO tracks (
                    path_original,
                    path_480p,
                    path_audio,
                    full_name,
                    registered,
                    published,
                    volume_offset,
                    duration,
                    source,
                    cover
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id;
            """

            values = (
                file_paths["orig"],
                file_paths["p480"],
                file_paths["audio"],
                data["title"],
                registered,
                data["published"],
                lufs,
                duration,
                source,
                [data["channel"]]
            )

            print(values,sep=",\n")

            cur.execute(command, values)

            track_id = cur.fetchone()[0]

            # -------------------------
            # sourcesにも登録
            # -------------------------

            command = """
                INSERT INTO sources (
                    track_id,
                    url
                )
                VALUES (
                    %s,
                    %s
                );
            """

            cur.execute(command, (track_id, url))

            # -------------------------
            # 確定
            # -------------------------

            conn.commit()

            print(f"DB registered: id={track_id}")

        except Exception as e:
            conn.rollback()
            print(f"DB registration error: {e}")

        finally:
            cur.close()
            conn.close()