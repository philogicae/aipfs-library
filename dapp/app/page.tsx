'use client'

import Home from '@components/frames/Home'
import Loading from '@components/frames/Loading'
import NotFound from '@components/frames/NotFound'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { createHashRouter, redirect } from 'react-router'
import { RouterProvider } from 'react-router/dom'

const hydrateFallbackElement = <Loading />

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

	const [hashRouter, setHashRouter] = useState<any>()
	useEffect(() => {
		console.log(`appVersion v${process.env.version}`)
		setHashRouter(
			createHashRouter([
				{
					path: '',
					element: <Home />,
					hydrateFallbackElement,
				},
				{ path: '404', element: <NotFound />, hydrateFallbackElement },
				{
					path: '*',
					loader: async () => redirect('404'),
					hydrateFallbackElement,
				},
			])
		)
	}, [])

	if (!hashRouter) return <Loading />
	return <RouterProvider router={hashRouter} />
}
