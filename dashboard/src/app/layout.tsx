import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import './globals.css'
import { SpotlightEffect } from '@/components/SpotlightEffect'
import { UnicornBackground } from '@/components/UnicornBackground'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'OPTIC-SHIELD Dashboard',
  description: 'Enterprise Wildlife Detection & Monitoring System',
  keywords: ['wildlife', 'detection', 'monitoring', 'AI', 'computer vision'],
  authors: [{ name: 'OPTIC-SHIELD Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#0f172a',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased text-white selection:bg-nexus-accent selection:text-white`}>
        {/* GLOBAL BACKDROP */}
        <div className="fixed inset-0 bg-[#050505] -z-50"></div>

        {/* 3D BACKGROUND (Unicorn Studio) */}
        {/* 3D BACKGROUND (Unicorn Studio) */}
        <UnicornBackground />

        {/* NOISE LAYER */}
        <div className="noise-overlay"></div>

        <SpotlightEffect />

        {children}
      </body>
    </html>
  )
}
