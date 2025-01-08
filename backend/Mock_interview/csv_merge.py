import os
import pandas as pd

def merge_csv_files_sequentially(input_folder: str, output_file: str):
    """
    주어진 폴더의 모든 CSV 파일을 행 단위로 병합하고 저장합니다.
    각 파일은 이전 파일 뒤에 이어붙습니다.

    Args:
        input_folder (str): 병합할 CSV 파일이 있는 폴더 경로.
        output_file (str): 병합된 CSV 파일을 저장할 경로.
    """
    # CSV 파일 리스트
    csv_files = [file for file in os.listdir(input_folder) if file.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the folder.")
        return

    # 모든 CSV 파일 병합
    merged_data = pd.DataFrame()  # 빈 데이터프레임 생성
    for file in csv_files:
        file_path = os.path.join(input_folder, file)
        print(f"Reading {file_path}...")
        data = pd.read_csv(file_path)  # CSV 읽기
        merged_data = pd.concat([merged_data, data], ignore_index=True)  # 행 단위로 병합

    # 병합된 데이터를 저장
    merged_data.to_csv(output_file, index=False)
    print(f"All files merged and saved to {output_file}")

# 사용 예시
input_folder = "C:/dev/SKN03-Final_Project/csv_folder"  # CSV 파일들이 있는 폴더 경로
output_file = "C:/dev/SKN03-Final_Project/csv_folder/merged_python.csv"  # 병합된 결과를 저장할 파일 경로

merge_csv_files_sequentially(input_folder, output_file)
