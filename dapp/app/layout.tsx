import type { Metadata, Viewport } from 'next'
import '@app/globals.css'
import { HeroUI } from '@components/layout/HeroUI'

const SITE_NAME = 'aipfs-library'
const SITE_DESCRIPTION =
	'Decentralized media library managed by AI agents indexing torrents and curated by the community'
const SITE_URL = 'https://aipfs.on-fleek.app'

export const metadata: Metadata = {
	applicationName: SITE_NAME,
	title: SITE_NAME,
	metadataBase: new URL(SITE_URL),
	description: SITE_DESCRIPTION,
	manifest: '/manifest.json',
	appLinks: {
		web: {
			url: SITE_URL,
			should_fallback: true,
		},
	},
	appleWebApp: {
		title: SITE_NAME,
		capable: true,
		statusBarStyle: 'black-translucent',
	},
}

/* icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  }, */

export const viewport: Viewport = {
	themeColor: 'black',
	colorScheme: 'dark',
	width: 'device-width',
	initialScale: 1,
}

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode
}>) {
	return (
		<html lang="en" className="dark">
			<body>
				<HeroUI>{children}</HeroUI>
			</body>
		</html>
	)
}
