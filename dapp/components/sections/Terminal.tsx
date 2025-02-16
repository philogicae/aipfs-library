import { useAppState } from '@components/context/AppState'
import Message from '@components/elements/Message'
import { TerminalFrame } from '@components/elements/TerminalFrame'
import useAgent from '@components/hooks/useAgent'
import Background from '@components/layout/Background'
import { extractToolContent } from '@components/utils/parser'
import { type RefObject, useEffect, useMemo, useRef, useState } from 'react'
import useDetectKeyboardOpen from 'use-detect-keyboard-open'

const adjustHeight = (element: RefObject<HTMLTextAreaElement>) => {
	const el = element.current
	if (el) {
		el.style.height = 'auto'
		el.style.height = `${el.scrollHeight}px`
	}
}

export default function Terminal() {
	const { isLoading, profile, history, setHistory } = useAppState()
	const isKeyboardOpen = useDetectKeyboardOpen()
	const messagesContainerRef = useRef<HTMLDivElement>(null)
	const textareaRef = useRef<HTMLTextAreaElement>(null)
	const [value, setValue] = useState('')
	const callAgent = useAgent()
	const chat_id = useMemo(() => profile.chat_ids.at(-1) as string, [profile])
	const messages = useMemo(
		() => (
			<>
				{history[chat_id].map((msg, idx) => {
					const parsed_messages =
						msg.role === 'agent'
							? (extractToolContent(msg.content, 'search-torrents') as {
									role: string
									content: string
								}[])
							: [{ role: msg.role, content: msg.content }]
					return parsed_messages.map((parsed_msg, contentIdx) => {
						const msgKey = btoa(`${chat_id}-${idx}-${contentIdx}`)
						return <Message key={msgKey} msg={parsed_msg} />
					})
				})}
			</>
		),
		[history, chat_id]
	)

	const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		!isLoading && setValue(e.target.value)
	}

	const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (event.key === 'Enter') {
			event.preventDefault()
			const message = value.trim()
			if (message) {
				setValue('')
				const new_history = {
					...history,
					[chat_id]: [...history[chat_id], { role: 'you', content: message }],
				}
				setHistory(new_history)
				callAgent(message, new_history)
			}
		}
	}

	useEffect(() => {
		if (messagesContainerRef.current) {
			messagesContainerRef.current.scrollTop =
				messagesContainerRef.current.scrollHeight
			adjustHeight(textareaRef)
		}
	}, [history, value, isKeyboardOpen])

	return (
		<TerminalFrame subTitle='terminal'>
			<Background />
			<div
				ref={messagesContainerRef}
				className='flex flex-col w-full h-full items-start justify-start p-3 sm:py-4 sm:px-6 gap-3 text-sm overflow-y-auto scrollbar-hide z-40'
			>
				{messages}
				{isLoading && (
					<div>
						<Message
							msg={{
								role: 'agent',
								content: <div className='animate-pulse'>{'*thinking...*'}</div>,
							}}
						/>
					</div>
				)}
			</div>
			<div className='flex flex-row w-full items-start halo-text text-md sm:text-lg bg-gray-950 p-2 pt-1 z-50 border border-green-500'>
				<span className='text-xl sm:text-2xl pr-2 pb-0.5'>{'>'}</span>
				<textarea
					ref={textareaRef}
					id='terminal-input'
					inputMode='text'
					value={value}
					onChange={handleInputChange}
					onKeyDown={handleKeyDown}
					className='outline-none bg-transparent w-full pt-0.5 resize-none min-h-[24px] overflow-hidden placeholder:text-gray-700'
					autoComplete='off'
					placeholder='chat with the agent'
					rows={1}
				/>
			</div>
		</TerminalFrame>
	)
}
