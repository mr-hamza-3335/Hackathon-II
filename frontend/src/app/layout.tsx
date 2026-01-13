/**
 * Root layout with providers and theme support.
 * PakAura - Premium Todo Application
 */

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/providers/ThemeProvider';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'PakAura - Organize Your Day with Clarity',
  description: 'A premium task management application designed to help you achieve focus and productivity.',
  keywords: ['todo', 'tasks', 'productivity', 'organization', 'task management'],
  authors: [{ name: 'PakAura Team' }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="min-h-screen w-full bg-mesh">
            {children}
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
