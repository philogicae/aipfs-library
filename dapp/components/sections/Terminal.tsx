import Message from "@components/elements/Message"
import { useState, useRef, useEffect } from "react"
import {TerminalFrame} from '@components/elements/TerminalFrame'
import Background from '@components/frames/Background'

export default function Terminal() {
  const [value, setValue] = useState("")
  const [history, setHistory] = useState<string[]>(['How can I help you today?'])
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  const adjustHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${textarea.scrollHeight}px`
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value)
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      const trimmedValue = value.trim()
      if (trimmedValue) {
        setHistory([...history, trimmedValue, 'How can I help you today?'])
        setValue('')
      }
    }
  }

  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
      adjustHeight()
    }
  }, [history, value])

  return (
    <TerminalFrame subTitle="terminal">
      <Background />
      <div 
        ref={messagesContainerRef}
        className="flex flex-col w-full h-full items-start justify-start pl-3 py-2 text-sm overflow-y-auto scrollbar-hide"
      >
        {history.map((item, index) => (
          <Message 
            key={`msg-${index}`}
            text={item}
            isAgent={index % 2 === 0}
          />
        ))}
      </div>
      <div className="flex flex-row w-full items-start halo-text text-md sm:text-lg bg-gray-900 p-2 pt-1">
        <span className="text-xl sm:text-2xl pr-2 pb-0.5">{'>'}</span>
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
  )
}