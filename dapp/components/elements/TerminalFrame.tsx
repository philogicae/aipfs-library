import {
	FaRegWindowMinimize,
	FaRegWindowRestore,
	FaXmark,
} from 'react-icons/fa6'

export function TerminalFrame({
	children,
	subTitle,
}: { children: React.ReactNode; subTitle: string }) {
	return (
		<div className='flex flex-col sm:text-3xl font-mono w-full h-full items-center justify-between border border-green-500 rounded-md shadow-sm shadow-green-200'>
			<div className='flex w-full h-5 justify-between text-sm text-[#baffdb] border-green-500 border-b pl-1 pr-0.5'>
				<span className='font-semibold'>aipfs-library: {subTitle} </span>
				<div className='flex flex-row gap-1 items-center justify-center'>
					<FaRegWindowMinimize />
					<FaRegWindowRestore className='ml-1' />
					<FaXmark className='text-lg' />
				</div>
			</div>
			{children}
		</div>
	)
}

export default TerminalFrame
