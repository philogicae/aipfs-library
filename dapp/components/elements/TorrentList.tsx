import React from 'react';
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from '@heroui/react';

export interface TorrentType {
    filename: string;
    date: string;
    size: string;
    magnetLink: string;
    seeders: number;
    leechers: number;
    uploader: string;
  }

export interface TorrentResultsType {
	torrentList: TorrentType[];
}

const columns = [
    { key: 'filename', value: 'filename' },
    { key: 'date', value: 'date' },
    { key: 'size', value: 'size' },
    { key: 'seeders', value: 'seeders' },
    { key: 'leechers', value: 'leechers' },
	
];

export default function TorrentList({ torrents } :{ torrents: TorrentResultsType }) {
	const dataSource = torrents?.torrentList?.map((torrent) => ({
		filename: torrent.filename,
		date: torrent.date,
		size: torrent.size,
		seeders: torrent.seeders,
		leechers: torrent.leechers,
	}));

	return (
		<Table aria-label="Simple table">
		<TableHeader>
			{columns?.map((column) => (
				<TableColumn key={column.key}>{column.value}</TableColumn>
			))}
		</TableHeader>
		<TableBody>
			{dataSource?.map((torrent) => (
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
	)
}