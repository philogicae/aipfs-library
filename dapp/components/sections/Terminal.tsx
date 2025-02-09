import { type RefObject, useEffect, useMemo, useRef, useState } from 'react'
import { TerminalFrame } from '@components/elements/TerminalFrame'
import Background from '@components/layout/Background'
import { useAppState } from '@components/context/AppState'
import useAgent from '@components/hooks/useAgent'
import Message from '@components/elements/Message'

const adjustHeight = (element: RefObject<HTMLTextAreaElement>) => {
	const el = element.current
	if (el) {
		el.style.height = 'auto'
		el.style.height = `${el.scrollHeight}px`
	}
}

export default function Terminal() {
	const { hasTyped, setHasTyped, isLoading, profile, history, setHistory } =
		useAppState();
	const messagesContainerRef = useRef<HTMLDivElement>(null)
	const textareaRef = useRef<HTMLTextAreaElement>(null)
	const [value, setValue] = useState('')
	const chat_id = useMemo(() => profile.chat_ids.at(-1) as string, [profile])
	const callAgent = useAgent()

	const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		!isLoading && setValue(e.target.value)
	}

	const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
		!hasTyped && setHasTyped(true)
		if (event.key === 'Enter') {
			event.preventDefault()
			const message = value.trim()
			if (message) {
				setValue("");
				const new_history = {
					...history,
					[chat_id]: [...history[chat_id], { role: "you", content: message }],
				}
				setHistory(new_history)
				callAgent(message, new_history);
			}
		}
	}

	useEffect(() => {
		if (messagesContainerRef.current) {
			messagesContainerRef.current.scrollTop =
				messagesContainerRef.current.scrollHeight
			adjustHeight(textareaRef)
		}
	}, [history, value])

	return (
		<TerminalFrame subTitle="terminal">
			<Background />
			<div
				ref={messagesContainerRef}
				className="flex flex-col w-full h-full items-start justify-start p-3 sm:py-4 sm:px-6 gap-3 text-sm overflow-y-auto scrollbar-hide z-40"
			>
				{history[profile.chat_ids.at(-1) as string].map((msg, index) => (
					<Message key={`msg-${index}`} msg={msg} />
				))}
				{isLoading && (
					<div>
						<Message
							msg={{
								role: "agent",
								content: (
									<div className="animate-pulse">
										{"*thinking...*"}
									</div>
								),
							}}
						/>
					</div>
				)}
			</div>
			<div className="flex flex-row w-full items-start halo-text text-md sm:text-lg bg-gray-900 p-2 pt-1 z-50">
				<span className="text-xl sm:text-2xl pr-2 pb-0.5">{">"}</span>
				<textarea
					ref={textareaRef}
					id="terminal-input"
					inputMode="text"
					value={value}
					onChange={handleInputChange}
					onKeyDown={handleKeyDown}
					className="outline-none bg-transparent w-full pt-0.5 resize-none min-h-[24px] overflow-hidden"
					autoFocus={true}
					autoComplete="off"
					placeholder="chat with the agent"
					rows={1}
				/>
			</div>
		</TerminalFrame>
	);
}
