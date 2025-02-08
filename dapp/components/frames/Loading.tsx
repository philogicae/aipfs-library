export default function Loading() {
	return (
		<div className="absolute flex flex-col items-center justify-center w-full h-full">
			<div className="h-12 w-12 animate-spin rounded-full border-3 border-solid border-current border-r-transparent motion-reduce:animate-[spin_1.5s_linear_infinite]"/>
		</div>
	)
}
