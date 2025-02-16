export function extractToolContent(
	content: string,
	htmlTag: string
): { role: string; content: string }[] {
	const firstResults = content.trim().split(`<tool-${htmlTag}>`, 2)
	if (firstResults.length > 1) {
		const secondResults = firstResults[1].trim().split(`</tool-${htmlTag}>`, 2)
		return [
			{ role: 'agent', content: firstResults[0].trim() },
			{ role: htmlTag, content: secondResults[0].trim() },
			{ role: 'agent', content: secondResults[1].trim() },
		].filter((x) => x.content)
	}
	return [{ role: 'agent', content: firstResults[0] }]
}
