"use client"

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ScatterChart, Scatter } from 'recharts';
import { useState } from 'react';

const XG2DPlots = () => {
 const [plotType, setPlotType] = useState('distance');

 // 生成距离-xG数据
 const generateDistancePlotData = () => {
   const data = [];
   const centerY = 40; // 球门中心
   
   for (let x = 60; x <= 120; x += 1) {
     const distance = 120 - x;
     const xg = calculateXG(x, centerY);
     data.push({
       distance,
       xg: xg.toFixed(3),
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
       xg: xg.toFixed(3),
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

 // 计算 xG 值
 const calculateXG = (x: number, y: number) => {
   const GOAL_WIDTH = 8;
   const GOAL_Y1 = 36;
   const GOAL_Y2 = 44;
   
   // 计算到球门两端的距离
   const d1 = Math.sqrt((120-x)**2 + (GOAL_Y1-y)**2);
   const d2 = Math.sqrt((120-x)**2 + (GOAL_Y2-y)**2);
   
   // 计算射门角度
   const cosAngle = (d1**2 + d2**2 - GOAL_WIDTH**2)/(2*d1*d2);
   const angle = Math.acos(Math.min(1, Math.max(-1, cosAngle)));
   
   // 简单的 xG 模型
   const distance = Math.sqrt((120-x)**2 + (40-y)**2);
   return Math.exp(-distance/50) * Math.exp(-angle);
 };

 return (
   <Card className="w-full max-w-4xl">
     <CardHeader>
       <CardTitle>xG data analysis</CardTitle>
       <Select value={plotType} onValueChange={setPlotType}>
         <SelectTrigger className="w-[180px]">
           <SelectValue placeholder="选择图表类型" />
         </SelectTrigger>
         <SelectContent>
           <SelectItem value="distance">Distance-xG relation</SelectItem>
           <SelectItem value="angle">Angle-xG relation</SelectItem>
           <SelectItem value="scatter">Shot position distribution</SelectItem>
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
                 value: 'Distance between the Goal line (meter)', 
                 position: 'bottom',
                 offset: 20
               }}
             />
             <YAxis
               label={{ 
                 value: 'Rate of expected goals (xG)', 
                 angle: -90, 
                 position: 'insideLeft',
                 offset: -40
               }}
             />
             <Tooltip />
             <Legend 
               verticalAlign="top"
               height={36}
             />
             <Line 
               type="monotone" 
               dataKey="xg" 
               stroke="#2563eb" 
               name="expected goals"
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
                 value: 'angle (degree)', 
                 position: 'bottom',
                 offset: 20
               }}
             />
             <YAxis
               label={{ 
                 value: 'expected goals (xG)', 
                 angle: -90, 
                 position: 'insideLeft',
                 offset: -40
               }}
             />
             <Tooltip />
             <Legend 
               verticalAlign="top"
               height={36}
             />
             <Line 
               type="monotone" 
               dataKey="xg" 
               stroke="#2563eb" 
               name="expected goals"
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
               name="X position"
               label={{ 
                 value: 'X position (meter)', 
                 position: 'bottom',
                 offset: 20
               }}
               domain={[60, 120]}
             />
             <YAxis 
               type="number" 
               dataKey="y" 
               name="Y position"
               label={{ 
                 value: 'Y position (meter)', 
                 angle: -90, 
                 position: 'insideLeft',
                 offset: -40
               }}
               domain={[20, 60]}
             />
             <Tooltip cursor={{ strokeDasharray: '3 3' }} />
             <Legend 
               verticalAlign="top"
               height={36}
             />
             <Scatter 
               name="shot position" 
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