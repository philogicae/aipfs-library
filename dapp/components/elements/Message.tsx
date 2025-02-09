import { cn, type ClassName } from '@components/utils/tw';

export default function Message({
	msg,
  className,
}: { msg: { role: string; content: any }, className?: ClassName }) {
	return (
		<div
			className={cn(
				"flex flex-row w-full items-start font-mono text-sm sm:text-base",
				className,
			)}
		>
			<span
				className={cn(
					"font-semibold mr-1.5",
					msg.role === "agent" ? "text-cyan-200" : "text-orange-200",
				)}
			>
				{`${msg.role}:`}
			</span>
			<span className="halo-text">{msg.content}</span>
		</div>
	)
}