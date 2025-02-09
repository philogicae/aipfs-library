"use client"

import type React from 'react'
import { useEffect, useState } from 'react'
import logo from '../../public/logo.png'

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
        <div className={`absoluteflex justify-center items-center absolute w-full h-full ${isTyping ? 'opacity-10' : 'opacity-65'} transition-opacity ease-in-out duration-1000`}>
            <div className="h-full w-full justify-center items-center bg-center bg-contain bg-no-repeat" style={{ backgroundImage: `url(${logo.src})` }} />
        </div>
    )
}