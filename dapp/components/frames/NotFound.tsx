'use client'

import TerminalFrame from '@components/elements/TerminalFrame'
import PageWrapper from '@components/layout/PageWrapper'
import { ExclamationCircleIcon } from '@heroicons/react/24/outline'
import { Button } from '@heroui/react'
import { useNavigate } from 'react-router'
import { useRouter } from 'next/navigation'

function NotFound({ redirect_func }: { redirect_func: () => void }) {
	return (
		<PageWrapper>
			<TerminalFrame subTitle='lost signal'>
				<div className='flex flex-col items-center justify-center w-full h-full gap-2 pb-8'>
					<ExclamationCircleIcon className='w-24 h-24 text-red-500' />
					<div className='text-4xl font-bold text-gray-200 leading-relaxed'>
						404 NOT FOUND
					</div>
					<div className='text-lg text-gray-500 leading-relaxed'>
						this page does not exist
					</div>
					<Button
						className='mt-3 font-extrabold text-black text-sm'
						onPress={redirect_func}
						radius='sm'
						color='success'
						size='sm'
					>
						go to terminal
					</Button>
				</div>
			</TerminalFrame>
		</PageWrapper>
	)
}

export function NotFoundOut() {
	const router = useRouter()
	return (
		<NotFound
			redirect_func={() => {
				console.log('native-router')
				router.push('/')
			}}
		/>
	)
}

export function NotFoundIn() {
	const navigate = useNavigate()
	return (
		<NotFound
			redirect_func={() => {
				console.log('navigate')
				navigate('/')
			}}
		/>
	)
}
