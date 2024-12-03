"use client"

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { 
  Select,
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';

const XGVisualization: React.FC = () => {
  const [viewMode, setViewMode] = useState('heatmap');
  
  // 球场尺寸常量
  const FIELD_WIDTH = 80;
  const FIELD_LENGTH = 120;
  const GOAL_WIDTH = 8;
  const GOAL_Y1 = 36;
  const GOAL_Y2 = 44;
  
  // 计算 xG
  const calculateXG = (x: number, y: number) => {
    // 示例系数 (之后替换为实际模型系数)
    const means = [60, 40, 0.5];
    const scales = [30, 20, 0.2];
    const coefficients = {
      x: 0.8,
      y: -0.3,
      shot_angle: 1.2
    };
    const intercept = -2.0;
    
    // 计算射门角度
    const d1 = Math.sqrt((FIELD_LENGTH-x)**2 + (GOAL_Y1-y)**2);
    const d2 = Math.sqrt((FIELD_LENGTH-x)**2 + (GOAL_Y2-y)**2);
    const cosAngle = (d1**2 + d2**2 - GOAL_WIDTH**2)/(2*d1*d2);
    const angle = Math.acos(Math.min(1, Math.max(-1, cosAngle)));
    
    // 标准化变量
    const x_std = (x - means[0]) / scales[0];
    const y_std = (y - means[1]) / scales[1];
    const angle_std = (angle - means[2]) / scales[2];
    
    // 计算对数几率
    const logOdds = intercept + 
                    coefficients.x * x_std +
                    coefficients.y * y_std +
                    coefficients.shot_angle * angle_std;
    
    // 转换为概率
    return 1 / (1 + Math.exp(-logOdds));
  };
  
  // 生成热图数据点
  const generateHeatmapPoints = () => {
    const points = [];
    for (let x = FIELD_LENGTH/2; x <= FIELD_LENGTH; x += 2) {
      for (let y = 0; y <= FIELD_WIDTH; y += 2) {
        const xg = calculateXG(x, y);
        points.push({ x, y, xg });
      }
    }
    return points;
  };
  
  // 颜色比例尺函数
  const getColor = (value: number) => {
    const r = Math.floor(255 * (1 - value));
    const g = Math.floor(255 * (1 - value));
    const b = 255;
    const alpha = value * 0.7;
    return `rgba(${r},${g},${b},${alpha})`;
  };

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <CardTitle>Expected Goals (xG) Model Visualization</CardTitle>
        <Select onValueChange={setViewMode} defaultValue="heatmap">
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select view mode" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="heatmap">Heatmap View</SelectItem>
            <SelectItem value="contour">Contour map</SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent>
        <div className="relative w-full" style={{ paddingBottom: '66.67%' }}>
          <svg
            viewBox={`0 0 ${FIELD_LENGTH} ${FIELD_WIDTH}`}
            className="absolute inset-0 w-full h-full"
          >
            {/* 球场背景 */}
            <rect width={FIELD_LENGTH} height={FIELD_WIDTH} fill="#638c5c" />
            
            {/* 禁区 */}
            <rect 
              x={FIELD_LENGTH - 18} 
              y={(FIELD_WIDTH - 44) / 2} 
              width={18} 
              height={44} 
              fill="none" 
              stroke="white" 
              strokeWidth={0.5}
            />
            
            {/* 球门 */}
            <rect
              x={FIELD_LENGTH}
              y={GOAL_Y1}
              width={1}
              height={GOAL_WIDTH}
              fill="white"
            />
            
            {/* 热图点 */}
            {viewMode === 'heatmap' && generateHeatmapPoints().map((point, i) => (
              <circle
                key={i}
                cx={point.x}
                cy={point.y}
                r={1.5}
                fill={getColor(point.xg)}
              />
            ))}
            
            {/* 中线 */}
            <line
              x1={FIELD_LENGTH/2}
              y1={0}
              x2={FIELD_LENGTH/2}
              y2={FIELD_WIDTH}
              stroke="white"
              strokeWidth={0.5}
            />
          </svg>
        </div>
        
        {/* 图例 */}
        <div className="mt-4 flex items-center justify-center">
          <div className="flex items-center space-x-2">
            <span className="text-sm">low goal probability</span>
            <div className="w-32 h-4 bg-gradient-to-r from-white to-blue-500" />
            <span className="text-sm">High goal probability</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default XGVisualization;