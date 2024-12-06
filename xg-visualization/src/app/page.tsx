"use client"

import { createElement, type ReactNode } from "react";
import Image from "next/image";
import XGVisualization from '@/components/visualization/XGVisualization';
import XG2DPlots from '@/components/visualization/XG2DPlots';

interface FooterLinkProps {
  href: string;
  icon: string;
  text: string;
}

const FooterLink = ({ href, icon, text }: FooterLinkProps): ReactNode => 
  createElement('a', {
    href,
    target: "_blank",
    rel: "noopener noreferrer",
    className: "flex items-center gap-2 hover:underline"
  }, [
    createElement(Image, {
      src: icon,
      alt: `${text} icon`,
      width: 16,
      height: 16,
      priority: true,
      key: 'image'
    }),
    text
  ]);

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen p-8">
      <main className="flex-1">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-center mb-8">
          Visualization of expected goals (xG) in soccer
          </h1>
          <XGVisualization />
          <div className="mt-8">
            <XG2DPlots />
          </div>
        </div>
      </main>

      <footer className="flex justify-center gap-6 mt-8">
        <FooterLink 
          href="https://nextjs.org/learn"
          icon="/file.svg"
          text="Learn"
        />
        <FooterLink 
          href="https://vercel.com/templates"
          icon="/window.svg"
          text="Examples"
        />
        <FooterLink 
          href="https://nextjs.org"
          icon="/globe.svg"
          text="Go to nextjs.org →"
        />
      </footer>
    </div>
  );
}