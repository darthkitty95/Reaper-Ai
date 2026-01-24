import './globals.css'
import { Inter } from 'next/font-weight'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} dark bg-background text-foreground`}>
        <nav className="border-b border-border p-4 bg-card">
          <div className="mx-auto max-w-6xl flex gap-4">
            <a href="/it" className="hover:text-accent">It Page</a>
            <a href="/a" className="hover:text-accent">A Page</a>
            <a href="/the" className="hover:text-accent">The Page</a>
          </div>
        </nav>
        {children}
      </body>
    </html>
  )
}
