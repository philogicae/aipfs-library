import { Image } from '@heroui/react'

export default function Background() {
	return (
		<div className='absolute flex w-full h-full justify-center items-center pb-8 z-0 opacity-5'>
			<Image src='logo.png' alt='logo' radius='sm' width={450} />
		</div>
	)
}
