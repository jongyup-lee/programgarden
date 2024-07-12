import os

# 파일을 생성할 디렉토리 경로
directory = 'files'
# 파일 이름
filename = 'test1.txt'
# 파일 경로
file_path = os.path.join(directory, filename)

# 파일 생성
with open(file_path, 'w') as f:
    f.write("This is a test file.")

print(f"{filename} 파일이 생성되었습니다.")

# 파일 삭제
os.remove(file_path)

print(f"{filename} 파일이 삭제되었습니다.")
