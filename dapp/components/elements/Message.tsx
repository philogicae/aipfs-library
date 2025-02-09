import { cn, type ClassName } from '@components/utils/tw'
import type { TorrentResultsType } from '@components/elements/TorrentList'
import TorrentList from '@components/elements/TorrentList'

export default function Message({
	msg,
	className,
}: { msg: { role: string; content: any }, className?: ClassName }) {
	try {
		const torrent_data =
			typeof msg.content === 'string' &&
			msg.content.startsWith('{') &&
			JSON.parse(msg.content)
		if (typeof torrent_data !== 'boolean' && torrent_data?.torrents?.length > 0) {
			return <TorrentList torrent_data={torrent_data as TorrentResultsType} />
		}
	} catch (e) {}
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
					msg.role === "agent" ? "text-cyan-200" : msg.role === "you" ? "text-orange-200" : "text-violet-300",
				)}
			>
				{`${msg.role}:`}
			</span>
			<span className="halo-text">{msg.content}</span>
		</div>
	)
}