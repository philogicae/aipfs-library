import {
	Table,
	TableHeader,
	TableColumn,
	TableBody,
	TableRow,
	TableCell,
} from '@heroui/react'
import Message from '@components/elements/Message'

export interface TorrentType {
	filename: string
	date: string
	size: string
	magnet_link: string
	seeders: number
	leechers: number
	uploader: string
}

export interface TorrentResultsType {
	torrents: TorrentType[]
}

const columns = [
	{ key: 'filename', value: 'filename' },
	{ key: 'date', value: 'date' },
	{ key: 'size', value: 'size' },
	{ key: 'seeders', value: 'seeders' },
	{ key: 'leechers', value: 'leechers' },
]

export default function TorrentList({
	torrent_data,
}: {
	torrent_data: TorrentResultsType
}) {
	const dataSource = torrent_data?.torrents?.map((torrent) => ({
		filename: torrent.filename,
		date: torrent.date,
		size: torrent.size,
		seeders: torrent.seeders,
		leechers: torrent.leechers,
	}))

	return dataSource ? (
		<Table
			aria-label="torrent-list"
			isCompact
			removeWrapper
			selectionMode="single"
			topContent={
				<Message msg={{ role: 'tool', content: 'search-torrents' }} />
			}
			topContentPlacement="inside"
		>
			<TableHeader>
				{columns.map((column) => (
					<TableColumn key={column.key}>{column.value}</TableColumn>
				))}
			</TableHeader>
			<TableBody>
				{dataSource.map((torrent) => (
					<TableRow key={torrent.filename}>
						<TableCell>{torrent.filename}</TableCell>
						<TableCell>{torrent.date}</TableCell>
						<TableCell>{torrent.size}</TableCell>
						<TableCell>{torrent.seeders}</TableCell>
						<TableCell>{torrent.leechers}</TableCell>
					</TableRow>
				))}
			</TableBody>
		</Table>
	) : (
		<></>
	);
}
