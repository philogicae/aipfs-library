import { useEffect, useState } from 'react'
import logo from '../../public/logo.png'
import { cn } from '@components/utils/tw'

export default function Background() {
    const [isTyping, setIsTyping] = useState(false)

    useEffect(() => {
        const handleKeyDown = () => setIsTyping(true)
        window.addEventListener('keydown', handleKeyDown)
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
        }
    }, [])

    return (
        <div className={cn('absolute flex w-full h-full justify-center items-center transition-opacity ease-in-out duration-1000', isTyping ? 'opacity-10' : 'opacity-65')}>
            <div className="h-full w-full justify-center items-center bg-center bg-contain bg-no-repeat" style={{ backgroundImage: `url(${logo.src})` }} />
        </div>
    )
}