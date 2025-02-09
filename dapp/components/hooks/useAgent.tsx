import { useAppState } from '@components/context/AppState'
import { useCallback } from 'react'
import { useNavigate } from 'react-router'
import useManager from '@components/hooks/useManager'

const call = async (
	data: any,
	parser = (output: any) => output,
): Promise<any> => {
	try {
		const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/chat`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(data),
		})
		if (res.ok) {
			const result = await res.json()
			try {
				return parser(result)
			} catch {
				console.error('Response invalid:', JSON.stringify(result))
			}
		} else console.error('Request failed:', res.status)
	} catch (error) {
		console.error('Request error:', error)
	}
}

export default function useAgent() {
	const navigate = useNavigate()
	const { setIsLoading, profile, setHistory } = useAppState()
	const { query } = useManager()

	return useCallback(
		async (
			message: string,
			history: Record<
				string,
				{
					role: string
					content: string
				}[]
			>,
		): Promise<undefined> => {
			setIsLoading(true)
			const chat_id = profile.chat_ids.at(-1) as string
			const response = await query({
				func: call,
				data: {
					user_id: profile.user_id,
					chat_id,
					message,
				},
				max_retries: 1,
			})
			if (response) {
				setHistory({
					...history,
					[chat_id]: [
						...history[chat_id],
						{ role: 'agent', content: response.message },
					],
				})
			}
			setIsLoading(false)
		},
		[navigate, profile],
	)
}
