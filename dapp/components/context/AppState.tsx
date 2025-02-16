'use client'

import { type SetStateAction, createContext, useContext, useState } from 'react'

const defaults = {
	isLoading: false,
	profile: { user_id: 'tester', chat_ids: ['1'] } as {
		user_id: string
		chat_ids: string[]
	},
	history: {
		'1': [{ role: 'agent', content: '<Say hi to me!>' }],
	} as Record<string, { role: string; content: string }[]>,
	setIsLoading: (_value: SetStateAction<boolean>) => {},
	setProfile: (
		_value: SetStateAction<{ user_id: string; chat_ids: string[] }>
	) => {},
	setHistory: (
		_value: SetStateAction<Record<string, { role: string; content: string }[]>>
	) => {},
}

const AppContext = createContext(defaults)

export default function AppState({ children }: { children: React.ReactNode }) {
	const [isLoading, setIsLoading] = useState(defaults.isLoading)
	const [profile, setProfile] = useState(defaults.profile)
	const [history, setHistory] = useState(defaults.history)
	return (
		<div className='flex w-full h-full'>
			<AppContext.Provider
				value={{
					isLoading,
					setIsLoading,
					profile,
					setProfile,
					history,
					setHistory,
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
