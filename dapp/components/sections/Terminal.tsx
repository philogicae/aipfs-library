import { useState } from "react"
import { FaRegWindowRestore, FaXmark, FaRegWindowMinimize } from "react-icons/fa6"

export default function Terminal() {
  const [input, setInput] = useState("")
  const [history, setHistory] = useState<string[]>(['How can I help you today?'])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      setHistory([...history, input, 'How can I help you today?'])
      setInput('')
    }
  }

  return (
    <div className="flex flex-col sm:text-3xl font-mono w-full h-full justify-between border border-green-300 rounded-md shadow-sm shadow-green-200">
      <div className="flex w-full h-5 justify-between text-sm text-[#baffdb] border-green-300 border-b pl-1 pr-0.5">
        <span className="font-semibold">Terminal</span>
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
      <div className="flex flex-row w-full items-start halo-text pl-3 pb-2 text-xl sm:text-2xl">
      <span className="pr-2">{'>'}</span>
        <input
          id="terminal-input"
          type="text"
          value={input}
          onChange={handleInputChange} 
          onKeyDown={handleKeyDown}
          className="outline-none bg-transparent w-full"
          // biome-ignore lint/a11y/noAutofocus: <explanation>
          autoFocus
        />
      </div>
    </div>
  )
}