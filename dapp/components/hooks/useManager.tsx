import { useNavigate } from "react-router"

export default function useManager() {
	const navigate = useNavigate()

	const query = async ({func, data, parser, max_retries = 2}: {func: any, data: any, parser?: any, max_retries?: number}) => {
		let retried = 0
		while (retried < max_retries) {
			const result = await func(data, parser)
			if (result) return result
			retried++
		}
		navigate('down')
	}

	return { query }
}
