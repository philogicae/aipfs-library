import Message from '@components/elements/Message'
import {
	Table,
	TableBody,
	TableCell,
	TableColumn,
	TableHeader,
	TableRow,
} from '@heroui/react'

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
			aria-label='torrent-list'
			isCompact
			removeWrapper
			selectionMode='single'
			topContent={
				<Message msg={{ role: 'tool', content: 'search-torrents' }} />
			}
			topContentPlacement='inside'
		>
			<TableHeader>
				{columns.map((column) => (
					<TableColumn key={column.key}>{column.value}</TableColumn>
				))}
			</TableHeader>
			<TableBody>
				{dataSource.map((torrent, index) => (
					<TableRow key={`${torrent.filename}-${index}`}>
						<TableCell>
							{torrent.filename.slice(0, 64) +
								(torrent.filename.length > 64 ? '...' : '')}
						</TableCell>
						<TableCell>{torrent.date}</TableCell>
						<TableCell>{torrent.size}</TableCell>
						<TableCell>{torrent.seeders}</TableCell>
						<TableCell>{torrent.leechers}</TableCell>
					</TableRow>
				))}
			</TableBody>
		</Table>
	) : (
		<Message msg={{ role: 'tool', content: 'search-torrents -> no result' }} />
	)
}
