import os

def extract_filenames_from_directory(directory):
    filenames = []
    # 디렉토리 내의 모든 파일에 대해 루프를 돌면서 파일명 추출
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            print(filename.split(".")[0])
    return filenames

# 예제 디렉토리 경로
directory = "xlsx"

# 디렉토리에서 파일명 추출
filenames = extract_filenames_from_directory(directory)
