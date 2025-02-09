import { cn, type ClassName } from '@components/utils/tw';
import type { TorrentResultsType } from '@components/elements/TorrentList';
import TorrentList from './TorrentList';

export default function Message({
	msg,
  className,
}: { msg: { role: string; content: any }, className?: ClassName }) {

	try {
		const torrentList = JSON.parse(msg.content) as TorrentResultsType
		if (torrentList.torrentList.length !== 0) {
			return <TorrentList torrents={torrentList} />
		}
		console.log(torrentList)
	} catch (e) {
		console.log(e)
	}
	
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