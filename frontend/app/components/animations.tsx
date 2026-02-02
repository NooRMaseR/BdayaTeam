/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { motion, TargetAndTransition, Transition, VariantLabels } from "motion/react";
import React from "react";

interface AnimationProps {
  children: React.ReactNode;
  component?: React.ComponentType<any> | string;
  className?: string;
  initial?: TargetAndTransition | VariantLabels;
  animate?: TargetAndTransition | VariantLabels;
  transition?: Transition<any>;
}

function Compo(component: AnimationProps['component'] = 'div') {
  return motion.create(component);
}

export default function NormalAnimation({ children, component = "div", className, initial = { opacity: 0, y: 30 }, animate = { opacity: 1, y: 0 }, transition = { ease: 'easeInOut' } }: AnimationProps) {
  const Com = Compo(component);
  return (
    <Com
      className={className}
      initial={initial}
      animate={animate}
      transition={transition}
    >
      {children}
    </Com>
  )
}
