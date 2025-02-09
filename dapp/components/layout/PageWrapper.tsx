import Background from '@components/frames/Background'

export default function PageWrapper({ children }: { children: React.ReactNode }) {
	return (
		<div className="absolute flex flex-col items-center justify-center w-full h-full px-1.5 py-2">
			<Background />
			{children}
		</div>
	)
}
