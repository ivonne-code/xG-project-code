"use client"

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ScatterChart, Scatter } from 'recharts';
import { useState } from 'react';

const XG2DPlots = () => {
 const [plotType, setPlotType] = useState('distance');

 // 使用实际训练好的模型计算 xG
 const calculateXG = (x: number, y: number) => {
   // Model parameters (data_cleaning/xg_formula.txt; 87,111 StatsBomb shots, 5-fold CV AUC 0.75)
   const means = [103.571, 39.761, 19.203, 0.443];  // [x, y, distance, angle]
   const scales = [8.802, 9.895, 8.753, 0.276];
   const coefficients = { x: -0.381, y: 0.007, distance: -1.125, shot_angle: 0.234 };
   const intercept = -2.422;
   // 1. Distance and shot angle
   const GOAL_WIDTH = 8;
   const GOAL_Y1 = 36;
   const GOAL_Y2 = 44;
   const distance = Math.sqrt((120-x)**2 + (40-y)**2);
   const d1 = Math.sqrt((120-x)**2 + (GOAL_Y1-y)**2);
   const d2 = Math.sqrt((120-x)**2 + (GOAL_Y2-y)**2);
   const cosAngle = (d1**2 + d2**2 - GOAL_WIDTH**2)/(2*d1*d2);
   const angle = Math.acos(Math.min(1, Math.max(-1, cosAngle)));
   // 2. Standardize
   const x_std = (x - means[0]) / scales[0];
   const y_std = (y - means[1]) / scales[1];
   const distance_std = (distance - means[2]) / scales[2];
   const angle_std = (angle - means[3]) / scales[3];
   // 3. Log odds
   const logOdds = intercept +
                   coefficients.x * x_std +
                   coefficients.y * y_std +
                   coefficients.distance * distance_std +
                   coefficients.shot_angle * angle_std;
   // 4. 转换为概率
   return 1 / (1 + Math.exp(-logOdds));
 };

 // 生成距离-xG数据
 const generateDistancePlotData = () => {
   const data = [];
   const centerY = 40; // 球门中心
   
   for (let x = 60; x <= 120; x += 1) {
     const distance = 120 - x;
     const xg = calculateXG(x, centerY);
     data.push({
       distance,
       xg: xg.toFixed(4),
     });
   }
   return data;
 };

 // 生成角度-xG数据
 const generateAnglePlotData = () => {
   const data = [];
   const x = 90; // 固定距离
   
   for (let y = 20; y <= 60; y += 1) {
     const angle = Math.atan2(Math.abs(y - 40), 30) * (180 / Math.PI);
     const xg = calculateXG(x, y);
     data.push({
       angle: angle.toFixed(1),
       xg: xg.toFixed(4),
     });
   }
   return data;
 };

 // 生成散点数据
 const generateScatterData = () => {
   const data = [];
   for (let i = 0; i < 50; i++) {
     const x = 60 + Math.random() * 60;
     const y = 20 + Math.random() * 40;
     data.push({
       x,
       y,
       xg: calculateXG(x, y),
     });
   }
   return data;
 };

 return (
   <Card className="w-full max-w-4xl">
     <CardHeader>
       <CardTitle>xG 数据分析</CardTitle>
       <Select value={plotType} onValueChange={setPlotType}>
         <SelectTrigger className="w-[180px]">
           <SelectValue placeholder="选择图表类型" />
         </SelectTrigger>
         <SelectContent>
           <SelectItem value="distance">距离-xG关系</SelectItem>
           <SelectItem value="angle">角度-xG关系</SelectItem>
           <SelectItem value="scatter">射门位置分布</SelectItem>
         </SelectContent>
       </Select>
     </CardHeader>
     <CardContent>
       <div className="w-full h-[400px] flex justify-center">
         {plotType === 'distance' && (
           <LineChart
             width={600}
             height={350}
             data={generateDistancePlotData()}
             margin={{ top: 20, right: 30, left: 60, bottom: 40 }}
           >
             <CartesianGrid strokeDasharray="3 3" />
             <XAxis 
               dataKey="distance"
               label={{ 
                 value: '与球门的距离 (米)', 
                 position: 'bottom',
                 offset: 20
               }}
             />
             <YAxis
               label={{ 
                 value: '期望进球率 (xG)', 
                 angle: -90, 
                 position: 'insideLeft',
                 offset: -40
               }}
             />
             <Tooltip 
               formatter={(value: any) => [Number(value).toFixed(4), '期望进球率']}
             />
             <Legend 
               verticalAlign="top"
               height={36}
             />
             <Line 
               type="monotone" 
               dataKey="xg" 
               stroke="#2563eb" 
               name="期望进球"
               dot={false}
             />
           </LineChart>
         )}

         {plotType === 'angle' && (
           <LineChart
             width={600}
             height={350}
             data={generateAnglePlotData()}
             margin={{ top: 20, right: 30, left: 60, bottom: 40 }}
           >
             <CartesianGrid strokeDasharray="3 3" />
             <XAxis 
               dataKey="angle"
               label={{ 
                 value: '射门角度 (度)', 
                 position: 'bottom',
                 offset: 20
               }}
             />
             <YAxis
               label={{ 
                 value: '期望进球率 (xG)', 
                 angle: -90, 
                 position: 'insideLeft',
                 offset: -40
               }}
             />
             <Tooltip 
               formatter={(value: any) => [Number(value).toFixed(4), '期望进球率']}
             />
             <Legend 
               verticalAlign="top"
               height={36}
             />
             <Line 
               type="monotone" 
               dataKey="xg" 
               stroke="#2563eb" 
               name="期望进球"
               dot={false}
             />
           </LineChart>
         )}

         {plotType === 'scatter' && (
           <ScatterChart
             width={600}
             height={350}
             margin={{ top: 20, right: 30, left: 60, bottom: 40 }}
           >
             <CartesianGrid strokeDasharray="3 3" />
             <XAxis 
               type="number" 
               dataKey="x" 
               name="X位置"
               label={{ 
                 value: 'X位置 (米)', 
                 position: 'bottom',
                 offset: 20
               }}
               domain={[60, 120]}
             />
             <YAxis 
               type="number" 
               dataKey="y" 
               name="Y位置"
               label={{ 
                 value: 'Y位置 (米)', 
                 angle: -90, 
                 position: 'insideLeft',
                 offset: -40
               }}
               domain={[20, 60]}
             />
             <Tooltip 
               cursor={{ strokeDasharray: '3 3' }}
               formatter={(value: any) => [Number(value).toFixed(4), '期望进球率']}
             />
             <Legend 
               verticalAlign="top"
               height={36}
             />
             <Scatter 
               name="射门位置" 
               data={generateScatterData()} 
               fill="#2563eb"
             />
           </ScatterChart>
         )}
       </div>
     </CardContent>
   </Card>
 );
};

export default XG2DPlots;