'use client'

import TerminalFrame from '@components/elements/TerminalFrame'
import PageWrapper from '@components/layout/PageWrapper'
import { ExclamationCircleIcon } from '@heroicons/react/24/outline'
import { Button } from '@heroui/react'
import { useRouter } from 'next/navigation'

export default function NotFound() {
	const router = useRouter()
	return (
		<PageWrapper>
			<TerminalFrame subTitle="lost signal">
				<div className="flex flex-col items-center justify-center w-full h-full gap-2 pb-8">
					<ExclamationCircleIcon className="w-24 h-24 text-red-500" />
					<div className="text-4xl font-bold text-gray-200 leading-relaxed">
						404 NOT FOUND
					</div>
					<div className="text-lg text-gray-500 leading-relaxed">
						the page does not exist
					</div>
					<Button
						className="mt-3 font-extrabold text-black text-sm"
						onPress={() => router.push('/')}
						radius="sm"
						color="success"
						size="sm"
					>
						go to terminal
					</Button>
				</div>
			</TerminalFrame>
		</PageWrapper>
	)
}
