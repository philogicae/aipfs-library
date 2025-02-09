import { useAppState } from '@components/context/AppState'
import { cn } from '@components/utils/tw'
import { Image } from '@heroui/react'

export default function Background() {
	const { hasTyped } = useAppState()

	return (
		<div
			className={cn(
				'absolute flex w-full h-full justify-center items-center transition-opacity duration-1000 pb-8 z-0',
				hasTyped ? 'opacity-15' : 'opacity-70'
			)}
		>
			<Image src="logo.png" alt="logo" radius="sm" width={400} />
		</div>
	)
}
