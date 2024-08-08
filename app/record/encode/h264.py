import subprocess


def encode(input_file, output_file):
    # ffmpegコマンドを作成
    command = [
        "ffmpeg",
        "-t",
        "10",
        "-i",
        input_file,  # 入力ファイル
        "-codec:v",
        "libx264",  # ビデオコーデック
        "-crf",
        "23",  # 画質
        "-preset",
        "medium",  # エンコード速度
        output_file,  # 出力ファイル
    ]

    print(" ".join(command))
    # コマンドを実行
    subprocess.run(command, check=True)
