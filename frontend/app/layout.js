import "./globals.css";

export const metadata = {
  title: "PRIMO Audit Dashboard",
  description: "Clinical Data Management Quality Dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex flex-col">
          <header className="bg-primo-900 text-white px-6 py-4 shadow">
            <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-3">
              <div>
                <div className="text-lg font-bold tracking-wide">PRIMO</div>
                <div className="text-xs text-blue-200">Mpox Study &mdash; Audit Dashboard</div>
              </div>
              <nav className="flex gap-4 text-sm">
                <a href="/" className="hover:text-blue-200">
                  Clinical Dashboard
                </a>
                <a href="/review" className="hover:text-blue-200">
                  Participant Review
                </a>
                <a href="/daily-missing" className="hover:text-blue-200">
                  Daily Missing Visits
                </a>
              </nav>
            </div>
          </header>

          <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">{children}</main>

          <footer className="text-center text-xs text-gray-400 py-4">
            PRIMO Mpox Study | Clinical Data Management Team
          </footer>
        </div>
      </body>
    </html>
  );
}
