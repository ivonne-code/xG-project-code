import json
import math
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from tqdm import tqdm

def load_json_safely(file_path):
    """
    安全地加载JSON文件
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def extract_shot_data(event):
    """
    从事件中提取射门数据
    """
    try:
        # 查找射门者位置（在freeze_frame中actor=true的球员）
        shot_location = None
        for player in event.get('freeze_frame', []):
            if player.get('actor', False):
                shot_location = player.get('location')
                break
        
        if not shot_location:
            return None
            
        x, y = shot_location
        
        # 计算基本特征
        shot_features = calculate_shot_features(x, y)
        if shot_features is None:
            return None
            
        # 添加事件ID
        shot_features['event_uuid'] = event.get('event_uuid', '')
        
        return shot_features
        
    except Exception as e:
        print(f"Error extracting shot data: {str(e)}")
        return None

def calculate_shot_features(x, y):
    """
    计算射门的关键特征：
    - x, y: 射门位置坐标
    - shot_angle: 射门角度
    """
    try:
        x = float(x)
        y = float(y)
        
        # 计算射门角度 (使用余弦定理)
        GOAL_WIDTH = 8
        goal_y1, goal_y2 = 36, 44  # 球门柱的y坐标
        
        # 计算到两个球门柱的距离
        d1 = math.sqrt((120-x)**2 + (goal_y1-y)**2)
        d2 = math.sqrt((120-x)**2 + (goal_y2-y)**2)
        
        # 使用余弦定理计算角度
        cos_angle = (d1**2 + d2**2 - GOAL_WIDTH**2)/(2*d1*d2)
        angle = math.acos(min(1, max(-1, cos_angle)))
        
        return {
            'x': x,
            'y': y,
            'shot_angle': angle
        }
        
    except Exception as e:
        print(f"Error calculating features for coordinates ({x}, {y}): {str(e)}")
        return None

def train_xg_model(shots_df):
    """
    训练xG模型并返回系数
    """
    print("\nAvailable columns for training:", shots_df.columns.tolist())
    
    # 只使用x, y和角度特征
    required_columns = ['x', 'y', 'shot_angle']
    
    # 准备特征
    X = shots_df[required_columns]
    
    # 检查是否有无效值
    if X.isna().any().any():
        print("Warning: Found NaN values in features. Removing rows with NaN...")
        X = X.dropna()
    
    # 使用示例目标变量（这里应该替换为实际的进球数据）
    y = np.random.binomial(n=1, p=0.1, size=len(X))
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 训练模型
    model = LogisticRegression(random_state=42)
    model.fit(X_scaled, y)
    
    # 获取每个特征的系数
    feature_coefficients = dict(zip(required_columns, model.coef_[0]))
    
    return model, scaler, feature_coefficients

def get_xg_formula(model, scaler, feature_coefficients):
    """
    生成可解释的xG计算公式
    """
    intercept = model.intercept_[0]
    means = scaler.mean_
    scales = scaler.scale_
    
    formula = f"""
    xG计算公式(xG calculated function):
    
    1. 标准化变量(standard variable):
        x_std = (x - {means[0]:.3f}) / {scales[0]:.3f}
        y_std = (y - {means[1]:.3f}) / {scales[1]:.3f}
        shot_angle_std = (shot_angle - {means[2]:.3f}) / {scales[2]:.3f}
    
    2. 计算对数几率 (log odds):
        log_odds = {intercept:.3f} 
                   + {feature_coefficients['x']:.3f} * x_std 
                   + {feature_coefficients['y']:.3f} * y_std 
                   + {feature_coefficients['shot_angle']:.3f} * shot_angle_std
    
    3. 转换为概率 (xG)(transfer to probability):
        xG = 1 / (1 + e^(-log_odds))
    """
    
    return formula

def process_all_json_files(folder_path):
    """
    处理文件夹中的所有JSON文件
    """
    folder = Path(folder_path)
    json_files = list(folder.glob('*.json'))
    all_shots_data = []
    
    print(f"Processing {len(json_files)} files...")
    for json_file in tqdm(json_files):
        try:
            match_data = load_json_safely(json_file)
            if match_data is None:
                continue
                
            # 打印文件的键以了解结构
            if len(all_shots_data) == 0:
                print("\nFile structure keys:", match_data[0].keys() if match_data else "No data")
            
            # 遍历每个事件
            for event in match_data:
                if isinstance(event, dict):
                    shot_data = extract_shot_data(event)
                    if shot_data is not None:
                        all_shots_data.append(shot_data)
        
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    if not all_shots_data:
        raise ValueError("No valid shot data found in any of the files")
        
    df = pd.DataFrame(all_shots_data)
    print(f"\nFound {len(df)} valid shots")
    print("\nDataFrame columns:", df.columns.tolist())
    print("\nFirst few rows:")
    print(df.head())
    
    return df

def main(folder_path,output_file):
    """
    主函数：处理数据并生成xG公式
    """
    try:
        # 处理所有文件
        shots_df = process_all_json_files(folder_path)
        
        # 训练模型并获取系数
        model, scaler, feature_coefficients = train_xg_model(shots_df)
        
        # 生成公式
        formula = get_xg_formula(model, scaler, feature_coefficients)
        
        # 打印统计信息
        print("\n数据统计(data statistic):")
        print(f"总射门数(total scored count): {len(shots_df)}")
        print("\n特征重要性(PFI):")
        for feature, coef in feature_coefficients.items():
            print(f"{feature}: {abs(coef):.3f}")
        
        print("\nxG公式(xg function):")
        print(formula)

        with open(output_file, 'w') as f:
            f.write("Data Statistics:\n")
            f.write(f"Total shots: {len(shots_df)}\n\n")
            f.write("Feature Importance:\n")
            for feature, coef in feature_coefficients.items():
                f.write(f"{feature}: {abs(coef):.3f}\n")
            f.write("\nxG Formula:\n")
            f.write(formula)

        return shots_df, model, scaler, feature_coefficients
        
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        raise

# 使用示例
if __name__ == "__main__":
    folder_path = "/Users/yifengluo/Desktop/xG-project-code/open-data/data/three-sixty"
    output_file = "xg_model_outputs.txt"
    shots_df, model, scaler, coefficients = main(folder_path,output_file)
