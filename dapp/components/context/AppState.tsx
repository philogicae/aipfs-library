'use client'

import { type SetStateAction, createContext, useContext, useState } from 'react'

const AppContext = createContext({
	hasTyped: false,
	setHasTyped: (_value: SetStateAction<boolean>) => {},
})

export default function AppState({ children }: { children: React.ReactNode }) {
	const [hasTyped, setHasTyped] = useState(false)
	return (
		<div className="flex w-full h-full">
			<AppContext.Provider
				value={{
					hasTyped,
					setHasTyped,
				}}
			>
				{children}
			</AppContext.Provider>
		</div>
	)
}

export const useAppState = () => {
	const context = useContext(AppContext)
	if (!context) {
		throw new Error('useAppState was called outside AppState')
	}
	return context
}
