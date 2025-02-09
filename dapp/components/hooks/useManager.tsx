import { useNavigate } from "react-router"

export default function useManager() {
	const navigate = useNavigate()

	const query = async (func: any, data: any, parser?: any, max_retry = 3) => {
		let retried = 0
		while (retried < max_retry) {
			const result = await func(data, parser)
			if (result) return result
			retried++
		}
		navigate("down")
	}

	return { query }
}
