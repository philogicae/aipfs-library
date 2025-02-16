'use client'

import { OnchainKitProvider } from '@coinbase/onchainkit'
import { baseSepolia } from 'viem/chains'

export function OnchainKit({ children }: { children: React.ReactNode }) {
	return (
		<OnchainKitProvider
			apiKey={process.env.NEXT_PUBLIC_ONCHAINKIT_API_KEY}
			chain={baseSepolia}
			config={{
				appearance: { mode: 'dark', theme: 'default' },
			}}
		>
			{children}
		</OnchainKitProvider>
	)
}
