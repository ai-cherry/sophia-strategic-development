import React from 'react';
import { cn } from "@/lib/utils"

export const Skeleton = ({ className = '', ...props }) => {
  return (
    <div 
      className={`animate-pulse bg-gray-300 rounded ${className}`}
      {...props}
    />
  );
};
