'use client'

import Home from '@components/frames/Home'
import Loading from '@components/frames/Loading'
import NotFound from '@components/frames/NotFound'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { createHashRouter, redirect } from 'react-router'
import { RouterProvider } from 'react-router/dom'

const hydrateFallbackElement = <Loading />
const hashRouter = createHashRouter([
	{
		path: '',
		element: <Home />,
		hydrateFallbackElement,
	},
	{ path: '404', element: <NotFound />, hydrateFallbackElement },
	{ path: '*', loader: async () => redirect('404'), hydrateFallbackElement },
])

export default function Router() {
	const router = useRouter()
	useEffect(() => {
		if (window.location.pathname + window.location.hash === '/')
			router.replace('/#/')
	}, [router])

	if (typeof window !== 'undefined') {
		const storedVersion = localStorage.getItem('appVersion')
		if (storedVersion !== process.env.version) {
			localStorage.setItem('appVersion', process.env.version as string)
			window.location.reload()
		}
	}

	useEffect(() => {
		console.log(`appVersion v${process.env.version}`)
	}, [])

	return <RouterProvider router={hashRouter} />
}
