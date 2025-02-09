import { useEffect, useState } from 'react'
import { cn } from '@components/utils/tw'
import { Image } from "@heroui/react"

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
        <div className={cn('absolute flex w-full h-full justify-center items-center transition-opacity ease-in-out duration-1000 pb-8 z-0', isTyping ? 'opacity-15' : 'opacity-70')}>
            <Image
                src='logo.png'
                alt="logo"
                radius="sm"
                width={400}
            />
        </div>
    )
}