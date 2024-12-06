import json
import math
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

def create_shot_visualizations(shots_df, output_prefix="shot_analysis"):
    """
    创建射门数据的2D和3D可视化图
    """
    # Set style
    plt.style.use('seaborn')
    
    # 2D Shot Map with xG
    plt.figure(figsize=(15, 10))
    scatter = plt.scatter(
        shots_df['x'],
        shots_df['y'],
        c=shots_df['predicted_xg'],
        s=shots_df['is_goal']*200 + 50,  # Bigger points for goals
        cmap='viridis',
        alpha=0.6
    )
    
    # Add pitch markings
    plt.plot([120, 120], [36, 44], 'white', linewidth=2)  # Goal line
    plt.plot([102, 102], [18, 62], 'white', linewidth=2)  # Penalty area
    plt.plot([114, 114], [30, 50], 'white', linewidth=2)  # Six yard box
    
    plt.colorbar(scatter, label='Expected Goals (xG)')
    plt.title('2D Shot Map with Expected Goals', pad=20)
    plt.xlabel('Distance from Goal Line (yards)')
    plt.ylabel('Width Position (yards)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_prefix}_2d.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3D Visualization
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    scatter = ax.scatter(
        shots_df['x'],
        shots_df['y'],
        shots_df['predicted_xg'],
        c=shots_df['is_goal'],
        cmap='coolwarm',
        s=100,
        alpha=0.6
    )
    
    # Customize 3D plot
    ax.set_xlabel('Distance from Goal (yards)')
    ax.set_ylabel('Width Position (yards)')
    ax.set_zlabel('Expected Goals (xG)')
    ax.view_init(elev=20, azim=45)  # Set viewing angle
    
    plt.colorbar(scatter, label='Actual Goal (1) or Miss (0)')
    plt.title('3D Shot Analysis: Location and xG', pad=20)
    plt.savefig(f"{output_prefix}_3d.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create heatmap
    plt.figure(figsize=(15, 10))
    pitch_zones = shots_df.pivot_table(
        values='predicted_xg',
        index=pd.cut(shots_df['y'], bins=10),
        columns=pd.cut(shots_df['x'], bins=10),
        aggfunc='mean'
    )
    
    sns.heatmap(
        pitch_zones,
        cmap='YlOrRd',
        annot=True,
        fmt='.3f',
        cbar_kws={'label': 'Average xG'}
    )
    plt.title('Shot Location Heat Map (Average xG by Zone)', pad=20)
    plt.xlabel('Distance from Goal Line')
    plt.ylabel('Width Position')
    plt.savefig(f"{output_prefix}_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Additional analysis - Angle vs Distance plot
    plt.figure(figsize=(12, 8))
    plt.scatter(
        shots_df['distance_to_goal'],
        shots_df['shot_angle'],
        c=shots_df['predicted_xg'],
        s=shots_df['is_goal']*200 + 50,
        cmap='viridis',
        alpha=0.6
    )
    plt.colorbar(label='Expected Goals (xG)')
    plt.title('Shot Angle vs Distance Analysis', pad=20)
    plt.xlabel('Distance to Goal (yards)')
    plt.ylabel('Shot Angle (radians)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_prefix}_angle_distance.png", dpi=300, bbox_inches='tight')
    plt.close()

def export_shot_data(shots_df, output_file='shot_data.json'):
    """
    导出射门数据为JSON格式，用于可视化
    """
    viz_data = shots_df.apply(
        lambda row: {
            'x': float(row['x']),
            'y': float(row['y']),
            'distance': float(row['distance_to_goal']),
            'angle': float(row['shot_angle']),
            'goal': int(row['is_goal']),
            'predicted_xg': float(row['predicted_xg']) if 'predicted_xg' in row else None
        }, 
        axis=1
    ).tolist()

    with open(output_file, 'w') as f:
        json.dump(viz_data, f)
    
    print(f"Data exported to {output_file}")
    return viz_data

def calculate_shot_metrics(x, y):
    """
    计算射门的关键指标
    """
    try:
        x = float(x)
        y = float(y)
        
        GOAL_WIDTH = 8
        GOAL_CENTER_Y = 40
        GOAL_X = 120
        GOAL_Y1, GOAL_Y2 = 36, 44
        
        # Calculate direct distance to goal
        distance_to_goal = math.sqrt((GOAL_X-x)**2 + (GOAL_CENTER_Y-y)**2)
        
        # Calculate shot angle using the law of cosines
        d1 = math.sqrt((GOAL_X-x)**2 + (GOAL_Y1-y)**2)
        d2 = math.sqrt((GOAL_X-x)**2 + (GOAL_Y2-y)**2)
        
        cos_angle = (d1**2 + d2**2 - GOAL_WIDTH**2)/(2*d1*d2)
        shot_angle = math.acos(min(1, max(-1, cos_angle)))
        
        return {
            'x': x,
            'y': y,
            'distance_to_goal': distance_to_goal,
            'shot_angle': shot_angle
        }
        
    except Exception as e:
        print(f"Error in calculation: {str(e)}")
        return None

def process_shot_data(event):
    """
    从事件数据中提取射门信息
    """
    try:
        if event.get('type', {}).get('name') != 'Shot':
            return None
            
        location = event.get('location')
        if not location:
            return None
            
        metrics = calculate_shot_metrics(location[0], location[1])
        if not metrics:
            return None
            
        shot_outcome = event.get('shot', {}).get('outcome', {}).get('name')
        metrics['is_goal'] = 1 if shot_outcome == 'Goal' else 0
        
        return metrics
        
    except Exception as e:
        print(f"Error processing shot: {str(e)}")
        return None

def train_xg_model(shots_df):
    """
    训练xG模型并生成公式
    """
    features = ['x', 'y', 'distance_to_goal', 'shot_angle']
    
    X = shots_df[features]
    y = shots_df['is_goal']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression(random_state=42)
    model.fit(X_scaled, y)
    
    coefficients = model.coef_[0]
    intercept = model.intercept_[0]
    means = scaler.mean_
    scales = scaler.scale_
    
    formula = f"""
    xG Formula:
    
    1. Standardize variables:
        x_std = (x - {means[0]:.3f}) / {scales[0]:.3f}
        y_std = (y - {means[1]:.3f}) / {scales[1]:.3f}
        distance_std = (distance_to_goal - {means[2]:.3f}) / {scales[2]:.3f}
        angle_std = (shot_angle - {means[3]:.3f}) / {scales[3]:.3f}
    
    2. Calculate log odds:
        log_odds = {intercept:.3f} + 
                   {coefficients[0]:.3f} * x_std + 
                   {coefficients[1]:.3f} * y_std + 
                   {coefficients[2]:.3f} * distance_std + 
                   {coefficients[3]:.3f} * angle_std
    
    3. Convert to probability:
        xG = 1 / (1 + exp(-log_odds))
    
    Feature coefficients:
    x: {coefficients[0]:.3f}
    y: {coefficients[1]:.3f}
    distance_to_goal: {coefficients[2]:.3f}
    shot_angle: {coefficients[3]:.3f}
    """
    
    return model, scaler, formula

def process_files(folder_path):
    """
    处理所有事件文件
    """
    files = list(Path(folder_path).glob('*.json'))
    all_shots = []
    
    print(f"Processing {len(files)} files...")
    for file in tqdm(files):
        with open(file, 'r', encoding='utf-8') as f:
            match_data = json.load(f)
            
        for event in match_data:
            shot_data = process_shot_data(event)
            if shot_data:
                all_shots.append(shot_data)
    
    return pd.DataFrame(all_shots)

def plot_shot_map(shots_df, output_file='shot_map.png'):
    """
    生成射门分布图
    """
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(
        shots_df['x'],
        shots_df['y'],
        c=shots_df['predicted_xg'],
        s=100,
        cmap='YlOrRd',
        alpha=0.6
    )
    plt.colorbar(scatter, label='Expected Goals (xG)')
    plt.title('Shot Map with xG Values')
    plt.xlabel('Field Length (yards)')
    plt.ylabel('Field Width (yards)')
    plt.savefig(output_file)
    plt.close()

def main(data_path, output_file):
    """
    主函数
    """
    shots_df = process_files(data_path)
    if len(shots_df) == 0:
        raise ValueError("No shot data found")
    
    print(f"\nTotal shots: {len(shots_df)}")
    print(f"Goals: {shots_df['is_goal'].sum()}")
    print(f"Conversion rate: {shots_df['is_goal'].mean():.3f}")
    
    model, scaler, formula = train_xg_model(shots_df)
    
    # Add predicted xG values
    X = shots_df[['x', 'y', 'distance_to_goal', 'shot_angle']]
    X_scaled = scaler.transform(X)
    shots_df['predicted_xg'] = model.predict_proba(X_scaled)[:, 1]
    create_shot_visualizations(shots_df)
    # Export data for visualization
    export_shot_data(shots_df, 'shot_data.json')
    
    # Create visualizations
    plot_shot_map(shots_df)
    
    with open(output_file, 'w') as f:
        f.write(formula)
    
    return shots_df, model, scaler

if __name__ == "__main__":
    data_path = "../open-data/data/events"
    output_file = "xg_formula.txt"
    shots_df, model, scaler = main(data_path, output_file)