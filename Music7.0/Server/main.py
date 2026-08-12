import psycopg2
import os
import init_db
import dbname
import download
import download_url_writer
import enter_data






db = init_db.InitDB()

txtfile1 = "C:\TailScaleServer\Technology\Music7\Music7.0\Server\download_url.txt"
txtfile2 = "Z:\Technology\Music7\Music7.0\Server\download_url.txt"
txtfile = ""

if os.path.exists(txtfile1):
    txtfile = txtfile1
else:
    txtfile = txtfile2

if __name__ == "__main__":
    mode = input("\n\n\
1:Download audio/video\n\
2:Watch clipboard\n\
3:Enter metadata\n\
\n>>")

    mode = int(mode)
    if mode == 1:
        output_base = input(r"output_base\n[C:\Users\kaito\Documents\Music\v7_Storage]\n>>") or r"C:\Users\kaito\Documents\Music\v7_Storage"
        while not os.path.exists(output_base):
            print("no folder found")
            output_base = input("output_base\n>>")
        download.download(output_base,txtfile)
    elif mode == 2:
        download_url_writer.watch_clipboard(txtfile)
    elif mode == 3:
        enter_data.enter()