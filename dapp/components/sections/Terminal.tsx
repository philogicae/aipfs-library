import { useState, useRef, useEffect } from "react"
import { FaRegWindowRestore, FaXmark, FaRegWindowMinimize } from "react-icons/fa6"

export default function Terminal() {
  const [value, setValue] = useState("")
  const [history, setHistory] = useState<string[]>(['How can I help you today?'])
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const adjustHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${textarea.scrollHeight}px`
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value)
    adjustHeight()
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      const trimmedValue = value.trim()
      if (trimmedValue) {
        setHistory([...history, trimmedValue, 'How can I help you today?'])
        setValue('')
        adjustHeight()
      }
    }
  }

  useEffect(() => {
    adjustHeight()
  }, [])

  return (
    <div className="flex flex-col sm:text-3xl font-mono w-full h-full justify-between border border-green-300 rounded-md shadow-sm shadow-green-200">
      <div className="flex w-full h-5 justify-between text-sm text-[#baffdb] border-green-300 border-b pl-1 pr-0.5">
        <span className="font-semibold">aipfs-library</span>
        <div className="flex flex-row gap-1 items-center justify-center">
          <FaRegWindowMinimize />
          <FaRegWindowRestore className="ml-1" />
          <FaXmark className="text-lg" />
        </div>
      </div>
      <div className="flex flex-col w-full h-full items-start justify-start halo-text pl-3 py-2 text-sm">
        {history.map((item, index) => {
          const msgId = `msg-${index}`
          return (index % 2 === 0) ? (
            <span key={msgId} className="py-2">{'Agent: '}{item}</span>
          ) : (
            <span key={msgId} className="py-2">{'You: '}{item}</span>
          )
        })}
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
          placeholder="Enter an instruction"
          rows={1}
        />
      </div>
    </div>
  )
}