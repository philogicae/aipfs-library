import { cn, ClassName } from '@components/utils/tw'

interface MessageProps {
  text: string
  isAgent?: boolean
  className?: ClassName
}

export default function Message({ text, isAgent = true, className = null }: MessageProps) {
  return (
    <div className={cn(`flex flex-row items-start py-1 font-mono text-sm`, className)}>
      <span className={cn("font-semibold mr-1", isAgent ? 'text-cyan-200': 'text-orange-200')}>
        {isAgent ? 'Agent:' : 'You:'}
      </span>
      <span className='halo-text'>{text}</span>
    </div>
  )
}