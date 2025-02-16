'use client'

import TerminalFrame from '@components/elements/TerminalFrame'
import PageWrapper from '@components/layout/PageWrapper'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { Button } from '@heroui/react'
import { useNavigate } from 'react-router'

export default function Unavailable() {
	const navigate = useNavigate()
	return (
		<PageWrapper>
			<TerminalFrame subTitle='lost signal'>
				<div className='flex flex-col items-center justify-center w-full h-full gap-2 pb-8'>
					<ExclamationTriangleIcon className='w-24 h-24 text-orange-500' />
					<div className='text-4xl font-bold text-gray-200 leading-relaxed'>
						AGENT UNAVAILABLE
					</div>
					<div className='text-lg text-gray-500 leading-relaxed'>
						maybe the agent is not feeling well
					</div>
					<Button
						className='mt-3 font-extrabold text-black text-sm'
						onPress={() => navigate('/')}
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
