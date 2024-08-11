import shlex
import subprocess


def encode(input_file, output_file):
    # ffmpegコマンドを作成
    command = [
        "cat",
        shlex.quote(input_file),
        "|",
        "python3",
        shlex.quote("/app/record/encode/pmt.py"),
        "|",
        "ffmpeg",
        "-y",
        "-hwaccel",
        "vaapi",
        "-hwaccel_device",
        "/dev/dri/renderD128",
        "-hwaccel_output_format",
        "vaapi",
        "-analyzeduration",
        "10M",
        "-probesize",
        "30M",
        "-fflags",
        "+discardcorrupt",
        "-i",
        "-",  # 入力ファイル
        "-c:v",
        "hevc_vaapi",
        "-tag:v",
        "hvc1",
        "-vf",
        "deinterlace_vaapi",
        "-b:v",
        "1M",
        "-map",
        "0:v",
        "-c:a",
        "aac",
        "-ab",
        "128k",
        "-map",
        "0:a:0",
        # "-t",
        # "10",
        shlex.quote(output_file),  # 出力ファイル
    ]

    print(" ".join(command))
    # コマンドを実行
    subprocess.run(" ".join(command), check=True, shell=True)
