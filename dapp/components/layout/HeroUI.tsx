'use client'

import { HeroUIProvider } from '@heroui/react'

export function HeroUI({ children }: { children: React.ReactNode }) {
	return <HeroUIProvider>{children}</HeroUIProvider>
}
